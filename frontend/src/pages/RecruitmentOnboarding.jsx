import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'

const ONBOARDING_STATUSES = [
  'pending',
  'in_progress',
  'completed',
  'cancelled',
]

const EMPLOYMENT_TYPES = [
  'Full-time',
  'Part-time',
  'Contract',
  'Temporary',
  'Internship',
]

export default function RecruitmentOnboarding({ auth }) {
  const organizationId = auth?.organization_ids?.[0] || ''

  const [onboarding, setOnboarding] = useState([])
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [saving, setSaving] = useState(false)

  const [form, setForm] = useState({
    application_id: '',
    planned_start_date: '',
    employment_type: '',
    notes: '',
  })

  const loadOnboarding = async () => {
    if (!organizationId) {
      setLoading(false)
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await fetch(
        `/api/recruitment/onboarding?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        {
          credentials: 'include',
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to load onboarding records.'
        )
      }

      setOnboarding(
        Array.isArray(data)
          ? data
          : data.onboarding || []
      )
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadApplications = async () => {
    if (!organizationId) {
      return
    }

    try {
      const response = await fetch(
        `/api/applications?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        {
          credentials: 'include',
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to load applications.'
        )
      }

      setApplications(
        Array.isArray(data)
          ? data
          : data.applications || []
      )
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    loadOnboarding()
    loadApplications()
  }, [organizationId])

  const resetForm = () => {
    setForm({
      application_id: '',
      planned_start_date: '',
      employment_type: '',
      notes: '',
    })
  }

  const openForm = () => {
    resetForm()
    setError('')
    setShowForm(true)
  }

  const closeForm = () => {
    if (!saving) {
      setShowForm(false)
      resetForm()
    }
  }

  const handleChange = (event) => {
    const { name, value } = event.target

    setForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!form.application_id) {
      setError('Please select an application.')
      return
    }

    setSaving(true)
    setError('')

    try {
      const response = await fetch(
        `/api/recruitment/onboarding?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            application_id: form.application_id,
            status: 'pending',
            planned_start_date:
              form.planned_start_date || null,
            employment_type:
              form.employment_type || null,
            notes: form.notes || null,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to create onboarding record.'
        )
      }

      setShowForm(false)
      resetForm()
      await loadOnboarding()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const updateStatus = async (record, status) => {
    try {
      setError('')

      const response = await fetch(
        `/api/recruitment/onboarding/${encodeURIComponent(
          record.id
        )}?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        {
          method: 'PUT',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            status,
            planned_start_date:
              record.planned_start_date || null,
            employment_type:
              record.employment_type || null,
            notes: record.notes || null,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to update onboarding status.'
        )
      }

      const updatedRecord =
        data.onboarding || data

      setOnboarding((current) =>
        current.map((item) =>
          item.id === record.id
            ? updatedRecord
            : item
        )
      )
    } catch (err) {
      setError(err.message)
    }
  }

  const deleteRecord = async (record) => {
    if (
      !window.confirm(
        'Delete this onboarding record?'
      )
    ) {
      return
    }

    try {
      setError('')

      const response = await fetch(
        `/api/recruitment/onboarding/${encodeURIComponent(
          record.id
        )}?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        {
          method: 'DELETE',
          credentials: 'include',
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to delete onboarding record.'
        )
      }

      setOnboarding((current) =>
        current.filter(
          (item) => item.id !== record.id
        )
      )
    } catch (err) {
      setError(err.message)
    }
  }

  const formatDate = (value) => {
    if (!value) {
      return '—'
    }

    return new Date(value).toLocaleDateString()
  }

  const statusLabel = (status) =>
    status
      .replaceAll('_', ' ')
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      )

  if (!organizationId) {
    return (
      <>
        <PageHeader
          title="Onboarding"
          subtitle="Prepare successful candidates for onboarding."
        />

        <section className="placeholder-card">
          <h2>Organization access required</h2>
          <p>
            An authorized organization membership is required
            to manage recruitment onboarding.
          </p>
        </section>
      </>
    )
  }

  return (
    <>
      <PageHeader
        title="Onboarding"
        subtitle="Prepare successful candidates for onboarding."
      />

      {error && (
        <section className="placeholder-card">
          <p>{error}</p>
        </section>
      )}

      <section className="placeholder-card">
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '1rem',
            marginBottom: '1rem',
          }}
        >
          <div>
            <h2>Onboarding Management</h2>
            <p>
              Track onboarding preparation for candidate applications.
            </p>
          </div>

          <button
            type="button"
            onClick={openForm}
            disabled={saving}
          >
            Start Onboarding
          </button>
        </div>

        {showForm && (
          <form
            onSubmit={handleSubmit}
            style={{
              display: 'grid',
              gap: '1rem',
              marginBottom: '2rem',
            }}
          >
            <h3>Start Onboarding</h3>

            <label>
              Application
              <select
                name="application_id"
                value={form.application_id}
                onChange={handleChange}
                required
              >
                <option value="">
                  Select application
                </option>

                {applications.map((application) => {
                  const candidateName =
                    `${application.candidate_first_name || ''} ${
                      application.candidate_last_name || ''
                    }`.trim()

                  return (
                    <option
                      key={application.id}
                      value={application.id}
                    >
                      {candidateName || 'Candidate'}
                      {' — '}
                      {application.job_title || 'Job'}
                      {' — '}
                      {statusLabel(
                        application.status || 'submitted'
                      )}
                    </option>
                  )
                })}
              </select>
            </label>

            <label>
              Planned Start Date
              <input
                type="date"
                name="planned_start_date"
                value={form.planned_start_date}
                onChange={handleChange}
              />
            </label>

            <label>
              Employment Type
              <select
                name="employment_type"
                value={form.employment_type}
                onChange={handleChange}
              >
                <option value="">
                  Select employment type
                </option>

                {EMPLOYMENT_TYPES.map((type) => (
                  <option
                    key={type}
                    value={type}
                  >
                    {type}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Notes
              <textarea
                name="notes"
                value={form.notes}
                onChange={handleChange}
                rows="4"
                placeholder="Onboarding notes"
              />
            </label>

            <div
              style={{
                display: 'flex',
                gap: '0.75rem',
              }}
            >
              <button
                type="submit"
                disabled={saving}
              >
                {saving
                  ? 'Creating…'
                  : 'Start Onboarding'}
              </button>

              <button
                type="button"
                onClick={closeForm}
                disabled={saving}
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        {loading ? (
          <p>Loading onboarding records…</p>
        ) : onboarding.length === 0 ? (
          <div>
            <h3>No onboarding records</h3>
            <p>
              Onboarding records will appear here when
              successful candidate applications are prepared
              for onboarding.
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Job</th>
                  <th>Status</th>
                  <th>Planned Start</th>
                  <th>Employment Type</th>
                  <th>Notes</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {onboarding.map((record) => (
                  <tr key={record.id}>
                    <td>
                      <strong>
                        {`${record.candidate_first_name || ''} ${
                          record.candidate_last_name || ''
                        }`.trim() || 'Candidate'}
                      </strong>

                      <br />

                      <small>
                        {record.candidate_email || '—'}
                      </small>
                    </td>

                    <td>
                      {record.job_title || '—'}
                    </td>

                    <td>
                      {statusLabel(
                        record.status || 'pending'
                      )}
                    </td>

                    <td>
                      {formatDate(
                        record.planned_start_date
                      )}
                    </td>

                    <td>
                      {record.employment_type || '—'}
                    </td>

                    <td>
                      {record.notes || '—'}
                    </td>

                    <td>
                      <div
                        style={{
                          display: 'flex',
                          flexWrap: 'wrap',
                          gap: '0.5rem',
                        }}
                      >
                        {record.status === 'pending' && (
                          <button
                            type="button"
                            onClick={() =>
                              updateStatus(
                                record,
                                'in_progress'
                              )
                            }
                          >
                            Start
                          </button>
                        )}

                        {record.status === 'in_progress' && (
                          <button
                            type="button"
                            onClick={() =>
                              updateStatus(
                                record,
                                'completed'
                              )
                            }
                          >
                            Complete
                          </button>
                        )}

                        {(record.status === 'pending' ||
                          record.status === 'in_progress') && (
                          <button
                            type="button"
                            onClick={() =>
                              updateStatus(
                                record,
                                'cancelled'
                              )
                            }
                          >
                            Cancel
                          </button>
                        )}

                        <button
                          type="button"
                          onClick={() =>
                            deleteRecord(record)
                          }
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  )
}
