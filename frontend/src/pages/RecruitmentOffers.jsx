import { useEffect, useState } from 'react'

import PageHeader from '../components/PageHeader'


const OFFER_STATUSES = [
  'draft',
  'sent',
  'accepted',
  'declined',
  'expired',
  'withdrawn',
]


export default function RecruitmentOffers({ auth }) {

  const organizationId = auth?.organization_ids?.[0] || ''

  const [offers, setOffers] = useState([])
  const [applications, setApplications] = useState([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showForm, setShowForm] = useState(false)
  const [saving, setSaving] = useState(false)

  const [form, setForm] = useState({
    application_id: '',
    offer_date: '',
    expiry_date: '',
    start_date: '',
    employment_type: '',
    salary_compensation: '',
    currency: '',
    location: '',
    notes: '',
  })


  const loadOffers = async () => {

    if (!organizationId) {
      setLoading(false)
      return
    }

    setLoading(true)
    setError('')

    try {

      const response = await fetch(
        `/api/offers?organization_id=${encodeURIComponent(organizationId)}`,

        {
          credentials: 'include',
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to load offers.'
        )
      }

      setOffers(Array.isArray(data) ? data : data.offers || [])

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

      const applicationList =
        Array.isArray(data)
          ? data
          : data.applications || []

      setApplications(applicationList)

    } catch (err) {

      setError(err.message)

    }
  }


  useEffect(() => {

    loadOffers()
    loadApplications()

  }, [organizationId])


  const resetForm = () => {

    setForm({
      application_id: '',
      offer_date: '',
      expiry_date: '',
      start_date: '',
      employment_type: '',
      salary_compensation: '',
      currency: '',
      location: '',
      notes: '',
    })

  }


  const openForm = () => {

    resetForm()
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

    if (!form.offer_date) {
      setError('Please select an offer date.')
      return
    }

    setSaving(true)
    setError('')

    try {

      const payload = {
        application_id: form.application_id,
        offer_date: new Date(
          form.offer_date
        ).toISOString(),

        expiry_date: form.expiry_date
          ? new Date(form.expiry_date).toISOString()
          : null,

        start_date: form.start_date || null,

        employment_type:
          form.employment_type || null,

        salary_compensation:
          form.salary_compensation || null,

        currency:
          form.currency || null,

        location:
          form.location || null,

        notes:
          form.notes || null,
      }


      const response = await fetch(
        `/api/offers?organization_id=${encodeURIComponent(
          organizationId
        )}`,
        {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        }
      )


      const data = await response.json()


      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to create offer.'
        )
      }


      setShowForm(false)
      resetForm()

      await loadOffers()

    } catch (err) {

      setError(err.message)

    } finally {

      setSaving(false)

    }
  }


  const updateStatus = async (offer, status) => {

    try {

      const response = await fetch(
        `/api/offers/${encodeURIComponent(
          offer.id
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
            offer_date: offer.offer_date,

            expiry_date:
              offer.expiry_date || null,

            start_date:
              offer.start_date || null,

            employment_type:
              offer.employment_type || null,

            salary_compensation:
              offer.salary_compensation || null,

            currency:
              offer.currency || null,

            location:
              offer.location || null,

            notes:
              offer.notes || null,

            status,
          }),
        }
      )


      const data = await response.json()


      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to update offer status.'
        )
      }


      const updatedOffer =
        data.offer || data


      setOffers((current) =>
        current.map((item) =>
          item.id === offer.id
            ? updatedOffer
            : item
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


  const formatDateTime = (value) => {

    if (!value) {
      return '—'
    }

    return new Date(value).toLocaleString()

  }


  if (!organizationId) {

    return (
      <>
        <PageHeader
          title="Offers"
          subtitle="Manage candidate offers through the recruitment process."
        />

        <section className="placeholder-card">

          <h2>Organization access required</h2>

          <p>
            An authorized organization membership is required
            to manage recruitment offers.
          </p>

        </section>
      </>
    )

  }


  return (
    <>

      <PageHeader
        title="Offers"
        subtitle="Manage candidate offers through the recruitment process."
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

            <h2>Offer Management</h2>

            <p>
              Create and manage offers linked to candidate applications.
            </p>

          </div>


          <button
            type="button"
            onClick={openForm}
            disabled={saving}
          >
            Create Offer
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

            <h3>Create Offer</h3>


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
                    </option>
                  )

                })}

              </select>

            </label>


            <label>
              Offer Date

              <input
                type="datetime-local"
                name="offer_date"
                value={form.offer_date}
                onChange={handleChange}
                required
              />

            </label>


            <label>
              Expiry Date

              <input
                type="datetime-local"
                name="expiry_date"
                value={form.expiry_date}
                onChange={handleChange}
              />

            </label>


            <label>
              Start Date

              <input
                type="date"
                name="start_date"
                value={form.start_date}
                onChange={handleChange}
              />

            </label>


            <label>
              Employment Type

              <input
                type="text"
                name="employment_type"
                value={form.employment_type}
                onChange={handleChange}
                placeholder="Full-time"
              />

            </label>


            <label>
              Salary / Compensation

              <input
                type="text"
                name="salary_compensation"
                value={form.salary_compensation}
                onChange={handleChange}
                placeholder="e.g. 5000 per month"
              />

            </label>


            <label>
              Currency

              <input
                type="text"
                name="currency"
                value={form.currency}
                onChange={handleChange}
                placeholder="USD"
              />

            </label>


            <label>
              Location

              <input
                type="text"
                name="location"
                value={form.location}
                onChange={handleChange}
                placeholder="Dhaka / Remote / Overseas"
              />

            </label>


            <label>
              Notes

              <textarea
                name="notes"
                value={form.notes}
                onChange={handleChange}
                rows="4"
                placeholder="Offer notes"
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
                {saving ? 'Creating…' : 'Create Offer'}
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

          <p>Loading offers…</p>

        ) : offers.length === 0 ? (

          <div>

            <h3>No offers yet</h3>

            <p>
              Offers will appear here when candidates reach
              the offer stage of the recruitment process.
            </p>

          </div>

        ) : (

          <div style={{ overflowX: 'auto' }}>

            <table>

              <thead>

                <tr>

                  <th>Candidate</th>
                  <th>Email</th>
                  <th>Job</th>
                  <th>Offer Date</th>
                  <th>Expiry</th>
                  <th>Start Date</th>
                  <th>Compensation</th>
                  <th>Status</th>

                </tr>

              </thead>


              <tbody>

                {offers.map((offer) => (

                  <tr key={offer.id}>

                    <td>
                      {offer.candidate_first_name}{' '}
                      {offer.candidate_last_name}
                    </td>

                    <td>
                      {offer.candidate_email || '—'}
                    </td>

                    <td>
                      {offer.job_title || '—'}
                    </td>

                    <td>
                      {formatDateTime(
                        offer.offer_date
                      )}
                    </td>

                    <td>
                      {formatDateTime(
                        offer.expiry_date
                      )}
                    </td>

                    <td>
                      {formatDate(
                        offer.start_date
                      )}
                    </td>

                    <td>
                      {offer.salary_compensation
                        ? `${offer.salary_compensation}${
                            offer.currency
                              ? ` ${offer.currency}`
                              : ''
                          }`
                        : '—'}
                    </td>

                    <td>

                      <select
                        value={offer.status}
                        onChange={(event) =>
                          updateStatus(
                            offer,
                            event.target.value
                          )
                        }
                      >

                        {OFFER_STATUSES.map((status) => (

                          <option
                            key={status}
                            value={status}
                          >
                            {status}
                          </option>

                        ))}

                      </select>

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
