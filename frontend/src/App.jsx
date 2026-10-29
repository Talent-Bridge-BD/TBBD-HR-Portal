import logo from './assets/branding/talent-bridge-bd-logo.png'
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
import UserManagement from './pages/UserManagement'
import OrganizationManagement from './pages/OrganizationManagement'
import RolesManagement from './pages/RolesManagement'
import SystemConfiguration from './pages/SystemConfiguration'
import SystemActivity from './pages/SystemActivity'
import NotificationSettings from './pages/NotificationSettings'
import AdministratorNotifications from './pages/AdministratorNotifications'
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
import { getCurrentUser } from './utils/auth'
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

    getCurrentUser()
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
        title: 'Candidate Sign In',
        icon: '♙',
        description: 'Sign in to access your candidate profile and recruitment journey.',
        href: CANDIDATE_LOGIN_URL,
      },
      {
        title: 'New Candidate Registration',
        icon: '✚',
        description: 'Start your candidate registration and create your recruitment profile.',
        href: CANDIDATE_REGISTRATION_URL,
      },
      {
        title: 'Employer Access Request',
        icon: '▦',
        description: 'Request employer access for review by the portal team. Approval is required.',
        href: '/employer-access-request',
      },
      {
        title: 'Administrator / Staff Sign In',
        icon: '◇',
        description: 'Sign in with your Microsoft work account. Your assigned role determines your access.',
        href: STAFF_LOGIN_URL,
      },
    ]

    return (
      <div className="app-shell workplace-hub-shell">
        <main className="main-content workplace-hub-main">
          <section aria-labelledby="workplace-hub-title" className="workplace-hub-panel">
            <div className="workplace-hub-accent" />
            <div className="workplace-hub-content">
              <header className="workplace-hub-heading">
                <img src={logo} alt="Talent Bridge BD" className="workplace-hub-logo" />
                <p
                  style={{
                    margin: '0 0 10px',
                    color: '#0067B8',
                    fontSize: '12px',
                    fontWeight: 700,
                    letterSpacing: '1.8px',
                  }}
                >
                  TALENT BRIDGE BD
                </p>
                <h1
                  id="workplace-hub-title"
                  style={{
                    margin: '0 0 12px',
                    color: '#0F172A',
                    fontSize: 'clamp(25px, 4vw, 34px)',
                    lineHeight: 1.25,
                  }}
                >
                  Workplace Hub
                </h1>
                <p style={{ margin: 0, color: '#475569', lineHeight: 1.7 }}>
                  Choose the portal that matches your access needs. Access is
                  determined by your assigned role and approval status.
                </p>
              </header>

              <div
                className="workplace-hub-grid"
              >
                {hubCards.map((card) => (
                  <a
                    key={card.title}
                    href={card.href}
                    className="workplace-hub-card"
                  >
                    <span
                      aria-hidden="true"
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '52px',
                        height: '52px',
                        flexShrink: 0,
                        borderRadius: '16px',
                        background: '#EAF4FC',
                        color: '#0067B8',
                        fontSize: '27px',
                        fontWeight: 700,
                      }}
                    >
                      {card.icon}
                    </span>
                    <span
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '10px',
                        width: '100%',
                        textAlign: 'center',
                      }}
                    >
                      <strong
                        style={{
                          display: 'block',
                          marginBottom: '9px',
                          color: '#0067B8',
                          fontSize: '17px',
                        }}
                      >
                        {card.title}
                      </strong>
                      <span style={{ color: '#475569', fontSize: '14px', lineHeight: 1.65 }}>
                        {card.description}
                      </span>
                    </span>
                    <span style={{ color: '#0067B8', fontSize: '14px', fontWeight: 700 }}>
                      Continue →
                    </span>
                  </a>
                ))}
              </div>

              <p
                style={{
                  margin: '24px 0 0',
                  color: '#64748B',
                  fontSize: '12px',
                  lineHeight: 1.6,
                  textAlign: 'center',
                }}
              >
                Signing in does not automatically grant a role or employer access.
              </p>
            </div>
          </section>
        </main>
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
    'Candidate Approvals': <CandidateApprovals />,
    organizations: <OrganizationManagement onNavigate={setActivePage} />,
    users: <UserManagement auth={auth} />,
    roles: <RolesManagement />,
    notifications: <AdministratorNotifications />,
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
