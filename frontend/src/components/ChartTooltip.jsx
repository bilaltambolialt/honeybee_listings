// Shared hover tooltip: label, value and share of the total
export function ChartTooltip({ active, payload, total }) {
  if (!active || !payload?.length) {
    return null
  }
  const { label, count } = payload[0].payload
  return (
    <div className="tooltip">
      <div className="tooltip-label">{label}</div>
      <div className="tooltip-value">
        {count.toLocaleString()} listings
        <span className="tooltip-share"> · {((count / total) * 100).toFixed(1)}%</span>
      </div>
    </div>
  )
}
