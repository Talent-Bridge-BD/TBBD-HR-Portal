import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'

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
      const response = await fetch(
        `/api/job-requests?organization_id=${encodeURIComponent(organizationId)}`,
        { credentials: 'include' },
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
      const response = await fetch('/api/job-requests', {
        method: 'POST',
        credentials: 'include',
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
    <>
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
          <form onSubmit={createRequest} className="dashboard-form">
            <label>
              Job Title
              <input
                name="title"
                value={form.title}
                onChange={updateField}
                required
              />
            </label>

            <label>
              Employment Type
              <input
                name="employment_type"
                value={form.employment_type}
                onChange={updateField}
                placeholder="Full-time, Part-time, Contract"
              />
            </label>

            <label>
              Location
              <input
                name="location"
                value={form.location}
                onChange={updateField}
              />
            </label>

            <label>
              Country
              <input
                name="country"
                value={form.country}
                onChange={updateField}
              />
            </label>

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

            <label>
              Description
              <textarea
                name="description"
                value={form.description}
                onChange={updateField}
                rows="6"
              />
            </label>

            <div className="quick-actions">
              <button
                className="quick-action-button"
                type="submit"
                disabled={saving}
              >
                {saving ? 'Submitting...' : 'Submit Job Request'}
              </button>

              <button
                className="quick-action-button"
                type="button"
                onClick={() => setShowForm(false)}
                disabled={saving}
              >
                Cancel
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
          <div className="notification-list">
            {requests.map((request) => (
              <div className="notification-item" key={request.id}>
                <span className="notification-dot" />
                <span className="notification-content">
                  <strong>{request.title}</strong>
                  <small>
                    {request.status}
                    {request.number_of_positions
                      ? ` · ${request.number_of_positions} position(s)`
                      : ''}
                  </small>
                </span>
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  )
}
