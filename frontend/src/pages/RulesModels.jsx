import { useEffect, useMemo, useState } from "react";
import {
  Bot,
  CheckCircle2,
  Gauge,
  ListChecks,
  Save,
} from "lucide-react";
import { getRiskConfig, getModelMetrics, getTransactions } from "../api/client";

const agentMeta = {
  fraud: { label: "Fraud Agent", accent: "#60a5fa" },
  behavior: { label: "Behavior Agent", accent: "#22c55e" },
  merchant: { label: "Receiver Agent", accent: "#f59e0b" },
  location: { label: "Location Agent", accent: "#94a3b8" },
};

const fallbackConfig = {
  agent_risk_bands: {
    fraud_agent: { HIGH: 0.35, MEDIUM: 0.3 },
    behavior_agent: { HIGH: 0.3, MEDIUM: 0.2 },
    merchant_agent: { HIGH: 0.15, MEDIUM: 0.1 },
    location_agent: { HIGH: 0.1, MEDIUM: 0.05 },
  },
  final_agent_weights: {
    fraud: 0.45,
    behavior: 0.3,
    merchant: 0.15,
    location: 0.1,
  },
  final_system_thresholds: {
    ESCALATE: 0.3,
    BLOCK: 0.5,
  },
  agent_configs: {},
};

function formatPercent(value) {
  return `${(Number(value || 0) * 100).toFixed(1)}%`;
}

function buildDetectionRules(config) {
  const agents = config.agent_configs || {};
  return [
    {
      rule: `High amount > $${Number(agents.fraud_agent?.high_amount_threshold ?? 200000).toLocaleString()}`,
      agent: "Fraud Agent",
      impact: "High",
      status: "Active",
    },
    {
      rule: "Suspicious TRANSFER / CASH_OUT pattern",
      agent: "Fraud Agent",
      impact: "High",
      status: "Active",
    },
    {
      rule: "Balance anomaly detected",
      agent: "Fraud Agent",
      impact: "High",
      status: "Active",
    },
    {
      rule: `Amount ratio > ${agents.behavior_agent?.amount_ratio_medium_threshold ?? 5}x average`,
      agent: "Behavior Agent",
      impact: "Medium",
      status: "Active",
    },
    {
      rule: "Velocity risk detected",
      agent: "Behavior Agent",
      impact: "High",
      status: "Active",
    },
    {
      rule: `Unique senders >= ${agents.merchant_agent?.unique_senders_medium_threshold ?? 5}`,
      agent: "Receiver Agent",
      impact: "Medium",
      status: "Active",
    },
    {
      rule: `Geo distance > ${agents.location_agent?.moderate_distance_threshold ?? 100} km`,
      agent: "Location Agent",
      impact: "Medium",
      status: "Active",
    },
    {
      rule: `Geo distance > ${agents.location_agent?.extreme_distance_threshold ?? 500} km`,
      agent: "Location Agent",
      impact: "High",
      status: "Active",
    },
  ];
}

function RulesModels() {
  const [activeTab, setActiveTab] = useState("policy");
  const [riskConfig, setRiskConfig] = useState(fallbackConfig);
  const [modelMetrics, setModelMetrics] = useState(null);
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    let isActive = true;

    getRiskConfig()
      .then((config) => {
        if (isActive) setRiskConfig({ ...fallbackConfig, ...config });
      })
      .catch(() => {
        if (isActive) setRiskConfig(fallbackConfig);
      });

    getModelMetrics()
      .then((metrics) => {
        if (isActive) setModelMetrics(metrics);
      })
      .catch((error) => {
        console.error("Failed to load model metrics:", error);
      });

    getTransactions({ limit: 600, offset: 0 })
      .then((response) => {
        if (isActive) setTransactions(response.items || []);
      })
      .catch((error) => {
        console.error("Failed to load transactions for AI accuracy:", error);
      });

    return () => {
      isActive = false;
    };
  }, []);

  const weights = useMemo(
    () =>
      Object.entries(riskConfig.final_agent_weights || {}).map(([key, value]) => ({
        key,
        value,
        ...(agentMeta[key] || { label: key, accent: "#94a3b8" }),
      })),
    [riskConfig]
  );

  const thresholds = riskConfig.final_system_thresholds || {};
  const agentBands = riskConfig.agent_risk_bands || {};
  const detectionRules = useMemo(() => buildDetectionRules(riskConfig), [riskConfig]);

  const totalWeight = useMemo(
    () => weights.reduce((sum, item) => sum + Number(item.value || 0), 0),
    [weights]
  );

  const agentDisplayNames = {
    fraud_agent: "Fraud",
    behavior_agent: "Behavior",
    merchant_agent: "Receiver",
    location_agent: "Location",
  };

  const aiAccuracy = useMemo(() => {
    if (!transactions.length) return 0;

    const correct = transactions.filter((txn) => {
      const actualFraud = Number(txn.isFraud) === 1;
      const aiFlagged =
        txn.ai_decision === "ESCALATE" || txn.ai_decision === "BLOCK";

      return actualFraud === aiFlagged;
    }).length;

    return correct / transactions.length;
  }, [transactions]);

  const ruleBasedAccuracy = useMemo(() => {
    if (!transactions.length) return 0;

    const correct = transactions.filter((txn) => {
      const actualFraud = Number(txn.isFraud) === 1;
      const ruleFlagged =
        txn.decision === "ESCALATE" || txn.decision === "BLOCK";

      return actualFraud === ruleFlagged;
    }).length;

    return correct / transactions.length;
  }, [transactions]);

  return (
    <div className="dashboard rules-page">
      <header className="dashboard-page-header rules-page-header">
        <div>
          <h1>Rules & Models</h1>
          <p>Configure fraud detection policies, multi-agent scoring logic, and investigation thresholds.</p>
        </div>

        <div className="rules-header-actions">
          <span className="rules-status-pill">
            <CheckCircle2 size={15} strokeWidth={2.4} />
            Active policy
          </span>

          <button className="rules-primary-btn" type="button">
            <Save size={15} strokeWidth={2.4} />
            Save Policy
          </button>
        </div>
      </header>

      <div className="rules-tabs" role="tablist" aria-label="Rules and models sections">
        <button
          className={`rules-tab-button${activeTab === "policy" ? " active" : ""}`}
          type="button"
          onClick={() => setActiveTab("policy")}
        >
          Policy Configuration
        </button>
        <button
          className={`rules-tab-button${activeTab === "performance" ? " active" : ""}`}
          type="button"
          onClick={() => setActiveTab("performance")}
        >
          Performance Summary
        </button>
      </div>

      {activeTab === "policy" ? (
        <section className="rules-grid">
        <article className="rules-card model-weights-card">
          <div className="rules-card-header">
            <div className="rules-card-icon blue">
              <Bot size={20} strokeWidth={2.3} />
            </div>
            <div>
              <h2>Model Weights</h2>
              <p>Relative contribution of each risk agent.</p>
            </div>
          </div>

          <div className="weight-list">
            {weights.map((item) => (
              <label
                className={item.disabled ? "weight-row weight-row-disabled" : "weight-row"}
                key={item.key}
              >
                <div>
                  <span>
                    {item.label}
                    {item.note ? <em>{item.note}</em> : null}
                  </span>
                  <strong>{formatPercent(item.value)}</strong>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={item.value}
                  disabled
                  style={{ accentColor: item.accent }}
                  readOnly
                />
              </label>
            ))}
          </div>

          <div className={Math.abs(totalWeight - 1) < 0.001 ? "weight-total valid" : "weight-total warning"}>
            <span>Total</span>
            <strong>{formatPercent(totalWeight)}</strong>
          </div>
        </article>

        <article className="rules-card detection-rules-card">
          <div className="rules-card-header">
            <div className="rules-card-icon orange">
              <ListChecks size={20} strokeWidth={2.3} />
            </div>
            <div>
              <h2>Top Detection Rules</h2>
              <p>Currently active signals driving agent decisions.</p>
            </div>
          </div>

          <div className="rules-table-wrap">
            <table className="rules-table">
              <thead>
                <tr>
                  <th>Rule</th>
                  <th>Agent</th>
                  <th>Impact</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {detectionRules.map((item) => (
                  <tr key={`${item.rule}-${item.agent}`}>
                    <td>{item.rule}</td>
                    <td>{item.agent}</td>
                    <td>
                      <span className={`rule-impact ${item.impact.toLowerCase()}`}>
                        {item.impact}
                      </span>
                    </td>
                    <td>
                      <span className={`rule-status ${item.status.toLowerCase()}`}>
                        {item.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <aside className="rules-card threshold-card">
          <div className="rules-card-header">
            <div className="rules-card-icon green">
              <Gauge size={20} strokeWidth={2.3} />
            </div>
            <div>
              <h2>Thresholds</h2>
              <p>Current decision cutoffs for risk scoring.</p>
            </div>
          </div>

          <div className="threshold-list">
            <label className="threshold-row">
              <div>
                <span>BLOCK Threshold</span>
                <strong>{Number(thresholds.BLOCK ?? 0).toFixed(2)}</strong>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={thresholds.BLOCK ?? 0}
                disabled
                readOnly
              />
            </label>

            <label className="threshold-row">
              <div>
                <span>ESCALATE Threshold</span>
                <strong>{Number(thresholds.ESCALATE ?? 0).toFixed(2)}</strong>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={thresholds.ESCALATE ?? 0}
                disabled
                readOnly
              />
            </label>
          </div>

          <div className="future-tuning-card">
            <div>
              <h3>Agent Risk Bands</h3>

              {Object.entries(agentBands).map(([agent, bands]) => (
                <div className="agent-band-row compact" key={agent}>
                  <span className="agent-band-name">
                    {agentDisplayNames[agent] || agent}
                  </span>
                  <div className="agent-band-values">
                    <span>High: {Number(bands.HIGH).toFixed(2)}</span>
                    <span>Medium: {Number(bands.MEDIUM).toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </section>
      ) : (
        <section className="performance-summary-panel">
          <div className="model-performance-header">
            <h2>Detection Performance Summary</h2>
            <p>
              Rule-based scoring and AI Analyst decisions are evaluated on the same sampled demo transactions.
            </p>
          </div>

          <div className="performance-card-grid">
            <article className="model-performance-card">
              <span>Rule-Based Detection Accuracy</span>
              <strong>{formatPercent(ruleBasedAccuracy)}</strong>
              <p>Final rule-based multi-agent scoring accuracy across PaySim transactions.</p>
            </article>

            <article className="model-performance-card">
              <span>AI Analyst Accuracy</span>
              <strong>{formatPercent(aiAccuracy)}</strong>
              <p>AI decisions correctly aligned with known fraud labels.</p>
            </article>
          </div>
        </section>
      )}
    </div>
  );
}

export default RulesModels;
