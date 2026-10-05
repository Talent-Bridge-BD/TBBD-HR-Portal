import { useEffect, useState } from "react"

import { authenticatedFetch } from "../utils/auth"

import "./AdministratorNotifications.css"

export default function AdministratorNotifications() {

  const [templates, setTemplates] = useState([])
  const [deliveryLogs, setDeliveryLogs] = useState([])

  useEffect(() => {

    authenticatedFetch(
      "/api/administrator/notifications/templates"
    )
      .then((response) => response.json())
      .then((data) => setTemplates(data))
      .catch((error) => console.error(error))


    authenticatedFetch(
      "/api/administrator/notifications/delivery-logs"
    )
      .then((response) => response.json())
      .then((data) => setDeliveryLogs(data))
      .catch((error) => console.error(error))

  }, [])


  return (
    <div className="administrator-notifications">

      <h1>Notification Management</h1>

      <p>
        Manage notification templates and delivery monitoring.
      </p>

      <section>
        <h2>Templates</h2>
        <p>{templates.length} templates configured</p>
      </section>

      <section>
        <h2>Delivery Logs</h2>
        <p>{deliveryLogs.length} delivery records</p>
      </section>

    </div>
  )
}
