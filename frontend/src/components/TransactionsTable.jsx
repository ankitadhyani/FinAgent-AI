/**
 * TransactionsTable.jsx
 *
 * Scrollable transaction list with sticky headers.
 * Supports:
 * - Sorting columns
 * - Risk badges
 * - Status badges
 * - Row click interaction
 *
 * Clicking row opens Analysis Drawer.
 */

import { useMemo, useState } from "react";
import StatusBadge from "./StatusBadge";

const formatTimestamp = (value) => {
  if (!value) return "—";

  const date = new Date(value);
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
};

const formatScore = (score) => `${Math.round(Number(score || 0) * 100)}%`;

function TransactionsTable({
  data,
  onSelect,
  selectedTxn,
  totalCount,
  rowOffset = 0,
  loading = false,
}) {
  const [sortConfig, setSortConfig] = useState({
    key: "timestamp",
    direction: "desc",
  });

  const handleSort = (key) => {
    setSortConfig((current) => {
      if (current.key === key) {
        return {
          key,
          direction: current.direction === "asc" ? "desc" : "asc",
        };
      }
      return { key, direction: "asc" };
    });
  };

  const sortedData = useMemo(() => {
    const sorted = [...data];

    sorted.sort((a, b) => {
      let aValue = a[sortConfig.key];
      let bValue = b[sortConfig.key];

      if (sortConfig.key === "dayHour") {
        aValue = a.step;
        bValue = b.step;
      }

      if (sortConfig.key === "risk") {
        const riskOrder = { LOW: 1, MEDIUM: 2, HIGH: 3 };
        aValue = riskOrder[a.risk] ?? 0;
        bValue = riskOrder[b.risk] ?? 0;
      }

      if (typeof aValue === "string") {
        aValue = aValue.toUpperCase();
        bValue = bValue.toUpperCase();
      }

      if (aValue < bValue) return sortConfig.direction === "asc" ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === "asc" ? 1 : -1;
      return 0;
    });

    return sorted;
  }, [data, sortConfig]);

  const renderSortArrow = (key) => {
    if (sortConfig.key !== key) {
      return <span className="sort-arrow muted">↕</span>;
    }

    return (
      <span className="sort-arrow active">
        {sortConfig.direction === "asc" ? "↑" : "↓"}
      </span>
    );
  };

  return (
    <div className="table-section modern-table-section">
      <div className="table-toolbar">
        <div>
          <h2>Transaction List</h2>
          <p>Click a transaction row to open detailed analysis.</p>
        </div>

        <div className="table-results-count">
          Showing {sortedData.length.toLocaleString()} of{" "}
          {(totalCount ?? sortedData.length).toLocaleString()} transaction
          {(totalCount ?? sortedData.length) !== 1 ? "s" : ""}
        </div>
      </div>

      <div className={`table-shell${loading ? " table-shell-loading" : ""}`}>
        {loading ? (
          <div className="table-loading-overlay" role="status" aria-live="polite">
            <div className="table-loading-spinner" />
            <div>
              <strong>Loading next transaction page</strong>
              <span>Scoring 50 transactions with active agents...</span>
            </div>
          </div>
        ) : null}

        <div className="table-scroll-area">
          <table className="txn-table modern-txn-table">
            <thead>
              <tr>
                <th>#</th>

                <th onClick={() => handleSort("transaction_id")} className="sortable">
                  <span>Transaction ID</span>
                  {renderSortArrow("transaction_id")}
                </th>

                <th onClick={() => handleSort("timestamp")} className="sortable">
                  <span>Timestamp</span>
                  {renderSortArrow("timestamp")}
                </th>

                <th onClick={() => handleSort("type")} className="sortable">
                  <span>Type</span>
                  {renderSortArrow("type")}
                </th>

                <th onClick={() => handleSort("amount")} className="sortable">
                  <span>Amount</span>
                  {renderSortArrow("amount")}
                </th>

                <th onClick={() => handleSort("sender")} className="sortable">
                  <span>Sender</span>
                  {renderSortArrow("sender")}
                </th>

                <th onClick={() => handleSort("receiver")} className="sortable">
                  <span>Receiver</span>
                  {renderSortArrow("receiver")}
                </th>

                <th onClick={() => handleSort("final_score")} className="sortable">
                  <span>Final Rule-Based Score</span>
                  {renderSortArrow("final_score")}
                </th>

                <th onClick={() => handleSort("risk")} className="sortable">
                  <span>Risk Level</span>
                  {renderSortArrow("risk")}
                </th>

                <th onClick={() => handleSort("decision")} className="sortable">
                  <span>Decision</span>
                  {renderSortArrow("decision")}
                </th>
              </tr>
            </thead>

            <tbody>
              {sortedData.length > 0 ? (
                sortedData.map((txn, index) => (
                  <tr
                    key={txn.id}
                    onClick={() => onSelect(txn)}
                    className={`clickable-row ${
                      selectedTxn?.id === txn.id ? "selected-row" : ""
                    }`}
                  >
                    <td className="row-number-cell">{rowOffset + index + 1}</td>
                    <td>{txn.transaction_id ?? txn.id}</td>
                    <td>{formatTimestamp(txn.timestamp)}</td>
                    <td>{txn.type}</td>
                    <td className="amount-cell">
                      ${txn.amount.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </td>
                    <td>{txn.sender}</td>
                    <td>{txn.receiver}</td>
                    <td className="score-cell">
                      {formatScore(txn.final_score)}
                    </td>
                    <td>
                      <StatusBadge text={txn.risk} variant="risk" />
                    </td>
                    <td>
                      <StatusBadge text={txn.decision} variant="status" />
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="10" className="empty-table-state">
                    No transactions available for the selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default TransactionsTable;
