import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'

export default function CandidateMyApplications() {
  return (
    <>
      <PageHeader
        title="My Applications"
        subtitle="Track your job applications and recruitment progress."
      />

      <DashboardCard title="Application Activity">
        <div className="empty-state">
          <strong>No applications yet</strong>
          <span>
            Your submitted job applications and recruitment status will appear
            here.
          </span>
        </div>
      </DashboardCard>

      <section className="dashboard-card">
        <div className="card-heading">
          <h2>Application Status</h2>
        </div>

        <div className="overview-grid">
          <div className="overview-item">
            <span className="overview-icon">▤</span>
            <div>
              <strong>Submitted</strong>
              <span>Applications you have submitted.</span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">◌</span>
            <div>
              <strong>Under Review</strong>
              <span>Applications currently being reviewed.</span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">◷</span>
            <div>
              <strong>Interview</strong>
              <span>Applications that have reached the interview stage.</span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">✓</span>
            <div>
              <strong>Shortlisted</strong>
              <span>Applications where you have been shortlisted.</span>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
