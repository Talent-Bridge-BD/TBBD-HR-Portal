import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'

export default function CandidateAvailableJobs() {
  return (
    <>
      <PageHeader
        title="Available Jobs"
        subtitle="Explore recruitment opportunities that may match your profile."
      />

      <DashboardCard title="Job Opportunities">
        <div className="empty-state">
          <strong>No jobs available yet</strong>
          <span>
            New recruitment opportunities will appear here when they become
            available.
          </span>
        </div>
      </DashboardCard>

      <section className="dashboard-card">
        <div className="card-heading">
          <h2>How Job Matching Works</h2>
        </div>

        <div className="overview-grid">
          <div className="overview-item">
            <span className="overview-icon">◉</span>
            <div>
              <strong>Complete Your Profile</strong>
              <span>
                Keep your professional information, skills, and experience
                up to date.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">▤</span>
            <div>
              <strong>Explore Jobs</strong>
              <span>
                Review available opportunities and recruitment requirements.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">✓</span>
            <div>
              <strong>Apply</strong>
              <span>
                Submit your application for suitable opportunities.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">◷</span>
            <div>
              <strong>Track Progress</strong>
              <span>
                Follow your application, interview, and hiring progress.
              </span>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
