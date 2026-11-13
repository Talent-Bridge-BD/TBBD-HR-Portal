import logo from './assets/branding/talent-bridge-bd-logo.png'
import workplaceHubBanner from './assets/images/hubbanner.jpeg'
import { useEffect, useState } from 'react'

import Header from './components/Header'
import Sidebar from './components/Sidebar'

import Dashboard from './pages/Dashboard'
import MyProfile from './pages/MyProfile'
import Leave from './pages/Leave'
import Attendance from './pages/Attendance'
import Applications from './pages/Applications'
import Schedule from './pages/Schedule'
import WorkplaceAssistantPage from './pages/WorkplaceAssistantPage'
import PlatformPlaceholder from './pages/PlatformPlaceholder'
import AdministrationEmployers from './pages/AdministrationEmployers'
import EmployerAccessRequests from './pages/EmployerAccessRequests'
import UserManagement from './pages/UserManagement'
import OrganizationManagement from './pages/OrganizationManagement'
import RolesManagement from './pages/RolesManagement'
import SystemConfiguration from './pages/SystemConfiguration'
import SystemActivity from './pages/SystemActivity'
import AdministratorNotifications from './pages/AdministratorNotifications'
import WorkplaceNotifications from './pages/WorkplaceNotifications'
import EmployerDashboard from './pages/EmployerDashboard'
import EmployerOrganization from './pages/EmployerOrganization'
import EmployerJobRequests from './pages/EmployerJobRequests'
import EmployerJobOpenings from './pages/EmployerJobOpenings'
import EmployerApplications from './pages/EmployerApplications'
import Hiring from './pages/Hiring'
import CandidateDashboard from './pages/CandidateDashboard'
import CandidateMyProfile from './pages/CandidateMyProfile'
import CandidateApprovals from './pages/CandidateApprovals'
import CandidateMyApplications from './pages/CandidateMyApplications'
import CandidateAvailableJobs from './pages/CandidateAvailableJobs'
import Jobs from './pages/Jobs'
import RecruitmentCandidates from './pages/RecruitmentCandidates'
import RecruitmentApplications from './pages/RecruitmentApplications'
import RecruitmentScreening from './pages/RecruitmentScreening'
import RecruitmentInterviews from './pages/RecruitmentInterviews'
import RecruitmentTradeTests from './pages/RecruitmentTradeTests'
import EmployerInterviewsTests from './pages/EmployerInterviewsTests'
import RecruitmentMedical from './pages/RecruitmentMedical'
import RecruitmentVisaProcessing from './pages/RecruitmentVisaProcessing'
import RecruitmentTicketing from './pages/RecruitmentTicketing'
import RecruitmentDeployment from './pages/RecruitmentDeployment'
import RecruitmentOnboarding from './pages/RecruitmentOnboarding'
import CandidateInterviews from './pages/CandidateInterviews'
import CandidateDocuments from './pages/CandidateDocuments'
import CandidateNotifications from './pages/CandidateNotifications'
import CandidateOffers from './pages/CandidateOffers'
import EmployerNotifications from './pages/EmployerNotifications'
import CandidateHelpSupport from './pages/CandidateHelpSupport'
import { getCurrentUser, initializeMsal, signIn } from './utils/auth'
import { OrganizationProvider } from './context/OrganizationContext'
import OrganizationSelector from './components/OrganizationSelector'
import EmployerAccessRequest from './pages/EmployerAccessRequest'

const placeholderPages = {}

const STAFF_LOGIN_URL =
  '/.auth/login/aad?post_login_redirect_uri=%2F%3Fportal%3D1'

const CANDIDATE_LOGIN_URL =
  '/.auth/login/TBBDCandidateExternalID?post_login_redirect_uri=%2F%3FauthMode%3Dcandidate'

const CANDIDATE_REGISTRATION_URL =
  '/.auth/login/TBBDCandidateExternalID?prompt=create&post_login_redirect_uri=%2F%3FauthMode%3Dcandidate%26registration%3D1'

const PORTAL_ROLES = [
  'Administrator',
  'HR Manager',
  'Employer Manager',
  'Employer.Manager',
  'Candidate',
]

export default function App() {
  const searchParams = new URLSearchParams(window.location.search)

  const isEmployerAccessRequest =
    window.location.pathname === '/employer-access-request' ||
    searchParams.get('page') === 'employer-access-request'

  const isCandidateMode = searchParams.get('authMode') === 'candidate'

  const [activePage, setActivePage] = useState('Dashboard')
  const [auth, setAuth] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)
  const [authError, setAuthError] = useState('')

  useEffect(() => {
    let mounted = true

    Promise.resolve(
      import.meta.env.DEV ? initializeMsal() : undefined
    )
      .then(() => getCurrentUser())
      .then((data) => {
        if (!mounted) return

        setAuth(data)

        const roles = Array.isArray(data?.roles) ? data.roles : []

        if (roles.includes('Candidate')) {
          setActivePage('Candidate Dashboard')
        } else if (
          roles.includes('Employer Manager') ||
          roles.includes('Employer.Manager')
        ) {
          setActivePage('Employer Dashboard')
        } else {
          setActivePage('Dashboard')
        }
      })
      .catch((error) => {
        console.error('Failed to load current user:', error)

        if (mounted) {
          setAuthError(
            error?.message || 'Unable to verify your sign-in. Please try again.'
          )
        }
      })
      .finally(() => {
        if (mounted) {
          setAuthLoading(false)
        }
      })

    return () => {
      mounted = false
    }
  }, [])

  if (isEmployerAccessRequest) {
    return <EmployerAccessRequest />
  }

  if (authLoading) {
    return (
      <div className="app-shell">
        <main className="main-content">
          <p>Verifying your sign-in...</p>
        </main>
      </div>
    )
  }

  if (authError) {
    return (
      <div className="app-shell">
        <main className="main-content">
          <div className="empty-state" role="alert">
            <h2>Unable to verify your sign-in</h2>
            <p>{authError}</p>
            <button
              type="button"
              onClick={() => window.location.reload()}
            >
              Try Again
            </button>
          </div>
        </main>
      </div>
    )
  }

  if (!auth?.authenticated && !isCandidateMode) {
    const hubCards = [
      {
        id: 'candidate-access',
        title: 'Candidate Sign In',
        category: 'For Job Seekers',
        description: 'Sign in to access your candidate profile and recruitment journey.',
        cta: 'Candidate Sign In',
        icon: 'candidate',
        theme: 'blue',
        href: CANDIDATE_LOGIN_URL,
      },
      {
        id: 'registration-access',
        title: 'New Candidate Registration',
        category: 'New Candidates',
        description: 'Create your profile and begin your recruitment journey.',
        cta: 'Register Candidate',
        icon: 'plus',
        theme: 'green',
        href: CANDIDATE_REGISTRATION_URL,
      },
      {
        id: 'employer-access',
        title: 'Employer Access Request',
        category: 'For Employers',
        description: 'Request access to employer workforce services.',
        cta: 'Request Access',
        icon: 'briefcase',
        theme: 'purple',
        href: '/employer-access-request',
      },
      {
        id: 'staff-access',
        title: (
          <>
            <span className="staff-card-title-line">Staff & Administrator</span>
            <span className="staff-card-title-line">Sign In</span>
          </>
        ),
        category: 'Authorized Personnel',
        description: 'Sign in with your Microsoft work account.',
        cta: 'Sign in with Microsoft',
        icon: 'logo',
        theme: 'orange',
        href: STAFF_LOGIN_URL,
      },
    ]

    return (
      <div className="workplace-hub-shell">
        <header className="workplace-hub-header">
          <a className="workplace-hub-brand" href="/" aria-label="Talent Bridge BD home">
            <img src={logo} alt="Talent Bridge BD" />
            <span className="workplace-hub-brand-copy">
              <strong>TALENT BRIDGE BD</strong>
              <small>Connecting Talent • Building Tomorrow</small>
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
            <img
              className="workplace-hub-hero-image"
              src={workplaceHubBanner}
              alt=""
            />
            <div className="workplace-hub-hero-overlay">
              <h1 id="workplace-hub-title">Welcome to the TBBD Workplace Hub</h1>
              <h2>Talent, Employers and HR Operations<br />All in One Place</h2>
              <span className="workplace-hub-hero-accent" />
              <p>Secure Access. Seamless Experience.</p>
            </div>
          </section>

          <section className="workplace-hub-access" aria-label="Workplace access options">
            <div className="workplace-hub-grid">
              {hubCards.map((card) => (
                <a
                  key={card.id}
                  id={card.id}
                  href={card.href}
                  onClick={(event) => {
                    if (import.meta.env.DEV && card.id === 'staff-access') {
                      event.preventDefault()
                      signIn().catch((error) => {
                        console.error('Local Microsoft sign-in failed:', error)
                        setAuthError(
                          error?.message || 'Unable to start Microsoft sign-in.'
                        )
                      })
                    }
                  }}
                  className={`workplace-hub-card workplace-hub-card--${card.theme}`}
                >
                  <span className="workplace-hub-card-icon" aria-hidden="true">
                    {card.icon === 'candidate' && (
                      <svg viewBox="0 0 64 64" role="presentation">
                        <circle cx="32" cy="21" r="11" fill="currentColor" />
                        <path d="M12 55c0-12 8-19 20-19s20 7 20 19v2H12z" fill="currentColor" />
                      </svg>
                    )}
                    {card.icon === 'plus' && (
                      <svg viewBox="0 0 64 64" role="presentation">
                        <path d="M32 12v40M12 32h40" fill="none" stroke="currentColor" strokeWidth="9" strokeLinecap="round" />
                      </svg>
                    )}
                    {card.icon === 'briefcase' && (
                      <svg viewBox="0 0 64 64" role="presentation">
                        <rect x="9" y="22" width="46" height="31" rx="5" fill="none" stroke="currentColor" strokeWidth="5" />
                        <path d="M23 22v-7h18v7M9 34c13 8 33 8 46 0M28 34h8" fill="none" stroke="currentColor" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    )}
                    {card.icon === 'logo' && (
                      <svg viewBox="0 0 64 64" role="img" aria-label="Microsoft">
                        <rect x="4" y="4" width="26" height="26" fill="#F25022" />
                        <rect x="34" y="4" width="26" height="26" fill="#7FBA00" />
                        <rect x="4" y="34" width="26" height="26" fill="#00A4EF" />
                        <rect x="34" y="34" width="26" height="26" fill="#FFB900" />
                      </svg>
                    )}
                  </span>

                  <span className="workplace-hub-card-divider" />

                  <span className="workplace-hub-card-content">
                    <strong>{card.title}</strong>
                    <span className="workplace-hub-card-category">{card.category}</span>
                    <span className="workplace-hub-card-description">
                      {card.description}
                    </span>
                  </span>

                  <span className="workplace-hub-card-cta">
                    {card.cta} <span aria-hidden="true">→</span>
                  </span>
                </a>
              ))}
            </div>
          </section>

          <p className="workplace-hub-notice" id="about-tbbd">
            Access is granted based on assigned permissions.
          </p>
        </main>

        <footer className="workplace-hub-footer">
          © Talent Bridge BD. All Rights Reserved.
        </footer>
      </div>
    )
  }
  if (!auth?.authenticated && isCandidateMode) {
    return (
      <div className="app-shell">
        <main className="main-content">
          <div className="empty-state">
            <section
              className="candidate-landing"
              aria-label="Candidate portal access"
            >
              <header className="candidate-brand">
                <div className="candidate-brand-mark" aria-hidden="true">
                  TB
                </div>
                <div className="candidate-brand-copy">
                  <strong>TALENT BRIDGE BD</strong>
                  <span>Candidate Portal</span>
                </div>
              </header>

              <section className="candidate-access-card">
                <h1>Candidate Portal</h1>
                <p>
                  Sign in or continue to candidate registration.
                </p>

                <div className="candidate-unified-actions">
                  <a
                    className="candidate-action candidate-action-signin"
                    href={CANDIDATE_LOGIN_URL}
                  >
                    Candidate Sign In
                  </a>

                  <a
                    className="candidate-action candidate-action-register"
                    href={CANDIDATE_REGISTRATION_URL}
                  >
                    New Candidate Registration
                  </a>
                </div>

                <p>
                  <a href="/employer-access-request">
                    Employer Access Request
                  </a>
                </p>
              </section>

              <footer className="candidate-welcome-footer">
                <p>Talent Bridge BD — Secure candidate access</p>
              </footer>
            </section>
          </div>
        </main>
      </div>
    )
  }

  const roles = Array.isArray(auth?.roles) ? auth.roles : []

  const hasPortalRole = roles.some((role) => PORTAL_ROLES.includes(role))

  if (!hasPortalRole) {
    return (
      <div className="app-shell">
        <main className="main-content">
          <div className="empty-state">
            <strong>Access not assigned</strong>
            <p>
              Your account does not have a recognized TBBD Portal role.
              Please contact your administrator.
            </p>
          </div>
        </main>
      </div>
    )
  }

  const isCandidate = roles.includes('Candidate')

  const pages = {
    Dashboard: isCandidate ? (
      <CandidateDashboard onNavigate={setActivePage} />
    ) : (
      <Dashboard auth={auth} onNavigate={setActivePage} />
    ),

    'My Profile': isCandidate ? (
      <CandidateMyProfile />
    ) : (
      <MyProfile auth={auth} />
    ),

    Leave: <Leave />,
    Attendance: <Attendance />,
    Applications: <Applications />,
    Schedule: <Schedule />,
    'Workplace Assistant': <WorkplaceAssistantPage />,
    'Administration Employers': <AdministrationEmployers auth={auth} />,
    'Employer Access Requests': <EmployerAccessRequests />,
    'Candidate Approvals': <CandidateApprovals />,
    organizations: <OrganizationManagement onNavigate={setActivePage} />,
    users: <UserManagement auth={auth} />,
    roles: <RolesManagement />,
    notifications: <AdministratorNotifications />,
    'Notifications': <WorkplaceNotifications />,
    settings: <SystemConfiguration />,
    activity: <SystemActivity />,

    'Employer Dashboard': (
      <EmployerDashboard onNavigate={setActivePage} />
    ),
    'Employer My Organization': <EmployerOrganization />,
    'Employer Job Requests': <EmployerJobRequests auth={auth} />,
    'Employer Job Openings': <EmployerJobOpenings auth={auth} />,
        'Employer Applications': <EmployerApplications auth={auth} />,
    'Employer Candidates': <RecruitmentCandidates auth={auth} />,
    'Employer Interviews / Tests': <EmployerInterviewsTests auth={auth} />,
    'Employer Hiring': <Hiring auth={auth} />,
    'Employer Notifications': <EmployerNotifications />,

    'Candidate Dashboard': (
      <CandidateDashboard onNavigate={setActivePage} />
    ),
    'Candidate My Profile': <CandidateMyProfile />,
    'Candidate My Applications': <CandidateMyApplications />,
    'Candidate Available Jobs': <CandidateAvailableJobs />,
    'Candidate Interviews': <CandidateInterviews />,
    'Candidate Documents': <CandidateDocuments />,
    'Candidate My Offers': <CandidateOffers />,
    'Candidate Notifications': <CandidateNotifications />,
    'Candidate Help & Support': <CandidateHelpSupport />,

    'Recruitment Jobs': <Jobs auth={auth} />,
    'Recruitment Candidates': <RecruitmentCandidates auth={auth} />,
    'Recruitment Applications': <RecruitmentApplications auth={auth} />,
    'Recruitment Screening': <RecruitmentScreening auth={auth} />,
    'Recruitment Interviews': <RecruitmentInterviews auth={auth} />,
    'Recruitment Trade Tests': <RecruitmentTradeTests auth={auth} />,
    'Recruitment Medical': <RecruitmentMedical auth={auth} />,
    'Recruitment Visa Processing': <RecruitmentVisaProcessing auth={auth} />,
    'Recruitment Ticketing': <RecruitmentTicketing auth={auth} />,
    'Recruitment Deployment': <RecruitmentDeployment auth={auth} />,
    'Recruitment Onboarding': <RecruitmentOnboarding auth={auth} />,
  }

  Object.entries(placeholderPages).forEach(([page, config]) => {
    pages[page] = <PlatformPlaceholder {...config} />
  })

  return (
    <OrganizationProvider auth={auth}>
      <div className="app-shell">
        <Header auth={auth} />

        <div className="app-body">
          <Sidebar
            activePage={activePage}
            onNavigate={setActivePage}
            auth={auth}
          />

          <main className="main-content">
            <OrganizationSelector />
            {pages[activePage] || (
              <PlatformPlaceholder
                area="TBBD PLATFORM"
                title="Page Not Found"
                description="The requested platform area could not be found."
              />
            )}
          </main>
        </div>
      </div>
    </OrganizationProvider>
  )
}
