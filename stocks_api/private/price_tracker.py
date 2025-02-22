from datetime import datetime, timezone

import yfinance as yf

from stocks_api.structures import Price


async def fetch_current_price(ticker):
    stock = yf.Ticker(ticker)
    return (Price(
        stock.info['currentPrice'],
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S%z")
    ),)

async def fetch_hist_price(ticker, period):
    dat = yf.Ticker(ticker)
    hist_ = dat.history(period=period)
    return tuple([
        Price(*value) for value in hist_.reset_index()[["Close", "Date"]].values.tolist()
    ])