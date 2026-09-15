import PageHeader from "../components/PageHeader";

export default function RecruitmentTradeTests() {
  return (
    <>
      <PageHeader
        title="Trade Tests"
        subtitle="Manage trade testing and practical skill assessments."
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <section className="dashboard-card">
          <h3>Scheduled Tests</h3>
          <p>0</p>
        </section>

        <section className="dashboard-card">
          <h3>Completed Tests</h3>
          <p>0</p>
        </section>

        <section className="dashboard-card">
          <h3>Passed</h3>
          <p className="text-green-600">0</p>
        </section>

        <section className="dashboard-card">
          <h3>Failed</h3>
          <p className="text-red-600">0</p>
        </section>
      </div>

      <section className="dashboard-card">
        <h2>Candidate Trade Tests</h2>
        <p>Trade test module is ready for API integration.</p>
      </section>
    </>
  );
}
