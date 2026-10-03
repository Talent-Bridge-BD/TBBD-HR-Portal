import { useState } from 'react'
import PageHeader from '../components/PageHeader'

const notificationTypes = [
  {
    icon: '▤',
    title: 'Application Updates',
    description:
      'Stay informed when new applications are received or candidate application statuses change.',
  },
  {
    icon: '◷',
    title: 'Interview Notifications',
    description:
      'Receive updates about interview schedules, changes, completed interviews, and candidate outcomes.',
  },
  {
    icon: '✓',
    title: 'Hiring Updates',
    description:
      'Track important recruitment and hiring actions as candidates move through the hiring process.',
  },
  {
    icon: '🔔',
    title: 'Important Alerts',
    description:
      'Important actions, pending tasks, and time-sensitive employer information will be highlighted here.',
  },
]

export default function EmployerNotifications() {
  const [filter, setFilter] = useState('all')

  return (
    <section className="page-section">
      <PageHeader
        title="Notifications"
        subtitle="Stay informed about applications, interviews, hiring activity, and important recruitment updates."
      />

      <div className="employer-notifications-toolbar">
        <div className="employer-workspace-tabs" role="tablist" aria-label="Notification filters">
          <button
            type="button"
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
            role="tab"
            aria-selected={filter === 'all'}
          >
            All
          </button>

          <button
            type="button"
            className={filter === 'unread' ? 'active' : ''}
            onClick={() => setFilter('unread')}
            role="tab"
            aria-selected={filter === 'unread'}
          >
            Unread
          </button>
        </div>
      </div>

      <div className="dashboard-card employer-notifications-card">
        <div className="card-heading">
          <div>
            <span className="eyebrow">EMPLOYER ACTIVITY</span>
            <h2>Recent Notifications</h2>
          </div>
        </div>

        <div className="empty-state">
          <strong>
            {filter === 'unread'
              ? 'No unread notifications'
              : 'No notifications yet'}
          </strong>
          <span>
            {filter === 'unread'
              ? 'New employer recruitment alerts will appear here when available.'
              : 'Recruitment updates and important employer notifications will appear here when available.'}
          </span>
        </div>
      </div>

      <section className="dashboard-card">
        <div className="card-heading">
          <div>
            <span className="eyebrow">NOTIFICATION CENTER</span>
            <h2>Notification Types</h2>
          </div>
        </div>

        <div className="overview-grid">
          {notificationTypes.map((item) => (
            <div className="overview-item" key={item.title}>
              <span className="overview-icon">{item.icon}</span>
              <div>
                <strong>{item.title}</strong>
                <span>{item.description}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </section>
  )
}
