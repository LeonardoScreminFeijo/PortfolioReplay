from dataclasses import dataclass
from datetime import date

import pandas as pd

from app.data.base_provider import MarketDataProvider
from app.services.metrics import Metrics, calculate_metrics
from app.services.rebalance_strategies import RebalanceStrategy


@dataclass
class AssetInput:
    ticker: str
    weight: float  # 0.0–1.0; all weights must sum to 1.0


@dataclass
class TimelinePoint:
    date: date
    portfolio_value: float
    ibov_value: float
    cdi_value: float


@dataclass
class ReplayResult:
    timeline: list[TimelinePoint]
    metrics: Metrics


async def run_replay(
    assets: list[AssetInput],
    start: date,
    end: date,
    initial_value: float,
    monthly_contribution: float,
    strategy: RebalanceStrategy,
    provider: MarketDataProvider,
) -> ReplayResult:
    # 1. Fetch all price data
    price_dfs: dict[str, pd.Series] = {}
    for asset in assets:
        df = await provider.get_asset_history(asset.ticker, start, end)
        price_dfs[asset.ticker] = df["close"]

    ibov_df = await provider.get_ibov_history(start, end)
    cdi_df = await provider.get_cdi_history(start, end)

    # 2. Align on B3 trading days; forward-fill CDI and IBOV for holidays
    prices = pd.DataFrame(price_dfs)
    cdi_aligned = cdi_df["rate"].reindex(prices.index, method="ffill").fillna(0)
    ibov_aligned = ibov_df["close"].reindex(prices.index, method="ffill").bfill()

    prices = prices.dropna()
    cdi_aligned = cdi_aligned.reindex(prices.index)
    ibov_aligned = ibov_aligned.reindex(prices.index)

    weights = {asset.ticker: asset.weight for asset in assets}
    first_prices = prices.iloc[0]

    # 3. Initialize shares from initial investment
    shares = pd.Series(
        {t: weights[t] * initial_value / float(first_prices[t]) for t in prices.columns}
    )

    ibov_start = float(ibov_aligned.iloc[0])
    cdi_cumulative = initial_value
    timeline: list[TimelinePoint] = []
    prev_date: date | None = None

    # 4. Daily loop
    for current_ts in prices.index:
        current_date = current_ts.date()
        current_prices = prices.loc[current_ts]
        is_new_month = prev_date is not None and (
            current_date.month != prev_date.month or current_date.year != prev_date.year
        )

        # Monthly contribution applied before rebalance
        if monthly_contribution > 0 and is_new_month:
            for ticker in prices.columns:
                price = float(current_prices[ticker])
                shares[ticker] += weights[ticker] * monthly_contribution / price

        # Rebalance
        if strategy.should_rebalance(current_date, prev_date):
            total_value = float((shares * current_prices).sum())
            for ticker in prices.columns:
                shares[ticker] = weights[ticker] * total_value / float(current_prices[ticker])

        portfolio_value = float((shares * current_prices).sum())
        ibov_value = initial_value * (float(ibov_aligned.loc[current_ts]) / ibov_start)

        # CDI recorded before applying today's rate (both series start at initial_value on day 0)
        timeline.append(
            TimelinePoint(
                date=current_date,
                portfolio_value=portfolio_value,
                ibov_value=ibov_value,
                cdi_value=cdi_cumulative,
            )
        )

        cdi_cumulative *= 1 + float(cdi_aligned.loc[current_ts])
        prev_date = current_date

    # 5. Metrics from portfolio series
    portfolio_series = pd.Series(
        [p.portfolio_value for p in timeline],
        index=pd.to_datetime([p.date for p in timeline]),
    )
    metrics = calculate_metrics(portfolio_series, initial_value)

    return ReplayResult(timeline=timeline, metrics=metrics)
