import PageHeader from '../components/PageHeader'
import WorkplaceAssistant from '../components/WorkplaceAssistant'
import { useState } from 'react'

const suggestedQuestions = [
  'What is the annual leave policy?',
  'How do I apply for leave?',
  'What are the attendance rules?',
  'Where can I find workplace policies?'
]

export default function WorkplaceAssistantPage() {
  const [selectedQuestion, setSelectedQuestion] = useState('')
  return (
    <>
      <PageHeader
        title="Workplace Assistant"
        subtitle="Get answers about HR policies, leave, attendance, benefits, and workplace information."
      />

      <section className="assistant-workspace">
        <div className="assistant-workspace-header">
          <div>
            <span className="assistant-workspace-eyebrow">TBBD WORKPLACE ASSISTANT</span>
            <h2>How can we help you today?</h2>
            <p>
              Ask a question about your workplace, or start with one of the
              suggested questions below.
            </p>
          </div>
          <div className="assistant-workspace-badge">✦ AI Assistant</div>
        </div>

        <div className="suggested-questions">
          {suggestedQuestions.map((question) => (
            <button
            key={question}
            type="button"
            className="suggested-question"
            onClick={() => setSelectedQuestion(question)}
          >
              <span>↗</span>
              {question}
            </button>
          ))}
        </div>

        <WorkplaceAssistant initialQuestion={selectedQuestion} />
      </section>
    </>
  )
}


