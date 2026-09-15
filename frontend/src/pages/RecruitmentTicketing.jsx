import PageHeader from "../components/PageHeader";

export default function RecruitmentTicketing() {
  return (
    <>
      <PageHeader
        title="Ticketing"
        subtitle="Manage candidate travel tickets and flight arrangements."
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <section className="dashboard-card">
          <h3>Pending</h3>
          <p>0</p>
        </section>

        <section className="dashboard-card">
          <h3>Booked</h3>
          <p>0</p>
        </section>

        <section className="dashboard-card">
          <h3>Issued</h3>
          <p className="text-green-600">0</p>
        </section>

        <section className="dashboard-card">
          <h3>Completed</h3>
          <p>0</p>
        </section>
      </div>

      <section className="dashboard-card">
        <h2>Ticketing Records</h2>
        <p>Ticketing module is ready for API integration.</p>
      </section>
    </>
  );
}
