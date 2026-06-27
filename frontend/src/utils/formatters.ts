export function formatPercent(v: number, showSign = true): string {
  const sign = showSign && v >= 0 ? '+' : ''
  return `${sign}${(v * 100).toFixed(1)}%`
}

export function formatCurrency(v: number): string {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v)
}

export function formatShortDate(dateStr: string): string {
  const parts = dateStr.split('-')
  const d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]))
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })
}

export function formatTooltipDate(dateStr: string): string {
  const parts = dateStr.split('-')
  const d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]))
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}
