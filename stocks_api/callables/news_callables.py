from datetime import datetime
import typing
import os

import asyncio
import yfinance as yf
import tweepy

from stocks_api.structures import News
from stocks_api.private.monadic import safe_exec

from uuid import uuid4


async def yield_yahoo_news(ticker: str, timeout: int) -> typing.AsyncGenerator[News, None]:
    await asyncio.sleep(timeout)

    yahoo_monad = safe_exec(yf.Search, ticker, news_count=1)

    if yahoo_monad.is_right():
        news_articles = yahoo_monad.value.news

        for article in news_articles:
            yield News(
                article["title"],
                article["link"],
                datetime.fromtimestamp(article["providerPublishTime"]),
                article["uuid"],
                "Yahoo"
            )

async def yield_twitter_news(
    keyword: str,
    timeout: int
) -> typing.AsyncGenerator[News, None]:

    await asyncio.sleep(timeout)

    BEARER_TOKEN = os.environ.get("TWITTER_TOKEN", "")
    client = tweepy.Client(bearer_token=BEARER_TOKEN)

    tweets_monad = safe_exec(
        client.search_recent_tweets, 
        query=f"#{keyword}",
        max_results=10, 
        tweet_fields=["created_at", "author_id"]
    )

    if tweets_monad.is_right():
        tweets = tweets_monad.value
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
    dummy_ticker: str,
    timeout: int
) -> typing.AsyncGenerator[News, None]:
    
    await asyncio.sleep(timeout)

    for _ in range(10):
        yield News(
            dummy_ticker,
            f"https://twitter.com/plplp/status/popoop",
            datetime.now(),
            uuid4(),
            "Twitter"
        )