import { useState } from 'react'
import RecruitmentInterviews from './RecruitmentInterviews'
import RecruitmentTradeTests from './RecruitmentTradeTests'

export default function EmployerInterviewsTests({ auth }) {
  const [activeTab, setActiveTab] = useState('interviews')

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Interviews / Tests</h1>
          <p>Schedule interviews and manage candidate trade tests through the recruitment process.</p>
        </div>
      </div>

      <div className="employer-workspace-tabs" role="tablist" aria-label="Interviews and Tests">
        <button
          type="button"
          className={activeTab === 'interviews' ? 'active' : ''}
          onClick={() => setActiveTab('interviews')}
          role="tab"
          aria-selected={activeTab === 'interviews'}
        >
          Interviews
        </button>

        <button
          type="button"
          className={activeTab === 'tests' ? 'active' : ''}
          onClick={() => setActiveTab('tests')}
          role="tab"
          aria-selected={activeTab === 'tests'}
        >
          Trade Tests
        </button>
      </div>

      {activeTab === 'interviews' ? (
        <RecruitmentInterviews auth={auth} />
      ) : (
        <RecruitmentTradeTests auth={auth} />
      )}
    </div>
  )
}
