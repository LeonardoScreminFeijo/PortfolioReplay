import { useState } from 'react'
import type { PortfolioBuilderDefaults, RebalanceFrequency, RowState, SimulateRequest } from '../types'

interface Props {
  onSimulate: (req: SimulateRequest) => void
  loading: boolean
  defaults: PortfolioBuilderDefaults
}

function validate(rows: RowState[], startDate: string, initialValue: string): string | null {
  if (rows.length === 0) return 'Adicione pelo menos um ativo.'
  for (const r of rows) {
    if (!r.ticker.trim()) return 'Ticker nao pode ser vazio.'
    const w = parseFloat(r.weightStr)
    if (isNaN(w) || w <= 0) return `Peso de ${r.ticker || '?'} deve ser maior que 0.`
  }
  const tickers = rows.map(r => r.ticker.trim().toUpperCase())
  if (new Set(tickers).size !== tickers.length) return 'Tickers duplicados.'
  const sum = rows.reduce((acc, r) => acc + (parseFloat(r.weightStr) || 0), 0)
  if (Math.abs(sum - 100) > 0.1) return `Pesos somam ${sum.toFixed(1)}% - deve ser 100%.`
  if (!startDate) return 'Selecione a data de inicio.'
  if (new Date(startDate + 'T12:00:00') >= new Date()) return 'Data de inicio deve ser anterior a hoje.'
  const iv = parseFloat(initialValue)
  if (isNaN(iv) || iv <= 0) return 'Valor inicial deve ser maior que 0.'
  return null
}

const yesterday = (() => {
  const d = new Date()
  d.setDate(d.getDate() - 1)
  return d.toISOString().split('T')[0]
})()

const INPUT_CLASS =
  'w-full bg-zinc-950 text-zinc-100 placeholder-zinc-700 rounded-lg px-3 py-2 text-sm border border-white/[0.08] focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-colors'

const LABEL_CLASS = 'block text-xs text-zinc-500 mb-1.5'

const SELECT_ARROW =
  "url(\"data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%2352525b' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e\")"

export default function PortfolioBuilder({ onSimulate, loading, defaults }: Props) {
  const [rows, setRows] = useState<RowState[]>(defaults.rows)
  const [startDate, setStartDate] = useState(defaults.startDate)
  const [initialValue, setInitialValue] = useState(defaults.initialValue)
  const [monthlyContrib, setMonthlyContrib] = useState(defaults.monthlyContrib)
  const [rebalFreq, setRebalFreq] = useState<RebalanceFrequency>(defaults.rebalFreq)
  const [validationError, setValidationError] = useState<string | null>(null)

  const weightSum = rows.reduce((acc, r) => acc + (parseFloat(r.weightStr) || 0), 0)
  const sumOk = Math.abs(weightSum - 100) < 0.1

  function addRow() {
    setRows(prev => [...prev, { ticker: '', weightStr: '' }])
  }

  function removeRow(i: number) {
    setRows(prev => prev.filter((_, idx) => idx !== i))
  }

  function updateRow(i: number, field: keyof RowState, value: string) {
    setRows(prev => prev.map((r, idx) => (idx === i ? { ...r, [field]: value } : r)))
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const err = validate(rows, startDate, initialValue)
    if (err) {
      setValidationError(err)
      return
    }
    setValidationError(null)
    onSimulate({
      assets: rows.map(r => ({
        ticker: r.ticker.trim().toUpperCase(),
        weight: parseFloat(r.weightStr) / 100,
      })),
      start_date: startDate,
      initial_value: parseFloat(initialValue),
      monthly_contribution: parseFloat(monthlyContrib) || 0,
      rebalance_frequency: rebalFreq,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Ativos */}
      <div className="space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium">
            Ativos
          </span>
          <span
            className={`text-[11px] font-mono tabular-nums transition-colors ${
              sumOk ? 'text-emerald-400' : 'text-rose-400'
            }`}
          >
            {weightSum.toFixed(1)} / 100%
          </span>
        </div>

        {rows.map((row, i) => (
          <div key={i} className="flex gap-2 items-center">
            <input
              type="text"
              value={row.ticker}
              onChange={e => updateRow(i, 'ticker', e.target.value.toUpperCase())}
              placeholder="PETR4"
              maxLength={10}
              className="w-24 shrink-0 bg-zinc-950 text-zinc-100 placeholder-zinc-700 rounded-lg px-3 py-2 text-sm font-mono border border-white/[0.08] focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-colors"
            />
            <div className="relative flex-1">
              <input
                type="number"
                value={row.weightStr}
                onChange={e => updateRow(i, 'weightStr', e.target.value)}
                placeholder="50"
                min="0.1"
                max="100"
                step="0.1"
                className="w-full bg-zinc-950 text-zinc-100 placeholder-zinc-700 rounded-lg px-3 py-2 pr-7 text-sm font-mono tabular-nums border border-white/[0.08] focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-colors"
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-600 text-xs font-mono pointer-events-none">
                %
              </span>
            </div>
            <button
              type="button"
              onClick={() => removeRow(i)}
              disabled={rows.length === 1}
              className="shrink-0 w-7 h-7 flex items-center justify-center rounded text-zinc-600 hover:text-rose-400 disabled:opacity-20 disabled:pointer-events-none transition-colors"
            >
              <svg width="10" height="10" viewBox="0 0 10 10" fill="none" aria-hidden="true">
                <path d="M1 1L9 9M9 1L1 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </button>
          </div>
        ))}

        <button
          type="button"
          onClick={addRow}
          className="text-xs text-emerald-500 hover:text-emerald-400 transition-colors"
        >
          + Adicionar ativo
        </button>
      </div>

      <div className="border-t border-white/[0.06]" />

      {/* Periodo */}
      <div className="space-y-3">
        <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium">
          Periodo
        </span>
        <div>
          <label className={LABEL_CLASS}>Data de inicio</label>
          <input
            type="date"
            value={startDate}
            onChange={e => setStartDate(e.target.value)}
            max={yesterday}
            className={INPUT_CLASS}
          />
        </div>
      </div>

      <div className="border-t border-white/[0.06]" />

      {/* Aportes */}
      <div className="space-y-3">
        <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium">
          Aportes
        </span>
        <div>
          <label className={LABEL_CLASS}>Valor inicial (R$)</label>
          <input
            type="number"
            value={initialValue}
            onChange={e => setInitialValue(e.target.value)}
            min="1"
            step="any"
            className={`${INPUT_CLASS} font-mono tabular-nums`}
          />
        </div>
        <div>
          <label className={LABEL_CLASS}>Aporte mensal (R$)</label>
          <input
            type="number"
            value={monthlyContrib}
            onChange={e => setMonthlyContrib(e.target.value)}
            min="0"
            step="any"
            className={`${INPUT_CLASS} font-mono tabular-nums`}
          />
        </div>
      </div>

      <div className="border-t border-white/[0.06]" />

      {/* Estrategia */}
      <div className="space-y-3">
        <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium">
          Estrategia
        </span>
        <div>
          <label className={LABEL_CLASS}>Rebalanceamento</label>
          <select
            value={rebalFreq}
            onChange={e => setRebalFreq(e.target.value as RebalanceFrequency)}
            className={`${INPUT_CLASS} appearance-none cursor-pointer pr-8`}
            style={{
              backgroundImage: SELECT_ARROW,
              backgroundPosition: 'right 0.75rem center',
              backgroundRepeat: 'no-repeat',
              backgroundSize: '1rem',
            }}
          >
            <option value="none">Sem rebalanceamento</option>
            <option value="monthly">Mensal</option>
            <option value="quarterly">Trimestral</option>
          </select>
        </div>
      </div>

      {validationError && (
        <p className="text-xs text-rose-300 bg-rose-500/[0.08] border border-rose-500/20 rounded-lg px-3 py-2.5 leading-relaxed">
          {validationError}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-emerald-500 hover:bg-emerald-400 active:scale-[0.98] disabled:bg-zinc-800 disabled:text-zinc-600 disabled:cursor-not-allowed text-zinc-950 font-semibold py-2.5 rounded-xl transition-all duration-150 text-sm"
      >
        {loading ? 'Calculando...' : 'Simular'}
      </button>
    </form>
  )
}
