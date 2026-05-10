import { useState } from "react";
import Sidebar from "./components/Sidebar";
import FraudDetection from "./pages/FraudDetection";
import Investigations from "./pages/Investigations";
import Overview from "./pages/Overview";
import Reports from "./pages/Reports";
import RulesModels from "./pages/RulesModels";
import Transactions from "./pages/Transactions";

const App = () => {
  const [activePage, setActivePage] = useState("Overview");
  const [simulationWindow, setSimulationWindow] = useState(null);

  const renderPage = () => {
    switch (activePage) {
      case "Overview":
        return (
          <Overview
            simulationWindow={simulationWindow}
            onSimulationWindowChange={setSimulationWindow}
          />
        );

      case "Transactions":
        return (
          <Transactions
            simulationWindow={simulationWindow}
            onSimulationWindowChange={setSimulationWindow}
          />
        );

      case "Fraud Detection":
        return <FraudDetection simulationWindow={simulationWindow} />;

      case "Investigations":
        return <Investigations simulationWindow={simulationWindow} />;

      case "Reports":
        return <Reports simulationWindow={simulationWindow} />;

      case "Rules & Models":
        return <RulesModels />;

      default:
        return (
          <Overview
            simulationWindow={simulationWindow}
            onSimulationWindowChange={setSimulationWindow}
          />
        );
    }
  };

  return (
    <div className="app-layout">
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      <div className="main-content">
        {renderPage()}
      </div>
    </div>
  );
};

export default App;
