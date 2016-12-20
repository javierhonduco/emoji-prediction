from nltk.corpus import stopwords
from textblob.classifiers import NaiveBayesClassifier
from preprocessing import get_tweets


MAX_TWEETS = 1000000000
emoji_stats = {}
usually_together = {}

def count_emojis(emojis):
    for emoji in emojis:
        if emoji in emoji_stats:
            emoji_stats[emoji] += 1
        else:
            emoji_stats[emoji] = 1

def count_together_emojis(emojis):
    emojis_set = set(emojis)
    for emoji in emojis_set:
        if emoji in usually_together:
            for emoji_friend in (emojis_set-{emoji}):
                if emoji_friend in usually_together[emoji]:
                    usually_together[emoji][emoji_friend] += 1
                else:
                    usually_together[emoji][emoji_friend] = 1
        else:
            usually_together[emoji] = {}

for i, single_tweet in enumerate(get_tweets()):
    if i >= MAX_TWEETS:
        break
    print("{}...".format(i))
    tweet, emojis, raw_tweet = single_tweet
    count_emojis(emojis)
    count_together_emojis(emojis)

print("tip, run with -i")
print("`emoji_stats`, `usually_together`")
