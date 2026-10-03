export default function StatCard({ icon, label, value, detail, onClick }) {
  return (
    <article
      className={`stat-card ${onClick ? 'stat-card-clickable' : ''}`}
      onClick={onClick}
      onKeyDown={(event) => {
        if (!onClick) return

        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault()
          onClick()
        }
      }}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="stat-icon">{icon}</div>
      <div>
        <span className="stat-label">{label}</span>
        <strong className="stat-value">{value}</strong>
        {detail && <span className="stat-detail">{detail}</span>}
      </div>
    </article>
  )
}
