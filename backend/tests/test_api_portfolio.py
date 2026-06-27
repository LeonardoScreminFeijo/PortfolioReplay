from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import DataProviderError, TickerNotFoundError
from app.main import app
from app.services.metrics import Metrics
from app.services.replay_calculator import ReplayResult, TimelinePoint

client = TestClient(app)

_VALID_PAYLOAD = {
    "assets": [{"ticker": "PETR4", "weight": 1.0}],
    "start_date": "2024-01-02",
    "end_date": "2024-06-01",
    "initial_value": 1000.0,
}


def _mock_result() -> ReplayResult:
    return ReplayResult(
        timeline=[
            TimelinePoint(
                date=date(2024, 1, 2),
                portfolio_value=1000.0,
                ibov_value=1000.0,
                cdi_value=1000.0,
            ),
            TimelinePoint(
                date=date(2024, 1, 3),
                portfolio_value=1100.0,
                ibov_value=1050.0,
                cdi_value=1000.1,
            ),
        ],
        metrics=Metrics(
            total_return=0.10,
            annualized_return=0.45,
            max_drawdown=-0.05,
            volatility=0.20,
        ),
    )


@patch("app.routers.portfolio.run_replay", new_callable=AsyncMock)
def test_simulate_ok(mock_run: AsyncMock) -> None:
    mock_run.return_value = _mock_result()
    resp = client.post("/portfolio/simulate", json=_VALID_PAYLOAD)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["timeline"]) == 2
    assert body["timeline"][0]["portfolio_value"] == pytest.approx(1000.0)
    assert body["metrics"]["total_return"] == pytest.approx(0.10)
    assert body["metrics"]["max_drawdown"] == pytest.approx(-0.05)


@patch("app.routers.portfolio.run_replay", new_callable=AsyncMock)
def test_simulate_ticker_not_found(mock_run: AsyncMock) -> None:
    mock_run.side_effect = TickerNotFoundError("FAKEXX not found")
    resp = client.post("/portfolio/simulate", json=_VALID_PAYLOAD)
    assert resp.status_code == 404
    assert "FAKEXX" in resp.json()["detail"]


@patch("app.routers.portfolio.run_replay", new_callable=AsyncMock)
def test_simulate_data_provider_error(mock_run: AsyncMock) -> None:
    mock_run.side_effect = DataProviderError("yfinance down")
    resp = client.post("/portfolio/simulate", json=_VALID_PAYLOAD)
    assert resp.status_code == 502


def test_simulate_weights_not_sum_to_one() -> None:
    payload = {
        "assets": [
            {"ticker": "PETR4", "weight": 0.6},
            {"ticker": "VALE3", "weight": 0.6},
        ],
        "start_date": "2024-01-02",
        "end_date": "2024-06-01",
    }
    resp = client.post("/portfolio/simulate", json=payload)
    assert resp.status_code == 422


def test_simulate_empty_assets() -> None:
    payload = {"assets": [], "start_date": "2024-01-02", "end_date": "2024-06-01"}
    resp = client.post("/portfolio/simulate", json=payload)
    assert resp.status_code == 422


def test_simulate_start_after_end() -> None:
    payload = {
        "assets": [{"ticker": "PETR4", "weight": 1.0}],
        "start_date": "2024-06-01",
        "end_date": "2024-01-02",
    }
    resp = client.post("/portfolio/simulate", json=payload)
    assert resp.status_code == 422


def test_simulate_zero_weight_rejected() -> None:
    payload = {
        "assets": [{"ticker": "PETR4", "weight": 0.0}],
        "start_date": "2024-01-02",
        "end_date": "2024-06-01",
    }
    resp = client.post("/portfolio/simulate", json=payload)
    assert resp.status_code == 422


def test_simulate_negative_initial_value() -> None:
    payload = {
        "assets": [{"ticker": "PETR4", "weight": 1.0}],
        "start_date": "2024-01-02",
        "end_date": "2024-06-01",
        "initial_value": -500.0,
    }
    resp = client.post("/portfolio/simulate", json=payload)
    assert resp.status_code == 422
