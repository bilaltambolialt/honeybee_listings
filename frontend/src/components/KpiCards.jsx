// Headline numbers from /api/dashboard/summary
export function KpiCards({ summary }) {
  const phoneShare = summary.total_listings ? (summary.with_phone / summary.total_listings) * 100 : 0
  const cards = [
    { label: 'Total listings', value: summary.total_listings.toLocaleString() },
    { label: 'Cities', value: summary.cities },
    { label: 'Categories', value: summary.categories },
    { label: 'Data sources', value: summary.sources },
    { label: 'With phone number', value: `${phoneShare.toFixed(0)}%`, note: `${summary.with_phone.toLocaleString()} listings` },
  ]

  return (
    <section className="kpis" aria-label="Summary">
      {cards.map((card) => (
        <div className="card kpi" key={card.label}>
          <div className="kpi-label">{card.label}</div>
          <div className="kpi-value">{card.value}</div>
          {card.note && <div className="kpi-note">{card.note}</div>}
        </div>
      ))}
    </section>
  )
}
