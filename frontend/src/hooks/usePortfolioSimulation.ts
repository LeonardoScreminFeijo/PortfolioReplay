import { useState } from 'react'
import axios from 'axios'
import type { SimulateRequest, SimulateResponse } from '../types'

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000'

export function usePortfolioSimulation() {
  const [data, setData] = useState<SimulateResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function simulate(req: SimulateRequest): Promise<void> {
    setLoading(true)
    setError(null)
    try {
      const resp = await axios.post<SimulateResponse>(`${API_BASE}/portfolio/simulate`, req)
      setData(resp.data)
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail: unknown = err.response?.data?.detail
        setError(typeof detail === 'string' ? detail : err.message)
      } else {
        setError('Erro inesperado')
      }
    } finally {
      setLoading(false)
    }
  }

  return { data, loading, error, simulate }
}
