import './employer-access-request.css'

const form = document.querySelector('#employer-access-form')
const submitButton = document.querySelector('#submit-button')
const status = document.querySelector('#form-status')

form.addEventListener('submit', async (event) => {
  event.preventDefault()
  status.textContent = ''
  status.className = ''

  const formData = new FormData(form)
  const payload = Object.fromEntries(
    [...formData.entries()].map(([key, value]) => [key, value.trim()]),
  )

  submitButton.disabled = true
  submitButton.textContent = 'Submitting…'

  try {
    const response = await fetch('/api/public/employer-access-requests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    const result = await response.json().catch(() => ({}))

    if (!response.ok) {
      const detail = typeof result.detail === 'string'
        ? result.detail
        : 'Please check the information you entered and try again.'
      throw new Error(detail)
    }

    form.reset()
    status.textContent =
      result.message || 'Your employer access request was submitted for review.'
    status.className = 'public-request__status--success'
  } catch (error) {
    status.textContent =
      error instanceof TypeError
        ? 'We could not connect to the service. Please try again later.'
        : error.message || 'Your request could not be submitted. Please try again.'
    status.className = 'public-request__status--error'
  } finally {
    submitButton.disabled = false
    submitButton.textContent = 'Submit access request'
  }
})
