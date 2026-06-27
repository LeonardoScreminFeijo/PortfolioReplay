from datetime import date

import httpx
import pandas as pd

from app.core.cache import get_cached, set_cached
from app.core.exceptions import DataProviderError

BCB_BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series}/dados"
CDI_SERIES = 12
SELIC_SERIES = 11
TIMEOUT_SECONDS = 30.0


class BCBProvider:
    async def get_cdi_history(self, start: date, end: date) -> pd.DataFrame:
        return await self._fetch_series(CDI_SERIES, start, end)

    async def get_selic_history(self, start: date, end: date) -> pd.DataFrame:
        return await self._fetch_series(SELIC_SERIES, start, end)

    async def _fetch_series(self, series: int, start: date, end: date) -> pd.DataFrame:
        cache_key = f"bcb:{series}:{start}:{end}"

        cached = get_cached(cache_key)
        if cached is not None:
            return cached

        url = BCB_BASE.format(series=series)
        params = {
            "formato": "json",
            "dataInicial": start.strftime("%d/%m/%Y"),
            "dataFinal": end.strftime("%d/%m/%Y"),
        }

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
        except httpx.TimeoutException as e:
            raise DataProviderError(f"BCB API timeout for series {series}") from e
        except httpx.HTTPStatusError as e:
            code = e.response.status_code
            raise DataProviderError(f"BCB API error {code} for series {series}") from e

        raw = response.json()
        if not raw:
            raise DataProviderError(
                f"BCB returned empty data for series {series} in range {start}–{end}"
            )

        df = pd.DataFrame(raw)
        df["date"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        df["rate"] = df["valor"].astype(float) / 100
        df = df.set_index("date")[["rate"]].sort_index()

        set_cached(cache_key, df)
        return df
