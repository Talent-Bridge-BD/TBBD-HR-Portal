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

            <div className="recruitment-lifecycle" aria-label="Recruitment lifecycle">
              <div className="lifecycle-grid">
                {recruitmentJourney.map((stage) => {
                  const iconMap = {
                    Applications: {
                      color: "#0067B8",
                      bg: "#EFF6FF",
                      path: "M6 3.75A1.75 1.75 0 0 1 7.75 2h6.5A1.75 1.75 0 0 1 16 3.75v16.5A1.75 1.75 0 0 1 14.25 22h-6.5A1.75 1.75 0 0 1 6 20.25V3.75ZM9 5.25v2h4v-2H9Zm0 5v1.5h6v-1.5H9Zm0 3.5v1.5h6v-1.5H9Zm0 3.5v1.5h4v-1.5H9Z",
                    },
                    Screening: {
                      color: "#0891B2",
                      bg: "#ECFEFF",
                      path: "m20.25 20.25-4.35-4.35a7 7 0 1 0-1.06 1.06l4.35 4.35 1.06-1.06ZM10.5 16a5.5 5.5 0 1 1 0-11 5.5 5.5 0 0 1 0 11Z",
                    },
                    Interviews: {
                      color: "#7C3AED",
                      bg: "#F5F3FF",
                      path: "M8 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm8-1a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM2.5 20.5A6.5 6.5 0 0 1 9 14h1a6.5 6.5 0 0 1 6.5 6.5H2.5Zm13-4.75a5.6 5.6 0 0 1 3.95 4.75h2.05A5.99 5.99 0 0 0 16 14.8a5.8 5.8 0 0 0-.5-.05Z",
                    },
                    "Trade Tests": {
                      color: "#EA580C",
                      bg: "#FFF7ED",
                      path: "M7 3h10a2 2 0 0 1 2 2v14H5V5a2 2 0 0 1 2-2Zm2 3v2h6V6H9Zm0 4v1.5h6V10H9Zm0 3.5V15h4v-1.5H9Z",
                    },
                    Medical: {
                      color: "#16A34A",
                      bg: "#F0FDF4",
                      path: "M12 21s-7-4.35-7-10.1A4.1 4.1 0 0 1 9.1 7c1.2 0 2.3.53 2.9 1.43A3.48 3.48 0 0 1 14.9 7 4.1 4.1 0 0 1 19 10.9C19 16.65 12 21 12 21Zm-1.25-5.25h2.5v-2.5h2.5v-2.5h-2.5v-2.5h-2.5v2.5h-2.5v2.5h2.5v2.5Z",
                    },
                    Visa: {
                      color: "#D97706",
                      bg: "#FFFBEB",
                      path: "M5 3h10a2 2 0 0 1 2 2v2.5l2 2V21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm0 2v14h12v-8h-2a2 2 0 0 1-2-2V5H5Zm10 0v4h2l-2-2V5ZM7 13h8v1.5H7V13Zm0 3h6v1.5H7V16Z",
                    },
                    Ticketing: {
                      color: "#4F46E5",
                      bg: "#EEF2FF",
                      path: "M4 6a2 2 0 0 1 2-2h12v4a2 2 0 0 0 0 4v4H6a2 2 0 0 1-2-2V6Zm3 0v2h5V6H7Zm0 5v2h7v-2H7Zm0 4v2h4v-2H7Z",
                    },
                    Onboarding: {
                      color: "#0D9488",
                      bg: "#F0FDFA",
                      path: "M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm-6 9a6 6 0 0 1 12 0H3Zm14-7v-2h-2v2h-2v2h2v2h2v-2h2v-2h-2Z",
                    },
                    Deployment: {
                      color: "#059669",
                      bg: "#ECFDF5",
                      path: "M6 4h12a2 2 0 0 1 2 2v12H4V6a2 2 0 0 1 2-2Zm3 3v2h6V7H9Zm-2 5v4h10v-4H7Zm2 1.5h6v1H9v-1Z",
                    },
                  };

                  const icon = iconMap[stage.label] || {
                    color: "#0067B8",
                    bg: "#EFF6FF",
                    path: "M12 3 4 7v5c0 5 3.5 8.5 8 10 4.5-1.5 8-5 8-10V7l-8-4Z",
                  };

                  return (
                    <button
                      className="lifecycle-stage"
                      key={stage.label}
                      type="button"
                      onClick={() => onNavigate(stage.page)}
                    >
                      <span
                        className="lifecycle-stage-icon"
                        style={{
                          color: icon.color,
                          backgroundColor: icon.bg,
                        }}
                        aria-hidden="true"
                      >
                        <svg
                          viewBox="0 0 24 24"
                          width="20"
                          height="20"
                          fill="currentColor"
                        >
                          <path d={icon.path} />
                        </svg>
                      </span>

                      <span className="lifecycle-stage-label">
                        {stage.label}
                      </span>

                      <strong className="lifecycle-stage-count">
                        {stage.value}
                      </strong>
                    </button>
                  );
                })}
              </div>
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

            <DashboardCard title="Action Required">
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

      <WorkplaceAssistant />
    </>
  )
}
