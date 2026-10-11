import { useEffect, useState } from "react"

import { authenticatedFetch } from "../utils/auth"

import "./AdministratorNotifications.css"

export default function AdministratorNotifications() {
  const [templates, setTemplates] = useState([])
  const [deliveryLogs, setDeliveryLogs] = useState([])
  const [selectedId, setSelectedId] = useState("")
  const [subject, setSubject] = useState("")
  const [htmlBody, setHtmlBody] = useState("")
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")
  const [message, setMessage] = useState("")

  const selectedTemplate = templates.find((template) => String(template.id) === String(selectedId))

  async function loadTemplates(preferredId) {
    const response = await authenticatedFetch("/api/administrator/notifications/templates")
    if (!response.ok) throw new Error("Could not load notification templates.")
    const data = await response.json()
    setTemplates(data)
    const nextId = preferredId || selectedId || (data[0] ? String(data[0].id) : "")
    setSelectedId(nextId)
    const selected = data.find((template) => String(template.id) === String(nextId))
    setSubject(selected?.subject || "")
    setHtmlBody(selected?.html_body || "")
  }

  useEffect(() => {
    let active = true
    async function loadPage() {
      setLoading(true)
      try {
        const [templateResponse, logResponse] = await Promise.all([
          authenticatedFetch("/api/administrator/notifications/templates"),
          authenticatedFetch("/api/administrator/notifications/delivery-logs"),
        ])
        if (!templateResponse.ok || !logResponse.ok) throw new Error("Could not load notification management data. Check administrator access and try again.")
        const [templateData, logData] = await Promise.all([templateResponse.json(), logResponse.json()])
        if (!active) return
        setTemplates(templateData)
        setDeliveryLogs(logData)
        const firstId = templateData[0] ? String(templateData[0].id) : ""
        setSelectedId(firstId)
        setSubject(templateData[0]?.subject || "")
        setHtmlBody(templateData[0]?.html_body || "")
      } catch (err) {
        if (active) setError(err.message || "Unable to load notification data.")
      } finally {
        if (active) setLoading(false)
      }
    }
    loadPage()
    return () => { active = false }
  }, [])

  function chooseTemplate(id) {
    const template = templates.find((item) => String(item.id) === String(id))
    setSelectedId(id)
    setSubject(template?.subject || "")
    setHtmlBody(template?.html_body || "")
    setError("")
    setMessage("")
  }

  async function saveTemplate(event) {
    event.preventDefault()
    if (!selectedTemplate) return
    setSaving(true)
    setError("")
    setMessage("")
    try {
      const response = await authenticatedFetch(
        `/api/administrator/notifications/templates/${encodeURIComponent(selectedTemplate.id)}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ subject, html_body: htmlBody }),
        },
      )
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}))
        throw new Error(detail.detail || "Could not save this template.")
      }
      await loadTemplates(String(selectedTemplate.id))
      setMessage("Template saved successfully.")
    } catch (err) {
      setError(err.message || "Unable to save this template.")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="administrator-notifications">
      <h1>Notification Management</h1>
      <p>Manage notification templates and delivery monitoring.</p>

      {error && <p className="notification-feedback notification-error" role="alert">{error}</p>}
      {message && <p className="notification-feedback notification-success" role="status">{message}</p>}
      {loading ? (
        <p>Loading notification management data...</p>
      ) : (
        <>
          <section className="notification-editor-section">
            <h2>Edit Email Template</h2>
            {templates.length === 0 ? (
              <p>No notification templates are available.</p>
            ) : (
              <form className="notification-template-editor" onSubmit={saveTemplate}>
                <label htmlFor="notification-template-select">Template</label>
                <select id="notification-template-select" value={selectedId} onChange={(event) => chooseTemplate(event.target.value)}>
                  {templates.map((template) => (
                    <option key={template.id} value={String(template.id)}>
                      {template.name} ({template.event_type}){template.is_active ? "" : " — inactive"}
                    </option>
                  ))}
                </select>

                <label htmlFor="notification-template-subject">Email subject</label>
                <input id="notification-template-subject" value={subject} onChange={(event) => { setSubject(event.target.value); setMessage("") }} maxLength={500} required />

                <label htmlFor="notification-template-html">HTML email body</label>
                <textarea id="notification-template-html" value={htmlBody} onChange={(event) => { setHtmlBody(event.target.value); setMessage("") }} rows={12} maxLength={100000} spellCheck={false} />

                <p className="notification-editor-help">You can use placeholders such as {"{{candidate_name}}"}, {"{{interview_type}}"}, {"{{scheduled_start}}"}, {"{{scheduled_end}}"}, {"{{location_or_link}}"}, and {"{{interviewer_name}}"} where the event provides those values.</p>
                <button type="submit" disabled={saving || !subject.trim()}>
                  {saving ? "Saving..." : "Save changes"}
                </button>
              </form>
            )}
          </section>

          <section>
            <h2>Templates ({templates.length})</h2>
            {templates.map((template) => (
              <div key={template.id} className="notification-template-card">
                <strong>{template.name}</strong>
                <span>{template.event_type}</span>
                <p>{template.subject}</p>
                <span>{template.is_active ? "Active" : "Inactive"}</span>
                <button type="button" onClick={() => chooseTemplate(String(template.id))}>Edit template</button>
              </div>
            ))}
          </section>

          <section>
            <h2>Delivery Logs ({deliveryLogs.length})</h2>
            {deliveryLogs.length === 0 ? (
              <p>No delivery records available.</p>
            ) : (
              deliveryLogs.map((log) => (
                <div key={log.id}>{log.recipient} - {log.status}</div>
              ))
            )}
          </section>
        </>
      )}
    </div>
  )
}
