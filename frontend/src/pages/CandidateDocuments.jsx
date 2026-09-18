import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'

const API_BASE = '/api/candidate'

const DOCUMENT_LABELS = {
  profile_photo: 'Profile Photo',
  resume: 'CV / Resume',
  passport: 'Passport Copy',
  certificate: 'Certificate',
}

function formatFileSize(bytes) {
  if (!bytes) return 'Unknown size'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDocumentType(type) {
  return DOCUMENT_LABELS[type] || type
}

export default function CandidateDocuments() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function loadDocuments() {
      try {
        setLoading(true)
        setError('')

        const response = await fetch(`${API_BASE}/documents`, {
          credentials: 'include',
        })

        if (!response.ok) {
          throw new Error('Unable to load your documents.')
        }

        const data = await response.json()

        if (active) {
          setDocuments(Array.isArray(data.documents) ? data.documents : [])
        }
      } catch (err) {
        if (active) {
          setError(err.message || 'Unable to load your documents.')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    loadDocuments()

    return () => {
      active = false
    }
  }, [])

  const openDocument = (documentId) => {
    window.open(
      `${API_BASE}/documents/${documentId}`,
      '_blank',
      'noopener,noreferrer',
    )
  }

  return (
    <>
      <PageHeader
        title="Documents"
        subtitle="Manage documents related to your candidate profile and applications."
      />

      <DashboardCard title="My Documents">
        {loading ? (
          <div className="empty-state">
            <strong>Loading documents...</strong>
            <span>Checking your uploaded recruitment documents.</span>
          </div>
        ) : error ? (
          <div className="empty-state">
            <strong>Unable to load documents</strong>
            <span>{error}</span>
          </div>
        ) : documents.length === 0 ? (
          <div className="empty-state">
            <strong>No documents uploaded</strong>
            <span>
              Your recruitment documents will appear here once they are uploaded.
            </span>
          </div>
        ) : (
          <div className="overview-grid">
            {documents.map((document) => (
              <div className="overview-item" key={document.id}>
                <span className="overview-icon">▤</span>

                <div>
                  <strong>{document.file_name}</strong>

                  <span>
                    {formatDocumentType(document.document_type)}
                    {' · '}
                    {formatFileSize(document.file_size)}
                    {document.content_type
                      ? ` · ${document.content_type}`
                      : ''}
                  </span>

                  <span>
                    Status: {document.status || 'submitted'}
                  </span>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => openDocument(document.id)}
                  >
                    View / Download
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
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
