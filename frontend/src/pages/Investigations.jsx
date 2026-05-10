import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  FolderClock,
  Gauge,
  Search,
} from "lucide-react";
import { getTransactions } from "../api/client";

const toDateValue = (value) => (value ? String(value).slice(0, 10) : "");
const toTime = (value, endOfDay = false) => {
  if (!value) return endOfDay ? Infinity : -Infinity;
  return new Date(`${value}T${endOfDay ? "23:59:59" : "00:00:00"}`).getTime();
};

const formatTimestamp = (value) =>
  value
    ? new Date(value).toLocaleString(undefined, {
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      })
    : "—";

function getReason(txn) {
  if (txn.decision === "BLOCK") return "Auto-blocked high risk transaction";
  if (txn.decision === "ESCALATE") return "Escalated for analyst review";
  if (txn.risk === "HIGH") return "High risk score exceeded threshold";
  return "Rule-based investigation";
}

function getStatus(txn) {
  if (txn.decision === "BLOCK") return "Closed";
  if (txn.decision === "ESCALATE") return "Under Review";

  return "Open";
}

function getPriority(txn) {
  if (txn.decision === "BLOCK" || txn.risk === "HIGH") return "High";
  if (txn.decision === "ESCALATE" || txn.risk === "MEDIUM") return "Medium";
  return "Low";
}

function buildCase(txn, index) {
  return {
    id: txn.transaction_id,
    transaction: txn,
    priority: getPriority(txn),
    status: getStatus(txn, index),
    reason: getReason(txn),
    createdAt: formatTimestamp(txn.timestamp),
  };
}

function CaseStatusPill({ status }) {
  const className = status.toLowerCase().replace(/\s+/g, "-");
  return <span className={`case-status-pill case-status-${className}`}>{status}</span>;
}

function PriorityPill({ priority }) {
  return <span className={`priority-pill priority-${priority.toLowerCase()}`}>{priority}</span>;
}

function SummaryMetric({ icon: Icon, label, value, detail, tone = "blue" }) {
  return (
    <article className="investigation-summary-metric">
      <div className={`investigation-summary-icon investigation-summary-icon-${tone}`}>
        <Icon size={19} strokeWidth={2.3} />
      </div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <p>{detail}</p>
      </div>
    </article>
  );
}

function Investigations({ simulationWindow }) {
  const [transactions, setTransactions] = useState([]);
  const [loadingTransactions, setLoadingTransactions] = useState(true);
  const [transactionsError, setTransactionsError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");

  useEffect(() => {
    let isActive = true;

    const fetchTransactions = async () => {
      try {
        setLoadingTransactions(true);
        setTransactionsError("");

        const response = await getTransactions({ limit: 600, offset: 0 });

        if (!isActive) return;

        setTransactions(response.items);
      } catch (error) {
        if (!isActive) return;

        console.error("Failed to fetch investigations:", error);
        setTransactionsError("Failed to load investigation data from backend.");
        setTransactions([]);
      } finally {
        if (isActive) setLoadingTransactions(false);
      }
    };

    fetchTransactions();

    return () => {
      isActive = false;
    };
  }, []);

  const cases = useMemo(() => {
    if (!transactions.length) return [];

    const dates = transactions.map((txn) => toDateValue(txn.timestamp)).sort();
    const windowStart = simulationWindow?.startDate ?? dates[0];
    const windowEnd = simulationWindow?.endDate ?? dates.at(-1);
    const start = Math.min(toTime(windowStart), toTime(windowEnd));
    const end = Math.max(toTime(windowStart, true), toTime(windowEnd, true));

    return transactions
      .filter((txn) => {
        const txnTime = new Date(txn.timestamp).getTime();
        return txnTime >= start && txnTime <= end;
      })
      .filter((txn) => txn.decision !== "APPROVE" || txn.risk === "HIGH")
      .map(buildCase);
  }, [transactions, simulationWindow]);

  const filteredCases = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();

    return cases.filter((item) => {
      const searchable = [
        item.id,
        item.transaction.id,
        item.transaction.sender,
        item.transaction.receiver,
        item.transaction.final_score,
        item.priority,
        item.status,
        item.reason,
      ]
        .join(" ")
        .toLowerCase();

      const matchesSearch = !normalizedSearch || searchable.includes(normalizedSearch);
      const matchesStatus = statusFilter === "ALL" || item.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [cases, searchTerm, statusFilter]);

  const summary = useMemo(() => {
    const underReview = cases.filter(
      (item) => item.status === "Under Review"
    ).length;
    const closed = cases.filter((item) => item.status === "Closed").length;
    const highPriority = cases.filter((item) => item.priority === "High").length;
    const active = underReview;
    const resolutionRate = cases.length? Math.round((closed / cases.length) * 100): 0;

    return { underReview,
      closed,
      highPriority,
      active,
      resolutionRate, };
    }, [cases]);

  if (loadingTransactions) {
    return (
      <div className="dashboard investigations-page">
        <header className="dashboard-page-header">
          <h1>Investigations</h1>
          <p>Review and manage suspicious cases across the selected timestamp window.</p>
        </header>

        <div className="loading-panel">
          <h2>Loading investigations</h2>
          <p>Preparing suspicious case queue...</p>
        </div>
      </div>
    );
  }

  if (transactionsError) {
    return (
      <div className="dashboard investigations-page">
        <header className="dashboard-page-header">
          <h1>Investigations</h1>
          <p>Review and manage suspicious cases across the selected timestamp window.</p>
        </header>

        <div className="loading-panel">
          <h2>Unable to load investigations</h2>
          <p>{transactionsError}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard investigations-page">
      <header className="dashboard-page-header investigations-page-header">
        <div>
          <h1>Investigations</h1>
          <p>Review and manage suspicious cases across the selected timestamp window.</p>
        </div>

        <span className="investigation-count-pill">{cases.length} total cases</span>
      </header>

      <section className="investigation-controls">
        <div className="investigation-search-group">
          <label htmlFor="investigation-search">Case Search</label>
          <div className="investigation-search-field">
            <Search size={16} strokeWidth={2.3} />
            <input
              id="investigation-search"
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search case, transaction, reason..."
            />
          </div>
        </div>

        <div className="investigation-filter-group">
          <label htmlFor="investigation-status">Status</label>
          <select
            id="investigation-status"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
          >
            <option value="ALL">All</option>
            <option value="Under Review">Under Review</option>
            <option value="Closed">Closed</option>
          </select>
        </div>
      </section>

      <section className="investigation-layout">
        <div className="investigation-table-card">
          <div className="investigation-table-header">
            <div>
              <h2>Case Queue</h2>
              <p>Suspicious transactions requiring analyst action.</p>
            </div>
            <span>{filteredCases.length} visible</span>
          </div>

          <div className="investigation-table-scroll">
            <table className="investigation-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Transaction ID</th>
                  <th>Priority</th>
                  <th>Timestamp</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th>Reason</th>
                  <th>Risk Score</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredCases.length > 0 ? (
                  filteredCases.map((item, index) => (
                    <tr key={item.id}>
                      <td>{index + 1}</td>
                      <td>{item.id}</td>
                      <td>
                        <PriorityPill priority={item.priority} />
                      </td>
                      <td>{item.createdAt}</td>
                      <td>{item.transaction.type}</td>
                      <td>
                        ${Number(item.transaction.amount || 0).toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                      <td>{item.reason}</td>
                      <td className="investigation-score">
                        {Number(item.transaction.final_score ?? 0).toFixed(2)}
                      </td>
                      <td>
                        <CaseStatusPill status={item.status} />
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="9" className="investigation-empty-state">
                      No investigation cases match the current filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <aside className="investigation-summary-panel">
          <div className="investigation-summary-header">
            <h2>Investigation Summary</h2>
            <p>Case workload and resolution posture.</p>
          </div>

          <div className="investigation-summary-grid">
            <SummaryMetric
              icon={AlertTriangle}
              label="High Priority"
              value={summary.highPriority}
              detail="Requires attention"
              tone="red"
            />
            <SummaryMetric
              icon={FolderClock}
              label="Active Cases"
              value={summary.active}
              detail="Currently under review"
              tone="blue"
            />
            <SummaryMetric
              icon={CheckCircle2}
              label="Closed"
              value={summary.closed}
              detail="Resolved cases"
              tone="green"
            />
            <SummaryMetric
              icon={Gauge}
              label="Resolution Rate"
              value={`${summary.resolutionRate}%`}
              detail="Closed investigation cases"
              tone="yellow"
            />
          </div>

          <div className="resolutionRate-panel">
            <div>
              <span>Resolution Rate</span>
              <strong>{summary.resolutionRate}%</strong>
            </div>
            <div className="resolutionRate-panel-track">
              <i style={{ width: `${summary.resolutionRate}%` }} />
            </div>
          </div>

          <div className="investigation-status-breakdown">
            {[
              ["Under Review", summary.underReview],
              ["Closed", summary.closed],
            ].map(([label, value]) => (
              <div key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </aside>
      </section>
    </div>
  );
}

export default Investigations;
