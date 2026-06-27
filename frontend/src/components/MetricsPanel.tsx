import { useEffect, useRef, useState } from 'react'
import type { Metrics } from '../types'
import { formatPercent } from '../utils/formatters'

interface Props {
  metrics: Metrics
}

function useCountUp(target: number, duration = 650): number {
  const [value, setValue] = useState(0)
  const startRef = useRef<number | null>(null)
  const rafRef = useRef<number | null>(null)

  useEffect(() => {
    startRef.current = null
    if (rafRef.current) cancelAnimationFrame(rafRef.current)

    const step = (ts: number) => {
      if (!startRef.current) startRef.current = ts
      const progress = Math.min((ts - startRef.current) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setValue(target * eased)
      if (progress < 1) rafRef.current = requestAnimationFrame(step)
    }

    rafRef.current = requestAnimationFrame(step)
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [target, duration])

  return value
}

interface MetricItemProps {
  label: string
  rawValue: number
  showSign?: boolean
  colorClass: string
}

function MetricItem({ label, rawValue, showSign = true, colorClass }: MetricItemProps) {
  const animated = useCountUp(rawValue)

  return (
    <div className="flex-1 min-w-[130px] py-4 px-5 border-r border-white/[0.06] last:border-r-0">
      <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium mb-2">
        {label}
      </p>
      <p className={`text-[1.625rem] font-mono font-semibold tabular-nums leading-none ${colorClass}`}>
        {formatPercent(animated, showSign)}
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
          rawValue={metrics.total_return}
          colorClass={sign(metrics.total_return)}
        />
        <MetricItem
          label="Ret. Anualizado"
          rawValue={metrics.annualized_return}
          colorClass={sign(metrics.annualized_return)}
        />
        <MetricItem
          label="Drawdown Max."
          rawValue={metrics.max_drawdown}
          colorClass="text-rose-400"
        />
        <MetricItem
          label="Volatilidade"
          rawValue={metrics.volatility}
          showSign={false}
          colorClass="text-zinc-300"
        />
      </div>
    </div>
  )
}
