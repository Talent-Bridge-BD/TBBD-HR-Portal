import PageHeader from "../components/PageHeader"

export default function CandidateOffers() {
  return (
    <>
      <PageHeader
        title="My Offers"
        subtitle="View your employment offers and offer letters."
      />

      <section className="placeholder-card">
        <div className="page-section-header">
          <div>
            <h2>Employment Offers</h2>
            <p>
              Offers received from employers will appear here.
            </p>
          </div>
        </div>

        <div
          style={{
            marginTop: "20px",
            padding: "24px",
            background: "#F8FAFC",
            border: "1px solid #E2E8F0",
            borderRadius: "12px",
          }}
        >
          No offers available yet.
        </div>
      </section>
    </>
  )
}
