import logo from '../assets/branding/talent-bridge-bd-logo.png'

export default function Header({ auth }) {
  const roles = auth?.roles || []
  const displayRole = roles.includes('Administrator')
    ? 'Administrator'
    : roles.includes('Employer Manager')
      ? 'Employer'
      : roles.includes('Candidate')
        ? 'Candidate'
        : 'Employee'

  const avatar = displayRole.charAt(0)

  const handleSignOut = () => {
    window.location.href = '/.auth/logout'
  }

  return (
    <header className="top-header">
      <div className="brand">
        <img
          src={logo}
          alt="Talent Bridge BD"
        />
      </div>

      <div className="header-actions">
        <button className="header-button" aria-label="Notifications">
          🔔
        </button>

        <button className="header-button">
          Help
        </button>

        <details className="user-menu">
          <summary className="user-menu-trigger">
            <span className="avatar">{avatar}</span>
            <span>{displayRole}</span>
          </summary>

          <div className="user-menu-dropdown">
            <button
              type="button"
              className="user-menu-signout"
              onClick={handleSignOut}
            >
              Sign out
            </button>
          </div>
        </details>
      </div>
    </header>
  )
}
