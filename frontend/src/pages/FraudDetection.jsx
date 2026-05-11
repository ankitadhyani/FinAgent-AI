import { useEffect, useMemo, useState } from "react";
import {
  Bot,
  Clock3,
  Crosshair,
  MapPin,
  ShieldAlert,
  ShieldCheck,
  BadgeDollarSign,
  TrendingUp,
  Users,
} from "lucide-react";
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { getRiskConfig, getTransactions } from "../api/client";

const riskColors = {
  High: "#ef4444",
  Medium: "#f59e0b",
  Low: "#22c55e",
};

const toDateValue = (value) => (value ? String(value).slice(0, 10) : "");
const toTime = (value, endOfDay = false) => {
  if (!value) return endOfDay ? Infinity : -Infinity;
  return new Date(`${value}T${endOfDay ? "23:59:59" : "00:00:00"}`).getTime();
};

function percent(part, total) {
  return total > 0 ? Math.round((part / total) * 100) : 0;
}

// Fallback values in case backend fails
const defaultAgentRiskBands = {
  fraud_agent: { HIGH: 0.35, MEDIUM: 0.3 },
  behavior_agent: { HIGH: 0.3, MEDIUM: 0.2 },
  merchant_agent: { HIGH: 0.15, MEDIUM: 0.1 },
  location_agent: { HIGH: 0.3, MEDIUM: 0.15 },
};

function scoreRisk(score, agentName, agentRiskBands) {
  const bands = agentRiskBands?.[agentName] || defaultAgentRiskBands[agentName] || {};
  if (score >= Number(bands.HIGH ?? 1)) return "High";
  if (score >= Number(bands.MEDIUM ?? 1)) return "Medium";
  return "Low";
}

function AgentCard({ icon: Icon, title, score, risk, detail, tone, disabled = false }) {
  return (
    <article className={`agent-card agent-card-${tone}${disabled ? " agent-card-disabled" : ""}`}>
      <div className="agent-card-icon">
        <Icon size={22} strokeWidth={2.3} />
      </div>
      <div>
        <span>{title}</span>
        <strong>{score}</strong>
        <p>{risk} Risk</p>
        <small>{detail}</small>
      </div>
    </article>
  );
}

function RiskFactorRow({ label, value, tone }) {
  return (
    <div className="risk-factor-row">
      <div>
        <span>{label}</span>
        <strong>{value}%</strong>
      </div>
      <div className="risk-factor-track">
        <i className={`risk-factor-fill risk-factor-fill-${tone}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

function RuntimeMetric({ icon: Icon, label, value, detail }) {
  return (
    <article className="runtime-metric-card">
      <div className="runtime-metric-icon">
        <Icon size={20} strokeWidth={2.3} />
      </div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <p>{detail}</p>
      </div>
    </article>
  );
}

function FraudDetection() {
  const [transactions, setTransactions] = useState([]);
  const [agentRiskBands, setAgentRiskBands] = useState(defaultAgentRiskBands);
  const [loadingTransactions, setLoadingTransactions] = useState(true);
  const [transactionsError, setTransactionsError] = useState("");

  useEffect(() => {
    let isActive = true;

    const fetchTransactions = async () => {
      try {
        setLoadingTransactions(true);
        setTransactionsError("");

        const [response, config] = await Promise.all([
          getTransactions({ limit: 600, offset: 0 }),
          getRiskConfig().catch(() => ({ agent_risk_bands: defaultAgentRiskBands })),
        ]);

        if (!isActive) return;

        setTransactions(response.items);
        setAgentRiskBands(config.agent_risk_bands || defaultAgentRiskBands);
      } catch (error) {
        if (!isActive) return;

        console.error("Failed to fetch transactions:", error);
        setTransactionsError("Failed to load fraud detection data from backend.");
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

  const filteredTransactions = useMemo(() => {
    return transactions;
  }, [transactions]);

  const metrics = useMemo(() => {
    const total = filteredTransactions.length;

    const avgScore = (field) =>
      total > 0
        ? filteredTransactions.reduce(
            (sum, txn) => sum + Number(txn[field] || 0),
            0
          ) / total
        : 0;

    const highRisk = filteredTransactions.filter((txn) => txn.risk === "HIGH").length;
    const mediumRisk = filteredTransactions.filter((txn) => txn.risk === "MEDIUM").length;
    const lowRisk = filteredTransactions.filter((txn) => txn.risk === "LOW").length;
    const escalated = filteredTransactions.filter((txn) => txn.decision === "ESCALATE").length;
    const blocked = filteredTransactions.filter((txn) => txn.decision === "BLOCK").length;
    const flagged = escalated + blocked;
    const transferVolume = filteredTransactions.filter((txn) => txn.type === "TRANSFER").length;
    const cashOutVolume = filteredTransactions.filter((txn) => txn.type === "CASH_OUT").length;
    const highValue = filteredTransactions.filter((txn) => Number(txn.amount || 0) >= 50000).length;

    return {
      total,
      highRisk,
      mediumRisk,
      lowRisk,
      escalated,
      blocked,
      flagged,
      transferVolume,
      cashOutVolume,
      highValue,
      fraudScore: avgScore("fraud_score"),
      behaviorScore: avgScore("behavior_score"),
      merchantScore: avgScore("merchant_score"),
      locationScore: avgScore("location_score"),
      aiScore: avgScore("ai_score"),
    };
  }, [filteredTransactions]);

  const riskDistribution = [
    { name: "High", value: metrics.highRisk, color: riskColors.High },
    { name: "Medium", value: metrics.mediumRisk, color: riskColors.Medium },
    { name: "Low", value: metrics.lowRisk, color: riskColors.Low },
  ].filter((item) => item.value > 0);

  if (loadingTransactions) {
    return (
      <div className="dashboard fraud-page">
        <header className="dashboard-page-header">
          <h1>Fraud Detection</h1>
          <p>AI-powered agent risk analysis across the selected timestamp window.</p>
        </header>

        <div className="loading-panel">
          <h2>Loading fraud detection</h2>
          <p>Preparing agent risk analysis...</p>
        </div>
      </div>
    );
  }

  if (transactionsError) {
    return (
      <div className="dashboard fraud-page">
        <header className="dashboard-page-header">
          <h1>Fraud Detection</h1>
          <p>AI-powered agent risk analysis across the selected timestamp window.</p>
        </header>

        <div className="loading-panel">
          <h2>Unable to load fraud detection</h2>
          <p>{transactionsError}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard fraud-page">
      <header className="dashboard-page-header fraud-page-header">
        <div>
          <h1>Fraud Detection</h1>
          <p>AI-powered agent risk analysis across the selected timestamp window.</p>
        </div>

        <span className="fraud-window-pill">
          {metrics.total} transactions analyzed
        </span>
      </header>

      <section className="agent-grid">
        <AgentCard
          icon={ShieldAlert}
          title="Fraud Agent"
          score={metrics.fraudScore.toFixed(2)}
          risk={scoreRisk(metrics.fraudScore, "fraud_agent", agentRiskBands)}
          detail={`Average fraud score across ${metrics.total} transaction${metrics.total !== 1 ? "s" : ""}`}
          tone="red"
        />
        <AgentCard
          icon={TrendingUp}
          title="Behavior Agent"
          score={metrics.behaviorScore.toFixed(2)}
          risk={scoreRisk(metrics.behaviorScore, "behavior_agent", agentRiskBands)}
          detail={`Average behavior score across selected transactions`}
          tone="blue"
        />
        <AgentCard
          icon={BadgeDollarSign}
          title="Receiver Agent"
          score={metrics.merchantScore.toFixed(2)}
          risk={scoreRisk(metrics.merchantScore, "merchant_agent", agentRiskBands)}
          detail={`Average receiver score across selected transactions`}
          tone="yellow"
        />
        <AgentCard
          icon={MapPin}
          title="Location Agent"
          score={metrics.locationScore.toFixed(2)}
          risk={scoreRisk(metrics.locationScore, "location_agent", agentRiskBands)}
          detail="Average location score from dataset"
          tone="green"
        />
        <AgentCard
          icon={Bot}
          title="AI Risk Analyst Agent"
          score={metrics.aiScore.toFixed(2)}
          risk="Independent"
          detail="Independent AI analyst review, not included in final rule-based score"
          tone="purple"
        />
      </section>

      <section className="fraud-analytics-grid">
        <div className="fraud-panel">
          <div className="fraud-panel-header">
            <h2>Risk Factors Detected</h2>
            <p>Signals derived from agent decisions and transaction patterns.</p>
          </div>

          <div className="risk-factor-list">
            <RiskFactorRow label="High-value amount" value={percent(metrics.highValue, metrics.total)} tone="red" />
            <RiskFactorRow label="Escalated decisions" value={percent(metrics.escalated, metrics.total)} tone="yellow" />
            <RiskFactorRow label="Transfer concentration" value={percent(metrics.transferVolume, metrics.total)} tone="blue" />
            <RiskFactorRow label="Cash-out pattern" value={percent(metrics.cashOutVolume, metrics.total)} tone="green" />
          </div>
        </div>

        <div className="fraud-panel">
          <div className="fraud-panel-header">
            <h2>Risk Score Distribution</h2>
            <p>Current risk mix across analyzed transactions.</p>
          </div>

          <div className="fraud-distribution-layout">
            <div className="fraud-donut-wrap">
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={riskDistribution}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={62}
                    outerRadius={88}
                    paddingAngle={2}
                    stroke="rgba(5, 9, 22, 0.72)"
                    strokeWidth={3}
                  >
                    {riskDistribution.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>

              <div className="fraud-donut-center">
                <strong>{metrics.total}</strong>
                <span>Total</span>
              </div>
            </div>

            <div className="fraud-distribution-list">
              {[
                { label: "High", value: metrics.highRisk, color: riskColors.High },
                { label: "Medium", value: metrics.mediumRisk, color: riskColors.Medium },
                { label: "Low", value: metrics.lowRisk, color: riskColors.Low },
              ].map((item) => (
                <div className="fraud-distribution-row" key={item.label}>
                  <span>
                    <i style={{ background: item.color }} />
                    {item.label}
                  </span>
                  <strong>
                    {item.value} ({percent(item.value, metrics.total)}%)
                  </strong>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="runtime-grid">
        <RuntimeMetric icon={Bot} label="Models Running" value="5 / 5" detail="Fraud, behavior, receiver, location, AI analyst" />
        <RuntimeMetric icon={Users} label="Transactions Analyzed" value={metrics.total} detail="Selected timestamp window" />
        <RuntimeMetric icon={ShieldCheck} label="Detection Coverage" value={`${percent(metrics.flagged, metrics.total)}%`} detail="Flagged or escalated" />
        <RuntimeMetric icon={Clock3} label="Avg Processing Time" value="120ms" detail="Current backend target" />
        <RuntimeMetric icon={Crosshair} label="Blocked Decisions" value={metrics.blocked} detail="Auto-blocked transactions" />
      </section>
    </div>
  );
}

export default FraudDetection;
