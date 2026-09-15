import PageHeader from "../components/PageHeader";

export default function RecruitmentMedical() {
  return (
    <>
      <PageHeader
        title="Medical Examinations"
        subtitle="Manage candidate medical examinations and fitness results."
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <section className="dashboard-card">
          <h3>Scheduled</h3>
          <p>0</p>
        </section>

        <section className="dashboard-card">
          <h3>In Progress</h3>
          <p>0</p>
        </section>

        <section className="dashboard-card">
          <h3>Fit</h3>
          <p className="text-green-600">0</p>
        </section>

        <section className="dashboard-card">
          <h3>Unfit</h3>
          <p className="text-red-600">0</p>
        </section>
      </div>

      <section className="dashboard-card">
        <h2>Medical Examination Records</h2>
        <p>
          Medical examination module is ready for API integration.
        </p>
      </section>
    </>
  );
}
