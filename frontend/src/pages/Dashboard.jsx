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

function LifecycleIcon({ type }) {
  const paths = {
    applications: (
      <>
        <rect x="5" y="3.5" width="14" height="17" rx="2" />
        <path d="M8.5 8h7M8.5 12h7M8.5 16h4" />
      </>
    ),
    screening: (
      <>
        <circle cx="10.5" cy="10.5" r="5.5" />
        <path d="m15 15 4.5 4.5" />
      </>
    ),
    interviews: (
      <>
        <rect x="4" y="5.5" width="16" height="14" rx="2" />
        <path d="M8 3.5v4M16 3.5v4M4 10h16" />
        <path d="M8 14h2M14 14h2M8 17h2" />
      </>
    ),
    tradeTests: (
      <>
        <path d="m14.5 5.5 4 4" />
        <path d="m13 7 4 4" />
        <path d="M4 20l2.5-7.5L14.5 5 19 9.5l-7.5 8z" />
        <path d="m7 17 3 3" />
      </>
    ),
    medical: (
      <>
        <path d="M12 20.5s-7-4.3-7-10.3A4.2 4.2 0 0 1 12 7a4.2 4.2 0 0 1 7 3.2c0 6-7 10.3-7 10.3Z" />
        <path d="M12 9v5M9.5 11.5h5" />
      </>
    ),
    visa: (
      <>
        <rect x="4" y="4" width="16" height="16" rx="2" />
        <path d="M8 8h8M8 12h8M8 16h4" />
      </>
    ),
    ticketing: (
      <>
        <path d="M4 7.5a2 2 0 0 0 0 4v1a2 2 0 0 0 0 4v2h16v-2a2 2 0 0 0 0-4v-1a2 2 0 0 0 0-4v-2H4Z" />
        <path d="M12 7v10" />
      </>
    ),
    onboarding: (
      <>
        <rect x="5" y="3.5" width="14" height="17" rx="2" />
        <path d="M9 3.5v3h6v-3M9 12h6M9 16h4" />
      </>
    ),
    deployment: (
      <>
        <path d="m12 3 3 5h-2v5h-2V8H9l3-5Z" />
        <path d="M7 13v4.5A2.5 2.5 0 0 0 9.5 20h5a2.5 2.5 0 0 0 2.5-2.5V13" />
        <path d="M8 16h8" />
      </>
    ),
  }

  return (
    <svg
      className="lifecycle-stage-icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[type]}
    </svg>
  )
}

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
      icon: 'applications',
      page: 'Recruitment Applications',
    },
    {
      label: 'Screening',
      value: pipeline.Screening,
      icon: 'screening',
      page: 'Recruitment Screening',
    },
    {
      label: 'Interviews',
      value: pipeline.Interview,
      icon: 'interviews',
      page: 'Recruitment Interviews',
    },
    {
      label: 'Trade Tests',
      value: pipeline["Trade Test"],
      icon: 'tradeTests',
      page: 'Recruitment Trade Tests',
    },
    {
      label: 'Medical',
      value: pipeline.Medical,
      icon: 'medical',
      page: 'Recruitment Medical',
    },
    {
      label: 'Visa',
      value: pipeline["Visa Processing"],
      icon: 'visa',
      page: 'Recruitment Visa Processing',
    },
    {
      label: 'Ticketing',
      value: pipeline.Ticketing,
      icon: 'ticketing',
      page: 'Recruitment Ticketing',
    },
    {
      label: 'Onboarding',
      value: pipeline.Onboarding,
      icon: 'onboarding',
      page: 'Recruitment Onboarding',
    },
    {
      label: 'Deployment',
      value: pipeline.Deployment,
      icon: 'deployment',
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
              {recruitmentJourney.map((stage) => (
                <button
                  className="lifecycle-stage"
                  type="button"
                  key={stage.label}
                  onClick={() => onNavigate(stage.page)}
                >
                  <span className="lifecycle-stage-number">
                    <LifecycleIcon type={stage.icon} />
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
