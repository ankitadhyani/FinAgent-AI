# FinAgent AI

AI-Powered Multi-Agent Fraud Detection & Financial Risk Intelligence Framework.

FinAgent AI is an autonomous fraud investigation platform that analyzes financial transactions using multiple specialized AI agents. The system combines fraud detection, customer behavior analysis, receiver-side analysis, location intelligence, and AI-generated contextual reasoning to produce real-time transaction risk scores and decisions.

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
  - Uses AI-generated contextual reasoning fields to provide additional fraud intelligence and decision support.

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
- Model performance metrics dashboard

---

# Tech Stack

## Backend

- Python
- FastAPI
- LangGraph
- Pandas
- Scikit-learn

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

# Run the Project

## Backend Setup (FastAPI)

### Step 1: Navigate to backend

```bash
cd backend
```

### Step 2: Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Start backend server

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

### Step 4: Open a new terminal

Keep backend running.

### Step 5: Navigate to frontend

```bash
cd frontend
```

### Step 6: Install frontend dependencies

```bash
npm install
```

### Step 7: Start frontend

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

```bash
python3 -m tests.test_fraud_agent
```

## Behavior Agent Test

```bash
python3 -m tests.test_behavior_agent
```

## Risk Scoring Test

```bash
python3 -m tests.test_risk_scoring
```

---

# Frontend Dependency

```bash
npm install lucide-react
```

---

# Current Model Performance

Validation metrics on balanced fraud vs non-fraud dataset:

- Accuracy: 98.7%
- Precision: 97.8%
- Recall: 99.6%
- F1-Score: 98.7%

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

# Contributors

MSDS AI & LLM Project — Rutgers University