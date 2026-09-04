export default function StatCard({ icon, label, value, detail }) {
  return (
    <article className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div>
        <span className="stat-label">{label}</span>
        <strong className="stat-value">{value}</strong>
        {detail && <span className="stat-detail">{detail}</span>}
      </div>
    </article>
  )
}
