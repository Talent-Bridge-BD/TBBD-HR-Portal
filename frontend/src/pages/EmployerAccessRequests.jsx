import { useCallback, useEffect, useState } from 'react'
import { authenticatedFetch } from '../utils/auth'
import './EmployerAccessRequests.css'

const API = '/api/employer-access-requests'

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

export default function EmployerAccessRequests() {
  const [requests, setRequests] = useState([])
  const [status, setStatus] = useState('Pending')
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [notes, setNotes] = useState({})
  const [organizations, setOrganizations] = useState([])
  const [organizationsLoading, setOrganizationsLoading] = useState(false)
  const [organizationsError, setOrganizationsError] = useState('')
  const [activationForms, setActivationForms] = useState({})
  const [activatedIds, setActivatedIds] = useState([])

  const loadRequests = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const response = await authenticatedFetch(
        `${API}?status=${encodeURIComponent(status)}&limit=100`
      )
      if (!response.ok) {
        throw new Error(`Could not load requests (${response.status}).`)
      }
      const data = await response.json()
      setRequests(Array.isArray(data) ? data : data.requests || data.items || [])
    } catch (err) {
      setError(err.message || 'Could not load employer access requests.')
    } finally {
      setLoading(false)
    }
  }, [status])

  const loadOrganizations = useCallback(async () => {
    setOrganizationsLoading(true)
    setOrganizationsError('')
    try {
      const response = await authenticatedFetch('/api/organizations')
      const data = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(
          data.detail || `Could not load active organizations (${response.status}).`
        )
      }
      setOrganizations(
        Array.isArray(data.organizations) ? data.organizations : []
      )
    } catch (err) {
      setOrganizationsError(
        err.message || 'Could not load active organizations.'
      )
    } finally {
      setOrganizationsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadRequests()
  }, [loadRequests])

  useEffect(() => {
    if (status === 'Approved') {
      loadOrganizations()
    }
  }, [status, loadOrganizations])

  async function reviewRequest(requestId, decision) {
    const promptText = decision === 'Approved'
      ? 'Approve this request for review completion? This will not grant login access or organization membership.'
      : 'Reject this employer access request?'

    if (!window.confirm(promptText)) return

    setBusyId(requestId)
    setError('')
    setMessage('')

    try {
      const response = await authenticatedFetch(
        `${API}/${encodeURIComponent(requestId)}/review`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            status: decision,
            review_notes: notes[requestId] || null,
          }),
        }
      )

      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        throw new Error(body.detail || `Review failed (${response.status}).`)
      }

      setMessage(`Request ${decision.toLowerCase()} successfully.`)
      await loadRequests()
    } catch (err) {
      setError(err.message || 'Could not review this request.')
    } finally {
      setBusyId('')
    }
  }

  function updateActivationForm(requestId, field, value) {
    setActivationForms((current) => ({
      ...current,
      [requestId]: {
        ...(current[requestId] || {}),
        [field]: value,
      },
    }))
  }

  async function activateRequest(requestId) {
    const form = activationForms[requestId] || {}
    const organizationId = String(form.organization_id || '').trim()
    const entraObjectId = String(form.entra_object_id || '').trim()
    const applicationUserId = String(form.application_user_id || '').trim()

    if (!organizationId || !entraObjectId) {
      setError('Select an organization and enter the verified Entra Object ID.')
      return
    }

    if (form.identity_verified !== true) {
      setError('Confirm that the Entra identity was independently verified.')
      return
    }

    const confirmation = applicationUserId
      ? 'Link this verified Entra identity to the existing application account and selected organization?'
      : 'Activate this verified Entra identity and create its Employer Manager membership in the selected organization?'

    if (!window.confirm(
      `${confirmation} Check the organization and identity details before continuing.`
    )) {
      return
    }

    setBusyId(requestId)
    setError('')
    setMessage('')

    try {
      const payload = {
        organization_id: organizationId,
        entra_object_id: entraObjectId,
        identity_verified: true,
      }

      if (applicationUserId) {
        payload.application_user_id = applicationUserId
      }

      const response = await authenticatedFetch(
        `${API}/${encodeURIComponent(requestId)}/activate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        }
      )

      const body = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(
          body.detail || `Activation failed (${response.status}).`
        )
      }

      setActivatedIds((current) =>
        current.includes(requestId) ? current : [...current, requestId]
      )

      const resultMessages = [
        body.message,
        body.audit_warning,
        body.delivery_log_warning,
      ].filter(Boolean)

      setMessage(
        resultMessages.join(' ') || 'Employer activation completed.'
      )
      await loadRequests()
    } catch (err) {
      setError(err.message || 'Could not activate this employer request.')
    } finally {
      setBusyId('')
    }
  }

  return (
    <main className="employer-access-admin">
      <header className="employer-access-admin__header">
        <div>
          <h1>Employer Access Requests</h1>
          <p>Review employer enquiries before any account or organization access is granted.</p>
        </div>
        <button type="button" onClick={loadRequests} disabled={loading}>
          Refresh
        </button>
      </header>

      <div className="employer-access-admin__filters">
        <label htmlFor="employer-request-status">Request status</label>
        <select
          id="employer-request-status"
          value={status}
          onChange={(event) => setStatus(event.target.value)}
        >
          <option value="Pending">Pending</option>
          <option value="Approved">Approved</option>
          <option value="Rejected">Rejected</option>
        </select>
        <span>{requests.length} request{requests.length === 1 ? '' : 's'}</span>
      </div>

      {error && <p className="employer-access-admin__alert employer-access-admin__alert--error" role="alert">{error}</p>}
      {message && <p className="employer-access-admin__alert employer-access-admin__alert--success" role="status">{message}</p>}

      {loading ? (
        <p>Loading employer access requests…</p>
      ) : requests.length === 0 ? (
        <section className="employer-access-admin__empty">
          <h2>No {status.toLowerCase()} requests</h2>
          <p>Requests submitted through the public employer form will appear here.</p>
        </section>
      ) : (
        <div className="employer-access-admin__list">
          {requests.map((item) => {
            const id = item.id || item.request_id
            return (
              <article className="employer-access-admin__card" key={id}>
                <div className="employer-access-admin__card-heading">
                  <div>
                    <h2>{item.company_name}</h2>
                    <p>{item.representative_name} · {item.email}</p>
                  </div>
                  <span className={`employer-access-admin__status employer-access-admin__status--${String(item.status || status).toLowerCase()}`}>
                    {item.status || status}
                  </span>
                </div>

                <dl className="employer-access-admin__details">
                  <div><dt>Phone</dt><dd>{item.phone || '—'}</dd></div>
                  <div><dt>Country</dt><dd>{item.country || '—'}</dd></div>
                  <div><dt>Industry</dt><dd>{item.industry || '—'}</dd></div>
                  <div><dt>Requested roles</dt><dd>{item.requested_roles || '—'}</dd></div>
                  <div><dt>Submitted</dt><dd>{formatDate(item.created_at)}</dd></div>
                  {item.reviewed_by && <div><dt>Reviewed by</dt><dd>{item.reviewed_by}</dd></div>}
                </dl>

                {item.requirements && (
                  <div className="employer-access-admin__requirements">
                    <h3>Requirements</h3>
                    <p>{item.requirements}</p>
                  </div>
                )}

                {item.review_notes && (
                  <div className="employer-access-admin__requirements">
                    <h3>Review notes</h3>
                    <p>{item.review_notes}</p>
                  </div>
                )}

                {item.status === 'Approved' && (
                  <div className="employer-access-admin__review">
                    <h3>Activate employer access</h3>

                    {organizationsError && (
                      <p
                        className="employer-access-admin__alert employer-access-admin__alert--error"
                        role="alert"
                      >
                        {organizationsError}
                      </p>
                    )}

                    <label htmlFor={`organization-${id}`}>
                      Active organization
                    </label>
                    <select
                      id={`organization-${id}`}
                      value={activationForms[id]?.organization_id || ''}
                      disabled={organizationsLoading || activatedIds.includes(id)}
                      onChange={(event) => updateActivationForm(
                        id, 'organization_id', event.target.value
                      )}
                    >
                      <option value="">
                        {organizationsLoading
                          ? 'Loading organizations…'
                          : 'Select an organization'}
                      </option>
                      {organizations.map((organization) => (
                        <option key={organization.id} value={organization.id}>
                          {organization.name}
                        </option>
                      ))}
                    </select>

                    <label htmlFor={`entra-object-${id}`}>
                      Microsoft Entra Object ID
                    </label>
                    <input
                      id={`entra-object-${id}`}
                      type="text"
                      maxLength={200}
                      autoComplete="off"
                      value={activationForms[id]?.entra_object_id || ''}
                      disabled={activatedIds.includes(id)}
                      onChange={(event) => updateActivationForm(
                        id, 'entra_object_id', event.target.value
                      )}
                      placeholder="Verified Entra user Object ID"
                    />

                    <label htmlFor={`application-user-${id}`}>
                      Existing application user ID (optional)
                    </label>
                    <input
                      id={`application-user-${id}`}
                      type="text"
                      maxLength={100}
                      autoComplete="off"
                      value={activationForms[id]?.application_user_id || ''}
                      disabled={activatedIds.includes(id)}
                      onChange={(event) => updateActivationForm(
                        id, 'application_user_id', event.target.value
                      )}
                      placeholder="Leave blank for new-employer activation"
                    />

                    <label>
                      <input
                        type="checkbox"
                        checked={activationForms[id]?.identity_verified === true}
                        disabled={activatedIds.includes(id)}
                        onChange={(event) => updateActivationForm(
                          id, 'identity_verified', event.target.checked
                        )}
                      />
                      I independently verified this Entra identity.
                    </label>

                    <p className="employer-access-admin__notice">
                      Verify the Object ID against the correct Microsoft Entra
                      tenant before activating. Supplying an existing
                      application user ID links an existing account and
                      requires its active Employer Manager membership.
                    </p>

                    {organizations.length === 0 && !organizationsLoading && (
                      <p className="employer-access-admin__notice">
                        No active organizations are available. Activation
                        cannot proceed until an active organization is available.
                      </p>
                    )}

                    <div className="employer-access-admin__actions">
                      <button
                        type="button"
                        disabled={
                          busyId === id ||
                          activatedIds.includes(id) ||
                          organizationsLoading ||
                          organizations.length === 0
                        }
                        onClick={() => activateRequest(id)}
                      >
                        {activatedIds.includes(id)
                          ? 'Activated'
                          : busyId === id
                            ? 'Activating…'
                            : 'Activate employer access'}
                      </button>
                    </div>
                  </div>
                )}

                {item.status === 'Pending' && (
                  <div className="employer-access-admin__review">
                    <label htmlFor={`notes-${id}`}>Review notes (optional)</label>
                    <textarea
                      id={`notes-${id}`}
                      rows={2}
                      maxLength={2000}
                      value={notes[id] || ''}
                      onChange={(event) => setNotes((current) => ({
                        ...current,
                        [id]: event.target.value,
                      }))}
                    />
                    <div className="employer-access-admin__actions">
                      <button
                        type="button"
                        disabled={busyId === id}
                        onClick={() => reviewRequest(id, 'Approved')}
                      >
                        {busyId === id ? 'Saving…' : 'Approve request'}
                      </button>
                      <button
                        type="button"
                        className="employer-access-admin__reject"
                        disabled={busyId === id}
                        onClick={() => reviewRequest(id, 'Rejected')}
                      >
                        Reject request
                      </button>
                    </div>
                    <p className="employer-access-admin__notice">
                      Approval records the review decision only. Login access and organization membership must be handled separately.
                    </p>
                  </div>
                )}
              </article>
            )
          })}
        </div>
      )}
    </main>
  )
}
