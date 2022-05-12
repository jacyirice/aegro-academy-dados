from database.gera_conexao import get_conn
from twitter.twitter import (
    search_tweets_by_hashtag_and_lang,
    format_users_in_dicts,
    format_tweets_and_hashtags_in_dicts,
)


def get_five_users_with_most_followers(conn, tag):
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


def count_tweets_by_tag_group_by_date(conn, tag):
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


def count_tweets_by_tag(conn, tag):
    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT COUNT(t.id) FROM t_tweets AS t 
                INNER JOIN t_tweets_hashtags AS th ON th.tweet_id = t.id
                INNER JOIN t_hashtags AS h ON h.id = th.hashtag_id
                WHERE h.tag=%s""",
            (tag,),
        )
        return cursor.fetchone()[0]


def insert_data(tag):
    tweets = search_tweets_by_hashtag_and_lang(f"#{tag}")
    
    if tweets[0] is None:
        return None

    tweets_formated, hashtags_formated = format_tweets_and_hashtags_in_dicts(tweets[0])
    users_formated = format_users_in_dicts(tweets[1].get("users"))

    aegro_db.insert_or_update(
        table="t_users",
        list_fields=users_formated[0].keys(),
        list_objs=users_formated,
        unique_key_name="author_id",
    )
    tweets_ids = aegro_db.insert_or_update(
        table="t_tweets",
        list_fields=tweets_formated[0].keys(),
        list_objs=tweets_formated,
        unique_key_name="tweet_id",
    )

    tweets_hashtags_formated = []
    for i in range(len(hashtags_formated)):
        for hashtag in hashtags_formated[i]:
            hashtag_id = aegro_db.select_id_or_insert("t_hashtags", "tag", hashtag)

            tweets_hashtags_formated.append(
                {"tweet_id": tweets_ids[i][0], "hashtag_id": hashtag_id}
            )

    aegro_db.insert_or_nothing(
        table="t_tweets_hashtags",
        list_fields=tweets_hashtags_formated[0].keys(),
        list_objs=tweets_hashtags_formated,
        unique_key_name="tweet_id, hashtag_id",
    )


if __name__ == "__main__":
    tag = "bolhadev"
    aegro_db = get_conn()
    insert_data(tag)
    
    print('A quantidade de tweets para a tag', tag, 'é:', count_tweets_by_tag(aegro_db.conn, tag))
    
    print('\nA quantidade de tweets para a tag', tag, 'agrupada por data:')
    for t in count_tweets_by_tag_group_by_date(aegro_db.conn, tag):
        print('\t', t[0], 'tweets no dia:', t[1].strftime("%d/%m/%Y"))
    
    print('\nOs cinco usuários com mais seguidores para a tag', tag, 'são:')
    for u in get_five_users_with_most_followers(aegro_db.conn, tag):
        print('\tUsuario:',u[0])
        print('\t\tUsername:',u[1])
        print('\t\tSeguidores:',u[2])
