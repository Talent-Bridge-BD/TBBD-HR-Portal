import { useEffect, useState } from "react"
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import DashboardCard from '../components/DashboardCard'
import QuickAction from '../components/QuickAction'
import WorkplaceAssistant from '../components/WorkplaceAssistant'
import banner from '../assets/images/tbbd-workplace-hub.jpg'
import { getEmployeeDisplayName } from '../utils/employee'
import { authenticatedFetch } from '../utils/auth'
import { employeeDashboard } from '../data/employeeDashboard'

export default function Dashboard({ auth, onNavigate }) {
  const isAdministrator = auth?.roles?.includes('Administrator')
  const isHRManager = auth?.roles?.includes('HR Manager')
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

    authenticatedFetch('/api/employer/dashboard')
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
    applications,
    announcements,
  } = employeeDashboard

  const recruitmentJourney = [
    {
      label: 'Applications',
      value: pipeline.Applied,
      page: 'Recruitment Applications',
    },
    {
      label: 'Screening',
      value: pipeline.Screening,
      page: 'Recruitment Screening',
    },
    {
      label: 'Interviews',
      value: pipeline.Interview,
      page: 'Recruitment Interviews',
    },
    {
      label: 'Trade Tests',
      value: pipeline["Trade Test"],
      page: 'Recruitment Trade Tests',
    },
    {
      label: 'Medical',
      value: pipeline.Medical,
      page: 'Recruitment Medical',
    },
    {
      label: 'Visa',
      value: pipeline["Visa Processing"],
      page: 'Recruitment Visa Processing',
    },
    {
      label: 'Ticketing',
      value: pipeline.Ticketing,
      page: 'Recruitment Ticketing',
    },
    {
      label: 'Onboarding',
      value: pipeline.Onboarding,
      page: 'Recruitment Onboarding',
    },
    {
      label: 'Deployment',
      value: pipeline.Deployment,
      page: 'Recruitment Deployment',
    },
  ]

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
              Your connected recruitment and workforce workspace.
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
            ? 'Here is your recruitment and workforce operations overview.'
            : 'Welcome back to your Workplace Hub.'
        }
      />

      {isAdministrator || isHRManager ? (
        <>
          <div className="stats-grid admin-kpi-grid">
            <StatCard
              icon="◈"
              label="Active Candidates"
              value={operations.candidates_pipeline}
              detail="Candidates in active recruitment"
            />
            <StatCard
              icon="◉"
              label="Interviews"
              value={operations.interviews_upcoming}
              detail="Upcoming scheduled interviews"
            />
            <StatCard
              icon="◌"
              label="Pending"
              value={operations.new_applications}
              detail="Applications awaiting review"
            />
            <StatCard
              icon="✓"
              label="Completed"
              value={pipeline.Completed}
              detail="Completed recruitment stages"
            />
          </div>

          <section className="admin-dashboard-section">
            <PageHeader
              title="Recruitment Lifecycle"
              subtitle="Track candidates through every stage of the recruitment workflow."
            />

            <div className="recruitment-lifecycle">
              {recruitmentJourney.map((stage, index) => (
                <button
                  className="lifecycle-stage"
                  type="button"
                  key={stage.label}
                  onClick={() => onNavigate(stage.page)}
                >
                  <span className="lifecycle-stage-number">
                    {String(index + 1).padStart(2, '0')}
                  </span>

                  <span className="lifecycle-stage-main">
                    <strong>{stage.value}</strong>
                    <span>{stage.label}</span>
                  </span>

                  <span className="lifecycle-stage-arrow" aria-hidden="true">
                    →
                  </span>
                </button>
              ))}
            </div>
          </section>

          <section className="dashboard-two-column admin-dashboard-actions">
            <DashboardCard title="Quick Actions">
              <div className="quick-actions">
                <QuickAction
                  icon="+"
                  label="Create Job"
                  onClick={() => onNavigate('Recruitment Jobs')}
                />
                <QuickAction
                  icon="◈"
                  label="Add Candidate"
                  onClick={() => onNavigate('Recruitment Candidates')}
                />
                <QuickAction
                  icon="◌"
                  label="Review Applications"
                  onClick={() => onNavigate('Recruitment Applications')}
                />
                <QuickAction
                  icon="◷"
                  label="Screening"
                  onClick={() => onNavigate('Recruitment Screening')}
                />
                <QuickAction
                  icon="◉"
                  label="Schedule Interview"
                  onClick={() => onNavigate('Recruitment Interviews')}
                />
              </div>
            </DashboardCard>

            <DashboardCard
              title="Action Required"
              subtitle="Items that need your attention."
            >
              <div className="action-required-list">
                {pipeline.Applied > 0 ? (
                  <button
                    className="action-required-item"
                    type="button"
                    onClick={() => onNavigate('Recruitment Applications')}
                  >
                    <span className="action-required-icon">!</span>
                    <span>
                      <strong>{pipeline.Applied}</strong>
                      <small>Applications require review</small>
                    </span>
                    <span className="action-required-arrow">→</span>
                  </button>
                ) : null}

                {pipeline.Screening > 0 ? (
                  <button
                    className="action-required-item"
                    type="button"
                    onClick={() => onNavigate('Recruitment Screening')}
                  >
                    <span className="action-required-icon">!</span>
                    <span>
                      <strong>{pipeline.Screening}</strong>
                      <small>Candidates in screening</small>
                    </span>
                    <span className="action-required-arrow">→</span>
                  </button>
                ) : null}

                {pipeline.Interview > 0 ? (
                  <button
                    className="action-required-item"
                    type="button"
                    onClick={() => onNavigate('Recruitment Interviews')}
                  >
                    <span className="action-required-icon">!</span>
                    <span>
                      <strong>{pipeline.Interview}</strong>
                      <small>Interview-stage candidates</small>
                    </span>
                    <span className="action-required-arrow">→</span>
                  </button>
                ) : null}

                {pipeline.Applied === 0 &&
                pipeline.Screening === 0 &&
                pipeline.Interview === 0 ? (
                  <div className="action-required-empty">
                    No actions required.
                  </div>
                ) : null}
              </div>
            </DashboardCard>
          </section>
        </>
      ) : (
        <>
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
                  icon="◉"
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
        </>
      )}

      {isAdministrator || isHRManager ? (
        <section className="admin-dashboard-section admin-assistant-section">
          <WorkplaceAssistant />
        </section>
      ) : (
        <WorkplaceAssistant />
      )}
    </>
  )
}
