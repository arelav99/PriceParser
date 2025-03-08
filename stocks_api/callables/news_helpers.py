from pymonad.reader import Reader
import finnhub
import tweepy


def create_twitter_client():
    return Reader(lambda env: 
        tweepy.Client(bearer_token=env.get("TWITTER_TOKEN", ""))
    )

def create_finnhub_client():
    return Reader(lambda env: 
        finnhub.Client(api_key=env.get("FINNHUB_TOKEN", ""))
    )
