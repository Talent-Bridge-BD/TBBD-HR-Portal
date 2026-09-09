import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'

export default function CandidateInterviews() {
  return (
    <>
      <PageHeader
        title="Interviews"
        subtitle="View your scheduled interviews and recruitment appointments."
      />

      <DashboardCard title="Upcoming Interviews">
        <div className="empty-state">
          <strong>No interviews scheduled</strong>
          <span>
            Your upcoming interviews will appear here once they are scheduled.
          </span>
        </div>
      </DashboardCard>

      <section className="dashboard-card">
        <div className="card-heading">
          <h2>Interview Information</h2>
        </div>

        <div className="overview-grid">
          <div className="overview-item">
            <span className="overview-icon">◷</span>
            <div>
              <strong>Scheduled Interviews</strong>
              <span>
                View the date, time, and format of upcoming interviews.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">▤</span>
            <div>
              <strong>Interview Details</strong>
              <span>
                Review employer information and interview instructions.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">✓</span>
            <div>
              <strong>Interview Status</strong>
              <span>
                Track scheduled, completed, and cancelled interviews.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">□</span>
            <div>
              <strong>Preparation</strong>
              <span>
                Access relevant information and documents before your interview.
              </span>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
