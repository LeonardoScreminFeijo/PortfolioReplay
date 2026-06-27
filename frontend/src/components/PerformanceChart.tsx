import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { TimelinePoint } from '../types'
import { formatCurrency, formatShortDate, formatTooltipDate } from '../utils/formatters'

interface Props {
  timeline: TimelinePoint[]
}

const PORTFOLIO_COLOR = '#34d399'  // emerald-400
const IBOV_COLOR = '#fbbf24'       // amber-400
const CDI_COLOR = '#818cf8'        // indigo-400

export default function PerformanceChart({ timeline }: Props) {
  return (
    <div className="rounded-xl border border-white/[0.08] bg-zinc-900 p-5">
      <p className="text-xs font-medium text-zinc-400 mb-5">Evolucao patrimonial</p>
      <ResponsiveContainer width="100%" height={340}>
        <LineChart data={timeline} margin={{ top: 4, right: 4, left: 4, bottom: 0 }}>
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
          />
          <Tooltip
            formatter={(value) => {
              const num = typeof value === 'number' ? value : Number(value ?? 0)
              return formatCurrency(num)
            }}
            labelFormatter={(label) => formatTooltipDate(String(label ?? ''))}
            contentStyle={{
              backgroundColor: '#18181b',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: '8px',
              fontSize: '12px',
              fontFamily: 'inherit',
              boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
            }}
            itemStyle={{ color: '#e4e4e7', padding: '1px 0' }}
            labelStyle={{
              color: '#71717a',
              marginBottom: '6px',
              fontSize: '11px',
            }}
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
          <Line
            type="monotone"
            dataKey="portfolio_value"
            name="Carteira"
            stroke={PORTFOLIO_COLOR}
            dot={false}
            strokeWidth={2}
            activeDot={{ r: 3, strokeWidth: 0, fill: PORTFOLIO_COLOR }}
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
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
