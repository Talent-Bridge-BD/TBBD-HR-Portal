
﻿import { useEffect, useState } from 'react'
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

import { useEffect, useRef, useState } from 'react'
import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'

const DOCUMENT_TYPES = [
  {
    type: 'profile_photo',
    title: 'Profile Photo',
    description: 'A recent passport-size professional photo.',
    accept: '.jpg,.jpeg,.png',
    help: 'JPG, JPEG or PNG · Maximum 5 MB',
    icon: '◉',
  },
  {
    type: 'resume',
    title: 'CV / Resume',
    description: 'Your current professional CV or resume.',
    accept: '.pdf,.doc,.docx',
    help: 'PDF, DOC or DOCX · Maximum 10 MB',
    icon: '▤',
  },
  {
    type: 'passport',
    title: 'Passport Copy',
    description: 'A clear copy of your current passport.',
    accept: '.pdf,.jpg,.jpeg,.png',
    help: 'PDF, JPG, JPEG or PNG · Maximum 10 MB',
    icon: '▣',
  },
]

function formatFileSize(size) {
  if (!size) return 'Size unavailable'
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`
  }
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

function formatUploadedAt(value) {
  if (!value) return 'Upload date unavailable'

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Upload date unavailable'

  return date.toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function DocumentCard({
  definition,
  document,
  uploading,
  onUpload,
  onDelete,
  onDownload,
}) {
  const inputRef = useRef(null)

  return (
    <div
      className={
        definition.type === 'profile_photo'
          ? 'profile-document-card profile-document-card-photo'
          : 'profile-document-card'
      }
    >
      <div className="profile-document-icon">{definition.icon}</div>

      <div className="profile-document-content">
        <div className="profile-document-heading">
          <div>
            <h3>{definition.title}</h3>
            <p>{definition.description}</p>
          </div>

          <span
            className={
              document
                ? 'profile-document-status profile-document-status-ready'
                : 'profile-document-status'
            }
          >
            {document ? 'Uploaded' : 'Required'}
          </span>
        </div>

        {document ? (
          <>
            <div className="profile-document-file">
              <strong>{document.file_name}</strong>
              <span>
                {formatFileSize(document.file_size)} ·{' '}
                {formatUploadedAt(document.uploaded_at)}
              </span>
              <span>
                Status:{' '}
                {document.status
                  ? document.status.charAt(0).toUpperCase() +
                    document.status.slice(1)
                  : 'Submitted'}
              </span>
            </div>

            <div className="profile-document-actions">
              <button
                type="button"
                className="profile-document-upload-button"
                onClick={() => inputRef.current?.click()}
                disabled={uploading}
              >
                {uploading ? 'Uploading...' : 'Replace'}
              </button>

              <button
                type="button"
                className="profile-document-upload-button"
                onClick={() => onDownload(document)}
                disabled={uploading}
              >
                View / Download
              </button>

              <button
                type="button"
                className="profile-document-remove-button"
                onClick={() => onDelete(document)}
                disabled={uploading}
              >
                Remove
              </button>
            </div>
          </>
        ) : (
          <div className="profile-document-empty">
            <span>No document uploaded yet.</span>

            <button
              type="button"
              className="profile-document-upload-button"
              onClick={() => inputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        )}

        <input
          ref={inputRef}
          type="file"
          accept={definition.accept}
          hidden
          onChange={(event) => onUpload(definition.type, event)}
        />

        <div className="profile-document-file">
          <span>{definition.help}</span>
        </div>
      </div>
    </div>
  )
}

export default function CandidateDocuments() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploadingType, setUploadingType] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function refreshDocuments() {
    const response = await fetch('/api/candidate/documents')

    if (!response.ok) {
      const body = await response.text()
      throw new Error(
        body || `Unable to load documents (${response.status})`,
      )
    }

    const data = await response.json()
    const nextDocuments = data.documents || []

    setDocuments(nextDocuments)
    return nextDocuments
  }

  useEffect(() => {
    let active = true

    async function loadDocuments() {
      try {
        setLoading(true)
        setError('')
        const response = await fetch('/api/candidate/documents')

        if (!response.ok) {
          const body = await response.text()
          throw new Error(
            body || `Unable to load documents (${response.status})`,
          )
        }

        const data = await response.json()

        if (active) {
          setDocuments(data.documents || [])
        }
      } catch (err) {
        if (active) {
          setError(err.message || 'Unable to load candidate documents.')
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

  async function handleDocumentUpload(documentType, event) {
    const file = event.target.files?.[0]
    event.target.value = ''

    if (!file) return

    try {
      setUploadingType(documentType)
      setError('')
      setMessage('')

      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(
        `/api/candidate/documents?document_type=${encodeURIComponent(
          documentType,
        )}`,
        {
          method: 'POST',
          body: formData,
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.message ||
            `Unable to upload ${documentType}.`,
        )
      }

      await refreshDocuments()

      const definition = DOCUMENT_TYPES.find(
        (item) => item.type === documentType,
      )

      setMessage(
        `${definition?.title || 'Document'} uploaded successfully.`,
      )
    } catch (err) {
      setError(err.message || `Unable to upload ${documentType}.`)
    } finally {
      setUploadingType('')
    }
  }

  async function handleDocumentDelete(document) {
    const definition = DOCUMENT_TYPES.find(
      (item) => item.type === document.document_type,
    )

    const label = definition?.title || 'document'

    if (!window.confirm(`Remove your ${label}?`)) {
      return
    }

    try {
      setError('')
      setMessage('')

      const response = await fetch(
        `/api/candidate/documents/${encodeURIComponent(document.id)}`,
        {
          method: 'DELETE',
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.message ||
            `Unable to remove ${label}.`,
        )
      }

      await refreshDocuments()

      setMessage(`${label} removed successfully.`)
    } catch (err) {
      setError(err.message || `Unable to remove ${label}.`)
    }
  }

  async function handleDocumentDownload(document) {
    try {
      setError('')
      setMessage('')

      const response = await fetch(
        `/api/candidate/documents/${encodeURIComponent(document.id)}`,
      )

      if (!response.ok) {
        const body = await response.text()
        throw new Error(
          body || `Unable to retrieve ${document.file_name}.`,
        )
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const link = window.document.createElement('a')

      link.href = url
      link.download = document.file_name
      document.body.appendChild(link)
      link.click()
      link.remove()

      URL.revokeObjectURL(url)

      setMessage(`${document.file_name} is ready.`)
    } catch (err) {
      setError(
        err.message || `Unable to retrieve ${document.file_name}.`,
      )
    }
  }

  return (
    <div className="candidate-portal-page">
      <PageHeader
        title="My Documents"
        subtitle="Manage documents related to your candidate profile and overseas recruitment."
      />

      {message && (
        <div className="success-message" role="status">
          {message}
        </div>
      )}

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      <DashboardCard title="Candidate Documents">
        {loading ? (
          <div className="empty-state">
            <strong>Loading documents...</strong>
            <span>
              Retrieving your candidate documents securely.
            </span>
          </div>
        ) : (
          <div className="profile-document-grid">
            {DOCUMENT_TYPES.map((definition) => (
              <DocumentCard
                key={definition.type}
                definition={definition}
                document={documents.find(
                  (item) =>
                    item.document_type === definition.type,
                )}
                uploading={uploadingType === definition.type}
                onUpload={handleDocumentUpload}
                onDelete={handleDocumentDelete}
                onDownload={handleDocumentDownload}
              />
b78f15b (Enhance screening workflow and interview dashboard)
            ))}
          </div>
        )}
      </DashboardCard>

      <section className="dashboard-card">
        <div className="card-heading">
          <div>
            <h2>Document Status</h2>
            <p>
              Keep your profile photo, CV, and passport copy current
              for recruitment opportunities.
            </p>
          </div>
        </div>

        <div className="overview-grid">
          {DOCUMENT_TYPES.map((definition) => {
            const document = documents.find(
              (item) => item.document_type === definition.type,
            )

            return (
              <div className="overview-item" key={definition.type}>
                <span className="overview-icon">
                  {document ? '✓' : '□'}
                </span>

                <div>
                  <strong>{definition.title}</strong>
                  <span>
                    {document
                      ? `${document.file_name} · ${formatFileSize(
                          document.file_size,
                        )}`
                      : 'No document uploaded yet.'}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </section>

      <section className="dashboard-card">
        <div className="card-heading">
          <div>
            <h2>Application Documents</h2>
            <p>
              Application-specific documents can be added as the
              recruitment workflow requires them.
            </p>
          </div>
        </div>

        <div className="empty-state">
          <strong>No application-specific documents</strong>
          <span>
            Documents linked directly to job applications will appear
            here when that workflow is enabled.
          </span>
        </div>
      </section>
    </div>
  )
}
