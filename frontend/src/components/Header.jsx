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

      <div className="header-actions">
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
