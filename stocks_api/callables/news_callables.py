from datetime import datetime
import typing
import os

import asyncio
import yfinance as yf
import tweepy

from stocks_api.structures import News

from uuid import uuid4


async def yield_yahoo_news(ticker: str, timeout: int) -> typing.AsyncGenerator[News, None]:
    await asyncio.sleep(timeout)

    search = yf.Search(ticker, news_count=1)

    news_articles = search.news

    for article in news_articles:
        yield News(
            article["title"],
            article["link"],
            datetime.fromtimestamp(article["providerPublishTime"]),
            article["uuid"],
            "Yahoo"
        )

async def yield_twitter_news(
    keywords: typing.List[str],
    timeout: int
) -> typing.AsyncGenerator[News, None]:

    await asyncio.sleep(timeout)

    BEARER_TOKEN = os.environ.get("TWITTER_TOKEN", "")
    client = tweepy.Client(bearer_token=BEARER_TOKEN)

    for keyword in keywords:
        hashtag = f"#{keyword}" 

        try:
            tweets = client.search_recent_tweets(
                query=hashtag,
                max_results=10, 
                tweet_fields=["created_at", "author_id"]
            )
        except Exception as exception:
            print(f"Twitter api returned {type(exception).__name__};\n Skipping")
        else:
            if tweets.data:
                for tweet in tweets:
                    yield News(
                        tweet.text,
                        f"https://twitter.com/{tweet.author_id}/status/{tweet.id}",
                        tweet.created_at,
                        tweet.id,
                        "Twitter"
                    )


async def yield_dummy_twitter_news(
    _: typing.List[str],
    timeout: int
) -> typing.AsyncGenerator[News, None]:
    
    await asyncio.sleep(timeout)

    for _ in range(10):
        yield News(
            "some_text",
            f"https://twitter.com/plplp/status/popoop",
            datetime.now(),
            uuid4(),
            "Twitter"
        )