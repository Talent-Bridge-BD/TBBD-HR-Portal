import logo from '../assets/branding/talent-bridge-bd-logo.png'

export default function Header() {
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

      <div className="header-center">
        <div className="header-welcome">
          <span>Welcome to</span>
          <strong>Workplace Hub</strong>
        </div>
      </div>

      <div className="header-actions">
        <div className="header-user-info">
          <span>Employer Portal</span>
          <strong>Talent Bridge BD</strong>
        </div>

        <details className="user-menu">
          <summary className="user-menu-trigger">
            <span className="avatar">•</span>
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