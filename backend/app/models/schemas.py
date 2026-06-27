import math
from datetime import date
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator


class AssetWeight(BaseModel):
    ticker: str
    weight: float

    @field_validator("ticker")
    @classmethod
    def ticker_not_empty(cls, v: str) -> str:
        v = v.strip().upper()
        if not v:
            raise ValueError("ticker cannot be empty")
        return v

    @field_validator("weight")
    @classmethod
    def weight_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("weight must be > 0")
        return v


class SimulateRequest(BaseModel):
    assets: list[AssetWeight]
    start_date: date
    end_date: date | None = None
    initial_value: float = 1000.0
    monthly_contribution: float = 0.0
    rebalance_frequency: Literal["none", "monthly", "quarterly"] = "none"
    projection_months: int | None = None

    @field_validator("assets")
    @classmethod
    def assets_not_empty(cls, v: list[AssetWeight]) -> list[AssetWeight]:
        if not v:
            raise ValueError("at least one asset required")
        return v

    @field_validator("initial_value")
    @classmethod
    def initial_value_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("initial_value must be > 0")
        return v

    @field_validator("monthly_contribution")
    @classmethod
    def contribution_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("monthly_contribution must be >= 0")
        return v

    @field_validator("projection_months")
    @classmethod
    def projection_months_valid(cls, v: int | None) -> int | None:
        if v is not None and not (1 <= v <= 240):
            raise ValueError("projection_months must be between 1 and 240")
        return v

    @model_validator(mode="after")
    def validate_weights_and_dates(self) -> "SimulateRequest":
        total = sum(a.weight for a in self.assets)
        if not math.isclose(total, 1.0, abs_tol=0.001):
            raise ValueError(f"asset weights must sum to 1.0, got {total:.4f}")

        today = date.today()
        if self.end_date is None:
            self.end_date = today
        if self.start_date >= today:
            raise ValueError("start_date must be before today")
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self


class TimelinePointOut(BaseModel):
    date: date
    portfolio_value: float
    ibov_value: float
    cdi_value: float


class MetricsOut(BaseModel):
    total_return: float
    annualized_return: float
    max_drawdown: float
    volatility: float


class ProjectionBand(BaseModel):
    date: date
    p10: float
    p25: float
    p50: float
    p75: float
    p90: float


class SimulateResponse(BaseModel):
    timeline: list[TimelinePointOut]
    metrics: MetricsOut
    projection: list[ProjectionBand] | None = None


class BenchmarkPoint(BaseModel):
    date: date
    value: float


class BenchmarkResponse(BaseModel):
    indicator: str
    timeline: list[BenchmarkPoint]
