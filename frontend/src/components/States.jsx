// Placeholder shapes shown while data loads, so the layout doesn't jump when it arrives
export function LoadingState() {
  return (
    <div aria-busy="true" aria-label="Loading dashboard">
      <div className="kpis">
        {Array.from({ length: 5 }, (_, i) => (
          <div className="card kpi skeleton" key={i} />
        ))}
      </div>
      <div className="grid">
        <div className="card skeleton skeleton-chart span-2" />
        <div className="card skeleton skeleton-chart" />
        <div className="card skeleton skeleton-chart span-3" />
      </div>
    </div>
  )
}

export function ErrorState({ apiBase, error, onRetry }) {
  return (
    <div className="card message" role="alert">
      <h2>Couldn't load the dashboard</h2>
      <p>
        The API at <code>{apiBase}</code> didn't respond ({error.message}). Check that the backend is running,
        then try again.
      </p>
      <button type="button" className="button" onClick={onRetry}>
        Try again
      </button>
    </div>
  )
}

export function EmptyState() {
  return (
    <div className="card message">
      <h2>No listings yet</h2>
      <p>
        The database is empty. Load the clean dataset with <code>scraper/load_to_api.py</code>, then refresh.
      </p>
    </div>
  )
}
