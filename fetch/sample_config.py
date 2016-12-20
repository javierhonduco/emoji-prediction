from emoji.unicode_codes import UNICODE_EMOJI

class TwitterAuth:
    CONSUMER_KEY        = ''
    CONSUMER_SECRET     = ''
    ACCESS_TOKEN        = ''
    ACCESS_TOKEN_SECRET = ''

# max is 400
raw_emojis = '😀😂😅😆😇😘😍😜😎🤓😶😏🤗😐😡😟😞🙄☹️😔😮😴💤💩😭😈👿👌👸🎅👅👀👍💪👻🤖😺🐟🐠🐷🐌🐼🐺🐯🐅🦃🐕🐇🌾🎍🍀🐾🌏🌚🌝🌞🌦🔥💥☃️✨❄️💧🍏🍊🍌🌽🍔🌮☕️🍧⚽️🏐🎖🎹🎰🎣🏓🚵🎮🎬🚗🚓🚨🚋🚠🛥🚀🚢🎠🚧🚧🚧✈️🏥📱⌨💻📠📞🔦💴💸🔮💊🔬🔭📫📈📉🖇✂️🔒🔓📒💛❤️💙💔💞💕💝💘🚾⚠️♻️🎵💬🕐🇬🇧🇺🇸🇪🇸🇵🇹🇳🇺🇳🇷🇬🇾🇬🇦🇮🇸🇯🇵'

def is_valid(e):
    try:
        UNICODE_EMOJI[e]
        return e
    except KeyError:
        pass

LANGUAGE = 'en'
# filter out emojis not in our library
EMOJIS = list(filter(None, [is_valid(e) for e in raw_emojis]))
DOWNLOADED_TWEETS_PATH = 'emoji_twitter_data.txt'
SENTRY_DSN = ''
