# import requests
# import json
import tweepy

from .constants import MY_BEARER_TOKEN, TWEET_FIELDS, USER_FIELDS, MAX_RESULTS, EXPANSIONS

def format_users_in_dicts(users: list) -> list:
    users_formated = []

    for user in users:
        users_formated.append({
            "author_id": user.id,
            "created_at": str(user.created_at),
            "name": user.name,
            "username": user.username,
            "profile_image_url": user.profile_image_url,
            "url": user.url,
            "protected": user.protected,
            "verified": user.verified,
            "public_metrics_followers_count": user.public_metrics.get('followers_count'),
            "public_metrics_following_count": user.public_metrics.get('following_count'),
            "public_metrics_tweet_count": user.public_metrics.get('tweet_count'),
            "public_metrics_listed_count": user.public_metrics.get('listed_count'),
        })

    return users_formated


def format_hashtags(hashtags):
    return [{'tag': h.get('tag').lower()} for h in hashtags]


def format_tweets_in_dicts(tweets: list) -> list:
    tweets_formated = []

    for tweet in tweets:
        tweets_formated.append({
            "tweet_id": tweet.id,
            "author_id": tweet.author_id,
            "created_at": str(tweet.created_at),
            "lang": tweet.lang,
            "text": tweet.text,
            "public_metrics_retweet_count": tweet.public_metrics.get('retweet_count'),
            "public_metrics_reply_count": tweet.public_metrics.get('reply_count'),
            "public_metrics_like_count": tweet.public_metrics.get('like_count'),
            "public_metrics_quote_count": tweet.public_metrics.get('quote_count'),
            "hashtags": format_hashtags(tweet.entities.get('hashtags', []))
        })

    return tweets_formated


def format_tweets_and_hashtags_in_dicts(tweets: list) -> list:
    tweets_formated = []
    hashtags_formated = []

    for tweet in tweets:
        tweets_formated.append({
            "tweet_id": tweet.id,
            "author_id": tweet.author_id,
            "created_at": str(tweet.created_at),
            "lang": tweet.lang,
            "text": tweet.text,
            "public_metrics_retweet_count": tweet.public_metrics.get('retweet_count'),
            "public_metrics_reply_count": tweet.public_metrics.get('reply_count'),
            "public_metrics_like_count": tweet.public_metrics.get('like_count'),
            "public_metrics_quote_count": tweet.public_metrics.get('quote_count'),
        })
        hashtags_formated.append(format_hashtags(
            tweet.entities.get('hashtags', [])))

    return tweets_formated, hashtags_formated


def search_tweets_by_hashtag_and_lang(hashtag: str, lang: str = 'pt') -> list:
    query = f'{hashtag} lang:{lang} -is:retweet'

    client = tweepy.Client(bearer_token=MY_BEARER_TOKEN)
    tweets = client.search_recent_tweets(
        query=query,
        tweet_fields=TWEET_FIELDS,
        user_fields=USER_FIELDS,
        max_results=MAX_RESULTS,
        expansions=EXPANSIONS,
    )

    return tweets


if __name__ == '__main__':
    tweets = search_tweets_by_hashtag_and_lang('#bolhadev')
    tweets_formated = format_tweets_in_dicts(tweets[0])
    users_formated = format_users_in_dicts(tweets[1].get('users'))

    for tweet in tweets_formated:
        print(tweet['text'][:10], '-', tweet['lang'])
    print(len(tweets_formated))
