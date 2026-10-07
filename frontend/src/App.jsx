import { useEffect, useState } from 'react'
import { API_BASE } from './api.js'
import { BarCountChart } from './components/BarCountChart.jsx'
import { ChartCard } from './components/ChartCard.jsx'
import { KpiCards } from './components/KpiCards.jsx'
import { ListingsView } from './components/ListingsView.jsx'
import { SourceDonut } from './components/SourceDonut.jsx'
import { EmptyState, ErrorState, LoadingState } from './components/States.jsx'
import { usePalette } from './theme.js'
import { useDashboardData } from './useDashboardData.js'
import { useMediaQuery } from './useMediaQuery.js'

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'listings', label: 'Browse listings' },
]

function readHashTab() {
  return TABS.some((t) => `#${t.id}` === window.location.hash) ? window.location.hash.slice(1) : 'overview'
}

// The active tab lives in the URL hash (#listings), so it survives a refresh and can be linked to
function useHashTab() {
  const [tab, setTab] = useState(readHashTab)
  useEffect(() => {
    const onHashChange = () => setTab(readHashTab())
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])
  return [tab, (id) => { window.location.hash = id }]
}

function Overview({ data, palette }) {
  const { summary, cities, categories, sources } = data
  // On phones, city names don't fit under vertical bars, so that chart turns horizontal
  const isNarrow = useMediaQuery('(max-width: 600px)')
  return (
    <>
      <KpiCards summary={summary} />
      <div className="grid">
        <ChartCard title="Listings by city" subtitle={`${summary.cities} cities`} rows={cities} className="span-2">
          <BarCountChart rows={cities} palette={palette} horizontal={isNarrow} />
        </ChartCard>
        <ChartCard title="Listings by source" subtitle={`${summary.sources} data sources`} rows={sources}>
          <SourceDonut rows={sources} palette={palette} />
        </ChartCard>
        <ChartCard
          title="Listings by category"
          subtitle={`${summary.categories} categories, largest first`}
          rows={categories}
          className="span-3"
        >
          <BarCountChart rows={categories} palette={palette} horizontal />
        </ChartCard>
      </div>
    </>
  )
}

function App() {
  const { status, data, error, reload } = useDashboardData()
  const palette = usePalette()
  const [tab, setTab] = useHashTab()

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Business Listings Dashboard</h1>
          <p className="page-subtitle">
            Business listings across six Indian cities, collected from open data sources and served from MySQL
            through a FastAPI backend.
          </p>
        </div>
        <button type="button" className="button button-secondary" onClick={reload} disabled={status === 'loading'}>
          {status === 'loading' ? 'Loading…' : 'Refresh'}
        </button>
      </header>

      <nav className="tabs" role="tablist" aria-label="Views">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={tab === t.id}
            className="tab"
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main>
        {status === 'loading' && <LoadingState />}
        {status === 'error' && <ErrorState apiBase={API_BASE} error={error} onRetry={reload} />}
        {status === 'ready' && data.summary.total_listings === 0 && <EmptyState />}
        {status === 'ready' && data.summary.total_listings > 0 && (
          tab === 'overview' ? <Overview data={data} palette={palette} /> : <ListingsView options={data} />
        )}
      </main>

      <footer className="page-footer">
        Data: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> (ODbL) · Powered by{' '}
        <a href="https://www.geoapify.com/">Geoapify</a> · Bank branches from the Reserve Bank of India via{' '}
        <a href="https://github.com/razorpay/ifsc">razorpay/ifsc</a>
      </footer>
    </div>
  )
}

export default App
