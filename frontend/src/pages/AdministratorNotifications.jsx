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
      .catch(console.error)


    authenticatedFetch(
      "/api/administrator/notifications/delivery-logs"
    )
      .then((response) => response.json())
      .then((data) => setDeliveryLogs(data))
      .catch(console.error)

  }, [])


  return (

    <div className="administrator-notifications">

      <h1>
        Notification Management
      </h1>

      <p>
        Manage notification templates and delivery monitoring.
      </p>


      <section>

        <h2>
          Templates ({templates.length})
        </h2>


        {templates.map((template) => (

          <div
            key={template.id}
            className="notification-template-card"
          >

            <strong>
              {template.name}
            </strong>

            <span>
              {template.event_type}
            </span>

            <p>
              {template.subject}
            </p>

          </div>

        ))}

      </section>


      <section>

        <h2>
          Delivery Logs ({deliveryLogs.length})
        </h2>


        {deliveryLogs.length === 0 ? (

          <p>
            No delivery records available.
          </p>

        ) : (

          deliveryLogs.map((log) => (

            <div key={log.id}>
              {log.recipient} - {log.status}
            </div>

          ))

        )}

      </section>

    </div>

  )

}
