import math
from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd


@dataclass
class ProjectionPoint:
    date: date
    p10: float
    p25: float
    p50: float
    p75: float
    p90: float


def run_monte_carlo(
    last_value: float,
    annualized_return: float,
    volatility: float,
    horizon_months: int,
    last_date: date,
    n_simulations: int = 1000,
    seed: int = 42,
) -> list[ProjectionPoint]:
    rng = np.random.default_rng(seed)

    future_dates = pd.bdate_range(
        start=pd.Timestamp(last_date) + pd.offsets.BDay(1),
        periods=horizon_months * 21,
    )

    n_days = len(future_dates)
    if n_days == 0:
        return []

    mu = annualized_return / 252
    sigma = volatility / math.sqrt(252) if volatility > 0 else 0.0

    Z = rng.standard_normal((n_simulations, n_days))
    daily_returns = np.exp((mu - 0.5 * sigma**2) + sigma * Z)
    paths = last_value * np.cumprod(daily_returns, axis=1)

    pcts = np.percentile(paths, [10, 25, 50, 75, 90], axis=0)

    return [
        ProjectionPoint(
            date=d.date(),
            p10=float(pcts[0, i]),
            p25=float(pcts[1, i]),
            p50=float(pcts[2, i]),
            p75=float(pcts[3, i]),
            p90=float(pcts[4, i]),
        )
        for i, d in enumerate(future_dates)
    ]
