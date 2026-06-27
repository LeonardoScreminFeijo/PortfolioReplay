from datetime import date

import httpx
import pandas as pd
import pytest

from app.core.exceptions import DataProviderError
from app.data.bcb_provider import BCBProvider

BCB_SAMPLE = [
    {"data": "02/01/2023", "valor": "0.0409"},
    {"data": "03/01/2023", "valor": "0.0409"},
    {"data": "04/01/2023", "valor": "0.0409"},
]


async def test_get_cdi_history_cache_miss(mocker) -> None:
    mocker.patch("app.data.bcb_provider.get_cached", return_value=None)
    mocker.patch("app.data.bcb_provider.set_cached")

    mock_response = mocker.MagicMock()
    mock_response.json.return_value = BCB_SAMPLE
    mock_response.raise_for_status = mocker.MagicMock()

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.get = mocker.AsyncMock(return_value=mock_response)
    mocker.patch("app.data.bcb_provider.httpx.AsyncClient", return_value=mock_client)

    provider = BCBProvider()
    result = await provider.get_cdi_history(date(2023, 1, 2), date(2023, 1, 4))

    assert "rate" in result.columns
    assert len(result) == 3
    assert result["rate"].iloc[0] == pytest.approx(0.000409)


async def test_get_cdi_history_cache_hit(mocker) -> None:
    mock_df = pd.DataFrame(
        {"rate": [0.000409] * 3},
        index=pd.to_datetime(["2023-01-02", "2023-01-03", "2023-01-04"]),
    )
    mocker.patch("app.data.bcb_provider.get_cached", return_value=mock_df)
    client_mock = mocker.patch("app.data.bcb_provider.httpx.AsyncClient")

    provider = BCBProvider()
    result = await provider.get_cdi_history(date(2023, 1, 2), date(2023, 1, 4))

    client_mock.assert_not_called()
    assert len(result) == 3


async def test_get_cdi_history_timeout(mocker) -> None:
    mocker.patch("app.data.bcb_provider.get_cached", return_value=None)

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.get = mocker.AsyncMock(side_effect=httpx.TimeoutException("timeout"))
    mocker.patch("app.data.bcb_provider.httpx.AsyncClient", return_value=mock_client)

    provider = BCBProvider()
    with pytest.raises(DataProviderError, match="timeout"):
        await provider.get_cdi_history(date(2023, 1, 2), date(2023, 1, 4))


async def test_get_cdi_history_http_error(mocker) -> None:
    mocker.patch("app.data.bcb_provider.get_cached", return_value=None)

    mock_response = mocker.MagicMock()
    mock_response.status_code = 500
    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.get = mocker.AsyncMock(
        side_effect=httpx.HTTPStatusError(
            "error", request=mocker.MagicMock(), response=mock_response
        )
    )
    mocker.patch("app.data.bcb_provider.httpx.AsyncClient", return_value=mock_client)

    provider = BCBProvider()
    with pytest.raises(DataProviderError, match="500"):
        await provider.get_cdi_history(date(2023, 1, 2), date(2023, 1, 4))


async def test_get_cdi_history_empty_response(mocker) -> None:
    mocker.patch("app.data.bcb_provider.get_cached", return_value=None)

    mock_response = mocker.MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = mocker.MagicMock()

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = mocker.AsyncMock(return_value=False)
    mock_client.get = mocker.AsyncMock(return_value=mock_response)
    mocker.patch("app.data.bcb_provider.httpx.AsyncClient", return_value=mock_client)

    provider = BCBProvider()
    with pytest.raises(DataProviderError, match="empty"):
        await provider.get_cdi_history(date(2023, 1, 2), date(2023, 1, 4))
