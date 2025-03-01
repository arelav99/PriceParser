import typing

import numpy as np
import pandas as pd
from scipy.stats import linregress
from pymonad.either import Either, Left, Right

from stocks_api.structures import Price


def calculate_slopes(data: typing.List[float], window_size: int) -> Either:
    if len(data) < window_size * 2:
        return Right(data)

    slope_prev = linregress(range(window_size), data[-(window_size*2):-window_size]).slope
    slope_current = linregress(range(window_size), data[-window_size:]).slope

    return Right((slope_prev, slope_current))

def trend_has_shifted_linear_reg(batch: typing.List[Price]) -> Either:
    window_size = 10
    data = list(map(lambda x: x.price, batch))

    return calculate_slopes(data, window_size).then(
        lambda slopes:
            Left(f"""
                trend_has_shifted_linear_reg indicated trend shift at {batch[-1].timestamp}
                with price {batch[-1].price}, slope changed from {slopes[0]} to {slopes[1]}
                and windows_size = {window_size}
            """)
            if np.sign(slopes[0]) != np.sign(slopes[1])
            else Right(batch)
    )

def calculate_cusum(data: typing.List[float], window_size: int, k: float) -> Either:
    mean_value = np.mean(data)
    cusum = np.cumsum(data - mean_value)
    last_value = cusum[-1]

    rolling_std = pd.Series(data).rolling(window=window_size).std()
    threshold = k * rolling_std.iloc[-1] if not np.isnan(rolling_std.iloc[-1]) else k * np.std(data)
    return Right((last_value, threshold))

def trend_has_shifted_cusum(batch: typing.List[Price]) -> Either:
    window_size=5
    k=1.5
    data = list(map(lambda x: x.price, batch))
    
    return calculate_cusum(data, window_size, k).then(
        lambda last_val_threshold:
            Left(f"""
                trend_has_shifted_cusum indicated trend shift at {batch[-1].timestamp}
                with price {batch[-1].price}, with cumsum being {last_val_threshold[0]} 
                and threshold {last_val_threshold[1]}
                and windows_size = {window_size}
            """)
            if last_val_threshold[0] > last_val_threshold[1]
            else Right(batch)
    )


def trend_has_shifted_sliding_window(batch: typing.List[Price]):
    window_size=5
    percentage_threshold = .5

    data = list(map(lambda x: x.price, batch))
    rolling_std = pd.Series(data).rolling(window=window_size).std().values

    if np.isnan(rolling_std[-1]):
        return Right(batch)

    if np.abs(rolling_std[-1]) - np.abs(rolling_std[-2]) > np.abs(rolling_std[-2]) * percentage_threshold:
        return Left(f"""
            trend_has_shifted_sliding_window indicated trend shift at {batch[-1].timestamp}
            with price {batch[-1].price}, with rolling std increasing from {rolling_std[-2]} to {rolling_std[-1]}
            and windows_size = {window_size}
        """)

    return Right(batch)
