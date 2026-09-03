import PageHeader from '../components/PageHeader'

export default function Leave() {
  return (
    <>
      <PageHeader title="Leave" subtitle="Manage your leave requests and balance." />
      <section className="placeholder-card">
        <h2>Leave Management</h2>
        <p>Leave balances and applications will be connected to the HR backend.</p>
      </section>
    </>
  )
}
