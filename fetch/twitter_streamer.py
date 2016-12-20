import sys
import logging
import threading
import signal
import os
from queue import Queue
from datetime import datetime
from twython import TwythonStreamer
from raven import Client
from requests.exceptions import ChunkedEncodingError, ConnectionError
from config import TwitterAuth, EMOJIS, DOWNLOADED_TWEETS_PATH, SENTRY_DSN, LANGUAGE
import emoji

l = logging.getLogger(__name__)
l.setLevel(logging.DEBUG)

ls = logging.StreamHandler()
ls.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s: %(message)s')
ls.setFormatter(formatter)
l.addHandler(ls)

retrieved_tweets_count = 0
failed_tweets_count = 0
start_time = datetime.now()
queue = Queue()
threads = []
emoji_regexp = emoji.get_emoji_regexp()
work = True
store = open(DOWNLOADED_TWEETS_PATH, 'a')

class UnknownTwitterEmojiException(Exception):
    pass

def process_tweets():
    while work:
        tweet = queue.get()['text'].replace('\n', ' ')
        extracted_emojis = emoji_regexp.findall(tweet)
        for extracted_emoji in extracted_emojis:
            tweet = tweet.replace(extracted_emoji, emoji.unicode_codes.UNICODE_EMOJI[extracted_emoji])

        store.write('{}\n'.format(tweet))
        store.flush()

class TwitterEmojiStreamer(TwythonStreamer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_success(self, data):
        global retrieved_tweets_count
        global queue
        if 'text' in data:
            queue.put(data)
            retrieved_tweets_count += 1
            self.show_stats()

    def on_error(self, status_code, data):
        global failed_tweets_count
        failed_tweets_count += 1
        self.show_stats()

    def show_stats(self):
        global retrieved_tweets_count
        global failed_tweets_count
        elapsed_time = self.elapsed_time()
        l.info('current_stats: downloaded={} failed={} elapsed_time={} tweets_per_second={}'.format(
            retrieved_tweets_count,
            failed_tweets_count,
            elapsed_time,
            round(retrieved_tweets_count/elapsed_time.total_seconds(), 2))
        )

    def elapsed_time(self):
        global start_time
        return datetime.now() - start_time

def run_twitter_fetcher():
    sentry = Client(SENTRY_DSN)
    while True:
        try:
            l.info('starting streamer with {} emojis...'.format(len(EMOJIS)))
            sentry.captureMessage('starting `emoji-prediction`')
            streamer = TwitterEmojiStreamer(TwitterAuth.CONSUMER_KEY,
                                TwitterAuth.CONSUMER_SECRET,
                                TwitterAuth.ACCESS_TOKEN,
                                TwitterAuth.ACCESS_TOKEN_SECRET)
            streamer.statuses.filter(track=EMOJIS, language=LANGUAGE)
        # requests.exceptions.ConnectionError
        except ChunkedEncodingError:
            l.debug('chunked_encoding_error happened')
            pass
        except ConnectionError:
            l.debug('connection_error happened')
            pass
        except UnknownTwitterEmojiException as e:
            l.error('unknown exception ocurred')
            l.error(e)
            sentry.captureException()

if __name__ == '__main__':

    def sigint_handler(signal, frame):
        l.info('exiting...')
        work = False
        store.close()
        sys.exit()

    signal.signal(signal.SIGINT, sigint_handler)

    procs = [process_tweets, run_twitter_fetcher]
    for proc in procs:
        t = threading.Thread(target=proc)
        t.daemon = True
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()
    store.close()
