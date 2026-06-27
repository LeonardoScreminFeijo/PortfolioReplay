# PortfolioReplay

> Simulador de carteira de investimentos com replay histórico — monte uma carteira fictícia, escolha uma data de início e veja como ela teria se saído na realidade, comparada ao Ibovespa e CDI.

<!-- TODO: adicionar GIF de demo aqui -->

## O que é

PortfolioReplay reconstrói a evolução real de uma carteira de ações brasileiras a partir de dados históricos do Yahoo Finance. Você define os ativos, os pesos, o valor inicial e o período — o app calcula a trajetória diária, as métricas de performance e gera um link compartilhável com toda a configuração codificada na URL.

**Não é:**

- Um robô de investimentos / recomendador
- Um produto com dados em tempo real
- Uma plataforma com cadastro ou login

## Funcionalidades

- **Replay histórico** — evolução diária da carteira desde a data escolhida até hoje
- **Benchmarks** — comparação automática com Ibovespa (`^BVSP`) e CDI (fonte: BCB/SGS)
- **Estratégias de rebalanceamento** — sem rebalanceamento, mensal ou trimestral
- **Aporte mensal recorrente** — simula aportes periódicos ao longo do período
- **Métricas de performance** — retorno total, retorno anualizado, drawdown máximo, volatilidade
- **Link de compartilhamento** — estado da carteira serializado na URL, sem banco de dados de usuários
- **Skeleton screens e tratamento de erros** — feedback claro para tickers inválidos, fonte indisponível e erros de rede

## Stack

| Camada           | Tecnologias                                      |
| ---------------- | ------------------------------------------------ |
| Backend          | Python 3.11 · FastAPI · Uvicorn · Pydantic v2 |
| Dados de mercado | yfinance (Yahoo Finance) · httpx (async)        |
| Dados macro      | API SGS Banco Central (CDI/Selic)                |
| Cálculo         | pandas · numpy                                  |
| Cache            | diskcache (SQLite, TTL 24h)                      |
| Frontend         | React 19 · Vite · TypeScript                   |
| Gráficos        | Recharts                                         |
| Estilização    | Tailwind CSS v3                                  |

## Arquitetura

```
portfolio-replay/
├── backend/
│   └── app/
│       ├── routers/          # endpoints HTTP (FastAPI)
│       │   ├── portfolio.py  # POST /portfolio/simulate
│       │   └── benchmarks.py # GET  /benchmarks/{indicator}
│       ├── services/
│       │   ├── replay_calculator.py    # engine de cálculo principal
│       │   ├── rebalance_strategies.py # Strategy pattern (none/monthly/quarterly)
│       │   └── metrics.py             # retorno, drawdown, volatilidade
│       ├── data/
│       │   ├── yfinance_provider.py   # Repository pattern sobre yfinance
│       │   └── bcb_provider.py        # integração SGS/BCB
│       ├── models/schemas.py          # schemas Pydantic (request + response)
│       └── core/                      # config, cache, exceptions
└── frontend/
    └── src/
        ├── components/
        │   ├── PortfolioBuilder.tsx  # formulário (ativos, pesos, período)
        │   ├── PerformanceChart.tsx  # gráfico de linha (carteira vs benchmarks)
        │   ├── MetricsPanel.tsx      # cards de métricas
        │   └── ShareLink.tsx         # gerador de link compartilhável
        ├── hooks/
        │   └── usePortfolioSimulation.ts  # estado + chamada à API
        └── utils/
            └── formatters.ts         # formatação de moeda, datas, percentuais
```

**Padrões aplicados:**

- **Repository pattern** na camada de dados — abstrai o yfinance; troca de fonte sem alterar lógica de negócio
- **Strategy pattern** no rebalanceamento — cada frequência implementa a mesma interface de cálculo
- **URL-as-state** para compartilhamento — zero banco de dados de usuários

## API

A documentação interativa (Swagger) fica em `http://localhost:8000/docs` após subir o backend.

### `POST /portfolio/simulate`

```json
// Request
{
  "assets": [
    { "ticker": "PETR4.SA", "weight": 0.4 },
    { "ticker": "VALE3.SA", "weight": 0.6 }
  ],
  "start_date": "2020-01-01",
  "initial_value": 10000.0,
  "monthly_contribution": 500.0,
  "rebalance_frequency": "quarterly"
}

// Response
{
  "timeline": [
    { "date": "2020-01-02", "portfolio_value": 10000.0, "ibov_value": 10000.0, "cdi_value": 10000.0 },
    ...
  ],
  "metrics": {
    "total_return": 0.4215,
    "annualized_return": 0.0923,
    "max_drawdown": -0.3812,
    "volatility": 0.2651
  }
}
```

### `GET /benchmarks/{indicator}`

Parâmetros: `cdi` · `ibov`

## Como rodar localmente

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# .env (opcional — valores padrão funcionam em dev)
cp .env.example .env

uvicorn app.main:app --reload
# http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# http://localhost:5173
```

O frontend aponta para `http://localhost:8000` por padrão. Para produção, configure `VITE_API_URL` no ambiente Vercel.

### Testes

```bash
# backend
cd backend
pytest

# frontend (lint)
cd frontend
npm run lint
```

## Variáveis de ambiente

```bash
# backend/.env
CACHE_TTL_HOURS=24
CORS_ORIGINS=http://localhost:5173,https://<seu-app>.vercel.app
```

Nenhuma chave de API é necessária — yfinance e BCB SGS são públicos e não exigem autenticação.

## Deploy

### Frontend — Vercel

1. Importe o repositório no [Vercel](https://vercel.com/new)
2. **Não altere** Root Directory (o `vercel.json` raiz já configura o build do `frontend/`)
3. Adicione a variável de ambiente:
   ```
   VITE_API_URL = https://<seu-backend>.railway.app
   ```
4. Deploy → Vercel faz o build com `npm --prefix frontend run build` automaticamente

### Backend — Railway

1. Crie um novo projeto no [Railway](https://railway.app) a partir do repositório
2. Configure o serviço para usar `backend/` como Root Directory
3. Adicione as variáveis de ambiente:
   ```
   CORS_ORIGINS=["https://<seu-app>.vercel.app"]
   CACHE_TTL_HOURS=24
   ```
4. O `Procfile` já define o comando de start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

> **Ordem:** suba o backend primeiro para ter a URL antes de configurar o Vercel.

## Licença

MIT
