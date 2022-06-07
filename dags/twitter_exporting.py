from json import dump
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from datetime import datetime, timedelta

from helpers.functions import (get_conn_psql,
                               count_tweets_by_tag,
                               count_tweets_by_tag_group_by_date,
                               get_five_users_with_most_followers)

default_args = {
    'start_date': datetime(2022,  6,  5),
    'retry_delay': timedelta(minutes=5),
    'retries': 1,
}


def _get_exports(hashtag: str) -> None:
    conn = get_conn_psql()

    total_tweets = count_tweets_by_tag(conn, hashtag)
    total_tweets_group_by_day = [{
        'total': t[0],
        'date': str(t[1])
    } for t in count_tweets_by_tag_group_by_date(conn, hashtag)]
    five_users = [{
        'name': u[0],
        'username': u[1],
        'total_followers': u[2]
    } for u in get_five_users_with_most_followers(conn, hashtag)]

    with open('/tmp/exports_tweets.json', 'w') as file:
        dump({
            'hashtag': hashtag,
            'total_tweets': total_tweets,
            'five_users_with_most_followers': five_users,
            'total_tweets_group_by_date': total_tweets_group_by_day
        }, file, indent=4, ensure_ascii=False)

def _get_message() -> str:
    try:
        with open('/tmp/exports_tweets.json', 'r') as file:
            exports = file.read()
    except FileNotFoundError:
        exports = ''
        
    return f"""
        Seu relatorio diario está pronto!
        ```{exports}```
    """


with DAG('twitter_exporting', schedule_interval=timedelta(days=1),
         default_args=default_args,
         catchup=False) as dag:

    get_exports = PythonOperator(
        task_id='get_exports',
        python_callable=_get_exports,
        op_kwargs={"hashtag": 'bolhadev'},
    )

    send_slack_exports = SlackWebhookOperator(
        task_id='send_slack_exports',
        http_conn_id='slack_conn',
        message=_get_message(),
        attachments={

        }
    )

    get_exports >> send_slack_exports
