import os
import pandas as pd
import json
import math
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data_loader import load_data, load_profiles, get_sample_transaction
from orchestrator import investigate_transaction
from transaction_schema import build_transaction_record
from utils.config import (
    AGENT_RISK_BANDS,
    BEHAVIOR_AGENT_CONFIG,
    FINAL_AGENT_WEIGHTS,
    FINAL_SYSTEM_THRESHOLDS,
    FRAUD_AGENT_CONFIG,
    LOCATION_AGENT_CONFIG,
    MERCHANT_AGENT_CONFIG,
)

scored_transactions_cache = {}
DEFAULT_TRANSACTION_LIMIT = 100

app = FastAPI(
    title="FinAgent API",
    version="1.0",
    description="Multi-Agent Fraud Detection Backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset and profiles once at startup
df = load_data()
customer_profiles, merchant_profiles = load_profiles()


# ---------------------------
# Core Engine
# ---------------------------
def run_finagent(transaction: dict):
    return investigate_transaction(
        transaction,
        customer_profiles,
        merchant_profiles
    )


# ---------------------------
# Helpers
# ---------------------------

def build_transactions_cache(limit: int = DEFAULT_TRANSACTION_LIMIT, offset: int = 0):
    global scored_transactions_cache

    safe_offset = max(0, offset)
    safe_limit = max(1, min(limit, len(df)))
    records = df.iloc[safe_offset : safe_offset + safe_limit].to_dict(orient="records")
    added_count = 0

    for idx, row in enumerate(records):
        absolute_idx = safe_offset + idx

        if absolute_idx in scored_transactions_cache:
            continue

        try:
            scored_transactions_cache[absolute_idx] = to_frontend_transaction(row, absolute_idx)
            added_count += 1
        except Exception as e:
            print(f"Skipping row {absolute_idx} during cache build due to error: {e}")

    print(
        f"Prepared {added_count} scored rows for offset={safe_offset}, "
        f"limit={safe_limit}. Cache size={len(scored_transactions_cache)}."
    )


def get_first_fraud_transaction():
    fraud_df = df[df["isFraud"] == 1]

    if fraud_df.empty:
        return None

    return fraud_df.iloc[0].to_dict()

def clean_json_value(value, default=None):
    if pd.isna(value):
        return default

    if isinstance(value, float) and not math.isfinite(value):
        return default

    return value

def to_frontend_transaction(row: dict, idx: int) -> dict:
    transaction = build_transaction_record(row)

    final_result = {
        "decision": row.get("decision", "APPROVE"),
        "risk_level": row.get("risk_level", "LOW"),
        "final_score": row.get("final_score", 0.0),
        "location_score": row.get("location_score", 0.0),
        "ai_score": row.get("ai_score", 0.0),
        "ai_decision": row.get("ai_decision", ""),
        "ai_reasoning": row.get("ai_reasoning", ""),
    }

    fraud_result = {"fraud_score": row.get("fraud_score", 0.0)}
    behavior_result = {"behavior_score": row.get("behavior_score", 0.0)}
    merchant_result = {"merchant_score": row.get("merchant_score", 0.0)}

    frontend_txn = {
        "id": idx + 1,
        "transaction_id": transaction.get("transaction_id", row.get("transaction_id", idx + 1)),
        "timestamp": row.get("timestamp"),
        "type": transaction["type"],
        "amount": transaction["amount"],
        "sender": transaction["nameOrig"],
        "receiver": transaction["nameDest"],
        "step": transaction["step"],
        "oldbalanceOrg": transaction["oldbalanceOrg"],
        "newbalanceOrig": transaction["newbalanceOrig"],
        "oldbalanceDest": transaction["oldbalanceDest"],
        "newbalanceDest": transaction["newbalanceDest"],
        "decision": final_result.get("decision", "APPROVE"),
        "risk": final_result.get("risk_level", "LOW"),
        "final_score": final_result.get("final_score", 0.0),
        "fraud_score": fraud_result.get("fraud_score", 0.0),
        "behavior_score": behavior_result.get("behavior_score", 0.0),
        "merchant_score": merchant_result.get("merchant_score", 0.0),
        "location_score": row.get("location_score", 0.0),
        "ai_score": row.get("ai_score", 0.0),
        "ai_decision": row.get("ai_decision", ""),
        "ai_reasoning": row.get("ai_reasoning", ""),
        "home_lat": row.get("home_lat"),
        "home_long": row.get("home_long"),
        "origin_lat": row.get("origin_lat"),
        "origin_long": row.get("origin_long"),
        "geo_distance_km": row.get("geo_distance_km"),
        "geo_risk": row.get("geo_risk"),
        "device_type": row.get("device_type"),
        "device_risk": row.get("device_risk"),
        "velocity_risk": row.get("velocity_risk"),
        "behavior_risk": row.get("behavior_risk"),
        "amount_risk": row.get("amount_risk"),
        "balance_risk": row.get("balance_risk"),
        "customer_txn_count": row.get("customer_txn_count"),
        "customer_avg_amount": row.get("customer_avg_amount"),
        "customer_amount_ratio": row.get("customer_amount_ratio"),
        "isFraud": transaction["isFraud"],
        "isFlaggedFraud": transaction["isFlaggedFraud"],
    }

    return {
        key: clean_json_value(value, 0.0 if isinstance(value, (int, float)) else "")
        for key, value in frontend_txn.items()
    }


# ---------------------------
# Routes
# ---------------------------

@app.get("/")
def home():
    return {"message": "Welcome to FinAgent API"}


@app.get("/health")
def health():
    return {"status": "running"}


@app.get("/risk-config")
def risk_config():
    return {
        "agent_risk_bands": AGENT_RISK_BANDS,
        "agent_configs": {
            "fraud_agent": FRAUD_AGENT_CONFIG,
            "behavior_agent": BEHAVIOR_AGENT_CONFIG,
            "merchant_agent": MERCHANT_AGENT_CONFIG,
            "location_agent": LOCATION_AGENT_CONFIG,
        },
        "final_agent_weights": FINAL_AGENT_WEIGHTS,
        "final_system_thresholds": FINAL_SYSTEM_THRESHOLDS,
    }


@app.get("/sample-normal")
def sample_normal():
    normal_rows = df[df["isFraud"] == 0]

    if normal_rows.empty:
        return {"error": "No normal transaction found"}

    row = normal_rows.iloc[0].to_dict()
    return row


@app.get("/sample-fraud")
def sample_fraud():
    fraud_rows = df[df["isFraud"] == 1]

    if fraud_rows.empty:
        return {"error": "No fraud transaction found"}

    row = fraud_rows.iloc[0].to_dict()
    return row


@app.post("/analyze")
def analyze_transaction(transaction: dict):
    return run_finagent(transaction)


@app.on_event("startup")
def startup_event():
    print("Starting full transaction cache build...")

    build_transactions_cache(limit=len(df), offset=0)

    print(f"Cache build finished. Cached {len(scored_transactions_cache)} transactions.")


@app.get("/transactions")
def get_transactions(
    limit: int = DEFAULT_TRANSACTION_LIMIT,
    offset: int = 0,
    risk: str | None = None,
    type: str | None = None,
):
    safe_offset = max(0, offset)
    cached_items = list(scored_transactions_cache.values())
    safe_limit = max(1, min(limit, len(cached_items)))

    if risk is not None:
        cached_items = [txn for txn in cached_items if txn["risk"] == risk]

    if type is not None:
        cached_items = [txn for txn in cached_items if txn["type"] == type]

    total = len(cached_items)

    paginated_items = cached_items[safe_offset : safe_offset + safe_limit]

    return {
        "items": paginated_items,
        "total": total,
        "limit": safe_limit,
        "offset": safe_offset,
        "min_step": int(df["step"].min()),
        "max_step": int(df["step"].max()),
    }

@app.get("/model-metrics")
def get_model_metrics():
    metrics_path = os.path.join(
        os.path.dirname(__file__),
        "data",
        "model_metrics.json"
    )

    if not os.path.exists(metrics_path):
        return {
            "error": "model_metrics.json not found. Run utils/create_scored_dataset_and_metrics.py first.",
            "accuracy": 0,
            "precision": 0,
            "recall": 0,
            "f1": 0,
            "tp": 0,
            "fp": 0,
            "tn": 0,
            "fn": 0,
        }

    with open(metrics_path, "r") as f:
        return json.load(f)