from airflow.models import Variable

TWITTER_BEARER_TOKEN = Variable.get("TWITTER_BEARER_TOKEN")
USER_FORMAT = {
    "tweet_id": None,
    "author_id": None,
    "created_at": None,
    "name": None,
    "username": None,
    "profile_image_url": None,
    "url": None,
    "protected": None,
    "verified": None,
    "public_metrics_followers_count": None,
    "public_metrics_following_count": None,
    "public_metrics_tweet_count": None,
    "public_metrics_listed_count": None,
}
TWEET_FORMAT = {
    "id": None,
    "author_id": None,
    "created_at": None,
    "lang": None,
    "text": None,
    "public_metrics_retweet_count": None,
    "public_metrics_reply_count": None,
    "public_metrics_like_count": None,
    "public_metrics_quote_count": None,
}

TWEET_FIELDS = [
    "id",
    "created_at",
    "text",
    "author_id",
    "public_metrics",
    "lang",
    "entities",
]
USER_FIELDS = [
    "id",
    "created_at",
    "name",
    "username",
    "profile_image_url",
    "url",
    "public_metrics",
    "protected",
    "verified",
]
MAX_RESULTS = 100
EXPANSIONS = "author_id"
