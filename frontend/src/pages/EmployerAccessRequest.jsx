import { useState } from 'react'

const initialValues = {
  contact_name: '',
  work_email: '',
  organization_name: '',
  website: '',
  business_details: '',
  access_reason: '',
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
    <div className="app-shell">
      <main className="main-content">
        <div className="empty-state">
          <section className="candidate-landing candidate-unified-landing">
            <header className="candidate-brand">
              <div className="candidate-brand-mark" aria-hidden="true">TB</div>
              <div className="candidate-brand-copy">
                <strong>TALENT BRIDGE BD</strong>
                <span>Secure Workplace Access</span>
              </div>
            </header>

            <div className="candidate-welcome">
              <span className="candidate-eyebrow">EMPLOYER ACCESS</span>
              <h1>Request Employer Access</h1>
              <p>
                Tell us about your organization and why you need access to the
                Talent Bridge BD workplace.
              </p>
            </div>

            <section
              className="candidate-access-card candidate-unified-card employer-request-card"
              aria-label="Employer access request form"
            >
              {result ? (
                <div role="status" aria-live="polite">
                  <h2>Request submitted</h2>
                  <p>{result.message}</p>
                  <p>
                    Reference: <strong>{result.request_id}</strong>
                  </p>
                  <p>
                    Your request is pending review. It does not create an
                    account or grant portal permissions.
                  </p>
                  <button
                    type="button"
                    className="candidate-action candidate-action-signin"
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
                  <h2>Organization details</h2>
                  <p>All fields are required for review.</p>

                  {error && (
                    <p className="employer-request-error" role="alert">
                      {error}
                    </p>
                  )}

                  <form onSubmit={handleSubmit} className="employer-request-form">
                    <label>
                      Contact name
                      <input
                        name="contact_name"
                        value={values.contact_name}
                        onChange={updateField}
                        minLength={2}
                        maxLength={160}
                        autoComplete="name"
                        required
                      />
                    </label>

                    <label>
                      Work email
                      <input
                        name="work_email"
                        type="email"
                        value={values.work_email}
                        onChange={updateField}
                        maxLength={320}
                        autoComplete="email"
                        required
                      />
                    </label>

                    <label>
                      Organization name
                      <input
                        name="organization_name"
                        value={values.organization_name}
                        onChange={updateField}
                        minLength={2}
                        maxLength={200}
                        autoComplete="organization"
                        required
                      />
                    </label>

                    <label>
                      Organization website
                      <input
                        name="website"
                        type="text"
                        value={values.website}
                        onChange={updateField}
                        placeholder="https://example.com"
                        maxLength={500}
                        required
                      />
                    </label>

                    <label>
                      Business details
                      <textarea
                        name="business_details"
                        value={values.business_details}
                        onChange={updateField}
                        minLength={10}
                        maxLength={2000}
                        rows={4}
                        required
                      />
                    </label>

                    <label>
                      Why do you need employer access?
                      <textarea
                        name="access_reason"
                        value={values.access_reason}
                        onChange={updateField}
                        minLength={10}
                        maxLength={2000}
                        rows={4}
                        required
                      />
                    </label>

                    <button
                      type="submit"
                      className="candidate-action candidate-action-signin"
                      disabled={submitting}
                    >
                      {submitting ? 'Submitting…' : 'Submit access request'}
                    </button>
                  </form>
                </>
              )}

              <p className="candidate-unified-note">
                Employer requests are reviewed by the TBBD team. Submission
                does not create an account or grant access.
              </p>

              <a className="employer-request-back" href="/">
                Back to workplace access
              </a>
            </section>
          </section>
        </div>
      </main>
    </div>
  )
}
