import PageHeader from "../components/PageHeader";

export default function RecruitmentVisa() {
  return (
    <>
      <PageHeader
        title="Visa Processing"
        subtitle="Manage candidate visa applications and approvals."
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <section className="dashboard-card">
          <h3>Pending</h3>
          <p>0</p>
        </section>

        <section className="dashboard-card">
          <h3>Submitted</h3>
          <p>0</p>
        </section>

        <section className="dashboard-card">
          <h3>Approved</h3>
          <p className="text-green-600">0</p>
        </section>

        <section className="dashboard-card">
          <h3>Rejected</h3>
          <p className="text-red-600">0</p>
        </section>
      </div>

      <section className="dashboard-card">
        <h2>Visa Processing Records</h2>
        <p>
          Visa processing module is ready for API integration.
        </p>
      </section>
    </>
  );
}
