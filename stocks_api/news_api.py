from copy import copy
from datetime import datetime
import typing

import pandas as pd

from stocks_api.structures import News


class NewsCollectionAPI:
    def __init__(
            self,
            news_generators:  typing.Callable[..., typing.AsyncGenerator[typing.List[News], None]],
            previous_news: pd.DataFrame = None
        ):
            self.generators = news_generators
            self.__time_sorted_news = previous_news if previous_news is not None else \
            pd.DataFrame(
                {'date_time':pd.Series([], dtype='datetime64[ns]'),
                'title':pd.Series([], dtype='str'),
                'link':pd.Series([], dtype='str'),
                'uuid':pd.Series([], dtype='str'),
                'source': pd.Series([], dtype='str')}
            )

    async def fetch_news(self):
        time_sorted_news = copy(self.__time_sorted_news)
        for news_generator in self.generators:
            async for news in news_generator():
                if news.uuid not in time_sorted_news.uuid.values:
                    time_sorted_news = pd.concat([
                        time_sorted_news,
                        pd.DataFrame([news.__dict__])
                    ])

        return NewsCollectionAPI(self.generators, time_sorted_news)

    def get_n_latest_news_in_range(self, n_news: int, start_date: datetime, end_date: datetime):
        return self.__time_sorted_news[
            self.__time_sorted_news.date_time.between(start_date, end_date)
        ].sort_values(by=['date_time'], ascending=False).head(n_news)
    
    def get_n_latest_news(self, n_news: int):
        return self.__time_sorted_news.sort_values(by=['date_time'], ascending=False).head(n_news)
