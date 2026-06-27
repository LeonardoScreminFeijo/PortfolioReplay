from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import DataProviderError
from app.main import app

client = TestClient(app)

_DATES = pd.to_datetime(["2024-01-02", "2024-01-03"])


@patch("app.routers.benchmarks._bcb_provider")
def test_cdi_normalized_timeline(mock_bcb: AsyncMock) -> None:
    mock_bcb.get_cdi_history = AsyncMock(
        return_value=pd.DataFrame({"rate": [0.001, 0.001]}, index=_DATES)
    )
    resp = client.get(
        "/benchmarks/cdi?start_date=2024-01-02&end_date=2024-01-03&initial_value=1000"
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["indicator"] == "cdi"
    assert len(body["timeline"]) == 2
    assert body["timeline"][0]["value"] == pytest.approx(1000.0)
    assert body["timeline"][1]["value"] == pytest.approx(1001.0)


@patch("app.routers.benchmarks._bcb_provider")
def test_selic_returns_timeline(mock_bcb: AsyncMock) -> None:
    mock_bcb.get_selic_history = AsyncMock(
        return_value=pd.DataFrame({"rate": [0.0005, 0.0005]}, index=_DATES)
    )
    resp = client.get("/benchmarks/selic?start_date=2024-01-02&end_date=2024-01-03")
    assert resp.status_code == 200
    body = resp.json()
    assert body["indicator"] == "selic"
    assert len(body["timeline"]) == 2


@patch("app.routers.benchmarks._yf_provider")
def test_ibovespa_normalized(mock_yf: AsyncMock) -> None:
    mock_yf.get_ibov_history = AsyncMock(
        return_value=pd.DataFrame({"close": [100000.0, 110000.0]}, index=_DATES)
    )
    resp = client.get(
        "/benchmarks/ibovespa?start_date=2024-01-02&end_date=2024-01-03&initial_value=1000"
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["timeline"][0]["value"] == pytest.approx(1000.0)
    assert body["timeline"][1]["value"] == pytest.approx(1100.0)


def test_unknown_indicator_returns_404() -> None:
    resp = client.get("/benchmarks/bitcoin?start_date=2024-01-01&end_date=2024-06-01")
    assert resp.status_code == 404


def test_start_after_end_returns_422() -> None:
    resp = client.get("/benchmarks/cdi?start_date=2024-06-01&end_date=2024-01-01")
    assert resp.status_code == 422


def test_missing_start_date_returns_422() -> None:
    resp = client.get("/benchmarks/cdi?end_date=2024-06-01")
    assert resp.status_code == 422


@patch("app.routers.benchmarks._bcb_provider")
def test_data_provider_error_returns_502(mock_bcb: AsyncMock) -> None:
    mock_bcb.get_cdi_history = AsyncMock(side_effect=DataProviderError("BCB down"))
    resp = client.get("/benchmarks/cdi?start_date=2024-01-02&end_date=2024-01-03")
    assert resp.status_code == 502
