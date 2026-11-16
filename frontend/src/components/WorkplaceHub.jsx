import workplaceHubBanner from '../assets/images/banner-hub.jpeg'

export default function WorkplaceHub({
  staffLoginUrl,
  candidateLoginUrl,
  candidateRegistrationUrl,
}) {
    const hubCards = [
      {
        id: 'candidate-access',
        title: 'Candidate Sign In',
        label: 'For Job Seekers',
        description: 'Sign in to access your candidate profile and recruitment journey.',
        cta: 'Candidate Sign In',
        href: candidateLoginUrl,
        icon: 'candidate',
        theme: 'blue',
      },
      {
        id: 'registration-access',
        title: 'New Candidate Registration',
        label: 'New Candidates',
        description: 'Create your recruitment profile and get started.',
        cta: 'Register as a Candidate',
        href: candidateRegistrationUrl,
        icon: 'register',
        theme: 'green',
      },
      {
        id: 'employer-access',
        title: 'Employer Access Request',
        label: 'For Employers',
        description: 'Request employer access and workforce services.',
        cta: 'Request Access',
        href: '/employer-access-request',
        icon: 'employer',
        theme: 'purple',
      },
      {
        id: 'staff-access',
        title: 'Staff & Administrator Sign In',
        label: 'Authorized Personnel',
        description: 'Microsoft work account sign in.',
        cta: 'Sign in with Microsoft',
        href: staffLoginUrl,
        icon: 'staff',
        theme: 'orange',
      },
    ]

    return (
      <div className="workplace-hub-shell">
        <header className="workplace-hub-header">
          <a className="workplace-hub-brand" href="/" aria-label="Talent Bridge BD home">
            <img src="/assets/talent-bridge-bd-logo.png" alt="Talent Bridge BD" />
            <span className="workplace-hub-brand-copy">
              <strong>TALENT BRIDGE BD</strong>
              <small>Workplace Hub</small>
            </span>
          </a>
          <nav className="workplace-hub-nav" aria-label="Main navigation">
            <a href="#candidate-access">Candidates</a>
            <a href="#employer-access">Employers</a>
            <a href="#about-tbbd">About TBBD</a>
          </nav>
        </header>

        <main className="workplace-hub-main">
          <section className="workplace-hub-hero" aria-labelledby="workplace-hub-title">
            <img className="workplace-hub-hero-image" src={workplaceHubBanner} alt="" />
            <div className="workplace-hub-hero-overlay">
              <h1 id="workplace-hub-title">Welcome to the TBBD Workplace Hub</h1>
              <h2>Discover Opportunities • Connect With the TBBD Ecosystem</h2>
              <span className="workplace-hub-hero-accent" />
              <p>Secure access for candidates, employers, HR operations and administrators</p>
            </div>
          </section>

          <section className="workplace-hub-access" aria-label="Workplace access options">
            <div className="workplace-hub-grid">
              {hubCards.map((card) => {
                const isSignInCard =
                  card.href === candidateLoginUrl || card.icon === 'staff'
                const isLocalDocker =
                  window.location.hostname === 'localhost' ||
                  window.location.hostname === '127.0.0.1'

                return (
                  <a
                    key={card.id}
                    id={card.id}
                    href={card.href}
                    onClick={(event) => {
                      if (isLocalDocker && isSignInCard) {
                        event.preventDefault()
                        window.alert(
                          'Azure sign-in is available on the deployed TBBD HR Portal. Local Docker does not provide Azure sign-in. No sign-in has occurred.'
                        )
                        return
                      }
                    }}
                    className={`workplace-hub-card workplace-hub-card--${card.theme}`}
                  >
                    <span className={`workplace-hub-card-icon workplace-hub-icon-${card.icon}`} aria-hidden="true">
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        {card.icon === 'candidate' && (
                          <>
                            <circle cx="12" cy="8" r="3.5" />
                            <path d="M5 20v-1.5a7 7 0 0 1 14 0V20" />
                            <path d="M8.5 13.5 12 16l3.5-2.5" />
                          </>
                        )}
                        {card.icon === 'register' && (
                          <>
                            <circle cx="10" cy="7" r="4" />
                            <path d="M3 21v-2a7 7 0 0 1 11.5-5.4" />
                            <path d="M19 8v6" />
                            <path d="M16 11h6" />
                          </>
                        )}
                        {card.icon === 'employer' && (
                          <>
                            <rect x="3" y="7" width="18" height="14" rx="2" />
                            <path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                            <path d="M3 12h18M10 12v2h4v-2" />
                          </>
                        )}
                        {card.icon === 'staff' && (
                          <>
                            <rect x="2" y="2" width="9" height="9" fill="#F25022" stroke="none" />
                            <rect x="13" y="2" width="9" height="9" fill="#7FBA00" stroke="none" />
                            <rect x="2" y="13" width="9" height="9" fill="#00A4EF" stroke="none" />
                            <rect x="13" y="13" width="9" height="9" fill="#FFB900" stroke="none" />
                          </>
                        )}
                      </svg>
                    </span>
                    <span className="workplace-hub-card-divider" />
                    <span className="workplace-hub-card-content">
                      <span className="workplace-hub-label">{card.label}</span>
                      <strong className="workplace-hub-card-title">{card.title}</strong>
                      <span className="workplace-hub-card-description">{card.description}</span>
                    </span>
                    <span className="workplace-hub-action">
                      {card.cta} <span aria-hidden="true">→</span>
                    </span>
                  </a>
                )
              })}
            </div>
          </section>

          <p className="workplace-hub-notice" id="about-tbbd">
            Access is subject to assigned permissions.
          </p>
        </main>

        <footer className="workplace-hub-footer">
          © Talent Bridge BD. All Rights Reserved.
        </footer>
      </div>
    )
  
}
