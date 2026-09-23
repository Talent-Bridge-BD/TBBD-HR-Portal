import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { authenticatedFetch } from '../utils/auth'

const emptyForm = {
  title: '',
  description: '',
  employment_type: '',
  location: '',
  country: '',
  number_of_positions: '',
}

export default function EmployerJobRequests({ auth }) {
  const [requests, setRequests] = useState([])
  const [organizationId, setOrganizationId] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [approvingId, setApprovingId] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')

  useEffect(() => {
    const id = auth?.organization_ids?.[0] || ''
    setOrganizationId(id)
  }, [auth])

  async function loadRequests() {
    if (!organizationId) {
      setRequests([])
      setLoading(false)
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await authenticatedFetch(
        `/api/job-requests?organization_id=${encodeURIComponent(organizationId)}`,
      )

      if (!response.ok) {
        throw new Error(`Failed to load job requests: ${response.status}`)
      }

      const data = await response.json()
      setRequests(data.requests || [])
    } catch (err) {
      console.error(err)
      setError('Unable to load job requests.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRequests()
  }, [organizationId])

  async function approveRequest(request) {
    if (!organizationId || !request?.id) return

    setApprovingId(request.id)
    setError('')

    try {
      const response = await authenticatedFetch(
        `/api/job-requests/${request.id}/approve?organization_id=${encodeURIComponent(organizationId)}`,
        {
          method: 'POST',
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to approve job request.')
      }

      await loadRequests()
    } catch (err) {
      console.error(err)
      setError(err.message || 'Unable to approve job request.')
    } finally {
      setApprovingId('')
    }
  }

  function updateField(event) {
    const { name, value } = event.target
    setForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  async function createRequest(event) {
    event.preventDefault()

    if (!organizationId) {
      setError('Organization access is required.')
      return
    }

    setSaving(true)
    setError('')

    try {
      const response = await authenticatedFetch('/api/job-requests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          organization_id: organizationId,
          title: form.title,
          description: form.description,
          employment_type: form.employment_type,
          location: form.location,
          country: form.country,
          number_of_positions: form.number_of_positions
            ? Number(form.number_of_positions)
            : null,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to create job request.')
      }

      setForm(emptyForm)
      setShowForm(false)
      await loadRequests()
    } catch (err) {
      console.error(err)
      setError(err.message || 'Unable to create job request.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="employer-job-requests-page">
      <PageHeader
        title="Job Requests"
        subtitle="Create and manage employer workforce and recruitment requests."
      />

      <section className="dashboard-card">
        <div className="card-heading">
          <div>
            <h2>Employer Job Requests</h2>
            <p>
              Submit workforce requirements for review and conversion into job
              openings.
            </p>
          </div>

          <button
            className="quick-action-button"
            type="button"
            onClick={() => setShowForm((current) => !current)}
            disabled={!organizationId}
          >
            ＋ New Job Request
          </button>
        </div>

        {error && (
          <div className="empty-state">
            <strong>{error}</strong>
          </div>
        )}

        {!organizationId && !loading ? (
          <div className="empty-state">
            <strong>Organization access required</strong>
            <span>
              Your account must be connected to an employer organization.
            </span>
          </div>
        ) : showForm ? (
          <form onSubmit={createRequest} className="job-request-form">
            <div className="job-request-form-grid">
              <div className="job-request-field">
                <label>
                  Job Title
                  <input
                    name="title"
                    value={form.title}
                    onChange={updateField}
                    required
                  />
                </label>
              </div>

              <div className="job-request-field">
                <label>
                  Employment Type
                  <input
                    name="employment_type"
                    value={form.employment_type}
                    onChange={updateField}
                    placeholder="Full-time, Part-time, Contract"
                  />
                </label>
              </div>

              <div className="job-request-field">
                <label>
                  Location
                  <input
                    name="location"
                    value={form.location}
                    onChange={updateField}
                  />
                </label>
              </div>

              <div className="job-request-field">
                <label>
                  Country
                  <input
                    name="country"
                    value={form.country}
                    onChange={updateField}
                  />
                </label>
              </div>

              <div className="job-request-field">
                <label>
                  Number of Positions
                  <input
                    name="number_of_positions"
                    type="number"
                    min="1"
                    value={form.number_of_positions}
                    onChange={updateField}
                  />
                </label>
              </div>

              <div className="job-request-field full-width">
                <label>
                  Description
                  <textarea
                    name="description"
                    value={form.description}
                    onChange={updateField}
                    rows="6"
                  />
                </label>
              </div>
            </div>

            <div className="job-request-actions">
              <button
                className="secondary-action"
                type="button"
                onClick={() => setShowForm(false)}
                disabled={saving}
              >
                Cancel
              </button>

              <button
                className="primary-action"
                type="submit"
                disabled={saving}
              >
                {saving ? 'Submitting...' : 'Submit Job Request'}
              </button>
            </div>
          </form>
        ) : loading ? (
          <div className="empty-state">
            <strong>Loading job requests...</strong>
          </div>
        ) : requests.length === 0 ? (
          <div className="empty-state">
            <strong>No job requests yet</strong>
            <span>Create your first employer workforce request.</span>
          </div>
        ) : (
          <div className="job-request-list">
            {requests.map((request) => (
              <div className="job-request-card" key={request.id}>
                <div className="job-request-main">
                  <div className="job-request-title-row">
                    <strong>{request.title}</strong>
                    <span className="job-request-status">
                      {request.status || 'Pending'}
                    </span>
                  </div>

                  <div className="job-request-meta">
                    {request.employment_type && (
                      <span>{request.employment_type}</span>
                    )}

                    {request.location && (
                      <span>{request.location}</span>
                    )}

                    {request.country && (
                      <span>{request.country}</span>
                    )}

                    {request.number_of_positions && (
                      <span>
                        {request.number_of_positions}{' '}
                        {request.number_of_positions === 1
                          ? 'position'
                          : 'positions'}
                      </span>
                    )}
                  </div>

                  {request.description && (
                    <p className="job-request-description">
                      {request.description}
                    </p>
                  )}

                  {auth?.roles?.some((role) =>
                    ['Administrator', 'HR Manager'].includes(role)
                  ) && request.status === 'pending' && (
                    <div className="job-request-actions">
                      <button
                        className="primary-action"
                        type="button"
                        onClick={() => approveRequest(request)}
                        disabled={approvingId === request.id}
                      >
                        {approvingId === request.id
                          ? 'Approving...'
                          : 'Approve & Create Job'}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
