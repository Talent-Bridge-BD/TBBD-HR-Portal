import { useEffect, useMemo, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { authenticatedFetch } from '../utils/auth'
import { useOrganization } from '../context/OrganizationContext'

const emptyForm = {
  title: '',
  description: '',
  employment_type: '',
  location: '',
  country: '',
  number_of_positions: 1,
  working_hours: '',
  benefits: '',
}

function formatDate(value) {
  if (!value) return '—'

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function statusClass(status) {
  return `employer-request-status employer-request-status-${String(
    status || 'pending',
  ).toLowerCase()}`
}

export default function EmployerJobRequests({ auth }) {
  const {
    selectedOrganization,
    availableOrganizations,
    organizationLoading,
  } = useOrganization()

  const [requests, setRequests] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [reviewRequest, setReviewRequest] = useState(null)
  const [editingRequest, setEditingRequest] = useState(null)

  const organizationId = selectedOrganization?.id || ''

  const canReviewRequests = useMemo(() => {
    const roles = auth?.roles || []

    return roles.some((role) =>
      ['Administrator', 'HR Manager'].includes(role),
    )
  }, [auth])

  const loadRequests = async () => {
    if (!organizationId) {
      setRequests([])
      setLoading(false)
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await authenticatedFetch(
        `/api/job-requests?organization_id=${encodeURIComponent(
          organizationId,
        )}`,
      )

      if (!response.ok) {
        throw new Error('Unable to load job requests.')
      }

      const data = await response.json()
      setRequests(data.requests || [])
    } catch (err) {
      setError(err.message || 'Unable to load job requests.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRequests()
  }, [organizationId])

  const totalRequests = requests.length

  const pendingRequests = requests.filter(
    (request) => request.status === 'pending',
  ).length

  const approvedRequests = requests.filter(
    (request) => request.status === 'approved',
  ).length

  const totalPositions = requests.reduce(
    (total, request) =>
      total + (Number(request.number_of_positions) || 0),
    0,
  )

  const handleChange = (event) => {
    const { name, value } = event.target

    setForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!organizationId) {
      setError('No active organization is available for this account.')
      return
    }

    if (!form.title.trim()) {
      setError('Job title is required.')
      return
    }

    setSaving(true)
    setError('')

    try {
      const isEditing = Boolean(editingRequest)

      const endpoint = isEditing
        ? `/api/job-requests/${encodeURIComponent(editingRequest.id)}`
        : '/api/job-requests'

      const response = await authenticatedFetch(endpoint, {
        method: isEditing ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          organization_id: organizationId,
          title: form.title.trim(),
          description: form.description.trim(),
          employment_type: form.employment_type,
          location: form.location.trim(),
          country: form.country.trim(),
          number_of_positions:
            Number(form.number_of_positions) || 1,
          working_hours: form.working_hours.trim(),
          benefits: form.benefits.trim(),
        }),
      })

      if (!response.ok) {
        let message = isEditing
          ? 'Unable to update job request.'
          : 'Unable to create job request.'

        try {
          const data = await response.json()
          message = data.detail || message
        } catch {
          // Keep the default message.
        }

        throw new Error(message)
      }

      setForm(emptyForm)
      setEditingRequest(null)
      setShowForm(false)

      await loadRequests()
    } catch (err) {
      setError(
        err.message ||
          (editingRequest
            ? 'Unable to update job request.'
            : 'Unable to create job request.'),
      )
    } finally {
      setSaving(false)
    }
  }

  const handleEditRequest = (request) => {
    setError('')

    setEditingRequest(request)

    setForm({
      title: request.title || '',
      description: request.description || '',
      employment_type: request.employment_type || '',
      location: request.location || '',
      country: request.country || '',
      number_of_positions: request.number_of_positions ?? 1,
      working_hours: request.working_hours || '',
      benefits: request.benefits || '',
    })

    setReviewRequest(null)
    setShowForm(true)
  }

  const handleApprove = async (requestId) => {
    if (!organizationId) return

    setError('')

    try {
      const response = await authenticatedFetch(
        `/api/job-requests/${encodeURIComponent(
          requestId,
        )}/approve?organization_id=${encodeURIComponent(organizationId)}`,
        {
          method: 'POST',
        },
      )

      if (!response.ok) {
        let message = 'Unable to approve this request.'

        try {
          const data = await response.json()
          message = data.detail || message
        } catch {
          // Keep the default message.
        }

        throw new Error(message)
      }

      setRequests((current) =>
        current.map((request) =>
          request.id === requestId
            ? { ...request, status: 'approved' }
            : request,
        ),
      )

      await loadRequests()
    } catch (err) {
      setError(err.message || 'Unable to approve this request.')
    }
  }

  if (organizationLoading) {
    return (
      <section className="employer-job-requests-page">
        <PageHeader
          title="Job Requests"
          subtitle="Plan workforce demand and submit new recruitment requirements."
        />
        <div className="employer-request-empty">
          Loading organization details...
        </div>
      </section>
    )
  }

  if (!selectedOrganization) {
    return (
      <section className="employer-job-requests-page">
        <PageHeader
          title="Job Requests"
          subtitle="Plan workforce demand and submit new recruitment requirements."
        />

        <div className="employer-request-empty">
          <div className="employer-request-empty-icon">＋</div>
          <h2>No organization selected</h2>
          <p>
            {availableOrganizations.length
              ? 'Select an organization above to manage job requests.'
              : 'Your account is not currently connected to an active organization.'}
          </p>
        </div>
      </section>
    )
  }

  return (
    <section className="employer-job-requests-page">
      <div className="employer-request-hero">
        <div>
          <span className="employer-request-eyebrow">
            WORKFORCE PLANNING
          </span>

          <h1>Job Requests</h1>

          <p>
            Submit recruitment requirements for {selectedOrganization.name}
            and track each request through review.
          </p>
        </div>

        <button
          type="button"
          className="employer-request-primary-button"
          onClick={() => {
            setError('')
            setShowForm((current) => !current)
          }}
        >
          {showForm ? 'Close Request Form' : '＋ New Job Request'}
        </button>
      </div>

      {error && (
        <div className="employer-request-alert" role="alert">
          <strong>Something needs attention</strong>
          <span>{error}</span>
        </div>
      )}

      <div className="employer-request-kpi-grid">
        <article className="employer-request-kpi-card">
          <span>Total Requests</span>
          <strong>{totalRequests}</strong>
          <small>Submitted workforce requests</small>
        </article>

        <article className="employer-request-kpi-card">
          <span>Pending Review</span>
          <strong>{pendingRequests}</strong>
          <small>Awaiting HR or administrator review</small>
        </article>

        <article className="employer-request-kpi-card">
          <span>Approved</span>
          <strong>{approvedRequests}</strong>
          <small>Requests approved for recruitment</small>
        </article>

        <article className="employer-request-kpi-card">
          <span>Positions</span>
          <strong>{totalPositions}</strong>
          <small>Total requested positions</small>
        </article>
      </div>

      {showForm && (
        <div className="employer-request-form-card">
          <div className="employer-request-section-heading">
            <div>
              <span className="employer-request-eyebrow">
                {editingRequest ? 'EDIT REQUIREMENT' : 'NEW REQUIREMENT'}
              </span>
              <h2>
                {editingRequest ? 'Edit Job Request' : 'Create Job Request'}
              </h2>
              <p>
                {editingRequest
                  ? 'Update the pending recruitment requirement before HR review.'
                  : 'Provide the core recruitment requirement for HR review.'}
              </p>
            </div>
          </div>

          <form
            className="employer-request-form"
            onSubmit={handleSubmit}
          >
            <div className="employer-request-form-section">
              <div className="employer-request-form-section-title">
                <span>01</span>
                <div>
                  <strong>Job Details</strong>
                  <small>Define the role being requested.</small>
                </div>
              </div>

              <div className="employer-request-form-grid">
                <label className="employer-request-field full-width">
                  <span>Job Title *</span>
                  <input
                    name="title"
                    value={form.title}
                    onChange={handleChange}
                    placeholder="e.g. Office Executive"
                    required
                  />
                </label>

                <label className="employer-request-field">
                  <span>Employment Type</span>
                  <select
                    name="employment_type"
                    value={form.employment_type}
                    onChange={handleChange}
                  >
                    <option value="">Select employment type</option>
                    <option value="Full-time">Full-time</option>
                    <option value="Part-time">Part-time</option>
                    <option value="Contract">Contract</option>
                    <option value="Temporary">Temporary</option>
                  </select>
                </label>

                <label className="employer-request-field">
                  <span>Country</span>
                  <input
                    name="country"
                    value={form.country}
                    onChange={handleChange}
                    placeholder="e.g. Saudi Arabia"
                  />
                </label>

                <label className="employer-request-field full-width">
                  <span>Location</span>
                  <input
                    name="location"
                    value={form.location}
                    onChange={handleChange}
                    placeholder="e.g. Riyadh"
                  />
                </label>

                <label className="employer-request-field full-width">
                  <span>Role Description</span>
                  <textarea
                    name="description"
                    value={form.description}
                    onChange={handleChange}
                    placeholder="Describe the role, responsibilities, and recruitment requirement."
                  />
                </label>
              </div>
            </div>

            <div className="employer-request-form-section">
              <div className="employer-request-form-section-title">
                <span>02</span>
                <div>
                  <strong>Workforce Requirement</strong>
                  <small>Specify the number of people required.</small>
                </div>
              </div>

              <div className="employer-request-form-grid">
                <label className="employer-request-field">
                  <span>Number of Positions *</span>
                  <input
                    name="number_of_positions"
                    type="number"
                    min="1"
                    value={form.number_of_positions}
                    onChange={handleChange}
                    required
                  />
                </label>
                <label className="employer-request-field">
                  <span>Working Hours</span>
                  <input
                    name="working_hours"
                    value={form.working_hours}
                    onChange={handleChange}
                    placeholder="e.g. 8 hours/day, 6 days/week"
                  />
                </label>
                <label className="employer-request-field full-width">
                  <span>Benefits</span>
                  <textarea
                    name="benefits"
                    value={form.benefits}
                    onChange={handleChange}
                    placeholder="e.g. Accommodation, transport, medical insurance, annual leave"
                  />
                </label>
              </div>
            </div>

            <div className="employer-request-form-note">
              <strong>What happens next?</strong>
              <span>
                After submission, the request can be reviewed by HR or an
                administrator before progressing into the recruitment
                pipeline.
              </span>
            </div>

            <div className="employer-request-form-actions">
              <button
                type="button"
                className="employer-request-secondary-button"
                onClick={() => {
                  setForm(emptyForm)
                  setEditingRequest(null)
                  setError('')
                  setShowForm(false)
                }}
                disabled={saving}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="employer-request-primary-button"
                disabled={saving}
              >
                {saving
                  ? editingRequest
                    ? 'Saving...'
                    : 'Submitting...'
                  : editingRequest
                    ? 'Save Changes'
                    : 'Submit Job Request'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="employer-request-content-card">
        <div className="employer-request-section-heading">
          <div>
            <span className="employer-request-eyebrow">
              REQUEST PIPELINE
            </span>
            <h2>Recent Job Requests</h2>
            <p>
              Review workforce requests submitted by your organization.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="employer-request-empty compact">
            Loading job requests...
          </div>
        ) : requests.length === 0 ? (
          <div className="employer-request-empty compact">
            <div className="employer-request-empty-icon">＋</div>
            <h3>No job requests yet</h3>
            <p>
              Create your first workforce request to begin the recruitment
              process.
            </p>
            <button
              type="button"
              className="employer-request-secondary-button"
              onClick={() => setShowForm(true)}
            >
              Create First Request
            </button>
          </div>
        ) : (
          <div className="employer-request-list">
            {requests.map((request) => (
              <article
                className="employer-request-item"
                key={request.id}
              >
                <div className="employer-request-item-main">
                  <div className="employer-request-title-row">
                    <div>
                      <h3>{request.title}</h3>
                      <p>
                        Requested {formatDate(request.requested_at)}
                      </p>
                    </div>

                    <span className={statusClass(request.status)}>
                      {request.status || 'pending'}
                    </span>
                  </div>

                  <div className="employer-request-meta">
                    <span>
                      <strong>Positions</strong>{' '}
                      {request.number_of_positions || 0}
                    </span>

                    {request.employment_type && (
                      <span>
                        <strong>Type</strong>{' '}
                        {request.employment_type}
                      </span>
                    )}

                    {request.location && (
                      <span>
                        <strong>Location</strong>{' '}
                        {request.location}
                      </span>
                    )}

                    {request.country && (
                      <span>
                        <strong>Country</strong>{' '}
                        {request.country}
                      </span>
                    )}
                  </div>

                  {request.description && (
                    <p className="employer-request-description">
                      {request.description}
                    </p>
                  )}
                </div>

                {request.status === 'pending' && (
                  <div
                    className="employer-request-item-action"
                    style={{
                      display: 'flex',
                      gap: '10px',
                      flexWrap: 'wrap',
                    }}
                  >
                    <button
                      type="button"
                      className="employer-request-secondary-button"
                      onClick={() => handleEditRequest(request)}
                    >
                      Edit Request
                    </button>

                    {canReviewRequests && (
                      <>
                        <button
                          type="button"
                          className="employer-request-secondary-button"
                          onClick={() => setReviewRequest(request)}
                        >
                          Review Request
                        </button>

                        <button
                          type="button"
                          className="employer-request-primary-button"
                          onClick={() => handleApprove(request.id)}
                        >
                          Approve Request
                        </button>
                      </>
                    )}
                  </div>
                )}
              </article>
            ))}
          </div>
        )}
      </div>

      {reviewRequest && (
        <div
          role="presentation"
          onClick={() => setReviewRequest(null)}
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px',
            background: 'rgba(15, 23, 42, 0.45)',
          }}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="job-request-review-title"
            onClick={(event) => event.stopPropagation()}
            style={{
              width: 'min(760px, 100%)',
              maxHeight: 'calc(100vh - 48px)',
              overflowY: 'auto',
              borderRadius: '12px',
              background: '#fff',
              padding: '24px',
              boxShadow: '0 20px 50px rgba(15, 23, 42, 0.20)',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
                gap: '16px',
                marginBottom: '20px',
              }}
            >
              <div>
                <h2
                  id="job-request-review-title"
                  style={{
                    margin: 0,
                    color: '#0F172A',
                    fontSize: '20px',
                    fontWeight: 700,
                  }}
                >
                  Review Job Request
                </h2>
                <p
                  style={{
                    margin: '6px 0 0',
                    color: '#64748B',
                    fontSize: '13px',
                  }}
                >
                  Review the employer-submitted requirements before approval.
                </p>
              </div>

              <button
                type="button"
                onClick={() => setReviewRequest(null)}
                aria-label="Close review"
                style={{
                  border: '1px solid #E2E8F0',
                  background: '#fff',
                  color: '#475569',
                  borderRadius: '8px',
                  padding: '6px 10px',
                  cursor: 'pointer',
                  fontSize: '18px',
                  lineHeight: 1,
                }}
              >
                ×
              </button>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
                gap: '14px',
              }}
            >
              {[
                ['Job Title', reviewRequest.title],
                ['Employment Type', reviewRequest.employment_type],
                ['Location', reviewRequest.location],
                ['Country', reviewRequest.country],
                ['Number of Positions', reviewRequest.number_of_positions],
                ['Working Hours', reviewRequest.working_hours],
                ['Status', reviewRequest.status],
                ['Requested', formatDate(reviewRequest.requested_at)],
              ].map(([label, value]) => (
                <div
                  key={label}
                  style={{
                    padding: '12px 14px',
                    border: '1px solid #E2E8F0',
                    borderRadius: '8px',
                    background: '#F8FAFC',
                  }}
                >
                  <div
                    style={{
                      marginBottom: '4px',
                      color: '#64748B',
                      fontSize: '12px',
                      fontWeight: 600,
                    }}
                  >
                    {label}
                  </div>
                  <div
                    style={{
                      color: '#0F172A',
                      fontSize: '14px',
                      fontWeight: 500,
                      whiteSpace: 'pre-wrap',
                    }}
                  >
                    {value || '—'}
                  </div>
                </div>
              ))}

              <div
                style={{
                  gridColumn: '1 / -1',
                  padding: '14px',
                  border: '1px solid #E2E8F0',
                  borderRadius: '8px',
                }}
              >
                <div
                  style={{
                    marginBottom: '6px',
                    color: '#64748B',
                    fontSize: '12px',
                    fontWeight: 600,
                  }}
                >
                  Description
                </div>
                <div
                  style={{
                    color: '#475569',
                    fontSize: '14px',
                    lineHeight: 1.6,
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {reviewRequest.description || '—'}
                </div>
              </div>

              <div
                style={{
                  gridColumn: '1 / -1',
                  padding: '14px',
                  border: '1px solid #E2E8F0',
                  borderRadius: '8px',
                }}
              >
                <div
                  style={{
                    marginBottom: '6px',
                    color: '#64748B',
                    fontSize: '12px',
                    fontWeight: 600,
                  }}
                >
                  Benefits
                </div>
                <div
                  style={{
                    color: '#475569',
                    fontSize: '14px',
                    lineHeight: 1.6,
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {reviewRequest.benefits || '—'}
                </div>
              </div>
            </div>

            <div
              style={{
                display: 'flex',
                justifyContent: 'flex-end',
                gap: '10px',
                marginTop: '20px',
                paddingTop: '16px',
                borderTop: '1px solid #E2E8F0',
              }}
            >
              <button
                type="button"
                className="employer-request-secondary-button"
                onClick={() => setReviewRequest(null)}
              >
                Close Review
              </button>

              <button
                type="button"
                className="employer-request-primary-button"
                onClick={() => {
                  setReviewRequest(null)
                  handleApprove(reviewRequest.id)
                }}
              >
                Approve Request
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
