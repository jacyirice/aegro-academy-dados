from database.gera_conexao import aegro_db
from twitter.twitter import (search_tweets_by_hashtag_and_lang,
                     format_users_in_dicts,
                     format_tweets_and_hashtags_in_dicts, )

tweets = search_tweets_by_hashtag_and_lang('#bolhadev')

tweets_formated, hashtags_formated = format_tweets_and_hashtags_in_dicts(
    tweets[0])
users_formated = format_users_in_dicts(tweets[1].get('users'))

aegro_db.insert_many('t_users', users_formated[0].keys(), users_formated)
tweets_ids = aegro_db.insert_many(
    't_tweets', tweets_formated[0].keys(), tweets_formated)

tweets_hashtags_formated = []
for i in range(len(hashtags_formated)):
    for hashtag in hashtags_formated[i]:
        hashtag_id = aegro_db.select_id_or_insert('t_hashtags', 'tag', hashtag)

        tweets_hashtags_formated.append({
            'tweet_id': tweets_ids[i][0],
            'hashtag_id': hashtag_id
        })

aegro_db.insert_many('t_tweets_hashtags',
                     tweets_hashtags_formated[0].keys(), tweets_hashtags_formated)
