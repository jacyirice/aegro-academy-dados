import requests
from .constants import (
    TWITTER_BEARER_TOKEN,
    TWEET_FIELDS,
    USER_FIELDS,
    MAX_RESULTS,
    EXPANSIONS,
)


def format_users_in_dicts(users: list) -> list:
    users_formated = [{
        "author_id": user['id'],
        "created_at": user['created_at'],
        "name": user['name'],
        "username": user['username'],
        "profile_image_url": user['profile_image_url'],
        "url": user['url'],
        "protected": user['protected'],
        "verified": user['verified'],
        "public_metrics_followers_count": user['public_metrics'].get(
            "followers_count"
        ),
        "public_metrics_following_count": user['public_metrics'].get(
            "following_count"
        ),
        "public_metrics_tweet_count": user['public_metrics'].get("tweet_count"),
        "public_metrics_listed_count": user['public_metrics'].get("listed_count"),
    } for user in users]

    return users_formated


def format_hashtags(hashtags: list) -> list:
    return [{"tag": h.get("tag").lower()} for h in hashtags]


def format_tweets_and_hashtags_in_dicts(tweets: list) -> list:
    tweets_formated = []
    hashtags_formated = []

    for tweet in tweets:
        tweets_formated.append(
            {
                "tweet_id": tweet['id'],
                "author_id": tweet['author_id'],
                "created_at": tweet['created_at'],
                "lang": tweet['lang'],
                "text": tweet['text'],
                "public_metrics_retweet_count": tweet['public_metrics'].get(
                    "retweet_count"
                ),
                "public_metrics_reply_count": tweet['public_metrics'].get("reply_count"),
                "public_metrics_like_count": tweet['public_metrics'].get("like_count"),
                "public_metrics_quote_count": tweet['public_metrics'].get("quote_count"),
            }
        )
        hashtags_formated.append(format_hashtags(
            tweet['entities'].get("hashtags", [])))

    return tweets_formated, hashtags_formated


def search_tweets_by_hashtag_and_lang(ti, hashtag: str, lang: str = "pt") -> list:
    query = requests.utils.quote(f"#{hashtag} lang:{lang} -is:retweet")
    expansions = requests.utils.quote(EXPANSIONS)
    tweet_fields = requests.utils.quote(','.join(TWEET_FIELDS))
    user_fields = requests.utils.quote(','.join(USER_FIELDS))

    headers = {'Authorization': f'Bearer {TWITTER_BEARER_TOKEN}'}
    url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&max_results={MAX_RESULTS}\
&expansions={expansions}&tweet.fields={tweet_fields}&user.fields={user_fields}"

    tweets = requests.get(url, headers=headers).json()

    ti.xcom_push(key='tweets', value=tweets['data'])
    ti.xcom_push(key='users', value=tweets['includes'].get("users"))
