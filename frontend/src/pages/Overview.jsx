/**
 * Overview.jsx
 *
 * Main container page for the FinAgent Overview screen.
 * Handles filter state, selected transaction state,
 * computes filtered transactions,
 * and renders all core sections:
 * Filter Bar
 * KPI Summary Cards
 * Transaction Volume Chart
 * Transactions Table
 * Analysis Drawer
 */

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  Building2,
  CircleDollarSign,
  Zap,
} from "lucide-react";
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import SummaryCard from "../components/SummaryCard";
import FilterBar from "../components/FilterBar";
import AnalysisDrawer from "../components/AnalysisDrawer";
import TransactionVolumeChart from "../components/TransactionVolumeChart";
import { analyzeTransaction, getTransactions } from "../api/client";

const toDateValue = (value) => (value ? String(value).slice(0, 10) : "");
const toTime = (value, endOfDay = false) => {
  if (!value) return endOfDay ? Infinity : -Infinity;
  return new Date(`${value}T${endOfDay ? "23:59:59" : "00:00:00"}`).getTime();
};

function buildChartData(transactions, startDate, endDate, bucketCount = 8) {
  const start = Math.min(toTime(startDate), toTime(endDate));
  const end = Math.max(toTime(startDate, true), toTime(endDate, true));

  if (!transactions.length || start > end) return [];

  const range = end - start + 1;
  const bucketSize = Math.max(1, Math.ceil(range / bucketCount));

  const buckets = [];

  for (let bucketStart = start; bucketStart <= end; bucketStart += bucketSize) {
    const bucketEnd = Math.min(bucketStart + bucketSize - 1, end);

    const bucketTxns = transactions.filter(
      (txn) => {
        const txnTime = new Date(txn.timestamp).getTime();
        return txnTime >= bucketStart && txnTime <= bucketEnd;
      }
    );

    const approve = bucketTxns.filter((txn) => txn.decision === "APPROVE").length;
    const review = bucketTxns.filter((txn) => txn.decision === "REVIEW").length;
    const escalate = bucketTxns.filter((txn) => txn.decision === "ESCALATE").length;
    const block = bucketTxns.filter((txn) => txn.decision === "BLOCK").length;

    const total = bucketTxns.length;
    const flagged = review + escalate + block;

    buckets.push({
      timestamp: new Date(bucketStart).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
      }),
      total,
      flagged,
      approve,
      review,
      escalate,
      block,
    });
  }

  return buckets;
}

const decisionConfig = [
  { key: "APPROVE", label: "Approved", color: "#22c55e" },
  { key: "ESCALATE", label: "Escalated", color: "#f59e0b" },
  { key: "BLOCK", label: "Blocked", color: "#ef4444" },
];

function getTopCount(rows, key) {
  const counts = rows.reduce((acc, row) => {
    const value = row[key] || "Unknown";
    acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});

  const [label, count] =
    Object.entries(counts).sort((a, b) => b[1] - a[1])[0] || ["No activity", 0];

  return { label, count };
}

function RiskDistributionPanel({ transactions }) {
  const total = transactions.length;

  const distribution = decisionConfig.map((item) => ({
    ...item,
    value: transactions.filter((txn) => txn.decision === item.key).length,
  }));

  const chartData = distribution.filter((item) => item.value > 0);

  return (
    <section className="risk-distribution-panel">
      <div className="risk-distribution-header">
        <div>
          <h2>Risk Distribution</h2>
          <p>Decision mix for the selected simulation window.</p>
        </div>
      </div>

      <div className="risk-distribution-body">
        <div className="risk-donut-wrap">
          <ResponsiveContainer width="100%" height={210}>
            <PieChart>
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="label"
                innerRadius={58}
                outerRadius={82}
                paddingAngle={2}
                stroke="rgba(5, 9, 22, 0.72)"
                strokeWidth={3}
              >
                {chartData.map((entry) => (
                  <Cell key={entry.key} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>

          <div className="risk-donut-center">
            <strong>{total}</strong>
            <span>Total</span>
          </div>
        </div>

        <div className="risk-distribution-list">
          {distribution.map((item) => {
            const percentage = total > 0 ? ((item.value / total) * 100).toFixed(1) : "0.0";

            return (
              <div className="risk-distribution-row" key={item.key}>
                <span>
                  <i style={{ background: item.color }} />
                  {item.label}
                </span>
                <strong>
                  {item.value} ({percentage}%)
                </strong>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function InsightCard({ icon: Icon, eyebrow, title, detail, tone = "blue" }) {
  return (
    <article className={`overview-insight-card overview-insight-card-${tone}`}>
      <div className="overview-insight-icon">
        <Icon size={20} strokeWidth={2.3} />
      </div>
      <div>
        <span>{eyebrow}</span>
        <strong>{title}</strong>
        <p>{detail}</p>
      </div>
    </article>
  );
}

function Overview({ simulationWindow, onSimulationWindowChange }) {

  const [selectedTxn, setSelectedTxn] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  const [allTransactions, setAllTransactions] = useState([]);
  const [loadingTransactions, setLoadingTransactions] = useState(true);
  const [transactionsError, setTransactionsError] = useState("");

  const datasetMinDate =
    allTransactions.length > 0
      ? allTransactions.map((txn) => toDateValue(txn.timestamp)).sort()[0]
      : "";

  const datasetMaxDate =
    allTransactions.length > 0
      ? allTransactions.map((txn) => toDateValue(txn.timestamp)).sort().at(-1)
      : "";

  const [startDateInput, setStartDateInput] = useState("");
  const [endDateInput, setEndDateInput] = useState("");
  const [riskLevelInput, setRiskLevelInput] = useState("ALL");
  const [txnTypeInput, setTxnTypeInput] = useState("ALL");

  const [appliedFilters, setAppliedFilters] = useState({
    startDate: "",
    endDate: "",
    riskLevel: "ALL",
    txnType: "ALL",
  });

  useEffect(() => {
    if (allTransactions.length > 0) {
      const dates = allTransactions.map((txn) => toDateValue(txn.timestamp)).sort();
      const minDate = dates[0];
      const maxDate = dates.at(-1);
      const nextStart = simulationWindow?.startDate ?? minDate;
      const nextEnd = simulationWindow?.endDate ?? maxDate;

      setStartDateInput(nextStart);
      setEndDateInput(nextEnd);
      setAppliedFilters({
        startDate: nextStart,
        endDate: nextEnd,
        riskLevel: "ALL",
        txnType: "ALL",
      });

      if (!simulationWindow) {
        onSimulationWindowChange?.({
          startDate: minDate,
          endDate: maxDate,
        });
      }
    }
  }, [allTransactions]);

  const filteredTransactions = useMemo(() => {
    const start = Math.min(toTime(appliedFilters.startDate), toTime(appliedFilters.endDate));
    const end = Math.max(toTime(appliedFilters.startDate, true), toTime(appliedFilters.endDate, true));

    return allTransactions.filter((txn) => {
      const txnTime = new Date(txn.timestamp).getTime();
      const withinTimeRange = txnTime >= start && txnTime <= end;

      const matchesRisk =
        appliedFilters.riskLevel === "ALL" ||
        txn.risk === appliedFilters.riskLevel;

      const matchesType =
        appliedFilters.txnType === "ALL" ||
        txn.type === appliedFilters.txnType;

      return withinTimeRange && matchesRisk && matchesType;
    });
  }, [allTransactions, appliedFilters]);


  const filteredChartData = useMemo(() => {
    return buildChartData(
      filteredTransactions,
      appliedFilters.startDate,
      appliedFilters.endDate,
      8
    );
  }, [filteredTransactions, appliedFilters]);

  const overviewInsights = useMemo(() => {
    const highRiskTransactions = filteredTransactions.filter((txn) => txn.risk === "HIGH");
    const flaggedTransactions = filteredTransactions.filter((txn) =>
      ["REVIEW", "ESCALATE", "BLOCK"].includes(txn.decision)
    );
    const topType = getTopCount(flaggedTransactions.length ? flaggedTransactions : filteredTransactions, "type");
    const topReceiver = getTopCount(flaggedTransactions.length ? flaggedTransactions : filteredTransactions, "receiver");
    const blockedValue = filteredTransactions
      .filter((txn) => txn.decision === "BLOCK")
      .reduce((sum, txn) => sum + Number(txn.amount || 0), 0);

    return {
      highRiskCount: highRiskTransactions.length,
      topType,
      topReceiver,
      blockedValue,
    };
  }, [filteredTransactions]);

  const handleApplyFilters = async () => {
    const nextWindow = {
      startDate: startDateInput,
      endDate: endDateInput,
    };

    try {
      setLoadingTransactions(true);

      setAppliedFilters({
        ...nextWindow,
        riskLevel: riskLevelInput,
        txnType: txnTypeInput,
      });

      onSimulationWindowChange?.(nextWindow);
      setSelectedTxn(null);
      setAnalysisResult(null);
    } catch (error) {
      console.error("Filter fetch failed:", error);
      setTransactionsError("Failed to apply filters.");
    } finally {
      setLoadingTransactions(false);
    }
  };

  const analyzeSelectedTransaction = async (txn) => {
    setSelectedTxn(txn);
    setLoadingAnalysis(true);
    setAnalysisResult(null);

    const payload = {
      step: txn.step,
      type: txn.type,
      amount: txn.amount,
      nameOrig: txn.sender,
      oldbalanceOrg: txn.oldbalanceOrg ?? 0,
      newbalanceOrig: txn.newbalanceOrig ?? 0,
      nameDest: txn.receiver,
      oldbalanceDest: txn.oldbalanceDest ?? 0,
      newbalanceDest: txn.newbalanceDest ?? 0,
      isFraud: txn.isFraud ?? 0,
      isFlaggedFraud: txn.isFlaggedFraud ?? 0,
    };

    try {
      const result = await analyzeTransaction(payload);
      setAnalysisResult(result);
    } catch (error) {
      console.error("Backend analyze failed:", error);
      setAnalysisResult(null);
    } finally {
      setLoadingAnalysis(false);
    }
  };


  useEffect(() => {
    let isActive = true;

    const fetchTransactions = async () => {
      try {
        setLoadingTransactions(true);
        setTransactionsError("");

        const response = await getTransactions({
          limit: 600,
          offset: 0,
        });

        if (!isActive) return;

        setAllTransactions(response.items);
        setTransactionsError("");
      } catch (error) {
        if (!isActive) return;

        console.error("Failed to fetch transactions:", error);
        setTransactionsError("Failed to load transactions from backend.");
        setAllTransactions([]);
      } finally {
        if (!isActive) return;
        setLoadingTransactions(false);
      }
    };

    fetchTransactions();

    return () => {
      isActive = false;
    };
  }, []);

  if (loadingTransactions) {
    return (
      <div className="dashboard">
        <header className="dashboard-page-header">
          <h1>Overview</h1>
          <p>Monitor transaction risk, agent decisions, and escalation flow.</p>
        </header>

        <div className="loading-panel">
          <h2>Loading dashboard</h2>
          <p>Loading transactions... Scoring with Fraud / Behavior / Receiver agents...</p>
        </div>
      </div>
    );
  }

  if (transactionsError) {
    return (
      <div className="dashboard">
        <header className="dashboard-page-header">
          <h1>Overview</h1>
          <p>Monitor transaction risk, agent decisions, and escalation flow.</p>
        </header>

        <div className="loading-panel">
          <h2>Unable to load dashboard</h2>
          <p>{transactionsError}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-page-header">
        <h1>Overview</h1>
        <p>Monitor transaction risk, agent decisions, and escalation flow.</p>
      </header>

      <FilterBar
        startDate={startDateInput}
        endDate={endDateInput}
        riskLevel={riskLevelInput}
        txnType={txnTypeInput}
        resultCount={filteredTransactions.length}
        minDate={datasetMinDate}
        maxDate={datasetMaxDate}
        onStartDateChange={setStartDateInput}
        onEndDateChange={setEndDateInput}
        onRiskLevelChange={setRiskLevelInput}
        onTxnTypeChange={setTxnTypeInput}
        onApply={handleApplyFilters}
        onReset={() => {
          setStartDateInput(datasetMinDate);
          setEndDateInput(datasetMaxDate);
          setRiskLevelInput("ALL");
          setTxnTypeInput("ALL");

          setAppliedFilters({
            startDate: datasetMinDate,
            endDate: datasetMaxDate,
            riskLevel: "ALL",
            txnType: "ALL",
          });

          setSelectedTxn(null);
          setAnalysisResult(null);
        }}
      />

      <div className="summary-grid">
        <SummaryCard
          title="Total Transactions"
          value={filteredTransactions.length}
          subtitle="In selected window"
          variant="blue"
          iconKey="total"
        />

        <SummaryCard
          title="Approved"
          value={
            filteredTransactions.filter((txn) => txn.decision === "APPROVE").length
          }
          subtitle="Transactions cleared as low risk"
          variant="green"
          iconKey="approved"
        />

        <SummaryCard
          title="Escalated"
          value={
            filteredTransactions.filter((txn) => txn.decision === "ESCALATE").length
          }
          subtitle="Sent to fraud analyst for review"
          variant="yellow"
          iconKey="escalated"
        />

        <SummaryCard
          title="Blocked"
          value={
            filteredTransactions.filter((txn) => txn.decision === "BLOCK").length
          }
          subtitle="Auto-blocked high risk"
          variant="red"
          iconKey="blocked"
        />
      </div>

      <div className="overview-analytics-grid">
        <TransactionVolumeChart data={filteredChartData} />
        <RiskDistributionPanel transactions={filteredTransactions} />
      </div>

      <div className="overview-insights-grid">
        <InsightCard
          icon={Zap}
          eyebrow="Top Risk Factor"
          title={overviewInsights.highRiskCount > 0 ? "High-Risk Activity" : "Unusual Velocity"}
          detail={`${overviewInsights.highRiskCount} high-risk transaction${
            overviewInsights.highRiskCount !== 1 ? "s" : ""
          } in the selected window`}
          tone="green"
        />

        <InsightCard
          icon={Activity}
          eyebrow="Highest Risk Segment"
          title={overviewInsights.topType.label}
          detail={`${overviewInsights.topType.count} flagged transaction${
            overviewInsights.topType.count !== 1 ? "s" : ""
          }`}
          tone="blue"
        />

        <InsightCard
          icon={Building2}
          eyebrow="Top Risk Counterparty"
          title={overviewInsights.topReceiver.label}
          detail="Highest-risk receiver by transaction count"
          tone="yellow"
        />

        <InsightCard
          icon={CircleDollarSign}
          eyebrow="Blocked Value"
          title={`$${overviewInsights.blockedValue.toLocaleString(undefined, {
            maximumFractionDigits: 0,
          })}`}
          detail="Total value prevented by block decisions"
          tone="red"
        />
      </div>


      <AnalysisDrawer
        transaction={selectedTxn}
        analysis={analysisResult}
        loading={loadingAnalysis}
        onClose={() => {
          setSelectedTxn(null);
          setAnalysisResult(null);
        }}
      />
    </div>
  );
}

export default Overview;
