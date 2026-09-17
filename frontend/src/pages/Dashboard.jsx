import { useEffect, useState } from "react"
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import DashboardCard from '../components/DashboardCard'
import QuickAction from '../components/QuickAction'
import WorkplaceAssistant from '../components/WorkplaceAssistant'
import banner from '../assets/images/tbbd-workplace-hub.jpg'
import { getEmployeeDisplayName } from '../utils/employee'
import { employeeDashboard } from '../data/employeeDashboard'

export default function Dashboard({ auth, onNavigate }) {
  const isAdministrator = auth?.roles?.includes('Administrator')
  const isHRManager = auth?.roles?.includes('HR Manager')
  const isEmployee = !isAdministrator && !isHRManager
  const [operations, setOperations] = useState({
    active_jobs: 0,
    new_applications: 0,
    candidates_pipeline: 0,
    interviews_upcoming: 0,
  })

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
    if (!isAdministrator && !isHRManager) return

    fetch('/api/employer/dashboard')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Unable to load operations dashboard')
        }
        return response.json()
      })
      .then((data) => {
        setOperations(data.stats || {})
      })
      .catch((error) => console.error(error))
  }, [isAdministrator, isHRManager])

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
        title={
          isAdministrator || isHRManager
            ? `Welcome back, ${employeeName} 👋`
            : `Good morning, ${employeeName} 👋`
        }
        subtitle={
          isAdministrator || isHRManager
            ? 'Here is your Workplace Hub operations overview.'
            : 'Welcome back to your Workplace Hub.'
        }
      />

      {isAdministrator || isHRManager ? (
        <div className="stats-grid">
          <StatCard
            icon="▤"
            label="Active Jobs"
            value={operations.active_jobs}
            detail="Currently open"
          />
          <StatCard
            icon="◌"
            label="New Applications"
            value={operations.new_applications}
            detail="Awaiting review"
          />
          <StatCard
            icon="◎"
            label="Candidates in Pipeline"
            value={operations.candidates_pipeline}
            detail="Active applications"
          />
          <StatCard
            icon="◷"
            label="Upcoming Interviews"
            value={operations.interviews_upcoming}
            detail="Scheduled interviews"
          />
        </div>
      ) : (
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
      )}

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

      {isAdministrator || isHRManager ? (
        <section className="dashboard-two-column">
          <DashboardCard title="Quick Actions">
            <div className="quick-actions">
              <QuickAction
                icon="▤"
                label="Manage Jobs"
                onClick={() => onNavigate('Recruitment Jobs')}
              />
              <QuickAction
                icon="◎"
                label="Review Candidates"
                onClick={() => onNavigate('Recruitment Candidates')}
              />
              <QuickAction
                icon="◌"
                label="Review Applications"
                onClick={() => onNavigate('Recruitment Applications')}
              />
              <QuickAction
                icon="◷"
                label="Screen Candidates"
                onClick={() => onNavigate('Recruitment Screening')}
              />
              <QuickAction
                icon="◷"
                label="Schedule Interviews"
                onClick={() => onNavigate('Recruitment Interviews')}
              />
              <QuickAction
                icon="⚒"
                label="Trade Tests"
                onClick={() => onNavigate('Recruitment Trade Tests')}
              />
              <QuickAction
                icon="✚"
                label="Medical Processing"
                onClick={() => onNavigate('Recruitment Medical')}
              />
              <QuickAction
                icon="🛂"
                label="Visa Processing"
                onClick={() => onNavigate('Recruitment Visa Processing')}
              />
            </div>
          </DashboardCard>

          <DashboardCard title="Recruitment Operations">
            <div className="application-summary">
              <div>
                <strong>{pipeline.Applied}</strong>
                <span>Applications</span>
                <small>Total applications</small>
              </div>
              <div>
                <strong>{pipeline.Screening}</strong>
                <span>Screening</span>
                <small>Currently screening</small>
              </div>
              <div>
                <strong>{pipeline.Interview}</strong>
                <span>Interviews</span>
                <small>Current interview stage</small>
              </div>
            </div>
            <button
              className="card-link"
              type="button"
              onClick={() => onNavigate('Recruitment Applications')}
            >
              Review recruitment applications →
            </button>
          </DashboardCard>
        </section>
      ) : (
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
      )}
      {isAdministrator || isHRManager ? (
        <section className="dashboard-card announcements-card">
          <div className="card-heading">
            <div>
              <span className="section-eyebrow">WORKPLACE OPERATIONS</span>
              <h2>Recruitment Operations</h2>
            </div>
          </div>
          <div className="announcement-list">
            <article className="announcement-item">
              <span className="announcement-icon">▤</span>
              <div>
                <strong>Jobs & Applications</strong>
                <p>
                  Manage active recruitment jobs and review incoming candidate
                  applications.
                </p>
              </div>
              <button
                className="card-link"
                type="button"
                onClick={() => onNavigate('Recruitment Applications')}
              >
                Open →
              </button>
            </article>
            <article className="announcement-item">
              <span className="announcement-icon">◷</span>
              <div>
                <strong>Interviews & Assessments</strong>
                <p>
                  Review scheduled interviews and continue candidates through
                  assessment stages.
                </p>
              </div>
              <button
                className="card-link"
                type="button"
                onClick={() => onNavigate('Recruitment Interviews')}
              >
                Open →
              </button>
            </article>
            <article className="announcement-item">
              <span className="announcement-icon">🚀</span>
              <div>
                <strong>Deployment Operations</strong>
                <p>
                  Continue approved candidates through medical, visa,
                  ticketing, onboarding, and deployment workflows.
                </p>
              </div>
              <button
                className="card-link"
                type="button"
                onClick={() => onNavigate('Recruitment Deployment')}
              >
                Open →
              </button>
            </article>
          </div>
        </section>
      ) : (
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
      )}
      <WorkplaceAssistant />
    </>
  )
}
