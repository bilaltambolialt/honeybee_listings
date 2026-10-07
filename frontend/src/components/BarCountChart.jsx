import { Bar, BarChart, CartesianGrid, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { ChartTooltip } from './ChartTooltip.jsx'

// Single-series bar chart for [{label, count}] data, vertical or horizontal
export function BarCountChart({ rows, palette, horizontal = false }) {
  const total = rows.reduce((sum, row) => sum + row.count, 0)
  const axisTick = { fill: palette.textMuted, fontSize: 12 }
  // Explicit ticks on a "nice" step (0, 50, 100…) so the axis never shows values like 65 or 195
  const max = Math.max(...rows.map((row) => row.count), 1)
  const step = 10 ** Math.floor(Math.log10(max)) / 2
  const top = Math.ceil(max / step) * step
  const valueDomain = [0, top]
  const ticks = Array.from({ length: top / step + 1 }, (_, i) => i * step)
  // Horizontal charts grow with the number of bars so labels never overlap
  const height = horizontal ? Math.max(240, rows.length * 30 + 40) : 280

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={rows}
        layout={horizontal ? 'vertical' : 'horizontal'}
        margin={{ top: 20, right: horizontal ? 44 : 8, bottom: 0, left: 0 }}
        barCategoryGap="28%"
      >
        <CartesianGrid stroke={palette.grid} vertical={horizontal} horizontal={!horizontal} />
        {horizontal ? (
          <>
            <XAxis type="number" domain={valueDomain} ticks={ticks} tick={axisTick} axisLine={false} tickLine={false} allowDecimals={false} />
            <YAxis type="category" dataKey="label" tick={axisTick} axisLine={false} tickLine={false} width={124} />
          </>
        ) : (
          <>
            <XAxis dataKey="label" tick={axisTick} axisLine={{ stroke: palette.grid }} tickLine={false} interval={0} />
            <YAxis domain={valueDomain} ticks={ticks} tick={axisTick} axisLine={false} tickLine={false} allowDecimals={false} width={40} />
          </>
        )}
        <Tooltip content={<ChartTooltip total={total} />} cursor={{ fill: palette.grid, fillOpacity: 0.5 }} />
        <Bar
          dataKey="count"
          fill={palette.series[0]}
          radius={horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0]}
          isAnimationActive={false}
        >
          <LabelList dataKey="count" position={horizontal ? 'right' : 'top'} fill={palette.textMuted} fontSize={12} />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
