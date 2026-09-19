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

      <section className="dashboard-kpi-strip" aria-label="Executive recruitment summary">
        <article className="dashboard-kpi-strip-item">
          <span className="dashboard-kpi-strip-label">Active Candidates</span>
          <strong>{operations.candidates_pipeline}</strong>
          <small>Current recruitment pipeline</small>
        </article>

        <article className="dashboard-kpi-strip-item">
          <span className="dashboard-kpi-strip-label">Interviews</span>
          <strong>{pipeline.Interview}</strong>
          <small>Current interview stage</small>
        </article>

        <article className="dashboard-kpi-strip-item dashboard-kpi-strip-warning">
          <span className="dashboard-kpi-strip-label">Pending</span>
          <strong>{applications.pending}</strong>
          <small>Needs attention</small>
        </article>

        <article className="dashboard-kpi-strip-item">
          <span className="dashboard-kpi-strip-label">Success Rate</span>
          <strong>—</strong>
          <small>Awaiting verified metric</small>
        </article>
      </section>

      <PageHeader
        title="Recruitment Journey"
        subtitle="Track candidates across every recruitment stage."
      />

      <section className="recruitment-journey" aria-label="Recruitment journey">
        <div className="journey-row">
          {[
            ["Applications", pipeline.Applied, "journey-blue"],
            ["Screening", pipeline.Screening, "journey-cyan"],
            ["Interviews", pipeline.Interview, "journey-violet"],
            ["Trade Test", pipeline["Trade Test"], "journey-orange"],
          ].map(([label, value, accent], index) => (
            <div className="journey-stage" key={label}>
              <div className={`journey-stage-node ${accent}`}>
                <strong>{value}</strong>
              </div>
              <span>{label}</span>
              {index < 3 && <span className="journey-arrow" aria-hidden="true">→</span>}
            </div>
          ))}
        </div>

        <div className="journey-row journey-row-second">
          {[
            ["Medical", pipeline.Medical, "journey-green"],
            ["Visa", pipeline["Visa Processing"], "journey-amber"],
            ["Ticketing", pipeline.Ticketing, "journey-blue"],
            ["Onboarding", pipeline.Onboarding, "journey-cyan"],
            ["Deployment", pipeline.Deployment, "journey-emerald"],
          ].map(([label, value, accent], index) => (
            <div className="journey-stage" key={label}>
              <div className={`journey-stage-node ${accent}`}>
                <strong>{value}</strong>
              </div>
              <span>{label}</span>
              {index < 4 && <span className="journey-arrow" aria-hidden="true">→</span>}
            </div>
          ))}
        </div>
      </section>

      <PageHeader
        title="Recruitment Pipeline"
        subtitle="Real-time recruitment operations overview."
      />

      <div className="recruitment-pipeline-grid">
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
          detail="Currently screening"
        />
        <StatCard
          icon="◷"
          label="Interviews"
          value={pipeline.Interview}
          detail="Current interview stage"
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
        <StatCard
          icon="⚠"
          label="Pending"
          value={applications.pending}
          detail="Needs Immediate Attention"
        />
        <StatCard
          icon="✓"
          label="Approved"
          value={applications.approved}
          detail="Recently approved"
        />
        <StatCard
          icon="✅"
          label="Completed"
          value={applications.completed}
          detail="Successfully Processed"
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
        <section className="dashboard-operations">
          <DashboardCard title="Quick Actions">
            <div className="dashboard-action-list">
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


        </section>
      )}
      <section className="assistant-section">
        <WorkplaceAssistant />
      </section>
    </>
  )
}
