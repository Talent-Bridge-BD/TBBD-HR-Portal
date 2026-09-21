import { useEffect, useMemo, useState } from "react";

import { authenticatedFetch } from '../utils/auth'
const API_BASE = "/api/ticketing";
const APPLICATIONS_API = "/api/applications";

const STATUS_OPTIONS = [
  "Pending",
  "Booked",
  "Issued",
  "Completed",
  "Cancelled",
];

function getInitials(name = "") {
  const parts = name.trim().split(/\s+/).filter(Boolean);

  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();

  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
}

function formatDateTime(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getStatusClass(status) {
  return `recruitment-status-badge recruitment-ticketing-status-${String(
    status || "Pending"
  )
    .toLowerCase()
    .replace(/\s+/g, "-")}`;
}

export default function RecruitmentTicketing({ auth }) {
  const organizationId = auth?.organization_ids?.[0] || "";
  const [applications, setApplications] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadTicketing() {
      setLoading(true);
      setError("");

      try {
        if (!organizationId) {
          setLoading(false);
          return;
        }

        const applicationsResponse = await authenticatedFetch(
          `${APPLICATIONS_API}?organization_id=${encodeURIComponent(
            organizationId
          )}`
        );

        if (!applicationsResponse.ok) {
          throw new Error(
            `Unable to load applications (${applicationsResponse.status})`
          );
        }

        const applicationsData = await applicationsResponse.json();
        const applicationList = Array.isArray(applicationsData)
          ? applicationsData
          : applicationsData?.items || [];

        if (cancelled) return;

        setApplications(applicationList);

        const ticketResults = await Promise.all(
          applicationList.map(async (application) => {
            const applicationId =
              application.id || application.application_id;

            if (!applicationId) return [];

            const response = await authenticatedFetch(
              `${API_BASE}?application_id=${encodeURIComponent(
                applicationId
              )}`
            );

            if (!response.ok) return [];

            const data = await response.json();

            return (Array.isArray(data) ? data : []).map((ticket) => ({
              ...ticket,
              application,
            }));
          })
        );

        if (!cancelled) {
          setTickets(ticketResults.flat());
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || "Unable to load ticketing records.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadTicketing();

    return () => {
      cancelled = true;
    };
  }, []);

  const enrichedTickets = useMemo(
    () =>
      tickets.map((ticket) => {
        const application =
          ticket.application ||
          applications.find(
            (item) =>
              (item.id || item.application_id) === ticket.application_id
          );

        const candidateName =
          application?.candidate_name ||
          application?.candidate?.full_name ||
          application?.candidate?.name ||
          application?.full_name ||
          application?.name ||
          "Candidate";

        const jobTitle =
          application?.job_title ||
          application?.job?.title ||
          application?.position_title ||
          "Job application";

        return {
          ...ticket,
          candidateName,
          jobTitle,
        };
      }),
    [tickets, applications]
  );

  const filteredTickets = useMemo(() => {
    const query = search.trim().toLowerCase();

    return enrichedTickets.filter((ticket) => {
      const matchesStatus =
        statusFilter === "All" || ticket.status === statusFilter;

      if (!matchesStatus) return false;
      if (!query) return true;

      return [
        ticket.candidateName,
        ticket.jobTitle,
        ticket.airline_name,
        ticket.flight_number,
        ticket.booking_reference,
        ticket.ticket_number,
        ticket.departure_airport,
        ticket.arrival_airport,
      ]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query));
    });
  }, [enrichedTickets, search, statusFilter]);

  const counts = useMemo(
    () => ({
      Pending: enrichedTickets.filter((ticket) => ticket.status === "Pending")
        .length,
      Booked: enrichedTickets.filter((ticket) => ticket.status === "Booked")
        .length,
      Issued: enrichedTickets.filter((ticket) => ticket.status === "Issued")
        .length,
      Completed: enrichedTickets.filter(
        (ticket) => ticket.status === "Completed"
      ).length,
    }),
    [enrichedTickets]
  );

  async function openTicket(ticket) {
    setSelectedTicket(ticket);
    setDetailLoading(true);

    try {
      const response = await fetch(`${API_BASE}/${ticket.id}`);

      if (!response.ok) {
        throw new Error(`Unable to load ticket (${response.status})`);
      }

      const data = await response.json();

      setSelectedTicket({
        ...ticket,
        ...data,
      });
    } catch (err) {
      setError(err.message || "Unable to load ticket details.");
    } finally {
      setDetailLoading(false);
    }
  }

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Ticketing &amp; Travel</h1>
          <p>
            Manage candidate flight bookings, ticket issuance, and travel
            arrangements.
          </p>
        </div>
      </div>

      <div className="trade-test-kpi-grid recruitment-ticketing-kpi-grid">
        <section className="trade-test-kpi-card">
          <span>Pending</span>
          <strong>{counts.Pending}</strong>
          <small>Travel arrangements pending</small>
        </section>

        <section className="trade-test-kpi-card">
          <span>Booked</span>
          <strong>{counts.Booked}</strong>
          <small>Flights booked</small>
        </section>

        <section className="trade-test-kpi-card">
          <span>Issued</span>
          <strong>{counts.Issued}</strong>
          <small>Tickets issued</small>
        </section>

        <section className="trade-test-kpi-card">
          <span>Completed</span>
          <strong>{counts.Completed}</strong>
          <small>Travel completed</small>
        </section>
      </div>

      <section className="recruitment-candidates-card recruitment-ticketing-card">
        <div className="recruitment-candidates-toolbar">
          <div>
            <strong>Travel Ticketing Records</strong>
            <span>
              {filteredTickets.length} record
              {filteredTickets.length === 1 ? "" : "s"}
            </span>
          </div>

          <div className="recruitment-ticketing-filters">
            <input
              type="search"
              placeholder="Search candidate, airline, flight..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />

            <select
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
              aria-label="Filter ticketing records by status"
            >
              <option value="All">All statuses</option>
              {STATUS_OPTIONS.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </div>
        </div>

        {loading && (
          <div className="recruitment-detail-loading">
            Loading ticketing records...
          </div>
        )}

        {!loading && error && (
          <div className="recruitment-detail-error">
            <strong>Unable to load ticketing records</strong>
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && filteredTickets.length === 0 && (
          <div className="recruitment-ticketing-empty">
            <strong>No ticketing records found</strong>
            <p>
              Ticketing records will appear here when candidate travel
              arrangements are created.
            </p>
          </div>
        )}

        {!loading && !error && filteredTickets.length > 0 && (
          <div className="recruitment-candidates-table-wrap">
            <table className="recruitment-candidates-table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Flight</th>
                  <th>Route</th>
                  <th>Departure</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {filteredTickets.map((ticket) => (
                  <tr key={ticket.id}>
                    <td>
                      <div className="recruitment-candidate-cell">
                        <div className="recruitment-candidate-avatar">
                          {getInitials(ticket.candidateName)}
                        </div>

                        <div>
                          <strong>{ticket.candidateName}</strong>
                          <span>{ticket.jobTitle}</span>
                        </div>
                      </div>
                    </td>

                    <td>
                      <strong>{ticket.airline_name || "—"}</strong>
                      <span>{ticket.flight_number || "Flight pending"}</span>
                    </td>

                    <td>
                      <strong>
                        {ticket.departure_airport || "—"} →{" "}
                        {ticket.arrival_airport || "—"}
                      </strong>
                      <span>
                        {ticket.booking_reference || "Booking reference pending"}
                      </span>
                    </td>

                    <td>{formatDateTime(ticket.departure_datetime)}</td>

                    <td>
                      <span className={getStatusClass(ticket.status)}>
                        {ticket.status || "Pending"}
                      </span>
                    </td>

                    <td>
                      <button
                        type="button"
                        className="recruitment-view-button"
                        onClick={() => openTicket(ticket)}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedTicket && (
        <div
          className="recruitment-detail-overlay"
          role="presentation"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              setSelectedTicket(null);
            }
          }}
        >
          <aside className="recruitment-detail-panel">
            <div className="recruitment-detail-header">
              <div>
                <div className="recruitment-detail-eyebrow">
                  TICKETING RECORD
                </div>
                <h2>{selectedTicket.candidateName}</h2>
              </div>

              <button
                type="button"
                className="recruitment-detail-close"
                onClick={() => setSelectedTicket(null)}
                aria-label="Close ticketing details"
              >
                ×
              </button>
            </div>

            {detailLoading ? (
              <div className="recruitment-detail-loading">
                Loading ticket details...
              </div>
            ) : (
              <div className="recruitment-detail-content">
                <div className="recruitment-detail-profile">
                  <div className="recruitment-candidate-avatar">
                    {getInitials(selectedTicket.candidateName)}
                  </div>

                  <div>
                    <h3>{selectedTicket.jobTitle}</h3>
                    <p>
                      <span className={getStatusClass(selectedTicket.status)}>
                        {selectedTicket.status || "Pending"}
                      </span>
                    </p>
                  </div>
                </div>

                <div className="recruitment-detail-grid">
                  <div>
                    <span>Airline</span>
                    <strong>{selectedTicket.airline_name || "—"}</strong>
                  </div>

                  <div>
                    <span>Flight Number</span>
                    <strong>{selectedTicket.flight_number || "—"}</strong>
                  </div>

                  <div>
                    <span>Booking Reference</span>
                    <strong>
                      {selectedTicket.booking_reference || "—"}
                    </strong>
                  </div>

                  <div>
                    <span>Ticket Number</span>
                    <strong>{selectedTicket.ticket_number || "—"}</strong>
                  </div>

                  <div>
                    <span>Departure</span>
                    <strong>
                      {selectedTicket.departure_airport || "—"}
                    </strong>
                  </div>

                  <div>
                    <span>Arrival</span>
                    <strong>{selectedTicket.arrival_airport || "—"}</strong>
                  </div>

                  <div>
                    <span>Departure Date &amp; Time</span>
                    <strong>
                      {formatDateTime(selectedTicket.departure_datetime)}
                    </strong>
                  </div>

                  <div>
                    <span>Arrival Date &amp; Time</span>
                    <strong>
                      {formatDateTime(selectedTicket.arrival_datetime)}
                    </strong>
                  </div>
                </div>

                {selectedTicket.notes && (
                  <div className="recruitment-cover-letter">
                    <h3>Travel Notes</h3>
                    <p>{selectedTicket.notes}</p>
                  </div>
                )}

                {selectedTicket.ticket_document_reference && (
                  <div className="recruitment-cover-letter">
                    <h3>Ticket Document</h3>
                    <p>{selectedTicket.ticket_document_reference}</p>
                  </div>
                )}
              </div>
            )}
          </aside>
        </div>
      )}
    </>
  );
}
