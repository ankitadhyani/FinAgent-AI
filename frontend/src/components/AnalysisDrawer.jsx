import StatusBadge from "./StatusBadge";

function AnalysisDrawer({ transaction, analysis, loading, onClose }) {
  if (!transaction) return null;

  const finalResult = analysis?.final_result ?? null;
  const fraudAgent = analysis?.fraud_agent ?? null;
  const behaviorAgent = analysis?.behavior_agent ?? null;
  const merchantAgent = analysis?.merchant_agent ?? null;
  const locationAgent = analysis?.location_agent ?? null;
  const ai_analyst_agent = analysis?.ai_analyst_agent ?? null;

  const fraudRisk = fraudAgent?.risk_level || transaction?.risk || "LOW";
  const behaviorRisk = behaviorAgent?.risk_level || "LOW";
  const merchantRisk = merchantAgent?.risk_level || "LOW";
  const locationRisk = locationAgent?.risk_level || "LOW";
  const aiDecision =
    ai_analyst_agent?.decision ||
    ai_analyst_agent?.risk_level ||
    transaction?.ai_decision ||
    "APPROVE";
  const aiRisk =
    aiDecision === "BLOCK"
      ? "HIGH"
      : aiDecision === "ESCALATE"
      ? "MEDIUM"
      : "LOW";

  const decision = finalResult?.decision || transaction?.decision || "APPROVE";
  const riskLevel = finalResult?.risk_level || transaction?.risk || "LOW";

  const fraudScore = fraudAgent?.fraud_score ?? fraudAgent?.score ?? 0;

  const behaviorScore = behaviorAgent?.behavior_score ?? behaviorAgent?.score ?? 0;

  const merchantScore = merchantAgent?.merchant_score ?? merchantAgent?.score ?? 0;

  const locationScore = locationAgent?.location_score ?? locationAgent?.score ?? 0;

  const aiScore = ai_analyst_agent?.ai_score ?? ai_analyst_agent?.score ?? 0;

  const decisionToneClass = `decision-tone-${String(decision).toLowerCase()}`;

  const fraudReasons = Array.isArray(fraudAgent?.reasons) && fraudAgent.reasons.length > 0
    ? fraudAgent.reasons
    : ["No significant fraud indicators detected."];

  const behaviorReasons = Array.isArray(behaviorAgent?.reasons) && behaviorAgent.reasons.length > 0
    ? behaviorAgent.reasons
    : ["No strong behavioral anomalies detected."];

  const merchantReasons = Array.isArray(merchantAgent?.reasons) && merchantAgent.reasons.length > 0
    ? merchantAgent.reasons
    : ["No receiver-side anomalies detected."];
  
  const locationReasons =
    Array.isArray(locationAgent?.reasons) && locationAgent.reasons.length > 0
      ? locationAgent.reasons
      : ["No location anomalies detected."];

  const aiReasons =
    Array.isArray(ai_analyst_agent?.reasons) && ai_analyst_agent.reasons.length > 0
      ? ai_analyst_agent.reasons
      : ["No strong AI Risk Analyst signal detected."];

  const formatAmount = (value) =>
    Number(value || 0).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });

  const primaryReason =
    Array.isArray(finalResult?.reasons) && finalResult.reasons.length > 0
      ? finalResult.reasons[0]
      : "No major risk signals were triggered.";


  const finalScore = Number(finalResult?.final_score ?? 0).toFixed(2);

  const summaryLine = loading
    ? "Running backend analysis..."
    : `${transaction.type} • $${formatAmount(transaction.amount)} • Risk: ${riskLevel} • ${decision}`;

  const explanationPoints = loading
    ? []
    : [
        `${String(transaction.sender).startsWith("M") ? "Receiver" : "Customer"} → ${
          String(transaction.receiver).startsWith("M") ? "Receiver" : "Customer"
        }`,
        `Primary signal: ${primaryReason}`,
      ];

  return (
    <>
      <div className="drawer-overlay" onClick={onClose}></div>

      <aside className="drawer final-drawer">
        <div className="drawer-header clean-drawer-header">
          <div>
            <h2>Transaction Risk Review</h2>
            <p>Investigation view for selected transaction</p>
            <strong className="drawer-header-summary">{summaryLine}</strong>
          </div>

          <button
            className="close-btn clean-close-btn"
            onClick={onClose}
            aria-label="Close drawer"
          >
            ×
          </button>
        </div>

        <div className="drawer-content clean-drawer-content">
          {loading ? (
            <div className="drawer-analysis-loading" role="status" aria-live="polite">
              <div className="drawer-loading-spinner" />
              <div>
                <strong>Running agent analysis</strong>
                <span>Fraud, behavior, receiver, and location agents are scoring this transaction. AI Risk Analyst is preparing an independent review.</span>
              </div>
            </div>
          ) : null}

          <section className={`drawer-panel risk-agent-panel risk-card-${String(fraudRisk).toLowerCase()}`}>
            <div className="drawer-panel-header">
              <div>
                <h3>Fraud Agent Analysis</h3>
                <p className="agent-score">Score: {Number(fraudScore).toFixed(2)}</p>
              </div>
              <StatusBadge text={fraudRisk} variant="risk" />
            </div>

            <ul className="reason-list">
              {fraudReasons.map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          </section>

          <section className={`drawer-panel risk-agent-panel risk-card-${String(behaviorRisk).toLowerCase()}`}>
            <div className="drawer-panel-header">
              <div>
                <h3>Behavior Agent Analysis</h3>
                <p className="agent-score">Score: {Number(behaviorScore).toFixed(2)}</p>
              </div>
              <StatusBadge text={behaviorRisk} variant="risk" />
            </div>

            <ul className="reason-list">
              {behaviorReasons.map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          </section>

          <section className={`drawer-panel risk-agent-panel risk-card-${String(merchantRisk).toLowerCase()}`}>
            <div className="drawer-panel-header">
              <div>
                <h3>Receiver Agent Analysis</h3>
                <p className="agent-score">Score: {Number(merchantScore).toFixed(2)}</p>
              </div>
              <StatusBadge text={merchantRisk} variant="risk" />
            </div>

            <ul className="reason-list">
              {merchantReasons.map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          </section>

          <section className={`drawer-panel risk-agent-panel risk-card-${String(locationRisk).toLowerCase()}`}>
            <div className="drawer-panel-header">
              <div>
                <h3>Location Agent Analysis</h3>
                <p className="agent-score">
                  Score: {Number(locationScore).toFixed(2)}
                </p>
              </div>

              <StatusBadge text={locationRisk} variant="risk" />
            </div>

            <ul className="reason-list">
              {locationReasons.map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          </section>

          <section className={`drawer-panel risk-agent-panel risk-card-${String(aiRisk).toLowerCase()}`}>
            <div className="drawer-panel-header">
              <div>
                <h3>AI Risk Analyst Review</h3>
                <p className="agent-score">Score: {Number(aiScore).toFixed(2)}</p>
              </div>

              <StatusBadge text={aiRisk} variant="risk" />
            </div>

            <ul className="reason-list">
              {aiReasons.map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          </section>
        </div>
        <section className={`drawer-footer-decision final-decision-clean ${decisionToneClass}`}>
          <div className="drawer-panel-header">
            <h3>Final Decision</h3>
            <div className="decision-pill-group">
              <span className="score-pill">Score {finalScore}</span>
              <StatusBadge text={decision} variant="status" />
            </div>
          </div>

          <p className="decision-note">
            This rule-based multi-agent score assigns <strong>{riskLevel}</strong> risk
            and recommends <strong>{decision}</strong>. AI Risk Analyst is shown separately.
          </p>
        </section>
      </aside>
    </>
  );
}

export default AnalysisDrawer;
