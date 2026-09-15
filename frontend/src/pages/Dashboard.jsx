import { useEffect, useState } from "react"
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import DashboardCard from '../components/DashboardCard'
import QuickAction from '../components/QuickAction'
import WorkplaceAssistant from '../components/WorkplaceAssistant'
import banner from '../assets/images/tbbd-workplace-hub.jpg'
import { getEmployeeDisplayName } from '../utils/employee'
import { employeeDashboard } from '../data/employeeDashboard'

export default function Dashboard({ onNavigate }) {
  const [pipeline, setPipeline] = useState({
    Applied: 0,
    Screening: 0,
    Interview: 0,
    "Trade Test": 0,
    Medical: 0,
    "Visa Processing": 0,
    Ticketing: 0,
    Onboarding: 0,
    Deployment: 0,
    Completed: 0,
  })

  useEffect(() => {
    fetch('/api/recruitment/pipeline')
      .then((response) => response.json())
      .then((data) => setPipeline(data))
      .catch((error) => console.error(error))
  }, [])

  const employeeName =
    employeeDashboard.employee.name || getEmployeeDisplayName()

  const {
    attendance,
    leave,
    schedule,
    tasks,
    notifications,
    applications,
    announcements,
  } = employeeDashboard

  return (
    <>
      <section className="workplace-banner">
        <img src={banner} alt="TBBD Workplace Hub" />
        <div className="workplace-banner-overlay">
          <div className="workplace-banner-content">
            <span className="banner-eyebrow">
              WELCOME TO
            </span>
            <h1>TBBD Workplace Hub</h1>
            <p>
              One connected platform for employees, HR services, workplace
              information, and everyday productivity.
            </p>
          </div>
        </div>
      </section>

      <PageHeader
        title={`Good morning, ${employeeName} 👋`}
        subtitle="Welcome back to your Workplace Hub."
      />

      <div className="stats-grid">
        <StatCard
          icon="○"
          label="Attendance"
          value={`${attendance.percentage}%`}
          detail={`This month · ${attendance.status}`}
        />

        <StatCard
          icon="□"
          label="Leave balance"
          value={`${leave.balance} ${leave.unit}`}
          detail={leave.detail}
        />

        <StatCard
          icon="■"
          label="Today's schedule"
          value={`${schedule.start} — ${schedule.end}`}
          detail={schedule.location}
        />
      </div>

      <PageHeader
        title="Recruitment Pipeline"
        subtitle="Real-time recruitment operations overview."
      />

      <div className="stats-grid">
        <StatCard
          icon="▤"
          label="Applications"
          value={pipeline.Applied}
          detail="Total applications"
        />

        <StatCard
          icon="◌"
          label="Screening"
          value={pipeline.Screening}
          detail="Candidates in screening"
        />

        <StatCard
          icon="◷"
          label="Interviews"
          value={pipeline.Interview}
          detail="Interviews scheduled"
        />

        <StatCard
          icon="⚒"
          label="Trade Tests"
          value={pipeline["Trade Test"]}
          detail="Pending assessments"
        />

        <StatCard
          icon="✚"
          label="Medical"
          value={pipeline.Medical}
          detail="Medical processing"
        />

        <StatCard
          icon="🛂"
          label="Visa"
          value={pipeline["Visa Processing"]}
          detail="Visa processing"
        />

        <StatCard
          icon="✈"
          label="Ticketing"
          value={pipeline.Ticketing}
          detail="Tickets issued"
        />

        <StatCard
          icon="✓"
          label="Onboarding"
          value={pipeline.Onboarding}
          detail="Preparing deployment"
        />

        <StatCard
          icon="🚀"
          label="Deployment"
          value={pipeline.Deployment}
          detail="Successfully deployed"
        />
      </div>

      <section className="dashboard-two-column">
        <DashboardCard title="Today's Overview">
          <div className="overview-grid">
            <div className="overview-item">
              <span className="overview-icon success">✓</span>
              <div>
                <strong>Attendance</strong>
                <span>
                  {attendance.checkedIn
                    ? `Checked in · ${attendance.checkInTime}`
                    : 'Not checked in'}
                </span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">■</span>
              <div>
                <strong>Schedule</strong>
                <span>
                  {schedule.location} · {schedule.start}–{schedule.end}
                </span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">□</span>
              <div>
                <strong>Leave</strong>
                <span>
                  {leave.scheduled
                    ? 'Leave scheduled'
                    : 'No leave scheduled'}
                </span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">!</span>
              <div>
                <strong>Tasks</strong>
                <span>{tasks.pending} pending actions</span>
              </div>
            </div>
          </div>
        </DashboardCard>

        <DashboardCard title="Notifications">
          <div className="notification-list">
            {notifications.map((notification) => (
              <button
                className="notification-item"
                type="button"
                key={notification.id}
              >
                <span className="notification-dot" />
                <span className="notification-content">
                  <strong>{notification.title}</strong>
                  <small>{notification.message}</small>
                </span>
                <span className="notification-arrow">→</span>
              </button>
            ))}
          </div>
        </DashboardCard>
      </section>

      <section className="dashboard-two-column">
        <DashboardCard title="Quick Actions">
          <div className="quick-actions">
            <QuickAction
              icon="+"
              label="Apply Leave"
              onClick={() => onNavigate('Leave')}
            />

            <QuickAction
              icon="○"
              label="View Attendance"
              onClick={() => onNavigate('Attendance')}
            />

            <QuickAction
              icon="■"
              label="My Schedule"
              onClick={() => onNavigate('Schedule')}
            />

            <QuickAction
              icon="◎"
              label="My Profile"
              onClick={() => onNavigate('My Profile')}
            />
          </div>
        </DashboardCard>

        <DashboardCard title="My Applications">
          <div className="application-summary">
            <div>
              <strong>{applications.pending}</strong>
              <span>Pending</span>
              <small>Needs your attention</small>
            </div>

            <div>
              <strong>{applications.approved}</strong>
              <span>Approved</span>
              <small>Recently approved</small>
            </div>

            <div>
              <strong>{applications.completed}</strong>
              <span>Completed</span>
              <small>All time</small>
            </div>
          </div>

          <button
            className="card-link"
            type="button"
            onClick={() => onNavigate('Applications')}
          >
            View all applications →
          </button>
        </DashboardCard>
      </section>

      <section className="dashboard-card announcements-card">
        <div className="card-heading">
          <div>
            <span className="section-eyebrow">COMPANY NEWS</span>
            <h2>Company Announcements</h2>
          </div>
        </div>

        <div className="announcement-list">
          {announcements.map((announcement, index) => (
            <article className="announcement-item" key={announcement.id}>
              <span className="announcement-icon">
                {['!', '◆', '▣'][index % 3]}
              </span>

              <div>
                <strong>{announcement.title}</strong>
                <p>{announcement.message}</p>
              </div>

              <span className="announcement-arrow">→</span>
            </article>
          ))}
        </div>
      </section>

      <WorkplaceAssistant />
    </>
  )
}
