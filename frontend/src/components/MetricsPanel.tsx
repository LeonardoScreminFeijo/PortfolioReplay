import type { Metrics } from '../types'
import { formatPercent } from '../utils/formatters'

interface Props {
  metrics: Metrics
}

interface MetricItemProps {
  label: string
  value: string
  colorClass: string
}

function MetricItem({ label, value, colorClass }: MetricItemProps) {
  return (
    <div className="flex-1 min-w-[130px] py-4 px-5 border-r border-white/[0.06] last:border-r-0">
      <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium mb-2">
        {label}
      </p>
      <p className={`text-[1.625rem] font-mono font-semibold tabular-nums leading-none ${colorClass}`}>
        {value}
      </p>
    </div>
  )
}

export default function MetricsPanel({ metrics }: Props) {
  const sign = (v: number) => (v >= 0 ? 'text-emerald-400' : 'text-rose-400')

  return (
    <div className="overflow-x-auto">
      <div className="flex rounded-xl border border-white/[0.08] bg-zinc-900 overflow-hidden min-w-max md:min-w-0">
        <MetricItem
          label="Retorno Total"
          value={formatPercent(metrics.total_return)}
          colorClass={sign(metrics.total_return)}
        />
        <MetricItem
          label="Ret. Anualizado"
          value={formatPercent(metrics.annualized_return)}
          colorClass={sign(metrics.annualized_return)}
        />
        <MetricItem
          label="Drawdown Max."
          value={formatPercent(metrics.max_drawdown)}
          colorClass="text-rose-400"
        />
        <MetricItem
          label="Volatilidade"
          value={formatPercent(metrics.volatility, false)}
          colorClass="text-zinc-300"
        />
      </div>
    </div>
  )
}
