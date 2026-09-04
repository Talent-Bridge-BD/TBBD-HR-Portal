import { useEffect, useState } from 'react'

function cleanSnippet(snippet = '') {
  return snippet
    .replace(/^```text\s*/i, '')
    .replace(/```\s*$/i, '')
    .replace(/\r/g, '')
    .trim()
}

function getSourceName(document = '') {
  return document
    .replace(/\.(txt|pdf)$/i, '')
    .replace(/^TBBD\s+/i, 'TBBD ')
    .trim()
}

export default function WorkplaceAssistant({ initialQuestion = '' }) {
  const [question, setQuestion] = useState(initialQuestion)
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    setQuestion(initialQuestion)
  }, [initialQuestion])

  const handleSubmit = async (event) => {
    event.preventDefault()

    const query = question.trim()
    if (!query || loading) return

    setLoading(true)
    setError('')
    setAnswer('')
    setSources([])

    try {
      const response = await fetch('/mcp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: Date.now(),
          method: 'tools/call',
          params: {
            name: 'Semantic_Hybrid_Search',
            arguments: {
              query,
            },
          },
        }),
      })

      if (!response.ok) {
        throw new Error(`Assistant request failed (${response.status})`)
      }

      const data = await response.json()
      const content = data?.result?.content

      if (!Array.isArray(content) || content.length === 0) {
        throw new Error('The assistant returned no results.')
      }

      const results = content
        .filter((item) => item?.snippet)
        .map((item) => ({
          document: item.document || 'TBBD HR Policy',
          snippet: cleanSnippet(item.snippet),
          score: item.score,
        }))

      if (results.length === 0) {
        throw new Error('No relevant workplace policy information was found.')
      }

      setAnswer(results[0].snippet)

      const uniqueSources = []
      const seen = new Set()

      for (const result of results) {
        const name = getSourceName(result.document)

        if (!seen.has(name)) {
          seen.add(name)
          uniqueSources.push(name)
        }
      }

      setSources(uniqueSources)
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Unable to contact the Workplace Assistant.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="assistant-card">
      <div className="assistant-icon">✦</div>

      <div className="assistant-content">
        <h2>TBBD Workplace Assistant</h2>
        <p>
          Ask about HR policies, leave, benefits and workplace information.
        </p>

        <form className="assistant-input" onSubmit={handleSubmit}>
          <input
            type="text"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask a workplace question..."
            aria-label="Ask the Workplace Assistant"
            disabled={loading}
          />

          <button type="submit" disabled={loading}>
            {loading ? 'Searching...' : 'Ask'}
          </button>
        </form>

        {error && (
          <div className="assistant-error" role="alert">
            {error}
          </div>
        )}

        {answer && (
          <div className="assistant-result">
            <div className="assistant-result-label">
              Retrieved workplace information
            </div>

            <div className="assistant-answer">
              {answer.split('\n').map((line, index) => (
                <p key={index}>
                  {line.trim()}
                </p>
              ))}
            </div>

            {sources.length > 0 && (
              <div className="assistant-sources">
                <strong>Sources</strong>

                <div className="assistant-source-list">
                  {sources.map((source) => (
                    <span className="assistant-source" key={source}>
                      {source}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  )
}
