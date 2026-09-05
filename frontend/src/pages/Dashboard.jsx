import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import DashboardCard from '../components/DashboardCard'
import QuickAction from '../components/QuickAction'
import WorkplaceAssistant from '../components/WorkplaceAssistant'
import banner from '../assets/images/tbbd-workplace-hub.jpg'
import { getEmployeeDisplayName } from '../utils/employee'

export default function Dashboard({ onNavigate }) {
  const employeeName = getEmployeeDisplayName()

  return (
    <>
      <section className="workplace-banner">
        <img src={banner} alt="TBBD Workplace Hub" />
        <div className="workplace-banner-overlay">
          <div className="workplace-banner-content">
            <span className="banner-eyebrow">
              WELCOME TO YOUR WORKPLACE HUB
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
          value="95%"
          detail="This month · On track"
        />
        <StatCard
          icon="□"
          label="Leave balance"
          value="12 days"
          detail="Annual leave remaining"
        />
        <StatCard
          icon="■"
          label="Today's schedule"
          value="09:00 — 17:30"
          detail="Office · Dhaka"
        />
      </div>

      <section className="dashboard-two-column">
        <DashboardCard title="Today's Overview">
          <div className="overview-grid">
            <div className="overview-item">
              <span className="overview-icon success">✓</span>
              <div>
                <strong>Attendance</strong>
                <span>Checked in · 09:02 AM</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">■</span>
              <div>
                <strong>Schedule</strong>
                <span>Office · 09:00–17:30</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">□</span>
              <div>
                <strong>Leave</strong>
                <span>No leave scheduled</span>
              </div>
            </div>

            <div className="overview-item">
              <span className="overview-icon">!</span>
              <div>
                <strong>Tasks</strong>
                <span>2 pending actions</span>
              </div>
            </div>
          </div>
        </DashboardCard>

        <DashboardCard title="Notifications">
          <div className="notification-list">
            <button className="notification-item" type="button">
              <span className="notification-dot" />
              <span className="notification-content">
                <strong>Leave approved</strong>
                <small>Your recent leave request has been approved.</small>
              </span>
              <span className="notification-arrow">→</span>
            </button>

            <button className="notification-item" type="button">
              <span className="notification-dot" />
              <span className="notification-content">
                <strong>New HR policy</strong>
                <small>A new workplace policy is available to review.</small>
              </span>
              <span className="notification-arrow">→</span>
            </button>

            <button className="notification-item" type="button">
              <span className="notification-dot" />
              <span className="notification-content">
                <strong>Team announcement</strong>
                <small>There is a new announcement from your team.</small>
              </span>
              <span className="notification-arrow">→</span>
            </button>
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
              <strong>2</strong>
              <span>Pending</span>
              <small>Needs your attention</small>
            </div>

            <div>
              <strong>5</strong>
              <span>Approved</span>
              <small>Recently approved</small>
            </div>

            <div>
              <strong>12</strong>
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
          <article className="announcement-item">
            <span className="announcement-icon">!</span>
            <div>
              <strong>Important workplace updates</strong>
              <p>
                Stay informed about the latest workplace updates and HR
                information.
              </p>
            </div>
            <span className="announcement-arrow">→</span>
          </article>

          <article className="announcement-item">
            <span className="announcement-icon">◆</span>
            <div>
              <strong>Upcoming events</strong>
              <p>
                Check upcoming company events, meetings, and important dates.
              </p>
            </div>
            <span className="announcement-arrow">→</span>
          </article>

          <article className="announcement-item">
            <span className="announcement-icon">▣</span>
            <div>
              <strong>HR announcements</strong>
              <p>
                Review the latest HR announcements and employee information.
              </p>
            </div>
            <span className="announcement-arrow">→</span>
          </article>
        </div>
      </section>

      <WorkplaceAssistant />
    </>
  )
}
