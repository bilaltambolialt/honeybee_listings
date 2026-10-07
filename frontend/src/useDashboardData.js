import { useCallback, useEffect, useState } from 'react'
import { fetchDashboard } from './api.js'

// Loads dashboard data and exposes { status: 'loading' | 'error' | 'ready', data, error, reload }
export function useDashboardData() {
  const [state, setState] = useState({ status: 'loading', data: null, error: null })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    // Abort the request if the component unmounts or a reload starts before it finishes
    const controller = new AbortController()
    fetchDashboard(controller.signal)
      .then((data) => setState({ status: 'ready', data, error: null }))
      .catch((error) => {
        if (error.name !== 'AbortError') {
          setState({ status: 'error', data: null, error })
        }
      })
    return () => controller.abort()
  }, [attempt])

  // Show the loading state immediately, then let the effect re-fetch
  const reload = useCallback(() => {
    setState((prev) => ({ ...prev, status: 'loading', error: null }))
    setAttempt((n) => n + 1)
  }, [])
  return { ...state, reload }
}
