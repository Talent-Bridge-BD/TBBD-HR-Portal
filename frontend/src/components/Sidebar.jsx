const workplaceNavigation = [
  ['Dashboard', 'âŒ‚'],
  ['My Profile', 'â—‰'],
  ['Attendance', 'â—·'],
  ['Leave', 'â–£'],
  ['Schedule', 'â–¡'],
  ['Applications', 'â–¤'],
]

const recruitmentNavigation = [
  ['Recruitment Jobs', 'â–¤'],
  ['Recruitment Candidates', 'â™™'],
  ['Recruitment Applications', 'â–¤'],
  ['Recruitment Screening', 'â—Œ'],
  ['Recruitment Interviews', 'â—·'],
  ['Recruitment Trade Tests', 'âš’'],
  ['Recruitment Medical', 'âœš'],
  ['Recruitment Visa Processing', 'ðŸ›‚'],
  ['Recruitment Ticketing', 'âœˆ'],
  ['Recruitment Onboarding', 'âœ“'],
  ['Recruitment Deployment', 'ðŸš€'],
]

const employerNavigation = [
  ['Employer Dashboard', 'âŒ‚'],
  ['Employer My Organization', 'â—‰'],
  ['Employer Job Requests', 'ï¼‹'],
  ['Employer Job Openings', 'â–¤'],
  ['Employer Candidates', 'â™™'],
  ['Employer Applications', 'â–£'],
  ['Employer Interviews / Tests', 'â—·'],
  ['Employer Hiring', 'âœ“'],
  ['Employer Notifications', 'ðŸ””'],
]

const candidateNavigation = [
  ['Candidate Available Jobs', 'â–¤'],
  ['Candidate My Applications', 'â–¤'],
  ['Candidate Interviews', 'â—·'],
  ['Candidate My Offers', 'ðŸ“„'],
  ['Candidate Documents', 'â–¡'],
  ['Candidate Notifications', 'ðŸ””'],
]

const administrationNavigation = [
  ['Organization Management', '🏢', true, 'organizations'],
  ['User Management', '👥', true, 'users'],
  ['Roles & Permissions', '🔐', true, 'roles'],
  ['Notification System', '🔔', true, 'notifications'],
  ['System Configuration', '⚙️', true, 'settings'],
  ['System Activity', '📋', true, 'activity'],
  ['Administration Employers', '♙'],
  ['Candidate Approvals', '♙'],
]

const toolNavigation = [
  ['Workplace Assistant', 'âœ¦'],
]

function hasAnyRole(auth, roles) {
  return roles.some((role) => auth?.roles?.includes(role))
}

export default function Sidebar({ activePage, onNavigate, auth }) {
  const isAdministrator = auth?.roles?.includes('Administrator')
  const isHRManager = auth?.roles?.includes('HR Manager')

  const canAccessRecruitment = hasAnyRole(auth, [
    'HR Manager',
    'Administrator',
  ])

  const canAccessEmployerPortal = hasAnyRole(auth, [
    'Employer Manager',
    'HR Manager',
    'Administrator',
  ])
  const canAccessCandidatePortal =
    !isAdministrator &&
    !isHRManager &&
    hasAnyRole(auth, ['Candidate'])

  const renderItem = ([label, icon, enabled = true, pageKey = label]) => (
    <button
      key={label}
      className={`nav-item ${activePage === pageKey ? 'active' : ''} ${!enabled ? 'disabled' : ''}`}
      onClick={() => {
        if (!enabled) return
        onNavigate(pageKey)
      }}
      disabled={!enabled}
      title={!enabled ? `${label} — Coming Soon` : label}
    >
      <span className="nav-icon">{icon}</span>
      <span className="nav-label">
        {label
          .replace('Recruitment ', '')
          .replace('Employer ', '')
          .replace('Candidate ', '')}
      </span>
      {!enabled && <span className="nav-coming-soon">Soon</span>}
    </button>
  )

  return (
    <aside className="sidebar">
      <nav>
        <div className="nav-section">
          <span className="nav-section-title">WORKPLACE HUB</span>
          {workplaceNavigation
            .filter(([label]) => {
              if (canAccessCandidatePortal) {
                return ['Dashboard', 'My Profile'].includes(label)
              }

              return ['Dashboard', 'My Profile'].includes(label)
            })
            .map(([label, icon]) =>
              renderItem([label, icon, true])
            )}

        </div>

        {canAccessRecruitment && (
          <>
            <div className="nav-section platform-nav-section">
              <span className="nav-section-title">RECRUITMENT</span>
              {recruitmentNavigation
                .filter(([label]) =>
                  isAdministrator || isHRManager
                    ? [
                        'Recruitment Jobs',
                        'Recruitment Candidates',
                        'Recruitment Applications',
                        'Recruitment Screening',
                        'Recruitment Interviews',
                        'Recruitment Trade Tests',
                      ].includes(label)
                    : true
                )
                .map(renderItem)}
            </div>

            {(isAdministrator || isHRManager) && (
              <div className="nav-section platform-nav-section">
                <span className="nav-section-title">PROCESSING</span>
                {recruitmentNavigation
                  .filter(([label]) =>
                    [
                      'Recruitment Medical',
                      'Recruitment Visa Processing',
                      'Recruitment Ticketing',
                      'Recruitment Onboarding',
                      'Recruitment Deployment',
                    ].includes(label)
                  )
                  .map(renderItem)}
              </div>
            )}

            {isAdministrator && (
              <div className="nav-section platform-nav-section">
                <span className="nav-section-title">ADMINISTRATION</span>
                {administrationNavigation.map(renderItem)}
              </div>
            )}
          </>
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

        {!auth?.roles?.includes('Employer Manager') && (
          <div className="nav-section">
            <span className="nav-section-title">TOOLS</span>
            {toolNavigation.map(renderItem)}
          </div>
        )}

      </nav>
    </aside>
  )
}
