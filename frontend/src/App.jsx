import { useEffect, useState } from "react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from "recharts"

const API_URL = "http://127.0.0.1:8001"

function App() {
  const [summary, setSummary] = useState(null)
  const [categories, setCategories] = useState([])
  const [priorities, setPriorities] = useState([])
  const [statuses, setStatuses] = useState([])
  const [tickets, setTickets] = useState([])
  const [searchTerm, setSearchTerm] = useState("")

  const [error, setError] = useState("")

  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [creatingTicket, setCreatingTicket] = useState(false)
  const [createMessage, setCreateMessage] = useState("")
  const [duplicateWarning, setDuplicateWarning] = useState(null)

  const [selectedTicket, setSelectedTicket] = useState(null)
  const [slaDetails, setSlaDetails] = useState(null)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      setError("")

      const [
        summaryResponse,
        categoryResponse,
        priorityResponse,
        statusResponse,
        ticketsResponse
      ] = await Promise.all([
        fetch(`${API_URL}/tickets/stats/summary`),
        fetch(`${API_URL}/tickets/stats/categories`),
        fetch(`${API_URL}/tickets/stats/priorities`),
        fetch(`${API_URL}/tickets/stats/statuses`),
        fetch(`${API_URL}/tickets/`)
      ])

      const [
        summaryData,
        categoryData,
        priorityData,
        statusData,
        ticketsData
      ] = await Promise.all([
        summaryResponse.json(),
        categoryResponse.json(),
        priorityResponse.json(),
        statusResponse.json(),
        ticketsResponse.json()
      ])

      if (!summaryResponse.ok) {
        throw new Error(
          summaryData.detail || "Failed to load summary"
        )
      }

      setSummary(summaryData)

      setCategories(
        Object.entries(categoryData.categories || {}).map(
          ([name, value]) => ({
            name,
            value
          })
        )
      )

      setPriorities(
        Object.entries(priorityData.priorities || {}).map(
          ([name, value]) => ({
            name,
            value
          })
        )
      )

      setStatuses(
        Object.entries(statusData.statuses || {}).map(
          ([name, value]) => ({
            name,
            value
          })
        )
      )

      setTickets(ticketsData)
    } catch (err) {
      setError(err.message)
    }
  }

  const loadTicketDetails = async (ticketId) => {
    try {
      setError("")
      setSelectedTicket(null)
      setSlaDetails(null)

      const [ticketResponse, slaResponse] = await Promise.all([
        fetch(`${API_URL}/tickets/${ticketId}`),
        fetch(`${API_URL}/tickets/${ticketId}/sla`)
      ])

      const ticketData = await ticketResponse.json()
      const slaData = await slaResponse.json()

      if (!ticketResponse.ok) {
        throw new Error(
          ticketData.detail || "Failed to load ticket"
        )
      }

      if (!slaResponse.ok) {
        throw new Error(
          slaData.detail || "Failed to load SLA details"
        )
      }

      setSelectedTicket(ticketData)
      setSlaDetails(slaData)
    } catch (err) {
      setError(err.message)
    }
  }

  const updateTicketStatus = async (status) => {
    if (!selectedTicket) {
      return
    }

    try {
      setError("")

      const response = await fetch(
        `${API_URL}/tickets/${selectedTicket.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            status
          })
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to update ticket"
        )
      }

      setSelectedTicket(data)

      await loadDashboard()

      const slaResponse = await fetch(
        `${API_URL}/tickets/${data.id}/sla`
      )

      const slaData = await slaResponse.json()

      if (slaResponse.ok) {
        setSlaDetails(slaData)
      }
    } catch (err) {
      setError(err.message)
    }
  }
  const filteredTickets = tickets.filter((ticket) => {
  const search = searchTerm.toLowerCase().trim()

  if (!search) {
    return true
  }

  return (
    String(ticket.id).includes(search) ||
    (ticket.title || "").toLowerCase().includes(search) ||
    (ticket.description || "").toLowerCase().includes(search) ||
    (ticket.category || "").toLowerCase().includes(search) ||
    (ticket.priority || "").toLowerCase().includes(search) ||
    (ticket.status || "").toLowerCase().includes(search)
  )
})
  const createTicket = async (event) => {
    event.preventDefault()

    setCreatingTicket(true)
    setCreateMessage("")
    setDuplicateWarning(null)
    setError("")

    try {
      const duplicateResponse = await fetch(
        `${API_URL}/tickets/check-duplicate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            title,
            description
          })
        }
      )

      const duplicateData = await duplicateResponse.json()

      if (!duplicateResponse.ok) {
        throw new Error(
          duplicateData.detail || "Duplicate check failed"
        )
      }

      if (duplicateData.duplicate_detected) {
        setDuplicateWarning(duplicateData)
        setCreatingTicket(false)
        return
      }

      const response = await fetch(
        `${API_URL}/tickets/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            title,
            description
          })
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to create ticket"
        )
      }

      setCreateMessage(
        `Ticket #${data.ticket.id} created successfully`
      )

      setTitle("")
      setDescription("")

      await loadDashboard()
    } catch (err) {
      setCreateMessage(err.message)
    } finally {
      setCreatingTicket(false)
    }
  }

  return (
    <div className="app">

      {/* =================================================
          HEADER
      ================================================= */}

      <header className="header">

        <div className="header-content">

          <div>

            <h1>
              SupportIQ
            </h1>

            <p>
              AI-Powered IT Incident & Ticket Automation Platform
            </p>

          </div>

          <div className="header-status">
            <span className="status-dot"></span>
            System Operational
          </div>

        </div>

      </header>


      <main className="dashboard-container">

        {/* =================================================
            ERROR
        ================================================= */}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}


        {/* =================================================
            CREATE TICKET
        ================================================= */}

        <section className="create-ticket-section">

          <div className="section-heading">

            <div>

              <h2>
                Create Support Ticket
              </h2>

              <p>
                Submit an IT incident for automatic AI classification,
                priority prediction and SLA assignment.
              </p>

            </div>

          </div>


          <div className="create-ticket-card">

            <form onSubmit={createTicket}>

              <div className="form-group">

                <label htmlFor="ticket-title">
                  Ticket Title
                </label>

                <input
                  id="ticket-title"
                  type="text"
                  placeholder="Example: Production database connection failed"
                  value={title}
                  onChange={(event) =>
                    setTitle(event.target.value)
                  }
                  required
                  minLength={3}
                  maxLength={200}
                />

              </div>


              <div className="form-group">

                <label htmlFor="ticket-description">
                  Description
                </label>

                <textarea
                  id="ticket-description"
                  rows="5"
                  placeholder="Describe the incident, affected users and observed symptoms..."
                  value={description}
                  onChange={(event) =>
                    setDescription(event.target.value)
                  }
                  required
                  minLength={5}
                />

              </div>


              <button
                type="submit"
                className="create-ticket-button"
                disabled={creatingTicket}
              >
                {creatingTicket
                  ? "Checking..."
                  : "Create Ticket"}
              </button>

            </form>


            {createMessage && (
              <div className="create-ticket-message">
                {createMessage}
              </div>
            )}


            {duplicateWarning && (
              <div className="duplicate-warning">

                <strong>
                  Duplicate Ticket Detected
                </strong>

                <p>
                  A similar ticket already exists.
                </p>

                <p>
                  Existing Ticket: #
                  {duplicateWarning.duplicate_ticket_id}
                </p>

                <p>
                  Similarity:{" "}
                  {(duplicateWarning.similarity * 100).toFixed(1)}%
                </p>

                <p>
                  Review the existing ticket before creating another one.
                </p>

              </div>
            )}

          </div>

        </section>


        {/* =================================================
            SUMMARY CARDS
        ================================================= */}

        <section className="summary-section">

          <div className="section-heading">

            <div>

              <h2>
                Support Overview
              </h2>

              <p>
                Current IT support workload and incident status.
              </p>

            </div>

          </div>


          <div className="summary-grid">

            <div className="summary-card">

              <span className="summary-label">
                Total Tickets
              </span>

              <strong className="summary-value">
                {summary?.total_tickets ?? 0}
              </strong>

            </div>


            <div className="summary-card">

              <span className="summary-label">
                Open Tickets
              </span>

              <strong className="summary-value">
                {summary?.open_tickets ?? 0}
              </strong>

            </div>


            <div className="summary-card">

              <span className="summary-label">
                High Priority
              </span>

              <strong className="summary-value">
                {summary?.high_tickets ?? 0}
              </strong>

            </div>


            <div className="summary-card">

              <span className="summary-label">
                Critical
              </span>

              <strong className="summary-value">
                {summary?.critical_tickets ?? 0}
              </strong>

            </div>

          </div>

        </section>


        {/* =================================================
            CHARTS
        ================================================= */}

        <section className="charts-section">

          <div className="chart-card">

            <div className="chart-card-header">

              <h3>
                Tickets by Category
              </h3>

            </div>

            <div className="chart-container">

              <ResponsiveContainer
                width="100%"
                height={300}
              >

                <BarChart data={categories}>

                  <CartesianGrid
                    strokeDasharray="3 3"
                  />

                  <XAxis
                    dataKey="name"
                  />

                  <YAxis
                    allowDecimals={false}
                  />

                  <Tooltip />

                  <Bar
                    dataKey="value"
                    fill="#2563eb"
                    radius={[6, 6, 0, 0]}
                  />

                </BarChart>

              </ResponsiveContainer>

            </div>

          </div>


          <div className="chart-card">

            <div className="chart-card-header">

              <h3>
                Tickets by Priority
              </h3>

            </div>

            <div className="chart-container">

              <ResponsiveContainer
                width="100%"
                height={300}
              >

                <PieChart>

                  <Pie
                    data={priorities}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >

                    {priorities.map((entry, index) => (
                      <Cell
                        key={`priority-${index}`}
                        fill={
                          [
                            "#dc2626",
                            "#f97316",
                            "#eab308",
                            "#22c55e"
                          ][index % 4]
                        }
                      />
                    ))}

                  </Pie>

                  <Tooltip />

                  <Legend />

                </PieChart>

              </ResponsiveContainer>

            </div>

          </div>


          <div className="chart-card">

            <div className="chart-card-header">

              <h3>
                Tickets by Status
              </h3>

            </div>

            <div className="chart-container">

              <ResponsiveContainer
                width="100%"
                height={300}
              >

                <BarChart data={statuses}>

                  <CartesianGrid
                    strokeDasharray="3 3"
                  />

                  <XAxis
                    dataKey="name"
                  />

                  <YAxis
                    allowDecimals={false}
                  />

                  <Tooltip />

                  <Bar
                    dataKey="value"
                    fill="#0f766e"
                    radius={[6, 6, 0, 0]}
                  />

                </BarChart>

              </ResponsiveContainer>

            </div>

          </div>

        </section>


        {/* =================================================
            RECENT TICKETS
        ================================================= */}

        <section className="tickets-section">

          <div className="section-heading">

            <h2>
              Recent Tickets
            </h2>

            <span>
              {tickets.length} tickets
            </span>

          </div>
          <div className="ticket-search">

          <input
            type="text"
            placeholder="Search tickets by ID, title, category, priority or status..."
            value={searchTerm}
            onChange={(event) =>
            setSearchTerm(event.target.value)
          }
          />

        </div>
          <div className="ticket-search">

  <input
    type="text"
    placeholder="Search tickets by ID, title, category, priority or status..."
    value={searchTerm}
    onChange={(event) =>
      setSearchTerm(event.target.value)
    }
  />

</div>
          <div className="tickets-card">

            <div className="tickets-table-wrapper">

              <table className="tickets-table">

                <thead>

                  <tr>

                    <th>ID</th>

                    <th>Title</th>

                    <th>Category</th>

                    <th>Priority</th>

                    <th>Status</th>

                    <th>SLA Deadline</th>

                  </tr>

                </thead>


                <tbody>

                  {filteredTickets.map((ticket) => (

                    <tr
                      key={ticket.id}
                      onClick={() =>
                        loadTicketDetails(ticket.id)
                      }
                      className="ticket-row"
                    >

                      <td>
                        #{ticket.id}
                      </td>


                      <td className="ticket-title">
                        {ticket.title}
                      </td>


                      <td>
                        {ticket.category || "Uncategorized"}
                      </td>


                      <td>

                        <span
                          className={`priority-badge priority-${(
                            ticket.priority || "unknown"
                          ).toLowerCase()}`}
                        >

                          {ticket.priority || "N/A"}

                        </span>

                      </td>


                      <td>

                        <span
                          className={`status-badge status-${(
                            ticket.status || "unknown"
                          ).toLowerCase()}`}
                        >

                          {ticket.status || "UNKNOWN"}

                        </span>

                      </td>


                      <td>

                        {ticket.sla_deadline
                          ? new Date(
                              ticket.sla_deadline
                            ).toLocaleString()
                          : "N/A"}

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          </div>

        </section>


        {/* =================================================
            TICKET DETAILS
        ================================================= */}

        {selectedTicket && (

          <section className="ticket-details-section">

            <div className="section-heading">

              <h2>
                Ticket Details
              </h2>

              <button
                className="close-details-button"
                onClick={() => {
                  setSelectedTicket(null)
                  setSlaDetails(null)
                }}
              >
                Close
              </button>

            </div>


            <div className="ticket-details-card">

              <div className="ticket-detail-header">

                <div>

                  <span className="ticket-detail-id">
                    Ticket #{selectedTicket.id}
                  </span>

                  <h3>
                    {selectedTicket.title}
                  </h3>

                </div>

              </div>


              <div className="ticket-detail-description">

                <h4>
                  Description
                </h4>

                <p>
                  {selectedTicket.description}
                </p>

              </div>


              <div className="ticket-detail-grid">

                <div className="detail-item">

                  <span>
                    Category
                  </span>

                  <strong>
                    {selectedTicket.category || "N/A"}
                  </strong>

                </div>


                <div className="detail-item">

                  <span>
                    Priority
                  </span>

                  <strong>
                    {selectedTicket.priority || "N/A"}
                  </strong>

                </div>


                <div className="detail-item">

                  <span>
                    Status
                  </span>

                  <strong>
                    {selectedTicket.status || "N/A"}
                  </strong>

                </div>


                <div className="detail-item">

                  <span>
                    Created
                  </span>

                  <strong>
                    {selectedTicket.created_at
                      ? new Date(
                          selectedTicket.created_at
                        ).toLocaleString()
                      : "N/A"}
                  </strong>

                </div>


                <div className="detail-item">

                  <span>
                    SLA Deadline
                  </span>

                  <strong>
                    {selectedTicket.sla_deadline
                      ? new Date(
                          selectedTicket.sla_deadline
                        ).toLocaleString()
                      : "N/A"}
                  </strong>

                </div>


                <div className="detail-item">

                  <span>
                    SLA Status
                  </span>

                  <strong>
                    {slaDetails?.sla_status || "N/A"}
                  </strong>

                </div>

              </div>


              {/* =================================================
                  STATUS UPDATE
              ================================================= */}

              <div className="status-update-section">

                <h4>
                  Update Ticket Status
                </h4>

                <div className="status-buttons">

                  <button
                    type="button"
                    onClick={() =>
                      updateTicketStatus("OPEN")
                    }
                    disabled={
                      selectedTicket.status === "OPEN"
                    }
                  >
                    Open
                  </button>


                  <button
                    type="button"
                    onClick={() =>
                      updateTicketStatus("IN_PROGRESS")
                    }
                    disabled={
                      selectedTicket.status === "IN_PROGRESS"
                    }
                  >
                    In Progress
                  </button>


                  <button
                    type="button"
                    onClick={() =>
                      updateTicketStatus("RESOLVED")
                    }
                    disabled={
                      selectedTicket.status === "RESOLVED"
                    }
                  >
                    Resolved
                  </button>

                </div>

              </div>


              {/* =================================================
                  AI RESOLUTION
              ================================================= */}

              <div className="resolution-section">

                <h4>
                  AI Resolution Suggestion
                </h4>

                <p>
                  {selectedTicket.resolution_suggestion ||
                    "No resolution suggestion available."}
                </p>

              </div>

            </div>

          </section>

        )}

      </main>


      {/* =================================================
          FOOTER
      ================================================= */}

      <footer>

        SupportIQ • IT Incident Automation Platform

      </footer>

    </div>
  )
}

export default App