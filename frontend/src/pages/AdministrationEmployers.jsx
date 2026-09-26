import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'
import { authenticatedFetch } from '../utils/auth'

const MEMBER_ROLES = [
  'Administrator',
  'HR Manager',
  'Employer Manager',
  'Candidate',
]

const emptyForm = {
  user_id: '',
  role: 'Employer Manager',
}

export default function AdministrationEmployers({ auth }) {
  const [organizations, setOrganizations] = useState([])
  const [selectedOrganization, setSelectedOrganization] = useState(null)
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [membersLoading, setMembersLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [updatingUserId, setUpdatingUserId] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function loadOrganizations() {
    setLoading(true)
    setError('')

    try {
      const response = await authenticatedFetch('/api/organizations')

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to load organizations.')
      }

      setOrganizations(data.organizations || [])
    } catch (err) {
      console.error(err)
      setError(err.message || 'Unable to load organizations.')
    } finally {
      setLoading(false)
    }
  }

  async function loadMembers(organizationId) {
    if (!organizationId) {
      setMembers([])
      return
    }

    setMembersLoading(true)
    setError('')

    try {
      const response = await authenticatedFetch(
        `/api/organizations/${encodeURIComponent(organizationId)}/members`,
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to load organization members.')
      }

      setMembers(data.members || [])
    } catch (err) {
      console.error(err)
      setError(err.message || 'Unable to load organization members.')
    } finally {
      setMembersLoading(false)
    }
  }

  useEffect(() => {
    if (!auth?.roles?.includes('Administrator')) {
      setLoading(false)
      setError('Administrator access is required.')
      return
    }

    loadOrganizations()
  }, [auth])

  function openOrganization(organization) {
    setSelectedOrganization(organization)
    setShowAddForm(false)
    setForm(emptyForm)
    setMessage('')
    setError('')
    loadMembers(organization.id)
  }

  function closeOrganization() {
    setSelectedOrganization(null)
    setMembers([])
    setShowAddForm(false)
    setForm(emptyForm)
    setMessage('')
    setError('')
  }

  function updateField(event) {
    const { name, value } = event.target

    setForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  async function addMember(event) {
    event.preventDefault()

    if (!selectedOrganization?.id) return

    const userId = form.user_id.trim()

    if (!userId) {
      setError('Microsoft Entra User/Object ID is required.')
      return
    }

    setSaving(true)
    setError('')
    setMessage('')

    try {
      const response = await authenticatedFetch(
        `/api/organizations/${encodeURIComponent(selectedOrganization.id)}/members`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: userId,
            role: form.role,
          }),
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to add organization member.')
      }

      setForm(emptyForm)
      setShowAddForm(false)

      if (data.reactivated) {
        setMessage('The existing membership was reactivated.')
      } else {
        setMessage('Member added successfully.')
      }

      await loadMembers(selectedOrganization.id)
    } catch (err) {
      console.error(err)
      setError(err.message || 'Unable to add organization member.')
    } finally {
      setSaving(false)
    }
  }

  async function updateMemberStatus(member, status) {
    if (!selectedOrganization?.id || !member?.user_id) return

    setUpdatingUserId(member.user_id)
    setError('')
    setMessage('')

    try {
      const response = await authenticatedFetch(
        `/api/organizations/${encodeURIComponent(
          selectedOrganization.id,
        )}/members/${encodeURIComponent(member.user_id)}`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            status,
          }),
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to update member status.')
      }

      setMessage(
        status === 'active'
          ? 'Member reactivated successfully.'
          : 'Member access deactivated.',
      )

      await loadMembers(selectedOrganization.id)
    } catch (err) {
      console.error(err)
      setError(err.message || 'Unable to update member status.')
    } finally {
      setUpdatingUserId('')
    }
  }

  if (selectedOrganization) {
    const activeCount = members.filter(
      (member) => member.status === 'active',
    ).length

    return (
      <section className="page-section">
        <div className="page-header">
          <div>
            <button
              type="button"
              className="secondary-button"
              onClick={closeOrganization}
            >
              ← Organizations
            </button>
            <h1>{selectedOrganization.name}</h1>
            <p>
              Manage organization membership and application access.
            </p>
          </div>

          <button
            type="button"
            className="primary-button"
            onClick={() => {
              setShowAddForm((current) => !current)
              setError('')
              setMessage('')
            }}
          >
            {showAddForm ? 'Cancel' : '+ Add Member'}
          </button>
        </div>

        {error && <div className="empty-state">{error}</div>}

        {message && (
          <div className="empty-state">
            <strong>{message}</strong>
          </div>
        )}

        <section className="card">
          <div className="card-header">
            <div>
              <h2>Organization Members</h2>
              <p>
                {activeCount} active member{activeCount === 1 ? '' : 's'}
              </p>
            </div>
          </div>

          {showAddForm && (
            <form onSubmit={addMember} className="form-grid">
              <label>
                Microsoft Entra User/Object ID
                <input
                  name="user_id"
                  value={form.user_id}
                  onChange={updateField}
                  placeholder="Enter the Entra user/object ID"
                  autoComplete="off"
                />
              </label>

              <label>
                Application Role
                <select
                  name="role"
                  value={form.role}
                  onChange={updateField}
                >
                  {MEMBER_ROLES.map((role) => (
                    <option key={role} value={role}>
                      {role}
                    </option>
                  ))}
                </select>
              </label>

              <div className="form-actions">
                <button
                  type="submit"
                  className="primary-button"
                  disabled={saving}
                >
                  {saving ? 'Adding…' : 'Add Member'}
                </button>
              </div>
            </form>
          )}

          {membersLoading ? (
            <div className="empty-state">
              <strong>Loading members…</strong>
            </div>
          ) : members.length === 0 ? (
            <div className="empty-state">
              <strong>No organization members found.</strong>
              <span>Add a member to give the organization application access.</span>
            </div>
          ) : (
            <div className="onboarding-table-wrap">
              <table className="onboarding-table">
                <thead>
                  <tr>
                    <th>User / Object ID</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {members.map((member) => {
                    const isUpdating = updatingUserId === member.user_id
                    const isActive = member.status === 'active'

                    return (
                      <tr key={`${member.user_id}-${member.role}`}>
                        <td>{member.user_id}</td>
                        <td>{member.role}</td>
                        <td>{member.status}</td>
                        <td>
                          <button
                            type="button"
                            className={
                              isActive
                                ? 'secondary-button'
                                : 'primary-button'
                            }
                            disabled={isUpdating}
                            onClick={() =>
                              updateMemberStatus(
                                member,
                                isActive ? 'inactive' : 'active',
                              )
                            }
                          >
                            {isUpdating
                              ? 'Updating…'
                              : isActive
                                ? 'Deactivate'
                                : 'Reactivate'}
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </section>
    )
  }

  return (
    <section className="page-section">
      <PageHeader
        title="Employers"
        description="Manage organizations and their application access."
      />

      {error && <div className="empty-state">{error}</div>}

      {loading ? (
        <section className="card">
          <div className="empty-state">
            <strong>Loading organizations…</strong>
          </div>
        </section>
      ) : organizations.length === 0 ? (
        <section className="card">
          <div className="empty-state">
            <strong>No organizations found.</strong>
            <span>
              Active organizations will appear here when they are available.
            </span>
          </div>
        </section>
      ) : (
        <section className="card">
          <div className="card-header">
            <div>
              <h2>Organizations</h2>
              <p>Manage organization membership and access.</p>
            </div>
          </div>

          <div className="onboarding-table-wrap">
            <table className="onboarding-table">
              <thead>
                <tr>
                  <th>Organization</th>
                  <th>Status</th>
                  <th>Members</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {organizations.map((organization) => (
                  <tr key={organization.id}>
                    <td>
                      <strong>{organization.name}</strong>
                    </td>
                    <td>{organization.status}</td>
                    <td>
                      {organization.member_count ??
                        organization.members_count ??
                        '—'}
                    </td>
                    <td>
                      <button
                        type="button"
                        className="primary-button"
                        onClick={() => openOrganization(organization)}
                      >
                        Manage Members
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </section>
  )
}
