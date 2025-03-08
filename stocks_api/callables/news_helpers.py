from pymonad.reader import Reader
import tweepy


def create_twitter_client():
    return Reader(lambda env: 
        tweepy.Client(bearer_token=env.get("TWITTER_TOKEN", ""))
    )