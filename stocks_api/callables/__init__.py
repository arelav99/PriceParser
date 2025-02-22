from stocks_api.callables.news_callables import (
    yield_yahoo_news,
    yield_twitter_news,
    yield_dummy_twitter_news
)
from stocks_api.callables.trend_approximation_callables import (
    trend_has_shifted_linear_reg,
    trend_has_shifted_cusum,
    trend_has_shifted_sliding_window
)