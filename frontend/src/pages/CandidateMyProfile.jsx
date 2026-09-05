import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'

export default function CandidateMyProfile() {
  return (
    <>
      <PageHeader
        title="My Profile"
        subtitle="Manage your candidate profile and recruitment information."
      />

      <section className="dashboard-card">
        <div className="card-heading">
          <h2>Candidate Information</h2>
        </div>

        <div className="overview-grid">
          <div className="overview-item">
            <span className="overview-icon">◉</span>
            <div>
              <strong>Personal Information</strong>
              <span>Your contact and personal details.</span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">▤</span>
            <div>
              <strong>Professional Profile</strong>
              <span>Your experience, skills, and qualifications.</span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">□</span>
            <div>
              <strong>Documents</strong>
              <span>Your recruitment and qualification documents.</span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">✓</span>
            <div>
              <strong>Profile Status</strong>
              <span>Your candidate profile is ready to be completed.</span>
            </div>
          </div>
        </div>
      </section>

      <DashboardCard title="Profile Information">
        <div className="empty-state">
          <strong>Candidate profile setup</strong>
          <span>
            Profile editing and candidate information management will be
            connected to the candidate data service in a later phase.
          </span>
        </div>
      </DashboardCard>
    </>
  )
}
