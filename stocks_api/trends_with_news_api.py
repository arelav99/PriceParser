from datetime import datetime, timedelta
import typing

from stocks_api.news_api import NewsCollectionAPI


async def yield_trend_change_with_news(
    trend_shifter_function: typing.Callable[..., typing.AsyncGenerator[bool, None]],
    news_generator: NewsCollectionAPI,
    n_news: int = 10
):

    while True:  
        async for trend_has_shifted in trend_shifter_function():
            if trend_has_shifted: 
                news_generator = await news_generator.fetch_news()

                yield news_generator.get_n_latest_news_in_range(
                    n_news,
                    datetime.now() - timedelta(minutes=30),
                    datetime.now()
                )
