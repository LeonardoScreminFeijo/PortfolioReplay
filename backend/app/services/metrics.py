from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Metrics:
    total_return: float
    annualized_return: float
    max_drawdown: float
    volatility: float


def calculate_metrics(values: pd.Series, initial_value: float) -> Metrics:
    final_value = float(values.iloc[-1])
    total_return = (final_value / initial_value) - 1

    n_days = (values.index[-1] - values.index[0]).days
    years = n_days / 365.25
    if years > 0:
        annualized_return = (final_value / initial_value) ** (1 / years) - 1
    else:
        annualized_return = 0.0

    running_max = values.cummax()
    drawdowns = (values - running_max) / running_max
    max_drawdown = float(drawdowns.min())

    daily_returns = values.pct_change().dropna()
    volatility = float(daily_returns.std() * np.sqrt(252))

    return Metrics(
        total_return=total_return,
        annualized_return=annualized_return,
        max_drawdown=max_drawdown,
        volatility=volatility,
    )
