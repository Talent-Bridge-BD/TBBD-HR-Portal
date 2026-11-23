import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'
import { authenticatedFetch } from '../utils/auth'

export default function CandidateNotifications() {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadNotifications() {
      try {
        setLoading(true)
        setError('')

        const response = await authenticatedFetch('/api/notifications')

        if (!response.ok) {
          throw new Error(`Failed to load notifications: ${response.status}`)
        }

        const data = await response.json()

        if (!cancelled) {
          setNotifications(Array.isArray(data) ? data : [])
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || 'Unable to load notifications.')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadNotifications()

    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="candidate-portal-page">
      <>
        <PageHeader
          title="Notifications"
          subtitle="Stay informed about your applications, interviews, and recruitment updates."
        />

        <DashboardCard title="Recent Notifications">
          {loading ? (
            <div className="empty-state">
              <strong>Loading notifications</strong>
              <span>
                Please wait while your latest recruitment updates are loaded.
              </span>
            </div>
          ) : error ? (
            <div className="empty-state">
              <strong>Unable to load notifications</strong>
              <span>{error}</span>
            </div>
          ) : notifications.length === 0 ? (
            <div className="empty-state">
              <strong>No notifications</strong>
              <span>
                Recruitment updates and important candidate notifications will appear here.
              </span>
            </div>
          ) : (
            <div className="notifications-list">
              {notifications.map((notification) => (
                <article
                  className={`notification-item ${
                    notification.is_read ? 'read' : 'unread'
                  }`}
                  key={notification.id}
                >
                  <div className="notification-item-content">
                    <strong>{notification.title}</strong>
                    <span>{notification.message}</span>
                  </div>
                </article>
              ))}
            </div>
          )}
        </DashboardCard>

        <section className="dashboard-card">
          <div className="card-heading">
            <h2>Notification Types</h2>
          </div>

          <div className="overview-grid">
            <div className="overview-item">
              <span className="overview-icon">▤</span>
              <div>
                <strong>Application Updates</strong>
                <span>
                  Receive updates when the status of an application changes.
                </span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">◷</span>
              <div>
                <strong>Interview Notifications</strong>
                <span>
                  Stay informed about interview schedules and changes.
                </span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">✓</span>
              <div>
                <strong>Recruitment Updates</strong>
                <span>
                  Receive important messages related to your recruitment journey.
                </span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">🔔</span>
              <div>
                <strong>Important Alerts</strong>
                <span>
                  Important actions and time-sensitive candidate information will be highlighted here.
                </span>
              </div>
            </div>
          </div>
        </section>
      </>
    </div>
  )
}