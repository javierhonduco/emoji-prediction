import sys
import emoji
import math
import pickle
import numpy as np
from time import time
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from preprocessing import get_tweets
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.cluster import KMeans
from sklearn import tree
from sklearn import svm


en_stopwords = set(stopwords.words('english'))
snowball_stemmer = SnowballStemmer('english')

all_emojis = emoji.EMOJI_ALIAS_UNICODE.keys()
emoji_id_mapper = {emoji: id for (id, emoji) in enumerate(all_emojis)}
id_emoji_mapper = {id: emoji for (id, emoji) in enumerate(all_emojis)}

def linguistic_preprocess(tweet):
    without_stopwords = [w for w in tweet.split() if w not in en_stopwords]
    stemmed = [snowball_stemmer.stem(w) for w in without_stopwords]
    return ' '.join(stemmed)

def emojis_balanced_dataset(amount=None, lame_limit=10000, lame_min_classes=100):
    emoji_tweet_map = {}
    data = []
    target = []

    for i, single_tweet in enumerate(get_tweets()):
        if i >= lame_limit:
            break
        [tweet, emojis, raw_tweet] = single_tweet

        first_emoji = emojis[0]
        if first_emoji in emoji_tweet_map:
            emoji_tweet_map[first_emoji].append(tweet)
        else:
            emoji_tweet_map[first_emoji] = [tweet]

    emoji_names_in_dataset = emoji_tweet_map.keys()
    emoji_name_count = [(e, len(emoji_tweet_map[e])) for e in emoji_names_in_dataset]

    for emoji_name, count in emoji_name_count:
        if count < lame_min_classes:
            del emoji_tweet_map[emoji_name]
        else:
            # should probably be random...
            emoji_tweet_map[emoji_name] = emoji_tweet_map[emoji_name][:lame_min_classes]

    for emoji_name, tweets in emoji_tweet_map.items():
        for tweet in tweets:
            data.append(linguistic_preprocess(tweet))
            target.append(emoji_name)

    return [data, None, target]

def emojis_ordered_dataset(amount):
    data = []
    target_multi = []
    target_single = []

    for i, single_tweet in enumerate(get_tweets()):
        if i >= amount:
            break
        [tweet, emojis, raw_tweet] = single_tweet

        data.append(linguistic_preprocess(tweet))
        target_multi.append(set(emojis))
        target_single.append(emojis[0])

    return [data, target_multi, target_single]

def predict(text, vectorizer, classifier):
    cleaned = linguistic_preprocess(text)
    vector = vectorizer.transform([cleaned])
    prediction = classifier.predict(vector.toarray())[0]
    emoji_name = id_emoji_mapper[prediction]
    return emoji_name

def learn_with(classifier, params={}, vectorizer=None, dataset=None, save=True):
    [data, target_multi, target_single] = dataset

    #default_params = {}
    #params = {**params, **default_params}

    vectorizer = TfidfVectorizer(min_df=1)
    X = vectorizer.fit_transform(data)
    with open("trained_models/vectorizer", 'wb') as f:
        f.write(pickle.dumps(vectorizer))

    y = [emoji_id_mapper[c] for c in target_single]

    X_train, X_test, y_train, y_test = train_test_split(
        X.toarray(), y, test_size=1-TRAINING, random_state=42
    )

    b = classifier(**params)

    time_before = time()
    b.fit(X_train, y_train)
    runtime = time() - time_before

    predictions = b.predict(X_test)

    if save:
        with open("trained_models/" + classifier.__name__, 'wb') as f:
            f.write(pickle.dumps(b))

    correct = 0
    for i, prediction in enumerate(predictions):
        if(prediction == y_test[i]):
            correct += 1

    print("using `{}` with params={} over={} different emojis".format(
        classifier.__name__,
        params,
        len(set(target_single))
    ))
    print("accuracy: {0:.2f}%".format(correct/len(predictions)*100))
    print("runtime = {0:.3f}s".format(runtime))
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python sklearn_classifier.py <tweets_number>')
        sys.exit(1)

    MAX_TWEETS = int(sys.argv[1])

    #dataset = emojis_ordered_dataset(MAX_TWEETS)
    dataset = emojis_balanced_dataset()

    TRAINING = 0.8
    TRAIN = int(math.floor(MAX_TWEETS * TRAINING))
    print("total_tweets={} total_training={} diff_emojis={}".format(
        MAX_TWEETS,
        TRAIN,
        len(set(dataset[2]))
    ))

    learn_with(SGDClassifier, dataset=dataset)
    learn_with(MultinomialNB, dataset=dataset)
    learn_with(GaussianNB, dataset=dataset)
    learn_with(RandomForestClassifier, dataset=dataset)
    #learn_with(KMeans, params={'n_clusters':80, 'random_state':100}, dataset=dataset, vectorizer=vectorizer)
    learn_with(svm.SVC, params={'kernel':'sigmoid'}, dataset=dataset)
