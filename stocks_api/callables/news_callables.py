from datetime import datetime, timedelta
import typing
import os

import asyncio
import yfinance as yf

from stocks_api.structures import News
from stocks_api.private.monadic import safe_exec
from stocks_api.callables.news_helpers import create_twitter_client, create_finnhub_client

from uuid import uuid4


async def yield_yahoo_news(ticker: str, timeout: int) -> typing.AsyncGenerator[News, None]:
    yahoo_monad = safe_exec(yf.Search, ticker, news_count=10)

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

    await asyncio.sleep(timeout)

async def yield_twitter_news(
    keyword: str,
    timeout: int
) -> typing.AsyncGenerator[News, None]:

    client = create_twitter_client()(os.environ)

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
    
    await asyncio.sleep(timeout)

async def yield_dummy_twitter_news(
    dummy_ticker: str,
    timeout: int
) -> typing.AsyncGenerator[News, None]:

    for _ in range(10):
        yield News(
            dummy_ticker,
            f"https://twitter.com/plplp/status/popoop",
            datetime.now(),
            uuid4(),
            "Twitter"
        )

    await asyncio.sleep(timeout)

async def yield_finnhub_news(ticker: str, timeout: int) -> typing.AsyncGenerator[News, None]:
    client = create_finnhub_client()(os.environ)

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    finnhub_news = safe_exec(
        client.company_news,
        symbol=ticker,
        _from=yesterday.strftime("%Y-%m-%d"),
        to=today.strftime("%Y-%m-%d")
    )
    if finnhub_news.is_right():
        for news in finnhub_news.value:
            yield News(
                ticker,
                news["url"],
                datetime.fromtimestamp(news["datetime"]),
                str(news["id"]),
                "Finnhub"
            )

    await asyncio.sleep(timeout)
