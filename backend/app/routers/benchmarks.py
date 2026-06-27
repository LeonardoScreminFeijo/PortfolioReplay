from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.core.exceptions import DataProviderError, TickerNotFoundError
from app.data.bcb_provider import BCBProvider
from app.data.yfinance_provider import YFinanceProvider
from app.models.schemas import BenchmarkPoint, BenchmarkResponse

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])
_yf_provider = YFinanceProvider()
_bcb_provider = BCBProvider()

_VALID_INDICATORS = {"cdi", "selic", "ibovespa"}


@router.get("/{indicator}", response_model=BenchmarkResponse, summary="Get benchmark timeline")
async def get_benchmark(
    indicator: str,
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date | None = Query(
        default=None, description="End date (YYYY-MM-DD), defaults to today"
    ),
    initial_value: float = Query(default=1000.0, gt=0, description="Normalized starting value"),
) -> BenchmarkResponse:
    if indicator not in _VALID_INDICATORS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown indicator '{indicator}'. Valid: {sorted(_VALID_INDICATORS)}",
        )

    end = end_date or date.today()
    if start_date >= end:
        raise HTTPException(status_code=422, detail="start_date must be before end_date")

    try:
        timeline: list[BenchmarkPoint] = []

        if indicator == "ibovespa":
            df = await _yf_provider.get_ibov_history(start_date, end)
            ibov_start = float(df["close"].iloc[0])
            for ts, val in df["close"].items():
                timeline.append(
                    BenchmarkPoint(date=ts.date(), value=initial_value * float(val) / ibov_start)
                )
        else:
            if indicator == "cdi":
                df = await _bcb_provider.get_cdi_history(start_date, end)
            else:
                df = await _bcb_provider.get_selic_history(start_date, end)

            cumulative = initial_value
            for ts, rate in df["rate"].items():
                timeline.append(BenchmarkPoint(date=ts.date(), value=cumulative))
                cumulative *= 1 + float(rate)

    except TickerNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except DataProviderError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    return BenchmarkResponse(indicator=indicator, timeline=timeline)
