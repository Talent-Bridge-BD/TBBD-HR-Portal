import { useState } from 'react'
import talentBridgeLogo from '../assets/branding/talent-bridge-bd-logo.png'

const initialValues = {
  company_name: '',
  representative_name: '',
  email: '',
  phone: '',
  country: '',
  industry: '',
  requested_roles: '',
  requirements: '',
}

export default function EmployerAccessRequest() {
  const [values, setValues] = useState(initialValues)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  function updateField(event) {
    const { name, value } = event.target
    setValues((current) => ({ ...current, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setResult(null)
    setSubmitting(true)

    try {
      const response = await fetch('/api/employer-access-requests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      })

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        const detail = data.detail
        throw new Error(
          typeof detail === 'string'
            ? detail
            : 'We could not submit your request. Please check the details and try again.'
        )
      }

      setResult(data)
      setValues(initialValues)
    } catch (submissionError) {
      setError(
        submissionError.message ||
        'Unable to submit your request. Please try again later.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="public-request">
      <header className="public-request__header">
        <a
          className="public-request__brand"
          href="/"
          aria-label="Talent Bridge BD home"
        >
          <img
            src={talentBridgeLogo}
            alt="Talent Bridge BD"
            className="public-request__logo"
          />
          <span>Talent Bridge BD</span>
        </a>
      </header>

      <section
        className="public-request__card"
        aria-label="Employer access request form"
      >
        <p className="public-request__eyebrow">EMPLOYER SERVICES</p>

        <h1>Request Employer Access</h1>

        <p className="public-request__intro">
          Tell us about your organization. Our team will review your request
          before any portal access is granted.
        </p>

        {result ? (
          <div
            className="public-request__result"
            role="status"
            aria-live="polite"
          >
            <h2>Request submitted</h2>

            <p>{result.message}</p>

            <p>
              Reference: <strong>{result.request_id}</strong>
            </p>

            <p>
              Your request is pending review. It does not create an account or
              grant portal permissions.
            </p>

            <button
              type="button"
              className="public-request__button"
              onClick={() => {
                setResult(null)
                setError('')
              }}
            >
              Submit another request
            </button>
          </div>
        ) : (
          <>
            <h2 className="public-request__section-title">
              Organization details
            </h2>

            <p className="public-request__section-intro">
              Please complete the required fields. The remaining details are optional.
            </p>

            {error && (
              <p className="public-request__error" role="alert">
                {error}
              </p>
            )}

            <form onSubmit={handleSubmit} className="employer-request-form">
              <div className="public-request__grid">
                <label className="public-request__field">
                  Company name *
                  <input name="company_name" value={values.company_name}
                    onChange={updateField} minLength={2} maxLength={200}
                    autoComplete="organization" required />
                </label>

                <label className="public-request__field">
                  Representative name *
                  <input name="representative_name" value={values.representative_name}
                    onChange={updateField} minLength={2} maxLength={200}
                    autoComplete="name" required />
                </label>

                <label className="public-request__field">
                  Business email *
                  <input name="email" type="email" value={values.email}
                    onChange={updateField} maxLength={320}
                    autoComplete="email" required />
                </label>

                <label className="public-request__field">
                  Phone
                  <input name="phone" type="tel" value={values.phone}
                    onChange={updateField} maxLength={50} autoComplete="tel" />
                </label>

                <label className="public-request__field">
                  Country
                  <input name="country" value={values.country}
                    onChange={updateField} maxLength={100}
                    autoComplete="country-name" />
                </label>

                <label className="public-request__field">
                  Industry
                  <input name="industry" value={values.industry}
                    onChange={updateField} maxLength={150} />
                </label>

                <label className="public-request__field public-request__field--full">
                  Requested roles or hiring needs
                  <textarea name="requested_roles" value={values.requested_roles}
                    onChange={updateField} maxLength={1000} rows={3}
                    placeholder="For example: Steel Fixers, Electricians, Welders" />
                </label>

                <label className="public-request__field public-request__field--full">
                  Additional requirements
                  <textarea name="requirements" value={values.requirements}
                    onChange={updateField} maxLength={10000} rows={4}
                    placeholder="Tell us about your organization and recruitment needs" />
                </label>
              </div>

              <button
                type="submit"
                className="public-request__button"
                disabled={submitting}
              >
                {submitting ? 'Submitting…' : 'Submit access request'}
              </button>
            </form>
          </>
        )}

        <p className="public-request__note">
          Employer requests are reviewed by the TBBD team. Submission does not
          create an account or grant access.
        </p>

        <a className="public-request__back" href="/">
          Back to workplace access
        </a>
      </section>

      <footer className="public-request__footer">
        Talent Bridge BD — Employer Access
      </footer>
    </main>
  )
}