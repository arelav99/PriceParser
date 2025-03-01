import asyncio
import numpy as np
from pymonad.either import Left, Right

from stocks_api import yield_stock_price, yield_trend_shift
from stocks_api.callables import (
    trend_has_shifted_linear_reg,
    trend_has_shifted_cusum,
    trend_has_shifted_sliding_window
)
from stocks_api import NewsCollectionAPI
from stocks_api.callables import (
    yield_dummy_twitter_news,
    yield_yahoo_news
)
from stocks_api import yield_trend_change_with_news


async def example_of_yield_price_api():
    async for i in yield_stock_price('AAPL', '5s'):
        print(i[0])

async def example_of_yield_price_api_and_hist():
    async for batch in yield_stock_price('AAPL', '5s', '1mo'):
        for i in batch:
            print(i)

async def example_of_yield_trend_shift():
    async for has_shifted in yield_trend_shift(
        lambda: yield_stock_price('AAPL', '5s', '1mo'),
        [trend_has_shifted_linear_reg, trend_has_shifted_cusum, trend_has_shifted_sliding_window]
    ):
        if has_shifted:
            print("Trend has shifted")

async def example_of_fetch_news():
    news_collector = NewsCollectionAPI([
        lambda: yield_dummy_twitter_news("AAPL", 10),
        lambda: yield_yahoo_news("AAPL", 10)
    ])

    while True:
        await news_collector.fetch_news()
        print(news_collector.get_n_latest_news(10))

async def example_of_yield_trend_shift_with_news():
    news_collector = NewsCollectionAPI([
        lambda: yield_dummy_twitter_news("AAPL", 10),
        lambda: yield_yahoo_news("AAPL", 10)
    ])

    async for news in yield_trend_change_with_news(
        lambda: yield_trend_shift(
            lambda : yield_stock_price('AAPL', '5s', '1mo'),
            [lambda x: Left(0) if np.random.rand() < 0.4 else Right(0)]
        ),
        news_collector
    ):

        print(news)


if __name__ == "__main__":
    asyncio.run(example_of_yield_trend_shift())
