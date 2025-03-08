import typing

from stocks_api.news_api import NewsCollectionAPI
from stocks_api.private.monadic import AsyncIOMonad

async def yield_trend_change_with_news(
    trend_shifter_function: typing.Callable[..., typing.AsyncGenerator[bool, None]],
    news_generator: NewsCollectionAPI,
    n_news: int = 10
):

    async def get_next_value(func):
        return await anext(func)

    shifter_function = trend_shifter_function()
    while True:  
        news_monad = (
            AsyncIOMonad(lambda: get_next_value(shifter_function))
            .then(lambda has_shifted: AsyncIOMonad(lambda : news_generator.fetch_news()) if has_shifted else None)
            .then(lambda news_gen: (news_gen, news_gen.get_n_latest_news(n_news)) if news_gen else None)
        )

        result = await news_monad.run()
        if result is not None:
            news_generator, news = result
            if not news.empty:
                yield news
