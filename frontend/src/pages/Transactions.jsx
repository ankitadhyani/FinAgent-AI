import { useEffect, useMemo, useState } from "react";
import { Download, RotateCcw, Search } from "lucide-react";
import AnalysisDrawer from "../components/AnalysisDrawer";
import TransactionsTable from "../components/TransactionsTable";
import { analyzeTransaction, getTransactions } from "../api/client";

const PAGE_SIZE = 50;

function Transactions({ simulationWindow, onSimulationWindowChange }) {
  const [transactions, setTransactions] = useState([]);
  const [page, setPage] = useState(0);
  const [loadingTransactions, setLoadingTransactions] = useState(true);
  const [transactionsError, setTransactionsError] = useState("");
  const [selectedTxn, setSelectedTxn] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  const [searchTerm, setSearchTerm] = useState("");
  const [txnType, setTxnType] = useState("ALL");
  const [riskLevel, setRiskLevel] = useState("ALL");
  const [status, setStatus] = useState("ALL");
  const [minAmount, setMinAmount] = useState("");
  const [maxAmount, setMaxAmount] = useState("");
  const [startStep, setStartStep] = useState(1);
  const [endStep, setEndStep] = useState(1);

  const datasetMinStep =
    transactions.length > 0
      ? Math.min(...transactions.map((txn) => txn.step))
      : 1;

  const datasetMaxStep =
    transactions.length > 0
      ? Math.max(...transactions.map((txn) => txn.step))
      : 1;


  useEffect(() => {
    let isActive = true;

    const fetchTransactions = async () => {
      try {
        setLoadingTransactions(true);
        setTransactionsError("");

        const response = await getTransactions({ limit: 600, offset: 0 });

        if (!isActive) return;

        setTransactions(response.items || []);

      } catch (error) {
        if (!isActive) return;

        console.error("Failed to fetch transactions:", error);
        setTransactionsError("Failed to load transactions from backend.");
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

  useEffect(() => {
    if (!transactions.length) return;

    const windowStart = simulationWindow?.startStep ?? datasetMinStep;
    const windowEnd = simulationWindow?.endStep ?? datasetMaxStep;
    const nextStart = Math.min(Math.max(windowStart, datasetMinStep), datasetMaxStep);
    const nextEnd = Math.min(Math.max(windowEnd, datasetMinStep), datasetMaxStep);

    setStartStep(nextStart);
    setEndStep(nextEnd);

    if (!simulationWindow) {
      onSimulationWindowChange?.({
        startStep: datasetMinStep,
        endStep: datasetMaxStep,
      });
    }
  }, [transactions]);

  useEffect(() => {
    setPage(0);
  }, [searchTerm, txnType, riskLevel, status, minAmount, maxAmount]);

  const filterOptions = useMemo(() => {
    const types = [...new Set(transactions.map((txn) => txn.type).filter(Boolean))].sort();
    const risks = [...new Set(transactions.map((txn) => txn.risk).filter(Boolean))].sort();
    const statuses = [...new Set(transactions.map((txn) => txn.decision).filter(Boolean))].sort();

    return { types, risks, statuses };
  }, [transactions]);

  const filteredTransactions = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();
    const min = minAmount === "" ? null : Number(minAmount);
    const max = maxAmount === "" ? null : Number(maxAmount);

    return transactions.filter((txn) => {

    const searchable = [
      txn.id,
      txn.transaction_id,
      txn.timestamp,
      txn.step,
      txn.type,
      txn.sender,
      txn.receiver,
      txn.risk,
      txn.decision,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

      const matchesSearch = !normalizedSearch || searchable.includes(normalizedSearch);
      const matchesType = txnType === "ALL" || txn.type === txnType;
      const matchesRisk = riskLevel === "ALL" || txn.risk === riskLevel;
      const matchesStatus = status === "ALL" || txn.decision === status;
      const matchesMin = min === null || Number(txn.amount || 0) >= min;
      const matchesMax = max === null || Number(txn.amount || 0) <= max;

      return (
        matchesSearch &&
        matchesType &&
        matchesRisk &&
        matchesStatus &&
        matchesMin &&
        matchesMax
      );
    });
  }, [
    transactions,
    searchTerm,
    txnType,
    riskLevel,
    status,
    minAmount,
    maxAmount
  ]);

  const paginatedTransactions = useMemo(() => {
    const start = page * PAGE_SIZE;
    return filteredTransactions.slice(start, start + PAGE_SIZE);
  }, [filteredTransactions, page]);

  const totalPages = Math.max(1, Math.ceil(filteredTransactions.length / PAGE_SIZE));
  const pageStart = filteredTransactions.length === 0 ? 0 : page * PAGE_SIZE + 1;
  const pageEnd = Math.min((page + 1) * PAGE_SIZE, filteredTransactions.length);

  const resetFilters = () => {
    setSearchTerm("");
    setTxnType("ALL");
    setRiskLevel("ALL");
    setStatus("ALL");
    setMinAmount("");
    setMaxAmount("");
    setStartStep(datasetMinStep);
    setEndStep(datasetMaxStep);
    onSimulationWindowChange?.({
      startStep: datasetMinStep,
      endStep: datasetMaxStep,
    });
  };

  const goToPreviousPage = () => {
    setPage((current) => Math.max(current - 1, 0));
    setSelectedTxn(null);
    setAnalysisResult(null);
  };

  const goToNextPage = () => {
    setPage((current) => Math.min(current + 1, totalPages - 1));
    setSelectedTxn(null);
    setAnalysisResult(null);
  };

  const handleWindowChange = (nextWindow) => {
    setStartStep(nextWindow.startStep);
    setEndStep(nextWindow.endStep);
    onSimulationWindowChange?.(nextWindow);
  };

  const analyzeSelectedTransaction = async (txn) => {
    setSelectedTxn(txn);
    setLoadingAnalysis(true);
    setAnalysisResult(null);

    const payload = {
      ...txn,
      nameOrig: txn.sender,
      nameDest: txn.receiver,
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

  if (loadingTransactions && transactions.length === 0) {
    return (
      <div className="dashboard transactions-page">
        <header className="dashboard-page-header">
          <h1>Transactions</h1>
          <p>Review transaction-level risk scores, decisions, and counterparty activity.</p>
        </header>

        <div className="loading-panel">
          <h2>Loading transactions</h2>
          <p>Preparing transaction workbench...</p>
        </div>
      </div>
    );
  }

  if (transactionsError) {
    return (
      <div className="dashboard transactions-page">
        <header className="dashboard-page-header">
          <h1>Transactions</h1>
          <p>Review transaction-level risk scores, decisions, and counterparty activity.</p>
        </header>

        <div className="loading-panel">
          <h2>Unable to load transactions</h2>
          <p>{transactionsError}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard transactions-page">
      <header className="dashboard-page-header transactions-page-header">
        <div>
          <h1>Transactions</h1>
          <p>Review transaction-level risk scores, decisions, and counterparty activity.</p>
        </div>

        <button className="transactions-export-btn" type="button">
          <Download size={15} strokeWidth={2.3} />
          Export
        </button>
      </header>

      <section className="transactions-filter-card">
        <div className="transactions-filter-group transactions-search-group">
          <label htmlFor="transaction-search">Search</label>
          <div className="transactions-search-field">
            <Search size={16} strokeWidth={2.3} />
            <input
              id="transaction-search"
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Transaction ID, Sender, Receiver..."
            />
          </div>
        </div>

        <div className="transactions-filter-group">
          <label htmlFor="txn-type-filter">Transaction Type</label>
          <select
            id="txn-type-filter"
            value={txnType}
            onChange={(event) => setTxnType(event.target.value)}
          >
            <option value="ALL">All</option>
            {filterOptions.types.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <div className="transactions-filter-group">
          <label htmlFor="risk-filter">Risk Level</label>
          <select
            id="risk-filter"
            value={riskLevel}
            onChange={(event) => setRiskLevel(event.target.value)}
          >
            <option value="ALL">All</option>
            {filterOptions.risks.map((risk) => (
              <option key={risk} value={risk}>
                {risk}
              </option>
            ))}
          </select>
        </div>

        <div className="transactions-filter-group">
          <label htmlFor="status-filter">Status</label>
          <select
            id="status-filter"
            value={status}
            onChange={(event) => setStatus(event.target.value)}
          >
            <option value="ALL">All</option>
            {filterOptions.statuses.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </div>

        <div className="amount-filter-group">
          <label>Amount</label>
          <div>
            <input
              type="number"
              min="0"
              value={minAmount}
              onChange={(event) => setMinAmount(event.target.value)}
              placeholder="Min"
            />
            <input
              type="number"
              min="0"
              value={maxAmount}
              onChange={(event) => setMaxAmount(event.target.value)}
              placeholder="Max"
            />
          </div>
        </div>

        <button className="transactions-reset-btn" type="button" onClick={resetFilters}>
          <RotateCcw size={15} strokeWidth={2.3} />
          Reset
        </button>
      </section>

      <TransactionsTable
        data={paginatedTransactions}
        selectedTxn={selectedTxn}
        onSelect={analyzeSelectedTransaction}
        totalCount={filteredTransactions.length}
        rowOffset={page * PAGE_SIZE}
        loading={loadingTransactions}
      />

      <div className="transactions-pagination">
        <span>
          Page {(page + 1).toLocaleString()} of {totalPages.toLocaleString()} · rows{" "}
          {pageStart.toLocaleString()}-{pageEnd.toLocaleString()} of{" "}
          {filteredTransactions.length.toLocaleString()}
        </span>
        <div>
          <button
            type="button"
            onClick={goToPreviousPage}
            disabled={loadingTransactions || page === 0}
          >
            Previous
          </button>
          <button
            type="button"
            onClick={goToNextPage}
            disabled={loadingTransactions || page >= totalPages - 1}
          >
            Next
          </button>
        </div>
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

export default Transactions;
