import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { sourceColor } from '../theme.js'
import { ChartTooltip } from './ChartTooltip.jsx'

// Donut of listings per source, with total in the centre and a labelled legend (never colour alone)
export function SourceDonut({ rows, palette }) {
  const total = rows.reduce((sum, row) => sum + row.count, 0)

  return (
    <div className="donut-layout">
      <div className="donut-chart">
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={rows}
              dataKey="count"
              nameKey="label"
              innerRadius="62%"
              outerRadius="92%"
              paddingAngle={1}
              stroke={palette.surface}
              strokeWidth={2}
              isAnimationActive={false}
            >
              {rows.map((row) => (
                <Cell key={row.label} fill={sourceColor(palette, row.label)} />
              ))}
            </Pie>
            <Tooltip content={<ChartTooltip total={total} />} />
          </PieChart>
        </ResponsiveContainer>
        <div className="donut-centre" aria-hidden="true">
          <span className="donut-total">{total.toLocaleString()}</span>
          <span className="donut-caption">listings</span>
        </div>
      </div>
      <ul className="legend">
        {rows.map((row) => (
          <li key={row.label}>
            <span className="swatch" style={{ background: sourceColor(palette, row.label) }} />
            <span className="legend-label">{row.label}</span>
            <span className="legend-value">
              {row.count.toLocaleString()} · {((row.count / total) * 100).toFixed(0)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
