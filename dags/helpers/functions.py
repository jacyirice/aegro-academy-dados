from airflow.providers.postgres.operators.postgres import PostgresHook
from pandas import json_normalize, read_json, DataFrame
from psycopg2.extensions import connection

from daglibs.database.postgres import PostgreSQL
from daglibs.twitter.twitter import format_users, format_tweets_and_hashtags_in_dicts


def get_conn_psql() -> connection:
    return PostgresHook(
        postgres_conn_id="db_aegro_postgres",
    ).get_conn()


def processing_users(ti) -> None:
    users = ti.xcom_pull(task_ids='extract_tweets', key='users')
    processed_users = json_normalize(format_users(users))
    processed_users.to_json('/tmp/processed_users.json')


def processing_tweets_hashtags(ti) -> None:
    tweets = ti.xcom_pull(task_ids='extract_tweets', key='tweets')
    tweets_formated, hashtags_formated = format_tweets_and_hashtags_in_dicts(
        tweets)

    processed_tweets = json_normalize(tweets_formated)
    processed_hashtags = json_normalize(hashtags_formated)
    processed_tweets.to_json('/tmp/processed_tweets.json')
    processed_hashtags.to_json('/tmp/processed_hashtags.json')


def storing_users(conn: connection) -> None:
    processed_users = read_json('/tmp/processed_users.json')

    db = PostgreSQL(conn)
    db.insert_or_update(
        table="t_users",
        list_fields=processed_users.columns,
        list_objs=processed_users,
        unique_key_name="author_id",
    )


def storing_tweets_hashtags(conn: connection) -> None:
    processed_tweets = read_json('/tmp/processed_tweets.json')
    processed_hashtags = read_json('/tmp/processed_hashtags.json')

    db = PostgreSQL(conn)
    tweets_ids = db.insert_or_update(
        table="t_tweets",
        list_fields=processed_tweets.columns,
        list_objs=processed_tweets,
        unique_key_name="tweet_id",
    )

    tweets_hashtags = DataFrame()
    processed_hashtags_t = processed_hashtags.T
    for i in range(len(processed_hashtags)):
        for hashtag in processed_hashtags_t[i].dropna():
            hashtag_id = db.select_id_or_insert("t_hashtags", "tag", hashtag)

            tweets_hashtags = tweets_hashtags.append(
                {"tweet_id": tweets_ids[i][0], "hashtag_id": hashtag_id}, ignore_index=1
            )

    db.insert_or_nothing(
        table="t_tweets_hashtags",
        list_fields=tweets_hashtags.columns,
        list_objs=tweets_hashtags,
        unique_key_name="tweet_id, hashtag_id",
    )


def get_five_users_with_most_followers(conn: connection, tag: str) -> list:
    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT u.name, u.username, u.public_metrics_followers_count FROM t_users AS u 
                WHERE U.author_id IN (
                SELECT author_id FROM t_tweets AS t
                INNER JOIN t_tweets_hashtags AS th ON th.tweet_id = t.id
                INNER JOIN t_hashtags AS h ON h.id = th.hashtag_id
                WHERE h.tag=%s)
                ORDER BY u.public_metrics_followers_count DESC LIMIT 5;""",
            (tag,),
        )
        return cursor.fetchall()


def count_tweets_by_tag_group_by_date(conn: connection, tag: str) -> list:
    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT COUNT(t.id), date(t.created_at) FROM t_tweets AS t 
                INNER JOIN t_tweets_hashtags AS th ON th.tweet_id = t.id
                INNER JOIN t_hashtags AS h ON h.id = th.hashtag_id
                WHERE h.tag = %s
                GROUP BY date(created_at)""",
            (tag,),
        )
        return cursor.fetchall()


def count_tweets_by_tag(conn: connection, tag: str) -> int:
    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT COUNT(t.id) FROM t_tweets AS t 
                INNER JOIN t_tweets_hashtags AS th ON th.tweet_id = t.id
                INNER JOIN t_hashtags AS h ON h.id = th.hashtag_id
                WHERE h.tag=%s""",
            (tag,),
        )
        return cursor.fetchone()[0]
