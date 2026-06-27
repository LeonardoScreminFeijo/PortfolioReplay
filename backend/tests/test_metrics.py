import numpy as np
import pandas as pd
import pytest

from app.services.metrics import calculate_metrics


def _series(values: list[float], start: str = "2020-01-01") -> pd.Series:
    return pd.Series(values, index=pd.date_range(start, periods=len(values)))


def test_total_return_positive() -> None:
    m = calculate_metrics(_series([1000.0, 1100.0, 1050.0, 1200.0]), 1000.0)
    assert m.total_return == pytest.approx(0.20)


def test_total_return_negative() -> None:
    m = calculate_metrics(_series([1000.0, 900.0, 800.0]), 1000.0)
    assert m.total_return == pytest.approx(-0.20)


def test_max_drawdown() -> None:
    # peak=1100 at idx 1, trough=1050 at idx 2
    m = calculate_metrics(_series([1000.0, 1100.0, 1050.0, 1200.0]), 1000.0)
    assert m.max_drawdown == pytest.approx((1050 - 1100) / 1100)


def test_max_drawdown_monotonic_growth() -> None:
    m = calculate_metrics(_series([1000.0, 1100.0, 1200.0, 1300.0]), 1000.0)
    assert m.max_drawdown == pytest.approx(0.0)


def test_volatility_constant_returns() -> None:
    # identical daily returns → std = 0
    values = [1000.0 * (1.001**i) for i in range(50)]
    m = calculate_metrics(_series(values), 1000.0)
    assert m.volatility == pytest.approx(0.0, abs=1e-10)


def test_annualized_return_one_year() -> None:
    # exactly 100% return over 365 days → annualized = 100%
    values = [1000.0] + [2000.0] * 1
    idx = pd.DatetimeIndex(["2020-01-01", "2021-01-01"])
    series = pd.Series(values, index=idx)
    m = calculate_metrics(series, 1000.0)
    assert m.annualized_return == pytest.approx(1.0, rel=0.01)


def test_volatility_known_std() -> None:
    # daily returns of alternating +1% and -1% → std ≈ 0.01
    prices = [1000.0]
    for i in range(251):
        factor = 1.01 if i % 2 == 0 else 0.99
        prices.append(prices[-1] * factor)
    m = calculate_metrics(_series(prices), 1000.0)
    expected_vol = 0.01 * np.sqrt(252)
    assert m.volatility == pytest.approx(expected_vol, rel=0.01)
