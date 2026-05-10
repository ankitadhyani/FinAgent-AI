import os
import sys
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(BASE_DIR)

from agents.fraud_agent import analyze_fraud
from agents.behavior_agent import analyze_behavior
from agents.merchant_agent import analyze_merchant
from agents.location_agent import analyze_location
from services.risk_scoring import combine_agent_scores
from transaction_schema import build_transaction_record

ENRICHED_PATH = os.path.join(BASE_DIR, "data", "paysim_enriched.csv")
DEMO_PATH = os.path.join(BASE_DIR, "data", "paysim_demo.csv")

RANDOM_STATE = 42
NORMAL_SAMPLE_SIZE = 100000
DEMO_COUNTS = {
    "APPROVE": 360,
    "ESCALATE": 150,
    "BLOCK": 90,
}


def build_customer_profiles(df):
    return df.groupby("nameOrig").agg(
        avg_amount=("amount", "mean"),
        max_amount=("amount", "max"),
        txn_count=("amount", "count"),
    ).to_dict("index")


def build_merchant_profiles(df):
    return df.groupby("nameDest").agg(
        txn_count=("amount", "count"),
        unique_senders=("nameOrig", "nunique"),
        avg_amount=("amount", "mean"),
        max_amount=("amount", "max"),
    ).to_dict("index")


def score_transaction(row, customer_profiles, merchant_profiles):
    transaction = build_transaction_record(row.to_dict())

    fraud_result = analyze_fraud(transaction)
    behavior_result = analyze_behavior(transaction, customer_profiles)
    merchant_result = analyze_merchant(transaction, merchant_profiles)
    location_result = analyze_location(transaction)

    final_result = combine_agent_scores(
        fraud_result,
        behavior_result,
        merchant_result,
        location_result
    )

    return {
        "fraud_score": fraud_result.get("fraud_score", 0.0),
        "behavior_score": behavior_result.get("behavior_score", 0.0),
        "merchant_score": merchant_result.get("merchant_score", 0.0),
        "location_score": location_result.get("location_score", 0.0),
        "final_score": final_result.get("final_score", 0.0),
        "risk_level": final_result.get("risk_level", "LOW"),
        "decision": final_result.get("decision", "APPROVE"),
    }


def safe_sample(df, n, label):
    if len(df) == 0:
        print(f"[WARN] No rows found for {label}.")
        return df

    sample_size = min(n, len(df))
    print(f"[INFO] Sampling {sample_size} rows from {label} bucket.")
    return df.sample(sample_size, random_state=RANDOM_STATE)


def main():
    if os.path.exists(DEMO_PATH):
        print(f"[INFO] Demo dataset already exists. Skipping rebuild: {DEMO_PATH}")
        return

    print("[INFO] Loading enriched dataset...")
    df = pd.read_csv(ENRICHED_PATH)

    fraud_df = df[df["isFraud"] == 1]
    normal_df = df[df["isFraud"] == 0].sample(
        min(NORMAL_SAMPLE_SIZE, len(df[df["isFraud"] == 0])),
        random_state=RANDOM_STATE
    )

    candidate_df = pd.concat([fraud_df, normal_df], ignore_index=True)
    candidate_df = candidate_df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

    print("[INFO] Candidate dataset shape:", candidate_df.shape)

    print("[INFO] Building profiles from candidate dataset...")
    customer_profiles = build_customer_profiles(candidate_df)
    merchant_profiles = build_merchant_profiles(candidate_df)

    print("[INFO] Scoring candidate transactions...")
    scored_rows = []

    for idx, row in candidate_df.iterrows():
        scores = score_transaction(row, customer_profiles, merchant_profiles)
        scored_rows.append(scores)

        if (idx + 1) % 10000 == 0:
            print(f"[INFO] Scored {idx + 1} transactions...")

    scored_df = pd.concat(
        [candidate_df.reset_index(drop=True), pd.DataFrame(scored_rows)],
        axis=1
    )

    approve_df = scored_df[scored_df["decision"] == "APPROVE"]
    escalate_df = scored_df[scored_df["decision"] == "ESCALATE"]
    block_df = scored_df[scored_df["decision"] == "BLOCK"]

    print("\n[INFO] Decision distribution before sampling:")
    print(scored_df["decision"].value_counts())

    demo_df = pd.concat([
        safe_sample(approve_df, DEMO_COUNTS["APPROVE"], "APPROVE"),
        safe_sample(escalate_df, DEMO_COUNTS["ESCALATE"], "ESCALATE"),
        safe_sample(block_df, DEMO_COUNTS["BLOCK"], "BLOCK"),
    ], ignore_index=True)

    demo_df = demo_df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

    demo_df.to_csv(DEMO_PATH, index=False)

    print("\n[INFO] Demo dataset saved successfully")
    print("Saved to:", DEMO_PATH)
    print("Final shape:", demo_df.shape)
    print("\n[INFO] Final decision distribution:")
    print(demo_df["decision"].value_counts())


if __name__ == "__main__":
    main()