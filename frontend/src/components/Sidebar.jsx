const workplaceNavigation = [
  ['Dashboard', '⌂'],
  ['My Profile', '◉'],
  ['Attendance', '◷'],
  ['Leave', '▣'],
  ['Schedule', '□']
]

const serviceNavigation = [
  ['Applications', '▤', true],
  ['Documents', '▤', false],
  ['Payroll', '▥', false],
  ['Learning', '◇', false]
]

const toolNavigation = [
  ['Workplace Assistant', '✦', true],
  ['Microsoft 365', '▦', false]
]

export default function Sidebar({ activePage, onNavigate }) {
  const renderItem = ([label, icon, enabled = true]) => (
    <button
      key={label}
      className={`nav-item ${activePage === label ? 'active' : ''} ${!enabled ? 'disabled' : ''}`}
      onClick={() => enabled && onNavigate(label)}
      disabled={!enabled}
      title={!enabled ? `${label} — Coming Soon` : label}
    >
      <span className="nav-icon">{icon}</span>
      <span className="nav-label">{label}</span>
      {!enabled && <span className="nav-coming-soon">Soon</span>}
    </button>
  )

  return (
    <aside className="sidebar">
      <nav>
        <div className="nav-section">
          <span className="nav-section-title">WORKPLACE</span>
          {workplaceNavigation.map(([label, icon]) =>
            renderItem([label, icon, true])
          )}
        </div>

        <div className="nav-section">
          <span className="nav-section-title">SERVICES</span>
          {serviceNavigation.map(renderItem)}
        </div>

        <div className="nav-section">
          <span className="nav-section-title">TOOLS</span>
          {toolNavigation.map(renderItem)}
        </div>

        <div className="sidebar-support">
          <button className="nav-item support-item">
            <span className="nav-icon">?</span>
            <span className="nav-label">Help &amp; Support</span>
          </button>
        </div>
      </nav>
    </aside>
  )
}
