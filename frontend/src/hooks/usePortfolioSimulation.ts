import { useRef, useState } from 'react'
import axios from 'axios'
import type { SimulateRequest, SimulateResponse } from '../types'

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000'

export type ErrorKind = 'ticker' | 'source' | 'network' | null

export function usePortfolioSimulation() {
  const [data, setData] = useState<SimulateResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [errorKind, setErrorKind] = useState<ErrorKind>(null)
  const lastRequest = useRef<SimulateRequest | null>(null)

  async function simulate(req: SimulateRequest): Promise<void> {
    lastRequest.current = req
    setLoading(true)
    setError(null)
    setErrorKind(null)
    try {
      const resp = await axios.post<SimulateResponse>(`${API_BASE}/portfolio/simulate`, req)
      setData(resp.data)
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const status = err.response?.status
        const detail: unknown = err.response?.data?.detail
        setError(typeof detail === 'string' ? detail : err.message)
        if (status === 404) setErrorKind('ticker')
        else if (status === 502) setErrorKind('source')
        else setErrorKind('network')
      } else {
        setError('Erro inesperado')
        setErrorKind('network')
      }
    } finally {
      setLoading(false)
    }
  }

  function retry() {
    if (lastRequest.current) void simulate(lastRequest.current)
  }

  return { data, loading, error, errorKind, simulate, retry }
}
