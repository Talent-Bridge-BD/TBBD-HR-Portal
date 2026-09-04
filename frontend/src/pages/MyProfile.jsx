import PageHeader from '../components/PageHeader'

export default function MyProfile() {
  return (
    <>
      <PageHeader title="My Profile" subtitle="View and manage your employee profile." />
      <section className="placeholder-card">
        <h2>Employee Profile</h2>
        <p>Profile information will be connected to the HR backend.</p>
      </section>
    </>
  )
}
