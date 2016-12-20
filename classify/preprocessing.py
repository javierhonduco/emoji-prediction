import re
import sys


RAW_DATASET_FILE = 'emoji_twitter_data.txt'

HASHTAGS_REGEX = re.compile('#')
MENTIONS_REGEX = re.compile('@[^\s]+')
EMOJI_NAME_REGEX = re.compile(':[a-z_-]+:')
LINK_REGEX = re.compile('https?://[^\s]+')
EXTRA_SPACES_REGEX = re.compile('\s{2,}')
HAYSTACK_REGEX = re.compile('(RT)')
ASCII_REGEX = re.compile('[[:ascii:]]')

def preprocess_tweet(tweet, pipeline):
    for pipe in pipeline:
        tweet = pipe(tweet)
    return tweet

def preprocess_hashtags(tweet):
    return HASHTAGS_REGEX.sub('', tweet)

def preprocess_mentions(tweet):
    return MENTIONS_REGEX.sub('', tweet)

def remove_extra_spaces(tweet):
    return EXTRA_SPACES_REGEX.sub(' ', tweet).strip()

def remove_hyperlinks(tweet):
    return LINK_REGEX.sub('', tweet)

def remove_haystack(tweet):
    return HAYSTACK_REGEX.sub('', tweet)

def remove_unicode(tweet):
    return ASCII_REGEX.sub('', tweet)

def extract_emoji(tweet):
    emojis = EMOJI_NAME_REGEX.findall(tweet)
    tweet = EMOJI_NAME_REGEX.sub('', tweet)
    return [tweet, emojis]

def is_valid_training_data(tweet, emoji):
    if len(emoji) > 0 and len(tweet) > 2:
        return True
    return False

preprocessing_pipeline = [
    preprocess_hashtags,
    preprocess_mentions,
    remove_hyperlinks,
    remove_unicode,
    remove_haystack,
]

def get_tweets():
    with open(RAW_DATASET_FILE, 'r') as raw_dataset:
        for raw_tweet in raw_dataset:
            tweet, emojis = extract_emoji(preprocess_tweet(raw_tweet, preprocessing_pipeline))
            if is_valid_training_data(tweet, emojis):
                yield [remove_extra_spaces(tweet), emojis, raw_tweet]
