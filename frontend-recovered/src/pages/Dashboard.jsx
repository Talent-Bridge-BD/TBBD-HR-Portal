import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import DashboardCard from '../components/DashboardCard'
import QuickAction from '../components/QuickAction'
import WorkplaceAssistant from '../components/WorkplaceAssistant'
import banner from '../assets/images/tbbd-workplace-hub.jpg'

export default function Dashboard({ onNavigate, employee }) {
  const employeeName = employee?.displayName || 'Employee'

  return (
    <>
      <section className="workplace-banner">
        <img src={banner} alt="TBBD Workplace Hub" />
        <div className="workplace-banner-overlay">
          <div className="workplace-banner-content">
            <span className="banner-eyebrow">WELCOME TO YOUR WORKPLACE HUB</span>
            <h1>TBBD Workplace Hub</h1>
            <p>
              One connected platform for employees, HR services, workplace
              information, and everyday productivity.
            </p>
          </div>
        </div>
      </section>

      <PageHeader
        title={`Good morning, ${employeeName} \u{1F44B}`}
        subtitle="Welcome back to your Workplace Hub."
      />

      <div className="stats-grid">
        <StatCard
          icon="&#9675;"
          label="Attendance"
          value="95%"
          detail="This month &middot; On track"
        />
        <StatCard
          icon="&#9633;"
          label="Leave balance"
          value="12 days"
          detail="Annual leave remaining"
        />
        <StatCard
          icon="&#9632;"
          label="Today's schedule"
          value="09:00 &mdash; 17:30"
          detail="Office &middot; Dhaka"
        />
      </div>

      <section className="overview-section">
        <div className="section-heading">
          <div>
            <span className="section-eyebrow">TODAY</span>
            <h2>Today's Overview</h2>
          </div>
        </div>

        <div className="overview-grid">
          <div className="overview-item">
            <span className="overview-icon success">&#10003;</span>
            <div>
              <strong>Attendance</strong>
              <span>Checked in &middot; 09:02 AM</span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">&#9632;</span>
            <div>
              <strong>Schedule</strong>
              <span>Office &middot; 09:00&ndash;17:30</span>
            </div>
          </div>

          <div className="overview-item">
            <span className="overview-icon">&#9633;</span>
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
      </section>

      <div className="dashboard-grid">
        <DashboardCard title="Quick Actions">
          <div className="quick-actions">
            <QuickAction
              icon="&#43;"
              label="Apply Leave"
              onClick={() => onNavigate('Leave')}
            />
            <QuickAction
              icon="&#9675;"
              label="View Attendance"
              onClick={() => onNavigate('Attendance')}
            />
            <QuickAction
              icon="&#9632;"
              label="My Schedule"
              onClick={() => onNavigate('Schedule')}
            />
            <QuickAction
              icon="&#9673;"
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
            onClick={() => onNavigate('Applications')}
          >
            View all applications &rarr;
          </button>
        </DashboardCard>
      </div>

      <WorkplaceAssistant />
    </>
  )
}

