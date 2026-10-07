// Thin client for the FastAPI backend. The base URL comes from VITE_API_BASE_URL (see .env.example).
const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')

async function getJSON(path, signal) {
  const response = await fetch(`${API_BASE}${path}`, { signal })
  if (!response.ok) {
    throw new Error(`${path} returned HTTP ${response.status}`)
  }
  return response.json()
}

// All four dashboard endpoints in parallel; one failure rejects the whole load
export async function fetchDashboard(signal) {
  const [summary, cities, categories, sources] = await Promise.all([
    getJSON('/api/dashboard/summary', signal),
    getJSON('/api/dashboard/cities', signal),
    getJSON('/api/dashboard/categories', signal),
    getJSON('/api/dashboard/sources', signal),
  ])
  return { summary, cities, categories, sources }
}

// Query string from filter values, leaving out empty ones
function toQuery(params) {
  const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value !== '' && value != null))
  return query.toString()
}

// One page of listings: { items, total, page, page_size }
export function fetchListings(params, signal) {
  return getJSON(`/api/listings?${toQuery(params)}`, signal)
}

// Direct link to the CSV export with the same filters (the browser downloads it)
export function listingsExportUrl(filters) {
  const query = toQuery(filters)
  return `${API_BASE}/api/listings/export.csv${query ? `?${query}` : ''}`
}

export { API_BASE }
