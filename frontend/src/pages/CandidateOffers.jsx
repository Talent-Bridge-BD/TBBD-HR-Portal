import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'
import { authenticatedFetch } from '../utils/auth'

export default function CandidateOffers() {
  const [offers, setOffers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionLoading, setActionLoading] = useState('')
  const [actionError, setActionError] = useState('')

  async function loadOffers() {
    try {
      setLoading(true)
      setError('')

      const response = await authenticatedFetch(
        '/api/candidate/offers',
      )

      if (!response.ok) {
        const body = await response.text()

        throw new Error(
          body ||
            `Unable to load offers (${response.status})`,
        )
      }

      const data = await response.json()

      setOffers(
        Array.isArray(data.offers)
          ? data.offers
          : [],
      )
    } catch (err) {
      setError(
        err.message ||
          'Unable to load your employment offers.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadOffers()
  }, [])

  function formatDate(value) {
    if (!value) return 'Not specified'

    const date = new Date(value)

    if (Number.isNaN(date.getTime())) {
      return value
    }

    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  function formatSalary(amount, currency) {
    if (
      amount === null ||
      amount === undefined ||
      amount === ''
    ) {
      return 'Not specified'
    }

    const numericAmount = Number(amount)

    if (Number.isNaN(numericAmount)) {
      return `${amount} ${currency || ''}`.trim()
    }

    return `${currency || ''} ${numericAmount.toLocaleString()}`.trim()
  }

  async function acceptOffer(offerId) {
    setActionLoading(offerId)
    setActionError('')

    try {
      const response = await authenticatedFetch(
        `/api/candidate/offers/${encodeURIComponent(
          offerId,
        )}/accept`,
        {
          method: 'POST',
        },
      )

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        throw new Error(
          data.detail ||
            'Unable to accept this offer.',
        )
      }

      await loadOffers()
    } catch (err) {
      setActionError(
        err.message ||
          'Unable to accept this offer.',
      )
    } finally {
      setActionLoading('')
    }
  }

  return (
    <div className="candidate-portal-page">
      <PageHeader
        title="My Offers"
        subtitle="View your employment offers and offer letters."
      />

      <DashboardCard title="Employment Offers">
        {loading && (
          <div className="empty-state">
            <strong>Loading offers...</strong>
            <span>
              Please wait while your employment offers are retrieved.
            </span>
          </div>
        )}

        {!loading && error && (
          <div className="empty-state">
            <strong>Unable to load offers</strong>
            <span>{error}</span>
          </div>
        )}

        {!loading && !error && actionError && (
          <div className="empty-state">
            <strong>Offer action could not be completed</strong>
            <span>{actionError}</span>
          </div>
        )}

        {!loading &&
          !error &&
          offers.length === 0 && (
            <div className="empty-state">
              <strong>No employment offers</strong>
              <span>
                Offers received from employers will appear here.
              </span>
            </div>
          )}

        {!loading &&
          !error &&
          offers.length > 0 && (
            <div
              style={{
                display: 'grid',
                gap: '18px',
              }}
            >
              {offers.map((offer) => {
                const isSent =
                  offer.status === 'Sent'

                const isAccepted =
                  offer.status === 'Accepted'

                return (
                  <article
                    key={offer.id}
                    style={{
                      padding: '22px',
                      border: '1px solid #E2E8F0',
                      borderRadius: '12px',
                      background: '#FFFFFF',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        gap: '16px',
                      }}
                    >
                      <div>
                        <h3
                          style={{
                            margin: 0,
                            color: '#0F172A',
                            fontSize: '18px',
                            fontWeight: 700,
                          }}
                        >
                          {offer.offer_title ||
                            'Employment Offer'}
                        </h3>

                        <p
                          style={{
                            margin: '5px 0 0',
                            color: '#475569',
                            fontSize: '14px',
                          }}
                        >
                          {offer.job_title ||
                            'Job position'}
                        </p>
                      </div>

                      <span
                        style={{
                          padding: '5px 10px',
                          borderRadius: '999px',
                          background: isAccepted
                            ? '#ECFDF5'
                            : '#EFF6FF',
                          color: isAccepted
                            ? '#047857'
                            : '#1D4ED8',
                          fontSize: '12px',
                          fontWeight: 700,
                        }}
                      >
                        {offer.status}
                      </span>
                    </div>

                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns:
                          'repeat(auto-fit, minmax(180px, 1fr))',
                        gap: '14px',
                        marginTop: '20px',
                      }}
                    >
                      <div>
                        <span
                          style={{
                            display: 'block',
                            color: '#64748B',
                            fontSize: '12px',
                          }}
                        >
                          Employment Type
                        </span>

                        <strong
                          style={{
                            display: 'block',
                            marginTop: '4px',
                            color: '#0F172A',
                            fontSize: '14px',
                          }}
                        >
                          {offer.employment_type ||
                            'Not specified'}
                        </strong>
                      </div>

                      <div>
                        <span
                          style={{
                            display: 'block',
                            color: '#64748B',
                            fontSize: '12px',
                          }}
                        >
                          Salary
                        </span>

                        <strong
                          style={{
                            display: 'block',
                            marginTop: '4px',
                            color: '#0F172A',
                            fontSize: '14px',
                          }}
                        >
                          {formatSalary(
                            offer.salary_amount,
                            offer.salary_currency,
                          )}
                        </strong>
                      </div>

                      <div>
                        <span
                          style={{
                            display: 'block',
                            color: '#64748B',
                            fontSize: '12px',
                          }}
                        >
                          Start Date
                        </span>

                        <strong
                          style={{
                            display: 'block',
                            marginTop: '4px',
                            color: '#0F172A',
                            fontSize: '14px',
                          }}
                        >
                          {formatDate(
                            offer.start_date,
                          )}
                        </strong>
                      </div>

                      <div>
                        <span
                          style={{
                            display: 'block',
                            color: '#64748B',
                            fontSize: '12px',
                          }}
                        >
                          Offer Expiry
                        </span>

                        <strong
                          style={{
                            display: 'block',
                            marginTop: '4px',
                            color: '#0F172A',
                            fontSize: '14px',
                          }}
                        >
                          {formatDate(
                            offer.offer_expiry_date,
                          )}
                        </strong>
                      </div>
                    </div>

                    {offer.terms_and_conditions && (
                      <div
                        style={{
                          marginTop: '20px',
                          paddingTop: '18px',
                          borderTop:
                            '1px solid #E2E8F0',
                        }}
                      >
                        <span
                          style={{
                            display: 'block',
                            color: '#64748B',
                            fontSize: '12px',
                            fontWeight: 700,
                          }}
                        >
                          Terms and Conditions
                        </span>

                        <p
                          style={{
                            margin: '7px 0 0',
                            color: '#475569',
                            fontSize: '14px',
                            lineHeight: 1.6,
                            whiteSpace: 'pre-wrap',
                          }}
                        >
                          {offer.terms_and_conditions}
                        </p>
                      </div>
                    )}

                    {isSent && (
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'flex-end',
                          marginTop: '20px',
                          paddingTop: '18px',
                          borderTop:
                            '1px solid #E2E8F0',
                        }}
                      >
                        <button
                          type="button"
                          className="primary-action"
                          disabled={
                            actionLoading ===
                            offer.id
                          }
                          onClick={() =>
                            acceptOffer(
                              offer.id,
                            )
                          }
                        >
                          {actionLoading ===
                          offer.id
                            ? 'Processing...'
                            : 'Accept Offer'}
                        </button>
                      </div>
                    )}

                    {isAccepted && (
                      <div
                        style={{
                          marginTop: '20px',
                          paddingTop: '18px',
                          borderTop:
                            '1px solid #E2E8F0',
                          color: '#047857',
                          fontSize: '14px',
                          fontWeight: 600,
                        }}
                      >
                        Offer accepted
                        {offer.accepted_at
                          ? ` on ${formatDate(
                              offer.accepted_at,
                            )}.`
                          : '.'}
                      </div>
                    )}
                  </article>
                )
              })}
            </div>
          )}
      </DashboardCard>
    </div>
  )
}
