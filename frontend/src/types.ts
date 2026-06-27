export interface AssetWeight {
  ticker: string
  weight: number  // 0.0–1.0
}

export type RebalanceFrequency = 'none' | 'monthly' | 'quarterly'

export interface SimulateRequest {
  assets: AssetWeight[]
  start_date: string
  end_date?: string
  initial_value: number
  monthly_contribution: number
  rebalance_frequency: RebalanceFrequency
  projection_months?: number
}

export interface TimelinePoint {
  date: string
  portfolio_value: number
  ibov_value: number
  cdi_value: number
}

export interface Metrics {
  total_return: number
  annualized_return: number
  max_drawdown: number
  volatility: number
}

export interface ProjectionBand {
  date: string
  p10: number
  p25: number
  p50: number
  p75: number
  p90: number
}

export interface SimulateResponse {
  timeline: TimelinePoint[]
  metrics: Metrics
  projection?: ProjectionBand[]
}

export interface RowState {
  ticker: string
  weightStr: string
}

export interface PortfolioBuilderDefaults {
  rows: RowState[]
  startDate: string
  initialValue: string
  monthlyContrib: string
  rebalFreq: RebalanceFrequency
  projectionMonths: number
}
