export default function WorkplaceAssistant() {
  return (
    <section className="assistant-card">
      <div className="assistant-icon">✦</div>

      <div className="assistant-content">
        <h2>TBBD Workplace Assistant</h2>
        <p>
          Ask about HR policies, leave, benefits and workplace information.
        </p>

        <div className="assistant-input">
          <input
            type="text"
            placeholder="Ask a workplace question..."
            aria-label="Ask the Workplace Assistant"
          />
          <button>Ask</button>
        </div>
      </div>
    </section>
  )
}
