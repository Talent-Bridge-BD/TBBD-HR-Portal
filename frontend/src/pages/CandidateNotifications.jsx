import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'

export default function CandidateNotifications() {
  return (
    <>
      <PageHeader
        title="Notifications"
        subtitle="Stay informed about your applications, interviews, and recruitment updates."
      />

      <DashboardCard title="Recent Notifications">
        <div className="empty-state">
          <strong>No notifications</strong>
          <span>
            Recruitment updates and important candidate notifications will appear here.
          </span>
        </div>
      </DashboardCard>

      <section className="dashboard-card">
        <div className="card-heading">
          <h2>Notification Types</h2>
        </div>

        <div className="overview-grid">
          <div className="overview-item">
            <span className="overview-icon">▤</span>
            <div>
              <strong>Application Updates</strong>
              <span>
                Receive updates when the status of an application changes.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">◷</span>
            <div>
              <strong>Interview Notifications</strong>
              <span>
                Stay informed about interview schedules and changes.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">✓</span>
            <div>
              <strong>Recruitment Updates</strong>
              <span>
                Receive important messages related to your recruitment journey.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">🔔</span>
            <div>
              <strong>Important Alerts</strong>
              <span>
                Important actions and time-sensitive candidate information will be highlighted here.
              </span>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
