import { useEffect, useState } from 'react'
import type { SimulateRequest } from '../types'

interface Props {
  request: SimulateRequest
}

function buildUrl(req: SimulateRequest): string {
  const assetsStr = req.assets
    .map(a => `${a.ticker}:${Math.round(a.weight * 100)}`)
    .join(',')
  const params = new URLSearchParams({
    assets: assetsStr,
    start: req.start_date,
    initial: String(req.initial_value),
    contrib: String(req.monthly_contribution),
    rebal: req.rebalance_frequency,
  })
  return `${window.location.origin}${window.location.pathname}?${params.toString()}`
}

export default function ShareLink({ request }: Props) {
  const [copied, setCopied] = useState(false)
  const url = buildUrl(request)

  useEffect(() => {
    window.history.replaceState(
      null,
      '',
      `?${new URLSearchParams({
        assets: request.assets
          .map(a => `${a.ticker}:${Math.round(a.weight * 100)}`)
          .join(','),
        start: request.start_date,
        initial: String(request.initial_value),
        contrib: String(request.monthly_contribution),
        rebal: request.rebalance_frequency,
      }).toString()}`
    )
  }, [request])

  function handleCopy() {
    navigator.clipboard.writeText(url).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }).catch(() => undefined)
  }

  return (
    <div className="flex items-center gap-2 pt-1">
      <span className="text-[10px] uppercase tracking-widest text-zinc-600 font-medium shrink-0">
        Link
      </span>
      <div className="flex-1 min-w-0 bg-zinc-900 border border-white/[0.06] rounded-lg px-3 py-1.5 truncate">
        <span className="text-zinc-600 text-xs font-mono">{url}</span>
      </div>
      <button
        type="button"
        onClick={handleCopy}
        className="shrink-0 text-xs px-3 py-1.5 rounded-lg border transition-colors bg-zinc-900 border-white/[0.08] text-zinc-400 hover:text-zinc-200 hover:border-white/[0.15] active:scale-[0.97]"
      >
        {copied ? 'Copiado' : 'Copiar'}
      </button>
    </div>
  )
}
