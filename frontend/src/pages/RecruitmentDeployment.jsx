import PageHeader from "../components/PageHeader";

export default function RecruitmentDeployment() {
  return (
    <>
      <PageHeader
        title="Deployment"
        subtitle="Manage candidate deployment and overseas placement."
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <section className="dashboard-card">
          <h3>Ready</h3>
          <p>0</p>
        </section>

        <section className="dashboard-card">
          <h3>Deployed</h3>
          <p>0</p>
        </section>

        <section className="dashboard-card">
          <h3>Joined Employer</h3>
          <p className="text-green-600">0</p>
        </section>

        <section className="dashboard-card">
          <h3>Completed</h3>
          <p>0</p>
        </section>
      </div>

      <section className="dashboard-card">
        <h2>Deployment Records</h2>
        <p>Deployment module is ready for API integration.</p>
      </section>
    </>
  );
}
