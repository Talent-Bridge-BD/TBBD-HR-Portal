import logo from '../assets/branding/talent-bridge-bd-logo.png'

export default function Header({ employee }) {
  return (
    <header className="top-header">
      <div className="brand">
        <img
          src={logo}
          alt="Talent Bridge BD"
        />
        <div className="brand-title">
          <strong>Workplace Hub</strong>
        </div>
      </div>

      <div className="header-actions">
        <button
          className="header-button"
          aria-label="Notifications"
        >
          🔔
        </button>

        <button className="header-button">
          Help
        </button>

        <div className="user-menu">
          <span className="avatar">
            {employee?.initials || 'E'}
          </span>

          <span>
            {employee?.displayName || 'Employee'}
          </span>
        </div>
      </div>
    </header>
  )
}
