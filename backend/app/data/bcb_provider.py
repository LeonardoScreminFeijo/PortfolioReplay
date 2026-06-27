import asyncio
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
import httpx
import pandas as pd

from app.core.cache import get_cached, set_cached
from app.core.exceptions import DataProviderError

BCB_BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series}/dados"
CDI_SERIES = 12
SELIC_SERIES = 11
TIMEOUT_SECONDS = 30.0
CHUNK_MONTHS = 12
BCB_HISTORY_START = date(2000, 1, 1)


class BCBProvider:
    async def get_cdi_history(self, start: date, end: date) -> pd.DataFrame:
        return await self._get_series(CDI_SERIES, start, end)

    async def get_selic_history(self, start: date, end: date) -> pd.DataFrame:
        return await self._get_series(SELIC_SERIES, start, end)

    async def _get_series(self, series: int, start: date, end: date) -> pd.DataFrame:
        cache_key = f"bcb:full:{series}"
        full = get_cached(cache_key)

        if full is None:
            full = await self._fetch_full(series)
            set_cached(cache_key, full)

        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        sliced = full.loc[start_ts:end_ts]
        if sliced.empty:
            raise DataProviderError(f"BCB returned empty data for series {series} in range {start}–{end}")
        return sliced

    async def _fetch_full(self, series: int) -> pd.DataFrame:
        today = date.today()
        chunks: list[tuple[date, date]] = []
        chunk_start = BCB_HISTORY_START
        while chunk_start <= today:
            chunk_end = min(chunk_start + relativedelta(months=CHUNK_MONTHS) - timedelta(days=1), today)
            chunks.append((chunk_start, chunk_end))
            chunk_start = chunk_end + timedelta(days=1)

        results = await asyncio.gather(*[self._fetch_chunk(series, s, e) for s, e in chunks])
        return pd.concat(results).sort_index()

    async def _fetch_chunk(self, series: int, start: date, end: date) -> pd.DataFrame:
        url = BCB_BASE.format(series=series)
        params = {
            "formato": "json",
            "dataInicial": start.strftime("%d/%m/%Y"),
            "dataFinal": end.strftime("%d/%m/%Y"),
        }
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                response = await client.get(url, params=params, headers={"Accept": "application/json"})
                response.raise_for_status()
        except httpx.TimeoutException as e:
            raise DataProviderError(f"BCB API timeout for series {series}") from e
        except httpx.HTTPStatusError as e:
            raise DataProviderError(f"BCB API error {e.response.status_code} for series {series}") from e

        raw = response.json()
        if not raw:
            return pd.DataFrame(columns=["rate"])

        df = pd.DataFrame(raw)
        df["date"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        df["rate"] = df["valor"].astype(float) / 100
        return df.set_index("date")[["rate"]]
