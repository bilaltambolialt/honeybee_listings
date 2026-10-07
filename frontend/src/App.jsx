import { API_BASE } from './api.js'
import { useDashboardData } from './useDashboardData.js'

function CountTable({ title, rows }) {
  return (
    <section>
      <h2>{title}</h2>
      <table>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label}>
              <td>{row.label}</td>
              <td>{row.count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}

function App() {
  const { status, data, error, reload } = useDashboardData()

  if (status === 'loading') {
    return <p>Loading dashboard…</p>
  }
  if (status === 'error') {
    return (
      <div role="alert">
        <p>Could not load data from {API_BASE}: {error.message}</p>
        <button onClick={reload}>Try again</button>
      </div>
    )
  }

  const { summary, cities, categories, sources } = data
  return (
    <main>
      <h1>Business Listings Dashboard</h1>
      <ul>
        <li>Total listings: {summary.total_listings}</li>
        <li>Cities: {summary.cities}</li>
        <li>Categories: {summary.categories}</li>
        <li>Sources: {summary.sources}</li>
        <li>With phone: {summary.with_phone}</li>
      </ul>
      <CountTable title="City-wise count" rows={cities} />
      <CountTable title="Category-wise count" rows={categories} />
      <CountTable title="Source-wise count" rows={sources} />
    </main>
  )
}

export default App
