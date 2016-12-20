from nltk.corpus import stopwords
from textblob.classifiers import NaiveBayesClassifier
from preprocessing import get_tweets


MAX_TWEETS = 500
SPLIT_SETS = 400

def linguistic_preprocess(tweet):
    return tweet

tweets = []
for i, single_tweet in enumerate(get_tweets()):
    if i >= MAX_TWEETS:
        break
    tweet, emojis, raw_tweet = single_tweet
    tweets.append((linguistic_preprocess(tweet), emojis[0])) # just getting one emoji

training_set = tweets[:SPLIT_SETS]
test_set = tweets[SPLIT_SETS:]

cl = NaiveBayesClassifier(training_set)
print("accuracy on test set:")
print(cl.accuracy(test_set))
