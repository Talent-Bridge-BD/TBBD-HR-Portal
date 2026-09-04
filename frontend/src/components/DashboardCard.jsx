export default function DashboardCard({ title, children }) {
  return (
    <section className="dashboard-card">
      <div className="card-heading">
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  )
}
