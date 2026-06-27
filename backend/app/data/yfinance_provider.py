import asyncio
from datetime import date

import pandas as pd
import yfinance as yf

from app.core.cache import get_cached, set_cached
from app.core.exceptions import DataProviderError, TickerNotFoundError

IBOV_TICKER = "^BVSP"


def _normalize_ticker(ticker: str) -> str:
    ticker = ticker.upper().strip()
    if ticker.startswith("^") or "." in ticker:
        return ticker
    return f"{ticker}.SA"


def _fetch_history(ticker: str, start: date, end: date) -> pd.DataFrame:
    try:
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(start=start, end=end, auto_adjust=True)
    except Exception as e:
        raise DataProviderError(f"yfinance error for '{ticker}': {e}") from e

    if df.empty:
        raise TickerNotFoundError(f"No data for ticker '{ticker}' in range {start}–{end}")

    df.index = pd.to_datetime(df.index).normalize().tz_localize(None)
    return df[["Close"]].rename(columns={"Close": "close"})


class YFinanceProvider:
    async def get_asset_history(self, ticker: str, start: date, end: date) -> pd.DataFrame:
        normalized = _normalize_ticker(ticker)
        cache_key = f"asset:{normalized}:{start}:{end}"

        cached = get_cached(cache_key)
        if cached is not None:
            return cached

        df = await asyncio.to_thread(_fetch_history, normalized, start, end)
        set_cached(cache_key, df)
        return df

    async def get_ibov_history(self, start: date, end: date) -> pd.DataFrame:
        cache_key = f"asset:{IBOV_TICKER}:{start}:{end}"

        cached = get_cached(cache_key)
        if cached is not None:
            return cached

        df = await asyncio.to_thread(_fetch_history, IBOV_TICKER, start, end)
        set_cached(cache_key, df)
        return df

    async def get_cdi_history(self, start: date, end: date) -> pd.DataFrame:
        from app.data.bcb_provider import BCBProvider

        return await BCBProvider().get_cdi_history(start, end)
