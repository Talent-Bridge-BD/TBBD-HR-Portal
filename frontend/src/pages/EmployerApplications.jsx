import { useEffect, useMemo, useState } from 'react'

import PageHeader from '../components/PageHeader'

const STATUS_STYLES = {
  Applied: {
    color: '#0067B8',
    background: '#EAF4FB',
  },
  Screening: {
    color: '#D97706',
    background: '#FFF7E6',
  },
  Interview: {
    color: '#7C3AED',
    background: '#F3E8FF',
  },
  Completed: {
    color: '#16A34A',
    background: '#ECFDF3',
  },
}

function getDisplayStatus(status) {
  const normalized = String(status || '').toLowerCase()

  if (normalized === 'submitted') {
    return 'Applied'
  }

  if (normalized === 'screening') {
    return 'Screening'
  }

  if (normalized === 'interview') {
    return 'Interview'
  }

  if (
    normalized === 'completed' ||
    normalized === 'hired' ||
    normalized === 'approved'
  ) {
    return 'Completed'
  }

  return status || 'Applied'
}

function formatDate(value) {
  if (!value) {
    return '—'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return '—'
  }

  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function getCandidateName(application) {
  const name = [
    application.candidate_first_name,
    application.candidate_last_name,
  ]
    .filter(Boolean)
    .join(' ')

  return name || 'Unnamed Candidate'
}

function getInitials(application) {
  const name = getCandidateName(application)

  const parts = name.split(/\s+/).filter(Boolean)

  if (parts.length === 1) {
    return parts[0].slice(0, 2).toUpperCase()
  }

  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
}

export default function EmployerApplications({ auth }) {
  const organizationId = auth?.organization_ids?.[0] || ''

  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!organizationId) {
      setLoading(false)
      return
    }

    fetch(
      `/api/applications?organization_id=${encodeURIComponent(
        organizationId
      )}`,
      {
        credentials: 'include',
      }
    )
      .then(async (response) => {
        const data = await response.json()

        if (!response.ok) {
          throw new Error(
            data.detail || 'Unable to load applications.'
          )
        }

        return data
      })
      .then((data) => {
        setApplications(data.applications || [])
      })
      .catch((err) => {
        setError(err.message)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [organizationId])

  const summary = useMemo(() => {
    const counts = {
      total: applications.length,
      applied: 0,
      screening: 0,
      interview: 0,
    }

    applications.forEach((application) => {
      const status = getDisplayStatus(application.status)

      if (status === 'Applied') {
        counts.applied += 1
      }

      if (status === 'Screening') {
        counts.screening += 1
      }

      if (status === 'Interview') {
        counts.interview += 1
      }
    })

    return counts
  }, [applications])

  return (
    <>
      <PageHeader
        title="Applications"
        subtitle="Review candidate applications for your organization."
      />

      {!organizationId ? (
        <section className="placeholder-card">
          <h2>Organization access required</h2>
          <p>
            Your account is not currently assigned to an organization.
          </p>
        </section>
      ) : loading ? (
        <section className="placeholder-card">
          <p>Loading applications...</p>
        </section>
      ) : error ? (
        <section className="placeholder-card">
          <h2>Unable to load applications</h2>
          <p>{error}</p>
        </section>
      ) : (
        <>
          <section
            style={{
              display: 'grid',
              gridTemplateColumns:
                'repeat(auto-fit, minmax(190px, 1fr))',
              gap: '14px',
              marginBottom: '20px',
            }}
          >
            {[
              {
                label: 'Total Applications',
                value: summary.total,
                color: '#0067B8',
                background: '#EAF4FB',
              },
              {
                label: 'Applied',
                value: summary.applied,
                color: '#0067B8',
                background: '#EAF4FB',
              },
              {
                label: 'Screening',
                value: summary.screening,
                color: '#D97706',
                background: '#FFF7E6',
              },
              {
                label: 'Interview',
                value: summary.interview,
                color: '#7C3AED',
                background: '#F3E8FF',
              },
            ].map((item) => (
              <section
                key={item.label}
                className="dashboard-card"
                style={{
                  padding: '18px',
                  borderRadius: '14px',
                  border: '1px solid #E5E7EB',
                  boxShadow:
                    '0 2px 6px rgba(15, 23, 42, 0.06)',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '12px',
                  }}
                >
                  <div>
                    <div
                      style={{
                        fontSize: '13px',
                        color: '#64748B',
                        marginBottom: '6px',
                      }}
                    >
                      {item.label}
                    </div>

                    <div
                      style={{
                        fontSize: '28px',
                        fontWeight: 700,
                        color: '#0F172A',
                        lineHeight: 1,
                      }}
                    >
                      {item.value}
                    </div>
                  </div>

                  <div
                    style={{
                      width: '10px',
                      height: '10px',
                      borderRadius: '50%',
                      background: item.color,
                      flexShrink: 0,
                    }}
                  />
                </div>
              </section>
            ))}
          </section>

          <section
            className="dashboard-card"
            style={{
              padding: '20px',
              borderRadius: '16px',
              border: '1px solid #E5E7EB',
              boxShadow:
                '0 2px 8px rgba(15, 23, 42, 0.05)',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '12px',
                marginBottom: '18px',
              }}
            >
              <div>
                <h2
                  style={{
                    margin: 0,
                    fontSize: '18px',
                    color: '#0F172A',
                  }}
                >
                  Candidate Applications
                </h2>

                <p
                  style={{
                    margin: '5px 0 0',
                    color: '#64748B',
                    fontSize: '13px',
                  }}
                >
                  Review candidates progressing through recruitment.
                </p>
              </div>

              <div
                style={{
                  padding: '6px 10px',
                  borderRadius: '999px',
                  background: '#F8FAFC',
                  color: '#475569',
                  fontSize: '13px',
                  fontWeight: 600,
                }}
              >
                {summary.total}{' '}
                {summary.total === 1 ? 'application' : 'applications'}
              </div>
            </div>

            {applications.length === 0 ? (
              <div
                style={{
                  padding: '42px 20px',
                  textAlign: 'center',
                  border: '1px dashed #CBD5E1',
                  borderRadius: '12px',
                  color: '#64748B',
                }}
              >
                <div
                  style={{
                    fontSize: '16px',
                    fontWeight: 600,
                    color: '#334155',
                    marginBottom: '6px',
                  }}
                >
                  No applications yet
                </div>

                <div style={{ fontSize: '14px' }}>
                  Candidate applications for your organization will
                  appear here.
                </div>
              </div>
            ) : (
              <div
                style={{
                  display: 'grid',
                  gap: '12px',
                }}
              >
                {applications.map((application) => {
                  const status = getDisplayStatus(application.status)
                  const statusStyle =
                    STATUS_STYLES[status] || STATUS_STYLES.Applied

                  return (
                    <article
                      key={application.id}
                      style={{
                        display: 'grid',
                        gridTemplateColumns:
                          'auto minmax(180px, 1.4fr) minmax(180px, 1fr) auto',
                        alignItems: 'center',
                        gap: '18px',
                        padding: '16px',
                        border: '1px solid #E5E7EB',
                        borderRadius: '14px',
                        background: '#FFFFFF',
                        boxShadow:
                          '0 1px 3px rgba(15, 23, 42, 0.04)',
                      }}
                    >
                      <div
                        style={{
                          width: '48px',
                          height: '48px',
                          borderRadius: '14px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          background: '#EAF4FB',
                          color: '#0067B8',
                          fontWeight: 700,
                          fontSize: '14px',
                        }}
                      >
                        {getInitials(application)}
                      </div>

                      <div style={{ minWidth: 0 }}>
                        <div
                          style={{
                            fontSize: '16px',
                            fontWeight: 700,
                            color: '#0F172A',
                            marginBottom: '4px',
                          }}
                        >
                          {getCandidateName(application)}
                        </div>

                        <div
                          style={{
                            fontSize: '13px',
                            color: '#64748B',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {application.candidate_email || 'No email'}
                        </div>
                      </div>

                      <div style={{ minWidth: 0 }}>
                        <div
                          style={{
                            fontSize: '13px',
                            color: '#64748B',
                            marginBottom: '4px',
                          }}
                        >
                          Position
                        </div>

                        <div
                          style={{
                            fontSize: '14px',
                            fontWeight: 600,
                            color: '#334155',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {application.job_title || '—'}
                        </div>

                        <div
                          style={{
                            marginTop: '5px',
                            fontSize: '12px',
                            color: '#94A3B8',
                          }}
                        >
                          Applied {formatDate(application.applied_at)}
                        </div>
                      </div>

                      <div
                        style={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'flex-end',
                          gap: '8px',
                        }}
                      >
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            padding: '6px 10px',
                            borderRadius: '999px',
                            background: statusStyle.background,
                            color: statusStyle.color,
                            fontSize: '12px',
                            fontWeight: 700,
                          }}
                        >
                          {status}
                        </span>


                      </div>
                    </article>
                  )
                })}
              </div>
            )}
          </section>
        </>
      )}
    </>
  )
}
