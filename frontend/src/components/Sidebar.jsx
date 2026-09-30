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
  ['Recruitment Trade Tests', '⚒'],
  ['Recruitment Medical', '✚'],
  ['Recruitment Visa Processing', '🛂'],
  ['Recruitment Ticketing', '✈'],
  ['Recruitment Onboarding', '✓'],
  ['Recruitment Deployment', '🚀'],
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

  const renderItem = ([label, icon, enabled = true]) => (
    <button
      key={label}
      className={`nav-item ${activePage === label ? 'active' : ''} ${!enabled ? 'disabled' : ''}`}
      onClick={() => {
        if (!enabled) return

        onNavigate(label)
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
        {/* WORKPLACE HUB */}
        <div className="nav-section">
          <span className="nav-section-title">WORKPLACE HUB</span>

          {workplaceNavigation
            .filter(([label]) => {
              // Administrators, HR Managers, and Candidates
              // only see Dashboard and My Profile here.
              if (
                isAdministrator ||
                isHRManager ||
                canAccessCandidatePortal
              ) {
                return ['Dashboard', 'My Profile'].includes(label)
              }

              return true
            })
            .map(([label, icon]) =>
              renderItem([label, icon, true])
            )}
        </div>

        {/* RECRUITMENT */}
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

            {/* PROCESSING */}
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
          </>
        )}

        {/* EMPLOYER PORTAL */}
        {canAccessEmployerPortal && (
          <div className="nav-section platform-nav-section">
            <span className="nav-section-title">EMPLOYER PORTAL</span>

            {employerNavigation.map(renderItem)}
          </div>
        )}

        {/* CANDIDATE PORTAL */}
        {canAccessCandidatePortal && (
          <div className="nav-section platform-nav-section">
            <span className="nav-section-title">CANDIDATE PORTAL</span>

            {candidateNavigation.map(renderItem)}
          </div>
        )}

        {/* TOOLS */}
        <div className="nav-section">
          <span className="nav-section-title">TOOLS</span>

          {toolNavigation
            .filter(([label]) => {
              // Candidate users only see Workplace Assistant.
              if (canAccessCandidatePortal) {
                return label === 'Workplace Assistant'
              }

              // Administrators and HR Managers also only see
              // Workplace Assistant.
              if (isAdministrator || isHRManager) {
                return label === 'Workplace Assistant'
              }

              return true
            })
            .map(renderItem)}
        </div>
      </nav>
    </aside>
  )
}