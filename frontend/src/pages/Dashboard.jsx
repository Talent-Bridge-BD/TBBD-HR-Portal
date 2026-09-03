import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import DashboardCard from '../components/DashboardCard'
import QuickAction from '../components/QuickAction'
import WorkplaceAssistant from '../components/WorkplaceAssistant'

export default function Dashboard({ onNavigate }) {
  return (
    <>
      <PageHeader
        title="Good morning, Employee"
        subtitle="Welcome back to your Workplace Hub."
      />

      <div className="stats-grid">
        <StatCard
          icon="◷"
          label="Attendance"
          value="95%"
          detail="Current period"
        />
        <StatCard
          icon="▣"
          label="Leave"
          value="12 days"
          detail="Available balance"
        />
        <StatCard
          icon="□"
          label="Schedule"
          value="Today"
          detail="View your schedule"
        />
      </div>

      <div className="dashboard-grid">
        <DashboardCard title="Quick Actions">
          <div className="quick-actions">
            <QuickAction
              icon="＋"
              label="Apply Leave"
              onClick={() => onNavigate('Leave')}
            />
            <QuickAction
              icon="◷"
              label="View Attendance"
              onClick={() => onNavigate('Attendance')}
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
              <strong>2</strong>
              <span>Pending</span>
            </div>
            <div>
              <strong>5</strong>
              <span>Approved</span>
            </div>
            <div>
              <strong>12</strong>
              <span>Completed</span>
            </div>
          </div>
        </DashboardCard>
      </div>

      <WorkplaceAssistant />
    </>
  )
}
