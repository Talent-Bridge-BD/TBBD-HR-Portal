const workplaceNavigation = [
  ['Dashboard', '⌂'],
  ['My Profile', '◉'],
  ['Attendance', '◷'],
  ['Leave', '▣'],
  ['Schedule', '□'],
  ['Applications', '▤'],
]

const recruitmentNavigation = [
  ['Recruitment Jobs', '▤'],
  ['Recruitment Candidates', '♙'],
  ['Recruitment Applications', '▤'],
  ['Recruitment Screening', '◌'],
  ['Recruitment Interviews', '◷'],
  ['Recruitment Offers', '◇'],
  ['Recruitment Onboarding', '✓'],
]

const employerNavigation = [
  ['Employer Dashboard', '⌂'],
  ['Employer Job Requests', '＋'],
  ['Employer Job Openings', '▤'],
  ['Employer Applications', '♙'],
  ['Employer Hiring', '✓'],
]

const candidateNavigation = [
  ['Candidate Dashboard', '⌂'],
  ['Candidate My Profile', '◉'],
  ['Candidate My Applications', '▤'],
  ['Candidate Available Jobs', '▤'],
  ['Candidate Interviews', '◷'],
  ['Candidate Documents', '□'],
  ['Candidate Notifications', '🔔'],
]

const toolNavigation = [
  ['Workplace Assistant', '✦'],
  ['Microsoft 365', '▦', false],
]

function hasAnyRole(auth, roles) {
  return roles.some((role) => auth?.roles?.includes(role))
}

export default function Sidebar({ activePage, onNavigate, auth }) {
  const canAccessRecruitment = hasAnyRole(auth, [
    'Employer Manager',
    'HR Manager',
    'Administrator',
  ])

  const canAccessEmployerPortal = hasAnyRole(auth, [
    'Employer Manager',
    'HR Manager',
    'Administrator',
  ])
  const canAccessCandidatePortal = hasAnyRole(auth, [
    'Candidate',
  ])

  const renderItem = ([label, icon, enabled = true]) => (
    <button
      key={label}
      className={`nav-item ${activePage === label ? 'active' : ''} ${!enabled ? 'disabled' : ''}`}
      onClick={() => enabled && onNavigate(label)}
      disabled={!enabled}
      title={!enabled ? `${label} — Coming Soon` : label}
    >
      <span className="nav-icon">{icon}</span>
      <span className="nav-label">
        {label
          .replace('Recruitment ', '')
          .replace('Employer ', '')}
      </span>
      {!enabled && <span className="nav-coming-soon">Soon</span>}
    </button>
  )

  return (
    <aside className="sidebar">
      <nav>
        <div className="nav-section">
          <span className="nav-section-title">WORKPLACE HUB</span>
          {workplaceNavigation.map(([label, icon]) =>
            renderItem([label, icon, true])
          )}
        </div>

        {canAccessRecruitment && (
          <div className="nav-section platform-nav-section">
            <span className="nav-section-title">RECRUITMENT</span>
            {recruitmentNavigation.map(renderItem)}
          </div>
        )}

        {canAccessEmployerPortal && (
          <div className="nav-section platform-nav-section">
            <span className="nav-section-title">EMPLOYER PORTAL</span>
            {employerNavigation.map(renderItem)}
          </div>
        )}
        {canAccessCandidatePortal && (
          <div className="nav-section platform-nav-section">
            <span className="nav-section-title">CANDIDATE PORTAL</span>
            {candidateNavigation.map(renderItem)}
          </div>
        )}

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
