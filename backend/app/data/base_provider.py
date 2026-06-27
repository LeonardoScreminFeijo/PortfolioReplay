from datetime import date
from typing import Protocol

import pandas as pd


class MarketDataProvider(Protocol):
    async def get_asset_history(self, ticker: str, start: date, end: date) -> pd.DataFrame:
        """Returns DataFrame with DatetimeIndex and column 'close' (float)."""
        ...

    async def get_ibov_history(self, start: date, end: date) -> pd.DataFrame:
        """Returns DataFrame with DatetimeIndex and column 'close' (float)."""
        ...

    async def get_cdi_history(self, start: date, end: date) -> pd.DataFrame:
        """Returns DataFrame with DatetimeIndex and column 'rate' (daily rate as decimal)."""
        ...
