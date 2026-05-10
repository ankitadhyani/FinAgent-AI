/**
 * main.jsx
 *
 * React application entry point.
 * Loads global styles and mounts App into DOM.
 */

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

import "./styles/base.css";
import "./styles/simulation-time-window.css";
import "./styles/summary-cards.css";
import "./styles/transaction-volume.css";
import "./styles/transaction-list.css";
import "./styles/fraud-detection.css";
import "./styles/investigations.css";
import "./styles/reports.css";
import "./styles/rules-models.css";
import "./styles/drawer.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
