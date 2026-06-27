import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { ProjectionBand, TimelinePoint } from '../types'

interface TooltipPayloadItem {
  dataKey: string
  value: number | null | undefined
  color?: string
}

interface CustomTooltipInput {
  active?: boolean
  payload?: TooltipPayloadItem[]
  label?: string
}
import { formatCurrency, formatShortDate, formatTooltipDate } from '../utils/formatters'

interface Props {
  timeline: TimelinePoint[]
  projection?: ProjectionBand[]
}

interface ChartPoint {
  date: string
  portfolio_value?: number
  ibov_value?: number
  cdi_value?: number
  p10?: number
  p50?: number
  p90_minus_p10?: number
}

const PORTFOLIO_COLOR = '#34d399'
const IBOV_COLOR = '#fbbf24'
const CDI_COLOR = '#818cf8'

const NAME_MAP: Record<string, string> = {
  portfolio_value: 'Carteira',
  ibov_value: 'Ibovespa',
  cdi_value: 'CDI',
  p50: 'Mediana (proj.)',
}

function buildChartData(timeline: TimelinePoint[], projection?: ProjectionBand[]): ChartPoint[] {
  const historical: ChartPoint[] = timeline.map(p => ({
    date: p.date,
    portfolio_value: p.portfolio_value,
    ibov_value: p.ibov_value,
    cdi_value: p.cdi_value,
  }))

  if (!projection || projection.length === 0) return historical

  const last = timeline[timeline.length - 1]

  const bridge: ChartPoint = {
    date: last.date,
    portfolio_value: last.portfolio_value,
    ibov_value: last.ibov_value,
    cdi_value: last.cdi_value,
    p10: last.portfolio_value,
    p50: last.portfolio_value,
    p90_minus_p10: 0,
  }

  const projPoints: ChartPoint[] = projection.map(p => ({
    date: p.date,
    p10: p.p10,
    p50: p.p50,
    p90_minus_p10: p.p90 - p.p10,
  }))

  return [...historical.slice(0, -1), bridge, ...projPoints]
}

function CustomTooltip({ active, payload, label }: CustomTooltipInput) {
  if (!active || !payload?.length) return null

  const HIDDEN = new Set(['p10', 'p90_minus_p10'])
  const hasHistorical = payload.some((p: TooltipPayloadItem) => p.dataKey === 'portfolio_value' && p.value != null)

  const items = payload.filter((p: TooltipPayloadItem) => {
    if (HIDDEN.has(String(p.dataKey))) return false
    if (p.value == null) return false
    if (p.dataKey === 'p50' && hasHistorical) return false
    return true
  })

  if (!items.length) return null

  return (
    <div
      style={{
        backgroundColor: '#18181b',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: '8px',
        padding: '8px 12px',
        fontSize: '12px',
        fontFamily: 'inherit',
        boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
      }}
    >
      <p style={{ color: '#71717a', marginBottom: '6px', fontSize: '11px' }}>
        {formatTooltipDate(String(label ?? ''))}
      </p>
      {items.map((item: TooltipPayloadItem) => (
        <p key={item.dataKey} style={{ color: '#e4e4e7', padding: '1px 0' }}>
          <span style={{ color: item.color }}>
            {NAME_MAP[String(item.dataKey)] ?? String(item.dataKey)}
          </span>
          {': '}
          {formatCurrency(item.value as number)}
        </p>
      ))}
    </div>
  )
}

export default function PerformanceChart({ timeline, projection }: Props) {
  const hasProjection = projection != null && projection.length > 0
  const chartData = buildChartData(timeline, projection)
  const projectionStartDate = hasProjection ? timeline[timeline.length - 1].date : undefined

  return (
    <div className="rounded-xl border border-white/[0.08] bg-zinc-900 p-5">
      <p className="text-xs font-medium text-zinc-400 mb-5">Evolucao patrimonial</p>
      <ResponsiveContainer width="100%" height={340}>
        <ComposedChart data={chartData} margin={{ top: 4, right: 4, left: 4, bottom: 0 }}>
          <CartesianGrid
            strokeDasharray="0"
            stroke="rgba(255,255,255,0.04)"
            horizontal
            vertical={false}
          />
          <XAxis
            dataKey="date"
            tickFormatter={formatShortDate}
            interval="preserveStartEnd"
            tick={{ fill: '#52525b', fontSize: 10, fontFamily: 'inherit' }}
            tickLine={false}
            axisLine={false}
            dy={6}
          />
          <YAxis
            tickFormatter={(v: number) => formatCurrency(v)}
            width={104}
            tick={{ fill: '#52525b', fontSize: 10, fontFamily: 'inherit' }}
            tickLine={false}
            axisLine={false}
            domain={['auto', 'auto']}
          />
          <Tooltip
            content={<CustomTooltip />}
            cursor={{ stroke: 'rgba(255,255,255,0.08)', strokeWidth: 1 }}
          />
          <Legend
            wrapperStyle={{
              fontSize: '11px',
              paddingTop: '16px',
              color: '#71717a',
              fontFamily: 'inherit',
            }}
          />

          {hasProjection && (
            <>
              <Area
                type="monotone"
                dataKey="p10"
                fill="transparent"
                stroke="none"
                stackId="cone"
                legendType="none"
                dot={false}
                activeDot={false}
                isAnimationActive={false}
              />
              <Area
                type="monotone"
                dataKey="p90_minus_p10"
                fill="rgba(52,211,153,0.10)"
                stroke="none"
                stackId="cone"
                legendType="none"
                dot={false}
                activeDot={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="p50"
                name="Projecao (mediana)"
                stroke={PORTFOLIO_COLOR}
                strokeDasharray="5 4"
                strokeOpacity={0.6}
                strokeWidth={1.5}
                dot={false}
                activeDot={{ r: 3, strokeWidth: 0, fill: PORTFOLIO_COLOR }}
                connectNulls={false}
                isAnimationActive={false}
              />
              <ReferenceLine
                x={projectionStartDate}
                stroke="rgba(255,255,255,0.12)"
                strokeDasharray="4 4"
                label={{
                  value: 'Hoje',
                  position: 'insideTopRight',
                  fill: '#52525b',
                  fontSize: 10,
                  fontFamily: 'inherit',
                }}
              />
            </>
          )}

          <Line
            type="monotone"
            dataKey="portfolio_value"
            name="Carteira"
            stroke={PORTFOLIO_COLOR}
            dot={false}
            strokeWidth={2}
            activeDot={{ r: 3, strokeWidth: 0, fill: PORTFOLIO_COLOR }}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="ibov_value"
            name="Ibovespa"
            stroke={IBOV_COLOR}
            dot={false}
            strokeWidth={1.5}
            strokeOpacity={0.8}
            activeDot={{ r: 3, strokeWidth: 0, fill: IBOV_COLOR }}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="cdi_value"
            name="CDI"
            stroke={CDI_COLOR}
            dot={false}
            strokeWidth={1.5}
            strokeOpacity={0.8}
            activeDot={{ r: 3, strokeWidth: 0, fill: CDI_COLOR }}
            connectNulls={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
