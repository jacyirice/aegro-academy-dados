from airflow.models import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from daglibs.twitter.twitter import search_tweets_by_hashtag_and_lang
from helpers.functions import processing_tweets_hashtags, processing_users, get_conn_psql, storing_users, storing_tweets_hashtags

default_args = {
    'start_date': datetime(2022, 6, 5),
    'retry_delay': timedelta(minutes=1),
    'retries': 1,
}

with DAG('twitter_processing',
         schedule_interval=timedelta(minutes=5),
         default_args=default_args,
         catchup=False) as dag:

    extract_tweets_t = PythonOperator(
        task_id='extract_tweets',
        python_callable=search_tweets_by_hashtag_and_lang,
        op_kwargs={"hashtag": 'bolhadev'},
    )

    processing_users_t = PythonOperator(
        task_id='processing_users',
        python_callable=processing_users,
    )

    storing_users_t = PythonOperator(
        task_id='storing_users',
        python_callable=storing_users,
        op_kwargs={"conn": get_conn_psql()},
    )

    processing_tweets_hashtags_t = PythonOperator(
        task_id='processing_tweets_hashtags',
        python_callable=processing_tweets_hashtags,
    )

    storing_tweets_hashtags_t = PythonOperator(
        task_id='storing_tweets_hashtags',
        python_callable=storing_tweets_hashtags,
        op_kwargs={"conn": get_conn_psql()},
    )

    extract_tweets_t >> processing_users_t >> storing_users_t >> processing_tweets_hashtags_t >> storing_tweets_hashtags_t
