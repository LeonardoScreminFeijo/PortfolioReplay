from datetime import date

import pandas as pd
import pytest

from app.core.exceptions import DataProviderError, TickerNotFoundError
from app.data.yfinance_provider import YFinanceProvider, _normalize_ticker


@pytest.mark.parametrize(
    "ticker,expected",
    [
        ("PETR4", "PETR4.SA"),
        ("petr4", "PETR4.SA"),
        ("PETR4.SA", "PETR4.SA"),
        ("^BVSP", "^BVSP"),
        ("VALE3", "VALE3.SA"),
    ],
)
def test_normalize_ticker(ticker: str, expected: str) -> None:
    assert _normalize_ticker(ticker) == expected


def _make_history_df() -> pd.DataFrame:
    idx = pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"])
    return pd.DataFrame({"close": [28.5, 29.0, 28.8]}, index=idx)


async def test_get_asset_history_cache_miss(mocker) -> None:
    mock_df = _make_history_df()
    mocker.patch("app.data.yfinance_provider.get_cached", return_value=None)
    mocker.patch("app.data.yfinance_provider.set_cached")
    mocker.patch("app.data.yfinance_provider._fetch_history", return_value=mock_df)

    provider = YFinanceProvider()
    result = await provider.get_asset_history("PETR4", date(2023, 1, 2), date(2023, 1, 4))

    assert list(result.columns) == ["close"]
    assert len(result) == 3


async def test_get_asset_history_cache_hit(mocker) -> None:
    mock_df = _make_history_df()
    mocker.patch("app.data.yfinance_provider.get_cached", return_value=mock_df)
    fetch_mock = mocker.patch("app.data.yfinance_provider._fetch_history")

    provider = YFinanceProvider()
    result = await provider.get_asset_history("PETR4", date(2023, 1, 2), date(2023, 1, 4))

    fetch_mock.assert_not_called()
    assert len(result) == 3


async def test_get_asset_history_ticker_not_found(mocker) -> None:
    mocker.patch("app.data.yfinance_provider.get_cached", return_value=None)
    mocker.patch(
        "app.data.yfinance_provider._fetch_history",
        side_effect=TickerNotFoundError("No data for ticker 'FAKE.SA'"),
    )

    provider = YFinanceProvider()
    with pytest.raises(TickerNotFoundError):
        await provider.get_asset_history("FAKE", date(2023, 1, 2), date(2023, 1, 4))


async def test_get_asset_history_provider_error(mocker) -> None:
    mocker.patch("app.data.yfinance_provider.get_cached", return_value=None)
    mocker.patch(
        "app.data.yfinance_provider._fetch_history",
        side_effect=DataProviderError("yfinance error"),
    )

    provider = YFinanceProvider()
    with pytest.raises(DataProviderError):
        await provider.get_asset_history("PETR4", date(2023, 1, 2), date(2023, 1, 4))


async def test_get_ibov_history(mocker) -> None:
    mock_df = _make_history_df()
    mocker.patch("app.data.yfinance_provider.get_cached", return_value=None)
    mocker.patch("app.data.yfinance_provider.set_cached")
    mocker.patch("app.data.yfinance_provider._fetch_history", return_value=mock_df)

    provider = YFinanceProvider()
    result = await provider.get_ibov_history(date(2023, 1, 2), date(2023, 1, 4))

    assert "close" in result.columns
