const workplaceNavigation = [
  ['Dashboard', '\u{1F3E0}'],
  ['My Profile', '\u{1F464}'],
  ['Attendance', '\u{1F4C5}'],
  ['Leave', '\u{1F3D6}'],
  ['Schedule', '\u{1F5D3}'],
  ['Applications', '\u{1F4C4}'],
]

const recruitmentNavigation = [
  ['Recruitment Jobs', '\u{1F4BC}'],
  ['Recruitment Candidates', '\u{1F465}'],
  ['Recruitment Applications', '\u{1F4C4}'],
  ['Recruitment Screening', '\u{1F50D}'],
  ['Recruitment Interviews', '\u{1F91D}'],
  ['Recruitment Trade Tests', '\u{1F6E0}\u{FE0F}'],
  ['Recruitment Medical', '\u{1F3E5}'],
  ['Recruitment Visa Processing', '\u{1F6C2}'],
  ['Recruitment Ticketing', '\u{1F3AB}'],
  ['Recruitment Onboarding', '\u{2705}'],
  ['Recruitment Deployment', '\u{1F680}'],
]

const employerNavigation = [
  ['Employer Dashboard', '\u{1F3E0}'],
  ['Employer My Organization', '\u{1F3E2}'],
  ['Employer Job Requests', '\u{2795}'],
  ['Employer Job Openings', '\u{1F4BC}'],
  ['Employer Candidates', '\u{1F465}'],
  ['Employer Applications', '\u{1F4C4}'],
  ['Employer Interviews / Tests', '\u{1F91D}'],
  ['Employer Hiring', '\u{2705}'],
  ['Employer Notifications', '\u{1F514}'],
]

const candidateNavigation = [
  ['Candidate Available Jobs', '\u{1F4BC}'],
  ['Candidate My Applications', '\u{1F4C4}'],
  ['Candidate Interviews', '\u{1F91D}'],
  ['Candidate My Offers', '\u{1F4D1}'],
  ['Candidate Documents', '\u{1F4C1}'],
  ['Candidate Notifications', '\u{1F514}'],
]

const administrationNavigation = [
  ['Organization Management', '🏢', true, 'organizations'],
  ['User Management', '👥', true, 'users'],
  ['Roles & Permissions', '🔐', true, 'roles'],
  ['Notification System', '🔔', true, 'notifications'],
  ['System Configuration', '⚙️', true, 'settings'],
  ['System Activity', '📋', true, 'activity'],
  ['Administration Employers', '♙'],
  ['Employer Access Requests', '♙'],
  ['Candidate Approvals', '♙'],
]

const toolNavigation = [
  ['Workplace Assistant', '\u{2728}'],
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
