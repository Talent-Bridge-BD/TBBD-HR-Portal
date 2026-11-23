import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import DashboardCard from '../components/DashboardCard'
import { authenticatedFetch } from '../utils/auth'

export default function WorkplaceNotifications() {
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
      <PageHeader
        title="Notifications"
        subtitle="Stay informed about workplace updates, HR information, and important announcements."
      />

      <DashboardCard title="Recent Notifications">
        {loading ? (
          <div className="empty-state">
            <strong>Loading notifications</strong>
            <span>Please wait while your workplace notifications are loaded.</span>
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
              Workplace updates and important notifications will appear here.
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
    </div>
  )
}