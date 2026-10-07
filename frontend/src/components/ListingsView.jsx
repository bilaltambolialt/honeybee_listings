import { useEffect, useState } from 'react'
import { fetchListings, listingsExportUrl } from '../api.js'

const PAGE_SIZE = 25
const EMPTY_FILTERS = { city: '', category: '', source: '', q: '' }

// Waits until the value stops changing, so typing in the search box doesn't send a request per key
function useDebounced(value, delayMs) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs)
    return () => clearTimeout(timer)
  }, [value, delayMs])
  return debounced
}

function FilterSelect({ label, value, options, onChange }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">All</option>
        {options.map((option) => (
          <option key={option.label} value={option.label}>
            {option.label} ({option.count})
          </option>
        ))}
      </select>
    </label>
  )
}

// Searchable, filterable table of stored listings with CSV download
export function ListingsView({ options }) {
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const [page, setPage] = useState(1)
  const [result, setResult] = useState({ status: 'loading', data: null, error: null })
  const search = useDebounced(filters.q, 300)
  const active = { ...filters, q: search }

  const { city, category, source } = filters
  useEffect(() => {
    const controller = new AbortController()
    fetchListings({ city, category, source, q: search, page, page_size: PAGE_SIZE }, controller.signal)
      .then((data) => setResult({ status: 'ready', data, error: null }))
      .catch((error) => {
        if (error.name !== 'AbortError') {
          setResult({ status: 'error', data: null, error })
        }
      })
    return () => controller.abort()
  }, [city, category, source, search, page])

  // Keep showing the current rows (faded) while the next result loads
  const markLoading = () => setResult((prev) => ({ ...prev, status: 'loading' }))
  const goToPage = (next) => {
    markLoading()
    setPage(next)
  }
  const update = (key) => (value) => {
    if (key !== 'q') {
      markLoading()
    }
    setFilters((prev) => ({ ...prev, [key]: value }))
    setPage(1)
  }
  const isFiltered = Object.values(filters).some(Boolean)
  const data = result.data
  const pageCount = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1

  return (
    <section className="card listings" aria-label="Browse listings">
      <div className="filters">
        <label className="field field-search">
          <span className="field-label">Search</span>
          <input
            type="search"
            placeholder="Name or address"
            value={filters.q}
            onChange={(e) => update('q')(e.target.value)}
          />
        </label>
        <FilterSelect label="City" value={filters.city} options={options.cities} onChange={update('city')} />
        <FilterSelect label="Category" value={filters.category} options={options.categories} onChange={update('category')} />
        <FilterSelect label="Source" value={filters.source} options={options.sources} onChange={update('source')} />
      </div>

      <div className="listings-toolbar">
        <p className="result-count" aria-live="polite">
          {data ? `${data.total.toLocaleString()} ${data.total === 1 ? 'listing' : 'listings'}` : 'Loading…'}
          {isFiltered && (
            <button
              type="button"
              className="link-button"
              onClick={() => {
                markLoading()
                setFilters(EMPTY_FILTERS)
                setPage(1)
              }}
            >
              Clear filters
            </button>
          )}
        </p>
        <a className="button" href={listingsExportUrl(active)} download>
          Download CSV
        </a>
      </div>

      {result.status === 'error' && (
        <p role="alert" className="inline-error">Couldn't load listings: {result.error.message}</p>
      )}

      <div className={`table-wrap ${result.status === 'loading' ? 'is-loading' : ''}`}>
        <table className="listings-table">
          <thead>
            <tr>
              <th scope="col">Business</th>
              <th scope="col">Category</th>
              <th scope="col">City</th>
              <th scope="col">Address</th>
              <th scope="col">Phone</th>
              <th scope="col">Source</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((item) => (
              <tr key={item.id}>
                <td className="cell-name">{item.business_name}</td>
                <td data-label="Category">{item.category}</td>
                <td data-label="City">{item.city}</td>
                <td className="cell-address" data-label="Address">{item.address ?? '—'}</td>
                <td className="cell-phone" data-label="Phone">{item.phone ?? '—'}</td>
                <td data-label="Source">{item.source}</td>
              </tr>
            ))}
            {data && data.items.length === 0 && (
              <tr>
                <td colSpan={6} className="no-results">No listings match these filters.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {data && data.total > PAGE_SIZE && (
        <nav className="pagination" aria-label="Pages">
          <button type="button" className="toggle" disabled={page === 1} onClick={() => goToPage(page - 1)}>
            Previous
          </button>
          <span>
            Page {page} of {pageCount}
          </span>
          <button type="button" className="toggle" disabled={page >= pageCount} onClick={() => goToPage(page + 1)}>
            Next
          </button>
        </nav>
      )}
    </section>
  )
}
