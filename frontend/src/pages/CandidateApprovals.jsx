import { useCallback, useEffect, useState } from 'react'
import { authenticatedFetch } from '../utils/auth'
import './CandidateApprovals.css'

const API = '/api/administrator/candidate-approvals'
const PAGE_SIZE = 25

function displayName(candidate) {
  return (
    candidate.full_name ||
    [candidate.first_name, candidate.last_name].filter(Boolean).join(' ') ||
    candidate.email ||
    candidate.entra_object_id ||
    'Unnamed candidate'
  )
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

async function readResponse(response) {
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(
      data.detail || `Request failed (${response.status}).`
    )
  }
  return data
}

export default function CandidateApprovals() {
  const [items, setItems] = useState([])
  const [status, setStatus] = useState('pending')
  const [search, setSearch] = useState('')
  const [appliedSearch, setAppliedSearch] = useState('')
  const [offset, setOffset] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState('')
  const [bulkBusy, setBulkBusy] = useState(false)
  const [selected, setSelected] = useState([])
  const [notes, setNotes] = useState({})
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const loadApprovals = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams({
        status,
        search: appliedSearch,
        limit: String(PAGE_SIZE),
        offset: String(offset),
      })
      const data = await readResponse(
        await authenticatedFetch(`${API}?${params.toString()}`)
      )
      setItems(Array.isArray(data.items) ? data.items : [])
      setHasMore(data.has_more === true)
      setSelected([])
    } catch (err) {
      setError(err.message || 'Could not load candidate approvals.')
    } finally {
      setLoading(false)
    }
  }, [status, appliedSearch, offset])

  useEffect(() => {
    loadApprovals()
  }, [loadApprovals])

  function changeStatus(value) {
    setStatus(value)
    setOffset(0)
    setSelected([])
    setMessage('')
  }

  function submitSearch(event) {
    event.preventDefault()
    setOffset(0)
    setAppliedSearch(search.trim())
    setSelected([])
    setMessage('')
  }

  function toggleSelected(id, checked) {
    setSelected((current) =>
      checked
        ? [...new Set([...current, id])]
        : current.filter((value) => value !== id)
    )
  }

  async function reviewCandidate(candidate, decision) {
    const id = candidate.entra_object_id
    const name = displayName(candidate)
    if (!id) {
      setError('This candidate has no Entra object ID; no decision was made.')
      return
    }

    const verb = decision === 'approved' ? 'approve' : 'reject'
    if (!window.confirm(`Are you sure you want to ${verb} ${name}?`)) return

    setBusyId(id)
    setError('')
    setMessage('')
    try {
      await readResponse(
        await authenticatedFetch(
          `${API}/${encodeURIComponent(id)}/review`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              status: decision,
              approval_notes: notes[id] || null,
            }),
          }
        )
      )
      setMessage(`${name} was ${decision}.`)
      await loadApprovals()
    } catch (err) {
      setError(err.message || 'Could not save the review decision.')
    } finally {
      setBusyId('')
    }
  }

  async function bulkApprove() {
    const ids = items
      .filter(
        (item) =>
          selected.includes(item.entra_object_id) &&
          item.approval_status === 'pending' &&
          item.entra_object_id
      )
      .map((item) => item.entra_object_id)

    if (!ids.length) {
      setError('Select at least one pending candidate.')
      return
    }

    if (!window.confirm(`Approve ${ids.length} selected candidate(s)?`)) return

    setBulkBusy(true)
    setError('')
    setMessage('')
    try {
      const data = await readResponse(
        await authenticatedFetch(`${API}/bulk-approve`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            entra_object_ids: ids,
            approval_notes: 'Bulk approval by administrator',
          }),
        })
      )
      setMessage(
        `Bulk review complete: ${data.approved_count ?? 0} approved, ` +
        `${data.skipped_count ?? 0} skipped, ${data.error_count ?? 0} errors.`
      )
      await loadApprovals()
    } catch (err) {
      setError(err.message || 'Bulk approval failed.')
    } finally {
      setBulkBusy(false)
    }
  }

  return (
    <main className="candidate-approvals">
      <header className="candidate-approvals__header">
        <div>
          <h1>Candidate Approvals</h1>
          <p>
            Review candidate profiles before granting access to recruitment
            features.
          </p>
        </div>
        <button
          type="button"
          onClick={loadApprovals}
          disabled={loading || bulkBusy}
        >
          Refresh
        </button>
      </header>

      <form className="candidate-approvals__filters" onSubmit={submitSearch}>
        <label>
          Status
          <select
            value={status}
            onChange={(event) => changeStatus(event.target.value)}
          >
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </label>
        <label className="candidate-approvals__search">
          Search candidates
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Name, email, or Entra object ID"
          />
        </label>
        <button type="submit" disabled={loading}>Search</button>
      </form>

      {error && <p className="candidate-approvals__alert" role="alert">{error}</p>}
      {message && <p className="candidate-approvals__success" role="status">{message}</p>}

      {status === 'pending' && (
        <div className="candidate-approvals__bulk">
          <span>{selected.length} selected</span>
          <button
            type="button"
            onClick={bulkApprove}
            disabled={loading || bulkBusy || selected.length === 0}
          >
            {bulkBusy ? 'Approving…' : 'Approve selected'}
          </button>
        </div>
      )}

      {loading ? (
        <p className="candidate-approvals__empty" role="status">
          Loading candidate approvals…
        </p>
      ) : items.length === 0 ? (
        <section className="candidate-approvals__empty">
          <h2>No candidates found</h2>
          <p>Try another status or search term.</p>
        </section>
      ) : (
        <div className="candidate-approvals__list">
          {items.map((candidate) => {
            const id = candidate.entra_object_id
            const currentStatus = candidate.approval_status || status
            const isPending = currentStatus === 'pending'

            return (
              <article className="candidate-approvals__card" key={id || candidate.email}>
                <div className="candidate-approvals__card-heading">
                  <div className="candidate-approvals__identity">
                    {status === 'pending' && isPending && id && (
                      <input
                        aria-label={`Select ${displayName(candidate)}`}
                        type="checkbox"
                        checked={selected.includes(id)}
                        onChange={(event) => toggleSelected(id, event.target.checked)}
                      />
                    )}
                    <div>
                      <h2>{displayName(candidate)}</h2>
                      <p>{candidate.email || 'No email recorded'}</p>
                    </div>
                  </div>
                  <span className={`candidate-approvals__status candidate-approvals__status--${currentStatus}`}>
                    {currentStatus}
                  </span>
                </div>

                <dl className="candidate-approvals__details">
                  <div>
                    <dt>Entra object ID</dt>
                    <dd>{id || '—'}</dd>
                  </div>
                  <div>
                    <dt>Submitted / created</dt>
                    <dd>{formatDate(candidate.created_at)}</dd>
                  </div>
                  <div>
                    <dt>Reviewed at</dt>
                    <dd>{formatDate(candidate.reviewed_at)}</dd>
                  </div>
                  <div>
                    <dt>Reviewed by</dt>
                    <dd>{candidate.reviewed_by || '—'}</dd>
                  </div>
                </dl>

                {candidate.approval_notes && (
                  <p className="candidate-approvals__notes">
                    <strong>Review notes:</strong> {candidate.approval_notes}
                  </p>
                )}

                {isPending && (
                  <div className="candidate-approvals__review">
                    <label>
                      Review notes (optional)
                      <textarea
                        rows={2}
                        maxLength={2000}
                        value={notes[id] || ''}
                        onChange={(event) =>
                          setNotes((current) => ({
                            ...current,
                            [id]: event.target.value,
                          }))
                        }
                        placeholder="Add context for this decision"
                      />
                    </label>
                    <div className="candidate-approvals__actions">
                      <button
                        type="button"
                        disabled={!id || busyId === id || bulkBusy}
                        onClick={() => reviewCandidate(candidate, 'approved')}
                      >
                        {busyId === id ? 'Saving…' : 'Approve'}
                      </button>
                      <button
                        className="candidate-approvals__reject"
                        type="button"
                        disabled={!id || busyId === id || bulkBusy}
                        onClick={() => reviewCandidate(candidate, 'rejected')}
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                )}
              </article>
            )
          })}
        </div>
      )}

      <nav className="candidate-approvals__pagination" aria-label="Candidate approval pages">
        <button
          type="button"
          disabled={loading || offset === 0}
          onClick={() => setOffset((value) => Math.max(0, value - PAGE_SIZE))}
        >
          Previous
        </button>
        <span>
          Showing {items.length ? offset + 1 : 0}–{offset + items.length}
        </span>
        <button
          type="button"
          disabled={loading || !hasMore}
          onClick={() => setOffset((value) => value + PAGE_SIZE)}
        >
          Next
        </button>
      </nav>
    </main>
  )
}
