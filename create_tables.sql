CREATE TABLE "t_users" (
  "id" SERIAL PRIMARY KEY,
  "author_id" varchar NOT NULL,
  "created_at" timestamp,
  "name" varchar NOT NULL,
  "username" varchar NOT NULL,
  "profile_image_url" varchar,
  "url" varchar,
  "protected" boolean,
  "verified" boolean,
  "public_metrics_followers_count" int NOT NULL,
  "public_metrics_following_count" int,
  "public_metrics_tweet_count" int,
  "public_metrics_listed_count" int
);

CREATE TABLE "t_hashtags" (
  "id" SERIAL PRIMARY KEY,
  "tag" varchar NOT NULL
);

CREATE TABLE "t_tweets" (
  "id" SERIAL PRIMARY KEY,
  "tweet_id" varchar NOT NULL,
  "author_id" varchar NOT NULL,
  "created_at" timestamp NOT NULL,
  "lang" varchar NOT NULL,
  "text" varchar NOT NULL,
  "public_metrics_retweet_count" int,
  "public_metrics_reply_count" int,
  "public_metrics_like_count" int,
  "public_metrics_quote_count" int
);

CREATE TABLE "t_tweets_hashtags" (
  "tweet_id" int NOT NULL,
  "hashtag_id" int NOT NULL,
  PRIMARY KEY ("tweet_id", "hashtag_id")
);

CREATE UNIQUE INDEX "index_users_author_id" ON "t_users" ("author_id");

CREATE INDEX "index_users_public_metrics_followers_count" ON "t_users" ("public_metrics_followers_count");

CREATE INDEX "index_tweets_author_id" ON "t_tweets" ("author_id");

CREATE UNIQUE INDEX "index_tweets_tweet_id" ON "t_tweets" ("tweet_id");

CREATE INDEX "index_tweets_created_at" ON "t_tweets" ("created_at");

ALTER TABLE "t_tweets" ADD FOREIGN KEY ("author_id") REFERENCES "t_users" ("author_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "t_tweets_hashtags" ADD FOREIGN KEY ("tweet_id") REFERENCES "t_tweets" ("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "t_tweets_hashtags" ADD FOREIGN KEY ("hashtag_id") REFERENCES "t_hashtags" ("id") ON DELETE CASCADE ON UPDATE CASCADE;
