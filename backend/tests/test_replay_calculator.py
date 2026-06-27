from datetime import date

import pandas as pd
import pytest

from app.services.rebalance_strategies import MonthlyRebalance, NoRebalance
from app.services.replay_calculator import AssetInput, run_replay


class FixedProvider:
    def __init__(
        self,
        price_map: dict[str, list[float]],
        ibov: list[float],
        cdi: list[float],
        dates: list[str],
    ) -> None:
        self._dates = pd.to_datetime(dates)
        self._price_map = price_map
        self._ibov = ibov
        self._cdi = cdi

    async def get_asset_history(self, ticker: str, start: date, end: date) -> pd.DataFrame:
        return pd.DataFrame({"close": self._price_map[ticker]}, index=self._dates)

    async def get_ibov_history(self, start: date, end: date) -> pd.DataFrame:
        return pd.DataFrame({"close": self._ibov}, index=self._dates)

    async def get_cdi_history(self, start: date, end: date) -> pd.DataFrame:
        return pd.DataFrame({"rate": self._cdi}, index=self._dates)


DATES_JAN = ["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]


async def test_single_asset_no_rebalance_golden() -> None:
    provider = FixedProvider(
        price_map={"PETR4": [100.0, 110.0, 105.0, 120.0]},
        ibov=[10000.0, 10500.0, 10200.0, 11000.0],
        cdi=[0.0001] * 4,
        dates=DATES_JAN,
    )
    result = await run_replay(
        assets=[AssetInput(ticker="PETR4", weight=1.0)],
        start=date(2024, 1, 2),
        end=date(2024, 1, 5),
        initial_value=1000.0,
        monthly_contribution=0.0,
        strategy=NoRebalance(),
        provider=provider,
    )

    assert len(result.timeline) == 4
    # 10 shares at 100.0 → 10*price each day
    assert result.timeline[0].portfolio_value == pytest.approx(1000.0)
    assert result.timeline[1].portfolio_value == pytest.approx(1100.0)
    assert result.timeline[2].portfolio_value == pytest.approx(1050.0)
    assert result.timeline[3].portfolio_value == pytest.approx(1200.0)
    assert result.metrics.total_return == pytest.approx(0.20)


async def test_ibov_normalized_to_initial_value() -> None:
    provider = FixedProvider(
        price_map={"PETR4": [100.0, 110.0, 105.0, 120.0]},
        ibov=[10000.0, 11000.0, 9000.0, 12000.0],
        cdi=[0.0] * 4,
        dates=DATES_JAN,
    )
    result = await run_replay(
        assets=[AssetInput(ticker="PETR4", weight=1.0)],
        start=date(2024, 1, 2),
        end=date(2024, 1, 5),
        initial_value=1000.0,
        monthly_contribution=0.0,
        strategy=NoRebalance(),
        provider=provider,
    )

    assert result.timeline[0].ibov_value == pytest.approx(1000.0)
    assert result.timeline[1].ibov_value == pytest.approx(1100.0)
    assert result.timeline[2].ibov_value == pytest.approx(900.0)
    assert result.timeline[3].ibov_value == pytest.approx(1200.0)


async def test_cdi_starts_at_initial_value_and_accrues() -> None:
    provider = FixedProvider(
        price_map={"PETR4": [100.0] * 4},
        ibov=[10000.0] * 4,
        cdi=[0.001] * 4,
        dates=DATES_JAN,
    )
    result = await run_replay(
        assets=[AssetInput(ticker="PETR4", weight=1.0)],
        start=date(2024, 1, 2),
        end=date(2024, 1, 5),
        initial_value=1000.0,
        monthly_contribution=0.0,
        strategy=NoRebalance(),
        provider=provider,
    )

    assert result.timeline[0].cdi_value == pytest.approx(1000.0)
    assert result.timeline[1].cdi_value == pytest.approx(1000.0 * 1.001)
    assert result.timeline[2].cdi_value == pytest.approx(1000.0 * 1.001**2)
    assert result.timeline[3].cdi_value == pytest.approx(1000.0 * 1.001**3)


async def test_two_assets_no_rebalance() -> None:
    provider = FixedProvider(
        price_map={"A": [100.0, 110.0], "B": [200.0, 180.0]},
        ibov=[10000.0, 10000.0],
        cdi=[0.0, 0.0],
        dates=["2024-01-02", "2024-01-03"],
    )
    result = await run_replay(
        assets=[AssetInput(ticker="A", weight=0.5), AssetInput(ticker="B", weight=0.5)],
        start=date(2024, 1, 2),
        end=date(2024, 1, 3),
        initial_value=1000.0,
        monthly_contribution=0.0,
        strategy=NoRebalance(),
        provider=provider,
    )

    # shares_A = 0.5*1000/100 = 5, shares_B = 0.5*1000/200 = 2.5
    assert result.timeline[0].portfolio_value == pytest.approx(1000.0)
    # day 1: 5*110 + 2.5*180 = 550 + 450 = 1000
    assert result.timeline[1].portfolio_value == pytest.approx(1000.0)


async def test_monthly_rebalance_redistributes_shares() -> None:
    # Jan 31 → Feb 1 triggers rebalance
    dates = ["2024-01-30", "2024-01-31", "2024-02-01", "2024-02-02"]
    provider = FixedProvider(
        price_map={
            "A": [100.0, 110.0, 120.0, 110.0],
            "B": [200.0, 190.0, 180.0, 200.0],
        },
        ibov=[10000.0] * 4,
        cdi=[0.0] * 4,
        dates=dates,
    )
    result_rebal = await run_replay(
        assets=[AssetInput(ticker="A", weight=0.5), AssetInput(ticker="B", weight=0.5)],
        start=date(2024, 1, 30),
        end=date(2024, 2, 2),
        initial_value=1000.0,
        monthly_contribution=0.0,
        strategy=MonthlyRebalance(),
        provider=provider,
    )
    result_no = await run_replay(
        assets=[AssetInput(ticker="A", weight=0.5), AssetInput(ticker="B", weight=0.5)],
        start=date(2024, 1, 30),
        end=date(2024, 2, 2),
        initial_value=1000.0,
        monthly_contribution=0.0,
        strategy=NoRebalance(),
        provider=provider,
    )

    # Rebalance on Feb 1 doesn't change day-2 portfolio value
    v_rebal_2 = result_rebal.timeline[2].portfolio_value
    v_no_2 = result_no.timeline[2].portfolio_value
    assert v_rebal_2 == pytest.approx(v_no_2)
    # But day-3 values differ because share quantities changed
    v_rebal_3 = result_rebal.timeline[3].portfolio_value
    v_no_3 = result_no.timeline[3].portfolio_value
    assert v_rebal_3 != pytest.approx(v_no_3)


async def test_monthly_contribution_adds_to_portfolio() -> None:
    # Feb 1 is new month → contribution applied
    dates = ["2024-01-31", "2024-02-01"]
    provider = FixedProvider(
        price_map={"A": [100.0, 100.0]},
        ibov=[10000.0] * 2,
        cdi=[0.0] * 2,
        dates=dates,
    )
    result = await run_replay(
        assets=[AssetInput(ticker="A", weight=1.0)],
        start=date(2024, 1, 31),
        end=date(2024, 2, 1),
        initial_value=1000.0,
        monthly_contribution=200.0,
        strategy=NoRebalance(),
        provider=provider,
    )

    assert result.timeline[0].portfolio_value == pytest.approx(1000.0)
    # contribution of 200 at price 100 → 2 extra shares → 12 * 100 = 1200
    assert result.timeline[1].portfolio_value == pytest.approx(1200.0)


async def test_max_drawdown_in_replay() -> None:
    provider = FixedProvider(
        price_map={"A": [100.0, 80.0, 90.0, 110.0]},
        ibov=[10000.0] * 4,
        cdi=[0.0] * 4,
        dates=DATES_JAN,
    )
    result = await run_replay(
        assets=[AssetInput(ticker="A", weight=1.0)],
        start=date(2024, 1, 2),
        end=date(2024, 1, 5),
        initial_value=1000.0,
        monthly_contribution=0.0,
        strategy=NoRebalance(),
        provider=provider,
    )

    # peak=1000, trough=800, drawdown = (800-1000)/1000 = -0.20
    assert result.metrics.max_drawdown == pytest.approx(-0.20)
