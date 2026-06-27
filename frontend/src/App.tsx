import { useState } from 'react'
import PortfolioBuilder from './components/PortfolioBuilder'
import PerformanceChart from './components/PerformanceChart'
import MetricsPanel from './components/MetricsPanel'
import ShareLink from './components/ShareLink'
import { usePortfolioSimulation } from './hooks/usePortfolioSimulation'
import type { ErrorKind } from './hooks/usePortfolioSimulation'
import type { PortfolioBuilderDefaults, RebalanceFrequency, SimulateRequest } from './types'

function parseUrlDefaults(): PortfolioBuilderDefaults {
  const p = new URLSearchParams(window.location.search)
  const assetsStr = p.get('assets')
  const rows = assetsStr
    ? assetsStr.split(',').map(s => {
        const parts = s.split(':')
        return { ticker: parts[0] ?? '', weightStr: parts[1] ?? '' }
      })
    : [{ ticker: '', weightStr: '' }]
  return {
    rows,
    startDate: p.get('start') ?? '',
    initialValue: p.get('initial') ?? '1000',
    monthlyContrib: p.get('contrib') ?? '0',
    rebalFreq: (p.get('rebal') ?? 'none') as RebalanceFrequency,
    projectionMonths: 0,
  }
}

const ERROR_HINTS: Record<NonNullable<ErrorKind>, string> = {
  ticker: 'Verifique se o ticker existe e usa sufixo .SA para acoes brasileiras (ex: PETR4.SA).',
  source: 'Fonte de dados indisponivel. Tente novamente em alguns minutos.',
  network: 'Nao foi possivel conectar ao servidor.',
}

function ErrorBanner({
  message,
  kind,
  onRetry,
}: {
  message: string
  kind: ErrorKind
  onRetry: () => void
}) {
  const hint = kind ? ERROR_HINTS[kind] : null
  const canRetry = kind === 'source' || kind === 'network'

  return (
    <div className="rounded-lg border border-rose-500/20 bg-rose-500/[0.08] px-4 py-3 space-y-1.5">
      <p className="text-sm text-rose-300">{message}</p>
      {hint && <p className="text-xs text-rose-400/70">{hint}</p>}
      {canRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="text-xs text-rose-300 underline underline-offset-2 hover:text-rose-200 transition-colors"
        >
          Tentar novamente
        </button>
      )}
    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[420px] rounded-xl border border-dashed border-white/[0.08] gap-4">
      <div className="w-11 h-11 rounded-full bg-zinc-900 border border-white/[0.08] flex items-center justify-center">
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-zinc-500"
        >
          <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
          <polyline points="16 7 22 7 22 13" />
        </svg>
      </div>
      <div className="text-center space-y-1.5">
        <p className="text-zinc-300 text-sm font-medium">Nenhuma simulacao ainda</p>
        <p className="text-zinc-600 text-xs">
          Configure a carteira ao lado e clique em{' '}
          <span className="text-zinc-400">Simular</span>
        </p>
      </div>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="flex rounded-xl border border-white/[0.06] bg-zinc-900 overflow-hidden">
        {[0, 1, 2, 3].map(i => (
          <div key={i} className="flex-1 py-4 px-5 border-r border-white/[0.06] last:border-r-0">
            <div className="h-2 w-16 bg-zinc-800 rounded mb-4" />
            <div className="h-7 w-20 bg-zinc-800 rounded" />
          </div>
        ))}
      </div>
      <div className="rounded-xl border border-white/[0.06] bg-zinc-900 p-5">
        <div className="h-3.5 w-20 bg-zinc-800 rounded mb-6" />
        <div className="h-[340px] bg-zinc-800/40 rounded-lg" />
      </div>
    </div>
  )
}

export default function App() {
  const { data, loading, error, errorKind, simulate, retry } = usePortfolioSimulation()
  const [lastRequest, setLastRequest] = useState<SimulateRequest | null>(null)
  const [simCount, setSimCount] = useState(0)
  const [urlDefaults] = useState<PortfolioBuilderDefaults>(parseUrlDefaults)

  function handleSimulate(req: SimulateRequest) {
    setLastRequest(req)
    setSimCount(c => c + 1)
    simulate(req)
  }

  return (
    <div className="min-h-[100dvh] bg-zinc-950 text-zinc-50">
      <header className="sticky top-0 z-10 h-12 flex items-center gap-4 px-5 border-b border-white/[0.06] bg-zinc-950/90 backdrop-blur-sm">
        <span className="text-sm font-semibold tracking-tight">
          Portfolio<span className="text-emerald-400">Replay</span>
        </span>
        <span className="hidden sm:block text-zinc-600 text-xs">
          Simulador de Carteira Historica
        </span>
      </header>

      <div className="flex flex-col md:flex-row min-h-[calc(100dvh-48px)]">
        <aside className="md:w-[340px] md:shrink-0 border-b md:border-b-0 md:border-r border-white/[0.06] md:sticky md:top-12 md:max-h-[calc(100dvh-48px)] md:overflow-y-auto">
          <div className="p-5">
            <PortfolioBuilder
              onSimulate={handleSimulate}
              loading={loading}
              defaults={urlDefaults}
            />
          </div>
        </aside>

        <main className="flex-1 p-5 md:p-6 space-y-4">
          {error && <ErrorBanner message={error} kind={errorKind} onRetry={retry} />}
          {loading && <LoadingSkeleton />}
          {data && !loading && (
            <>
              <MetricsPanel key={simCount} metrics={data.metrics} />
              <PerformanceChart timeline={data.timeline} projection={data.projection} />
              {lastRequest && <ShareLink request={lastRequest} />}
            </>
          )}
          {!data && !loading && !error && <EmptyState />}
        </main>
      </div>
    </div>
  )
}
