import { useState } from 'react'

// Card wrapper for a chart, with a toggle to show the same numbers as an accessible table
export function ChartCard({ title, subtitle, rows, className = '', children }) {
  const [showTable, setShowTable] = useState(false)
  const total = rows.reduce((sum, row) => sum + row.count, 0)

  return (
    <section className={`card chart-card ${className}`} aria-label={title}>
      <header className="card-header">
        <div>
          <h2>{title}</h2>
          {subtitle && <p className="card-subtitle">{subtitle}</p>}
        </div>
        <button
          type="button"
          className="toggle"
          aria-pressed={showTable}
          onClick={() => setShowTable((value) => !value)}
        >
          {showTable ? 'Chart' : 'Table'}
        </button>
      </header>

      {showTable ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th scope="col">Name</th>
                <th scope="col" className="num">Listings</th>
                <th scope="col" className="num">Share</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.label}>
                  <td>{row.label}</td>
                  <td className="num">{row.count.toLocaleString()}</td>
                  <td className="num">{((row.count / total) * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        children
      )}
    </section>
  )
}
