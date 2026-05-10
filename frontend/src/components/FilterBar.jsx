/**
 * FilterBar.jsx
 *
 * Top control panel for simulation filtering.
 * Allows users to filter transactions by:
 * - Timestamp window
 * - Risk level
 * - Transaction type
 *
 * Triggers Apply Filters action.
 */

function FilterBar({
  startDate,
  endDate,
  riskLevel,
  txnType,
  resultCount,
  minDate,
  maxDate,
  onStartDateChange,
  onEndDateChange,
  onRiskLevelChange,
  onTxnTypeChange,
  onApply,
  onReset,
}) {
  return (
    <div className="filter-bar final-filter-bar">
      <div className="filter-top-row">
        <div>
          <h2>Simulation Time Window</h2>
          <p>Filter transactions using timestamps and risk criteria.</p>
        </div>

        <div className="result-pill">
          {resultCount} matching transaction{resultCount !== 1 ? "s" : ""}
        </div>
      </div>

      <div className="filter-main-layout">
        <div className="filter-slider-column">
          <div className="filter-controls-grid single-row-controls">
            <div className="filter-group">
              <label htmlFor="start-date">Start Timestamp</label>
              <input
                id="start-date"
                type="date"
                min={minDate}
                max={maxDate}
                value={startDate}
                onChange={(e) => onStartDateChange(e.target.value)}
              />
            </div>
            <div className="filter-group">
              <label htmlFor="end-date">End Timestamp</label>
              <input
                id="end-date"
                type="date"
                min={minDate}
                max={maxDate}
                value={endDate}
                onChange={(e) => onEndDateChange(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="filter-controls-column">
          <div className="filter-controls-grid single-row-controls">
            <div className="filter-group">
              <label htmlFor="risk-level">Risk Level</label>
              <select
                id="risk-level"
                value={riskLevel}
                onChange={(e) => onRiskLevelChange(e.target.value)}
              >
                <option value="ALL">All</option>
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
              </select>
            </div>

            <div className="filter-group">
              <label htmlFor="txn-type">Transaction Type</label>
              <select
                id="txn-type"
                value={txnType}
                onChange={(e) => onTxnTypeChange(e.target.value)}
              >
                <option value="ALL">All</option>
                <option value="PAYMENT">PAYMENT</option>
                <option value="TRANSFER">TRANSFER</option>
                <option value="CASH_OUT">CASH_OUT</option>
              </select>
            </div>

            <div className="filter-actions inline-actions">
              <button className="apply-btn" onClick={onApply}>
                Apply Filters
              </button>
              <button className="reset-btn" onClick={onReset}>
                Reset
              </button>
            </div>
          </div>
        </div>
      </div>

      {resultCount === 0 && (
        <div className="no-results-banner">
          No transactions match the current filters.
        </div>
      )}
    </div>
  );
}

export default FilterBar;
