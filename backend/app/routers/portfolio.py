from datetime import date

from fastapi import APIRouter, HTTPException

from app.core.exceptions import DataProviderError, DateRangeError, TickerNotFoundError
from app.data.yfinance_provider import YFinanceProvider
from app.models.schemas import MetricsOut, ProjectionBand, SimulateRequest, SimulateResponse, TimelinePointOut
from app.services.projection import run_monte_carlo
from app.services.rebalance_strategies import MonthlyRebalance, NoRebalance, QuarterlyRebalance
from app.services.replay_calculator import AssetInput, run_replay

router = APIRouter(prefix="/portfolio", tags=["portfolio"])
_provider = YFinanceProvider()


def _get_strategy(freq: str) -> NoRebalance | MonthlyRebalance | QuarterlyRebalance:
    if freq == "monthly":
        return MonthlyRebalance()
    if freq == "quarterly":
        return QuarterlyRebalance()
    return NoRebalance()


@router.post("/simulate", response_model=SimulateResponse, summary="Simulate portfolio replay")
async def simulate(request: SimulateRequest) -> SimulateResponse:
    end = request.end_date or date.today()
    assets = [AssetInput(ticker=a.ticker, weight=a.weight) for a in request.assets]
    strategy = _get_strategy(request.rebalance_frequency)

    try:
        result = await run_replay(
            assets=assets,
            start=request.start_date,
            end=end,
            initial_value=request.initial_value,
            monthly_contribution=request.monthly_contribution,
            strategy=strategy,
            provider=_provider,
        )
    except TickerNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except DateRangeError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except DataProviderError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    projection = None
    if request.projection_months:
        last = result.timeline[-1]
        proj_points = run_monte_carlo(
            last_value=last.portfolio_value,
            annualized_return=result.metrics.annualized_return,
            volatility=result.metrics.volatility,
            horizon_months=request.projection_months,
            last_date=last.date,
        )
        if proj_points:
            projection = [
                ProjectionBand(
                    date=p.date,
                    p10=p.p10,
                    p25=p.p25,
                    p50=p.p50,
                    p75=p.p75,
                    p90=p.p90,
                )
                for p in proj_points
            ]

    return SimulateResponse(
        timeline=[
            TimelinePointOut(
                date=p.date,
                portfolio_value=p.portfolio_value,
                ibov_value=p.ibov_value,
                cdi_value=p.cdi_value,
            )
            for p in result.timeline
        ],
        metrics=MetricsOut(
            total_return=result.metrics.total_return,
            annualized_return=result.metrics.annualized_return,
            max_drawdown=result.metrics.max_drawdown,
            volatility=result.metrics.volatility,
        ),
        projection=projection,
    )
