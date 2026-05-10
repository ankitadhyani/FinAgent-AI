import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import { useRef } from "react";

import { useEffect, useMemo, useState } from "react";
import {
  Download,
  FileText,
  Lightbulb,
  Search,
  ShieldAlert,
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

function buildCase(txn, index) {
  return {
    id: `INV-${String(100245 + index).padStart(6, "0")}`,
    transaction: txn,
    reason: getReason(txn),
  };
}

function formatAmount(value) {
  return Number(value || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

const formatValue = (value) => {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "number") return Number.isInteger(value) ? value : value.toFixed(2);
  return String(value);
};

const buildFraudReasons = (txn) => {
  const reasons = [];
  if (txn.type === "TRANSFER" || txn.type === "CASH_OUT") {
    reasons.push(`${txn.type} type is commonly associated with fraud.`);
  }
  if (Number(txn.amount || 0) > 200000) {
    reasons.push(`High transaction amount detected: $${formatAmount(txn.amount)}.`);
  }
  if (txn.balance_risk === 1) reasons.push("Balance-risk pattern detected.");
  if (txn.amount_risk === 1) reasons.push("Amount risk signal is active.");
  return reasons.length ? reasons : ["No major fraud pattern detected."];
};

const buildBehaviorReasons = (txn) => {
  const reasons = [];
  if (txn.customer_amount_ratio) {
    reasons.push(`Transaction is ${Number(txn.customer_amount_ratio).toFixed(2)}x the customer's average amount.`);
  }
  if (txn.velocity_risk === 1) reasons.push("High transaction velocity detected.");
  if (txn.behavior_risk === 1) reasons.push("Customer behavior risk signal is active.");
  if (txn.customer_txn_count && Number(txn.customer_txn_count) < 5) {
    reasons.push("Limited customer history available.");
  }
  return reasons.length ? reasons : ["No strong behavioral anomaly detected."];
};

const buildMerchantReasons = (txn) => {
  const reasons = [];
  if (txn.type === "TRANSFER" || txn.type === "CASH_OUT") {
    reasons.push(`Risky destination transaction type: ${txn.type}.`);
  }
  if (Number(txn.amount || 0) > 200000) reasons.push("High-value transfer/cash-out transaction.");
  if (txn.device_risk === 1) reasons.push("Device risk signal is active.");
  if (txn.balance_risk === 1) reasons.push("Balance risk signal is active.");
  return reasons.length ? reasons : ["No strong counterparty anomaly detected."];
};

const buildLocationReasons = (txn) => {
  const reasons = [];
  if (txn.geo_distance_km) {
    reasons.push(`Geographic distance: ${Number(txn.geo_distance_km).toFixed(2)} km.`);
  }
  if (txn.geo_distance_km && Number(txn.geo_distance_km) > 500) {
    reasons.push(`Large geographic jump detected: ${Number(txn.geo_distance_km).toFixed(2)} km.`);
  }
  if (txn.geo_risk === 1) reasons.push("Location risk signal is active.");
  return reasons.length ? reasons : ["No location anomaly detected."];
};

const buildAIReasons = (txn) => {
  const reasons = [];

  if (txn.ai_reasoning) {
    reasons.push(txn.ai_reasoning);
  }

  if (txn.ai_score && Number(txn.ai_score) > 0) {
    reasons.push("AI Risk Analyst detected contextual transaction risk patterns.");
  }

  return reasons.length ? reasons : ["No strong AI Risk Analyst signal detected."];
};

function calculateDecisionConfidence(txn) {
  const scores = [
    Number(txn?.fraud_score || 0),
    Number(txn?.behavior_score || 0),
    Number(txn?.merchant_score || 0),
    Number(txn?.location_score || 0),
    Number(txn?.ai_score || 0),
  ];

  const avg = scores.reduce((sum, score) => sum + score, 0) / scores.length;

  const disagreement =
    scores.reduce((sum, score) => sum + Math.abs(score - avg), 0) / scores.length;

  const agreement = Math.max(0, 1 - disagreement);

  const finalScore = Number(txn?.final_score || 0);
  const confidence = Math.round((agreement * 0.6 + finalScore * 0.4) * 100);

  return Math.min(99, Math.max(1, confidence));
}


function Reports({ simulationWindow }) {
  const [transactions, setTransactions] = useState([]);
  const [loadingTransactions, setLoadingTransactions] = useState(true);
  const [transactionsError, setTransactionsError] = useState("");
  const [selectedCaseId, setSelectedCaseId] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  const reportRef = useRef(null);

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

        console.error("Failed to fetch report data:", error);
        setTransactionsError("Failed to load report data from backend.");
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

  const reportCases = useMemo(() => {
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
      .sort((a, b) => Number(b.final_score || 0) - Number(a.final_score || 0))
      .map(buildCase);
  }, [transactions, simulationWindow]);

  const filteredReportCases = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();

    if (!normalizedSearch) return reportCases;

    return reportCases.filter((item) => {
      const txn = item.transaction;

      return [
        item.id,
        txn.transaction_id,
        txn.sender,
        txn.receiver,
        txn.type,
        txn.decision,
        txn.risk,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(normalizedSearch);
    });
  }, [reportCases, searchTerm]);

  useEffect(() => {
    if (!filteredReportCases.length) {
      setSelectedCaseId("");
      return;
    }

    const exists = filteredReportCases.some(
      (item) => item.id === selectedCaseId
    );

    if (!exists) {
      setSelectedCaseId(filteredReportCases[0].id);
    }
  }, [filteredReportCases, selectedCaseId]);

  const selectedCase =
    filteredReportCases.find((item) => item.id === selectedCaseId) ||
    filteredReportCases[0] ||
    null;

  const selectedTxn = selectedCase?.transaction ?? null;
  const finalScore = Number(selectedTxn?.final_score ?? 0);
  const reasonGroups = selectedTxn
    ? [
        ["Fraud Agent", selectedTxn.fraud_score, buildFraudReasons(selectedTxn)],
        ["Behavior Agent", selectedTxn.behavior_score, buildBehaviorReasons(selectedTxn)],
        ["Receiver Agent", selectedTxn.merchant_score, buildMerchantReasons(selectedTxn)],
        ["Location Agent", selectedTxn.location_score, buildLocationReasons(selectedTxn)],
        ["AI Risk Analyst Agent", selectedTxn.ai_score, buildAIReasons(selectedTxn)],
      ]
    : [];
  const transactionDetails = selectedTxn
    ? [
        ["Transaction ID", selectedTxn.transaction_id ?? selectedTxn.id],
        ["Timestamp", formatTimestamp(selectedTxn.timestamp)],
        ["Step", selectedTxn.step],
        ["Type", selectedTxn.type],
        ["Amount", `$${formatAmount(selectedTxn.amount)}`],
        ["Sender", selectedTxn.sender],
        ["Receiver", selectedTxn.receiver],
        ["Old Origin Balance", `$${formatAmount(selectedTxn.oldbalanceOrg)}`],
        ["New Origin Balance", `$${formatAmount(selectedTxn.newbalanceOrig)}`],
        ["Old Destination Balance", `$${formatAmount(selectedTxn.oldbalanceDest)}`],
        ["New Destination Balance", `$${formatAmount(selectedTxn.newbalanceDest)}`],
        ["Final Score", finalScore.toFixed(2)],
        ["Risk Level", selectedTxn.risk],
        ["Decision", selectedTxn.decision],
        ["Fraud Score", formatValue(selectedTxn.fraud_score)],
        ["Behavior Score", formatValue(selectedTxn.behavior_score)],
        ["Receiver Score", formatValue(selectedTxn.merchant_score)],
        ["Location Score", formatValue(selectedTxn.location_score)],
        ["AI Analyst Score", formatValue(selectedTxn.ai_score)],
        ["AI Decision", formatValue(selectedTxn.ai_decision)],
        ["AI Reasoning", formatValue(selectedTxn.ai_reasoning)],
        ["Customer Txn Count", formatValue(selectedTxn.customer_txn_count)],
        ["Customer Avg Amount", `$${formatAmount(selectedTxn.customer_avg_amount)}`],
        ["Customer Amount Ratio", formatValue(selectedTxn.customer_amount_ratio)],
        ["Geo Distance KM", formatValue(selectedTxn.geo_distance_km)],
        ["Geo Risk", formatValue(selectedTxn.geo_risk)],
        ["Device Type", formatValue(selectedTxn.device_type)],
        ["Device Risk", formatValue(selectedTxn.device_risk)],
        ["Velocity Risk", formatValue(selectedTxn.velocity_risk)],
        ["Behavior Risk", formatValue(selectedTxn.behavior_risk)],
        ["Amount Risk", formatValue(selectedTxn.amount_risk)],
        ["Balance Risk", formatValue(selectedTxn.balance_risk)],
        ["Actual Fraud Label", formatValue(selectedTxn.isFraud)],
        ["System Flagged Fraud", formatValue(selectedTxn.isFlaggedFraud)],
      ]
    : [];

  const decisionConfidence = selectedTxn
  ? calculateDecisionConfidence(selectedTxn)
  : 0;

  const recommendation =
    selectedTxn?.decision === "BLOCK"
      ? "Keep transaction blocked and create a permanent monitoring rule for this pattern."
      : selectedTxn?.decision === "ESCALATE"
      ? "Escalate for manual review and verify beneficiary legitimacy before releasing funds."
      : "No immediate escalation required. Continue monitoring for repeated patterns.";

  const exportReportPdf = async () => {
    if (!reportRef.current || !selectedTxn) return;

    const canvas = await html2canvas(reportRef.current, {
      scale: 2,
      backgroundColor: "#0b1020",
    });

    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF("p", "mm", "a4");

    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();

    const imgWidth = pageWidth;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    let heightLeft = imgHeight;
    let position = 0;

    pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    while (heightLeft > 0) {
      position -= pageHeight;
      pdf.addPage();
      pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    pdf.save(`FinAgent_Report_${selectedTxn.transaction_id}.pdf`);
  };

  if (loadingTransactions) {
    return (
      <div className="dashboard reports-page">
        <header className="dashboard-page-header">
          <h1>Reports</h1>
          <p>Generate investigation narratives and case summaries for suspicious activity.</p>
        </header>

        <div className="loading-panel">
          <h2>Loading reports</h2>
          <p>Preparing report workspace...</p>
        </div>
      </div>
    );
  }

  if (transactionsError) {
    return (
      <div className="dashboard reports-page">
        <header className="dashboard-page-header">
          <h1>Reports</h1>
          <p>Generate investigation narratives and case summaries for suspicious activity.</p>
        </header>

        <div className="loading-panel">
          <h2>Unable to load reports</h2>
          <p>{transactionsError}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard reports-page">
      <header className="dashboard-page-header reports-page-header">
        <div>
          <h1>Reports</h1>
          <p>Generate investigation narratives and case summaries for suspicious activity.</p>
        </div>

        <span className="reports-count-pill">{filteredReportCases.length} reportable cases</span>
      </header>

      <section className="reports-control-card">
        <div className="reports-search-group">
          <label htmlFor="report-search">Search Transaction</label>
          <div className="reports-search-field">
            <Search size={16} strokeWidth={2.3} />
            <input
              id="report-search"
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search transaction ID, sender, receiver..."
            />
          </div>
        </div>
        <div className="reports-select-group">
          <label htmlFor="report-case-select">Select Investigation</label>
          <select
            id="report-case-select"
            value={selectedCase?.id ?? ""}
            onChange={(event) => setSelectedCaseId(event.target.value)}
          >
            {filteredReportCases.length ? (
              filteredReportCases.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.transaction.transaction_id} - {item.transaction.type} - ${formatAmount(item.transaction.amount)}
                </option>
              ))
            ) : (
              <option value="">No reportable cases</option>
            )}
          </select>
        </div>

        <button className="report-primary-btn" type="button" onClick={exportReportPdf}>
          <Download size={15} strokeWidth={2.3} />
          Export PDF
        </button>
      </section>

      {selectedCase && selectedTxn ? (
        <section className="reports-layout" ref={reportRef}>
          <div className="report-case-card">
            <h2>Summary</h2>
            <p>Selected investigation context.</p>

            <div className="report-summary-grid">
              <div className="summary-item">
                <span>Transaction ID</span>
                <strong>{selectedTxn.transaction_id}</strong>
              </div>

              <div className="summary-item">
                <span>Timestamp</span>
                <strong>{formatTimestamp(selectedTxn.timestamp)}</strong>
              </div>

              <div className="summary-item">
                <span>Type</span>
                <strong>{selectedTxn.type}</strong>
              </div>

              <div className="summary-item">
                <span>Amount</span>
                <strong>{`$${formatAmount(selectedTxn.amount)}`}</strong>
              </div>

              <div className="summary-item">
                <span>Sender</span>
                <strong>{selectedTxn.sender}</strong>
              </div>

              <div className="summary-item">
                <span>Receiver</span>
                <strong>{selectedTxn.receiver}</strong>
              </div>

              <div className="summary-item">
                <span>Risk Score</span>
                <strong>{selectedTxn.final_score?.toFixed(2)}</strong>
              </div>

              <div className="summary-item">
                <span>Risk Level</span>
                <strong>{selectedTxn.risk}</strong>
              </div>

              <div className="summary-item">
                <span>Decision</span>
                <strong>{selectedTxn.decision}</strong>
              </div>

              <div className="summary-item">
                <span>Fraud Score</span>
                <strong>{selectedTxn.fraud_score?.toFixed(2)}</strong>
              </div>

              <div className="summary-item">
                <span>Behavior Score</span>
                <strong>{selectedTxn.behavior_score?.toFixed(2)}</strong>
              </div>

              <div className="summary-item">
                <span>Receiver Score</span>
                <strong>{selectedTxn.merchant_score?.toFixed(2)}</strong>
              </div>

              <div className="summary-item">
                <span>Location Score</span>
                <strong>{selectedTxn.location_score?.toFixed(2)}</strong>
              </div>

              <div className="summary-item">
                <span>AI Analyst Score</span>
                <strong>{selectedTxn.ai_score?.toFixed(2) ?? "0.00"}</strong>
              </div>

              <div className="summary-item">
                <span>AI Decision</span>
                <strong>{selectedTxn.ai_decision || "—"}</strong>
              </div>

              <div className="summary-item">
                <span>AI Reasoning</span>
                <strong>{selectedTxn.ai_reasoning || "—"}</strong>
              </div>

              <div className="summary-item">
                <span>Customer Amount Ratio</span>
                <strong>{selectedTxn.customer_amount_ratio?.toFixed(2)}</strong>
              </div>

              <div className="summary-item">
                <span>Geo Distance KM</span>
                <strong>{selectedTxn.geo_distance_km?.toFixed(2)}</strong>
              </div>

              <div className="summary-item">
                <span>Device Type</span>
                <strong>{selectedTxn.device_type}</strong>
              </div>
            </div>
          </div>
          <article className="report-document-card">
            <div className="report-document-header">
              <div>
                <h2>AI Investigation Report</h2>
                <p>Generated case narrative for analyst review.</p>
              </div>
              <FileText size={22} strokeWidth={2.2} />
            </div>

            <section className="report-section">
              <h3>Transaction Overview</h3>
              <p>
                Transaction of <strong>${formatAmount(selectedTxn.amount)}</strong> was observed
                at <strong>{formatTimestamp(selectedTxn.timestamp)}</strong>. The payment type is{" "}
                <strong>{selectedTxn.type}</strong>, moving funds from{" "}
                <strong>{selectedTxn.sender}</strong> to <strong>{selectedTxn.receiver}</strong>.
              </p>
            </section>

            <section className="report-section">
              <h3>Key Findings</h3>
              <ul>
                <li>Risk score is {finalScore.toFixed(2)}, classified as {selectedTxn.risk}.</li>
                <li>System decision is {selectedTxn.decision} based on current risk policy.</li>
                <li>{selectedCase.reason}.</li>
                <li>Primary signal: {reasonGroups.flatMap(([, , reasons]) => reasons)[0]}</li>
              </ul>
            </section>

            <section className="report-section">
              <h3>Agent Analysis</h3>
              <ul className="agent-analysis-list">
                {reasonGroups.map(([agentName, score, reasons]) => (
                  <li
                    key={agentName}
                    className={`agent-analysis-item ${
                      agentName === "Receiver Agent"
                        ? "agent-analysis-merchant"
                        : agentName === "AI Risk Analyst Agent"
                        ? "agent-analysis-ai"
                        : `agent-analysis-${agentName.split(" ")[0].toLowerCase()}`
                    }`}
                  >
                    <span>{agentName}:</span> Score {Number(score ?? 0).toFixed(2)}.
                    <ul className="report-reason-list">
                      {reasons.map((reason, index) => (
                        <li key={index}>{reason}</li>
                      ))}
                    </ul>
                  </li>
                ))}
              </ul>
            </section>
          </article>

          <aside className="report-side-rail">
            <section className="report-side-card report-recommendation-block">
              <div className="report-recommendation-icon">
                <Lightbulb size={20} strokeWidth={2.3} />
              </div>
              <div>
                <span>Recommendation</span>
                <p>{recommendation}</p>
              </div>
            </section>

            <section
              className={`report-side-card report-risk-callout report-risk-${selectedTxn.risk.toLowerCase()}`}
            >
              <ShieldAlert size={20} strokeWidth={2.3} />
              <div>
                <span>Risk Level</span>
                <strong>{selectedTxn.risk}</strong>
              </div>
            </section>

            <section className="report-side-card report-confidence">
              <span>Decision Confidence</span>

              <div className="report-confidence-score">
                <strong>{decisionConfidence}%</strong>
              </div>

              <p className="report-confidence-description">
                Confidence derived from agreement consistency across fraud, sender and receiver behavior, location, and AI Risk Analyst agents.
              </p>

              <div className="report-confidence-track">
                <i style={{ width: `${decisionConfidence}%` }} />
              </div>
            </section>
          </aside>
        </section>
      ) : (
        <section className="report-empty-card">
          <h2>No reportable cases</h2>
          <p>The selected timestamp window does not contain suspicious cases.</p>
        </section>
      )}
    </div>
  );
}

export default Reports;
