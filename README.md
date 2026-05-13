# FinAgent AI

AI-Powered Multi-Agent Fraud Detection & Financial Risk Intelligence Framework.

FinAgent AI is an autonomous fraud investigation platform that analyzes financial transactions using multiple specialized AI agents. The system combines fraud detection, customer behavior analysis, receiver-side analysis, location intelligence, and AI-generated contextual reasoning to produce real-time transaction risk scores and decisions.

This project is intended for academic demonstration and fraud-risk research purposes using synthetic PaySim transaction data.

---

# Features

## Multi-Agent Fraud Detection Pipeline

FinAgent AI uses 5 specialized agents:

- Fraud Agent
  - Detects suspicious transaction patterns, risky transfer types, balance anomalies, and high-value fraud indicators.

- Behavior Agent
  - Detects unusual customer behavior using transaction history, amount ratios, and transaction velocity.

- Receiver Agent
  - Evaluates receiver-side transaction activity, risky transfer patterns, and abnormal receiver behavior.

- Location Agent
  - Detects suspicious geographic movement patterns and high-risk location signals.

- AI Risk Analyst Agent
  - Gemini-powered AI contextual reasoning
  - Independent AI fraud decision analysis

---

# Core Capabilities

- Real-time transaction risk scoring
- Multi-agent weighted decision engine
- AI-powered fraud explanations
- Risk-level classification (LOW / MEDIUM / HIGH)
- Automated decisions:
  - APPROVE
  - ESCALATE
  - BLOCK
- Investigation report generation
- PDF export for fraud investigation reports
- Interactive fraud analytics dashboard
- Receiver-side intelligence analysis
- Geographic anomaly detection
- Detection performance monitoring dashboard

---

# Tech Stack

## Backend

- Python
- FastAPI
- LangGraph
- Pandas
- NumPy
- Google Gemini API
- Python-dotenv

## Frontend

- React
- Vite
- Recharts
- Lucide React

## AI / Analytics

- Multi-Agent Risk Scoring Engine
- AI-generated contextual reasoning
- LangGraph workflow orchestration

---

# Dataset

The project uses the PaySim financial transaction dataset enriched with engineered fraud-risk features, customer behavior profiles, receiver intelligence, and geographic risk signals.

Key engineered features include:

- Transaction velocity signals
- Amount risk indicators
- Balance anomaly detection
- Receiver-side risk profiling
- Geographic risk scoring
- Device and behavioral risk signals
- Historical customer transaction patterns

A lightweight demo dataset (`paysim_demo.csv`) is included for frontend visualization and testing.

For running the submitted project, the primary required dataset is `paysim_demo.csv`, which is included for lightweight backend execution, frontend visualization, and demo testing.

---

# Data Pipeline & Dataset Flow

The original PaySim financial transaction dataset is not included in submission due to file size limitations.

Raw PaySim dataset source:
https://www.kaggle.com/datasets/ealaxi/paysim1

FinAgent AI uses a multi-stage data engineering pipeline:

```text
paysim.csv
    ↓
Feature Engineering Pipeline
    ↓
paysim_enriched.csv
    ↓
Customer & Receiver Profile Generation
    ├── customer_profiles.pkl
    └── merchant_profiles.pkl
    ↓
Rule-Based Multi-Agent Scoring
    ↓
paysim_scored.csv
    ↓
Balanced Demo Dataset Builder
    ↓
paysim_demo.csv (once created will not be recreated)
```

## Pipeline Description

### `paysim.csv`
- Original raw PaySim transaction dataset.

### `paysim_enriched.csv`
- Enriched dataset containing engineered fraud-risk features such as:
  - velocity risk
  - amount risk
  - balance anomaly signals
  - geographic risk
  - customer behavior signals
  - device risk features

### `customer_profiles.pkl`
- Historical customer behavior profiles generated from the enriched dataset.

### `merchant_profiles.pkl`
- Receiver-side intelligence profiles generated from the enriched dataset.

### `paysim_scored.csv`
- Full dataset scored using the multi-agent fraud scoring pipeline.

### `paysim_demo.csv`
- Lightweight balanced demo dataset used for frontend visualization, backend execution, and presentation demonstrations.

For running the submitted project, only `paysim_demo.csv` is required.

---

# Project Structure

```text
FinAgent/
│
├── backend/
│   ├── agents/
│   ├── services/
│   ├── workflows/
│   ├── utils/
│   ├── tests/
│   ├── data/
│   ├── app.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```
---

# Environment Variables

Create a `.env` file inside the backend folder:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

---

# Run the Project

## Prerequisites

Before running the project on a new system, install:

- Python 3.10 or newer
- Node.js LTS, which includes npm
- Internet access for installing Python and frontend dependencies

Verify the tools are available:

Windows:

```powershell
python --version
node -v
npm -v
```

macOS / Linux:

```bash
python3 --version
node -v
npm -v
```

The demo backend requires `backend/data/paysim_demo.csv`, which is included in this project. The generated profile files `customer_profiles.pkl` and `merchant_profiles.pkl` are optional for the lightweight demo run.

If using Gemini AI features, create `backend/.env` with:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

## Backend Setup (FastAPI)

### Step 1: Navigate to backend

Windows:

```powershell
cd backend
```

macOS / Linux:

```bash
cd backend
```

### Step 2: Install Python dependencies

Windows:

```powershell
python -m pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m pip install -r requirements.txt
```

### Step 3: Start backend server

Windows:

```powershell
python -m uvicorn app:app --reload
```

macOS / Linux:

```bash
python3 -m uvicorn app:app --reload
```

Backend server:

```text
http://127.0.0.1:8000
```

Swagger API Docs:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup (React + Vite)

Install Node.js LTS before running the frontend:

```text
https://nodejs.org/
```

After installation, close and reopen your terminal, then verify:

Windows:

```powershell
node -v
npm -v
```

macOS / Linux:

```bash
node -v
npm -v
```

### Step 4: Open a new terminal

Keep backend running.

### Step 5: Navigate to frontend

Windows:

```powershell
cd frontend
```

macOS / Linux:

```bash
cd frontend
```

### Step 6: Install frontend dependencies

Windows:

```powershell
npm install
```

macOS / Linux:

```bash
npm install
```

If npm has certificate issues in a restricted school or corporate network, use:

Windows:

```powershell
npm install --strict-ssl=false
```

macOS / Linux:

```bash
npm install --strict-ssl=false
```

### Step 7: Start frontend

Windows:

```powershell
npm run dev
```

macOS / Linux:

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

# Running Test Files

## Fraud Agent Test

Windows:

```powershell
python -m tests.test_fraud_agent
```

macOS / Linux:

```bash
python3 -m tests.test_fraud_agent
```

## Behavior Agent Test

Windows:

```powershell
python -m tests.test_behavior_agent
```

macOS / Linux:

```bash
python3 -m tests.test_behavior_agent
```

## Risk Scoring Test

Windows:

```powershell
python -m tests.test_risk_scoring
```

macOS / Linux:

```bash
python3 -m tests.test_risk_scoring
```

---

# Detection Performance Summary

The rule-based multi-agent scoring engine and the AI Risk Analyst Agent are evaluated independently on sampled PaySim demo transactions.

- Rule-Based Detection Accuracy (sampled demo dataset): 100%
- AI Risk Analyst Accuracy: 72.5%

The AI Risk Analyst operates independently from the final rule-based scoring pipeline and provides separate contextual fraud analysis for analyst review.

---

# Workflow Overview

```text
Transaction Input
        ↓
Suspicious Transaction Check
        ↓
Parallel Multi-Agent Analysis
    ├── Fraud Agent
    ├── Behavior Agent
    ├── Receiver Agent
    ├── Location Agent
    └── AI Risk Analyst Agent
        ↓
Risk Scoring Engine
        ↓
Final Decision
(APPROVE / ESCALATE / BLOCK)
        ↓
Investigation Report Generation
```
---

# AI Decision Architecture

The rule-based multi-agent scoring system and the AI Risk Analyst Agent operate independently.

- Fraud, Behavior, Receiver, and Location agents contribute to the final rule-based transaction score.
- The AI Risk Analyst Agent performs separate contextual fraud analysis using Gemini-generated reasoning.
- The AI-generated decision is not merged into the final rule-based score and is displayed independently for analyst review.

---

# Submission Notes

The following large/generated files are excluded from submission:

- paysim_enriched.csv
- paysim_scored.csv
- customer_profiles.pkl
- merchant_profiles.pkl

Only the demo dataset (`paysim_demo.csv`) is included for lightweight execution and UI demonstration.

---

# Contributors

MSDS AI & LLM Project — Rutgers University
