import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import benchmarks, portfolio


def _parse_cors(raw: str) -> list[str]:
    raw = raw.strip()
    if raw.startswith("["):
        return json.loads(raw)
    return [o.strip() for o in raw.split(",") if o.strip()]


app = FastAPI(
    title="PortfolioReplay API",
    description="Simulador de carteira de investimentos com replay histórico",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio.router)
app.include_router(benchmarks.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
