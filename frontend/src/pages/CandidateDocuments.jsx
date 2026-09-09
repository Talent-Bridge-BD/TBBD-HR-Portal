import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'

export default function CandidateDocuments() {
  return (
    <>
      <PageHeader
        title="Documents"
        subtitle="Manage documents related to your candidate profile and applications."
      />

      <DashboardCard title="My Documents">
        <div className="empty-state">
          <strong>No documents uploaded</strong>
          <span>
            Your recruitment documents will appear here once they are uploaded.
          </span>
        </div>
      </DashboardCard>

      <section className="dashboard-card">
        <div className="card-heading">
          <h2>Document Categories</h2>
        </div>

        <div className="overview-grid">
          <div className="overview-item">
            <span className="overview-icon">□</span>
            <div>
              <strong>Resume / CV</strong>
              <span>
                Keep your latest resume available for recruitment opportunities.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">□</span>
            <div>
              <strong>Certificates</strong>
              <span>
                Store relevant education and professional certificates.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">□</span>
            <div>
              <strong>Application Documents</strong>
              <span>
                Access documents associated with your job applications.
              </span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">✓</span>
            <div>
              <strong>Document Status</strong>
              <span>
                Track documents that are required, submitted, or verified.
              </span>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
