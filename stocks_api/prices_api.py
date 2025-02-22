from copy import copy
import typing

import asyncio
from pymonad.either import Either
from pymonad.state import State

from stocks_api.structures import Price
from stocks_api.structures import (
    PRICE_TIMEDELTA,
    PRICE_PREVIOUS_PERIOD_TIME
)
from stocks_api.private import (
    fetch_hist_price,
    fetch_current_price
)


async def yield_stock_price(
    ticker: str, 
    timedelta: PRICE_TIMEDELTA,
    hist_period: PRICE_PREVIOUS_PERIOD_TIME = None
) -> typing.AsyncGenerator[typing.List[Price], None]:

    sleep_seconds = int(timedelta.replace("s", "").replace("m", "00"))

    if hist_period is not None:
        yield await fetch_hist_price(ticker, hist_period)

    while True:
        yield await fetch_current_price(ticker)
        await asyncio.sleep(sleep_seconds)


async def yield_trend_shift(
    price_yielder_func: typing.Callable[..., typing.AsyncGenerator[typing.List[Price], None]],
    callables: typing.List[typing.Callable[[typing.List[Price]], Either]],
    supress_signal_for: int = 10
) -> typing.AsyncGenerator[bool, None]:

    price_data = ()
    counter_monad = State.insert(0)
    async for batch in price_yielder_func():
        price_data = copy(price_data) + batch

        counter_monad = counter_monad.then(lambda x: max(x - 1, 0))
        counter = counter_monad.run(0)[0]
        if counter != 0:
            yield False
            continue

        monad = Either.insert(price_data)

        for filter_func in callables:
            monad = monad.then(filter_func)

        if monad.is_left():
            counter_monad = State.insert(supress_signal_for)
            yield True
        else:
            yield False
