import PageHeader from "../components/PageHeader";

export default function RecruitmentOnboarding() {
  return (
    <>
      <PageHeader
        title="Onboarding"
        subtitle="Manage candidate onboarding and pre-departure activities."
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <section className="dashboard-card">
          <h3>Pending</h3>
          <p>0</p>
        </section>

        <section className="dashboard-card">
          <h3>Documents Verified</h3>
          <p>0</p>
        </section>

        <section className="dashboard-card">
          <h3>Orientation Complete</h3>
          <p>0</p>
        </section>

        <section className="dashboard-card">
          <h3>Ready for Deployment</h3>
          <p className="text-green-600">0</p>
        </section>
      </div>

      <section className="dashboard-card">
        <h2>Onboarding Records</h2>
        <p>Onboarding module is ready for API integration.</p>
      </section>
    </>
  );
}
