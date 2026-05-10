import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_loader import load_data, load_profiles
from agents.fraud_agent import analyze_fraud
from agents.behavior_agent import analyze_behavior
from agents.merchant_agent import analyze_merchant
from agents.location_agent import analyze_location
from config import FINAL_AGENT_WEIGHTS

RANDOM_SEED = 42
NORMAL_SAMPLE_SIZE = 500
FRAUD_SAMPLE_SIZE = 500


def build_tuning_sample(df):
    fraud_df = df[df["isFraud"] == 1]
    normal_df = df[df["isFraud"] == 0]

    fraud = fraud_df.sample(
        n=min(FRAUD_SAMPLE_SIZE, len(fraud_df)),
        random_state=RANDOM_SEED
    )
    normal = normal_df.sample(
        n=min(NORMAL_SAMPLE_SIZE, len(normal_df)),
        random_state=RANDOM_SEED
    )

    return (
        pd.concat([normal, fraud])
        .sample(frac=1, random_state=RANDOM_SEED)
        .reset_index(drop=True)
    )


def calculate_final_score(row):
    return (
        FINAL_AGENT_WEIGHTS["fraud"] * row["fraud_score"]
        + FINAL_AGENT_WEIGHTS["behavior"] * row["behavior_score"]
        + FINAL_AGENT_WEIGHTS["merchant"] * row["merchant_score"]
        + FINAL_AGENT_WEIGHTS["location"] * row["location_score"]
    )


def score_transactions(df, customer_profiles, merchant_profiles):
    scored_rows = []

    for _, row in df.iterrows():
        txn = row.to_dict()

        fraud_result = analyze_fraud(txn)
        behavior_result = analyze_behavior(txn, customer_profiles)
        merchant_result = analyze_merchant(txn, merchant_profiles)
        location_result = analyze_location(txn)

        scored_rows.append({
            "actual": txn.get("isFraud", 0),
            "fraud_score": fraud_result.get("fraud_score", 0.0),
            "behavior_score": behavior_result.get("behavior_score", 0.0),
            "merchant_score": merchant_result.get("merchant_score", 0.0),
            "location_score": location_result.get("location_score", 0.0),
        })

    return scored_rows


def evaluate_escalate_threshold(scored_rows, threshold):
    tp = fp = tn = fn = 0

    for row in scored_rows:
        final_score = calculate_final_score(row)
        actual = row["actual"]
        predicted = final_score >= threshold

        if actual == 1 and predicted:
            tp += 1
        elif actual == 0 and predicted:
            fp += 1
        elif actual == 0 and not predicted:
            tn += 1
        elif actual == 1 and not predicted:
            fn += 1

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0

    return {
        "threshold": threshold,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
    }


def tune_escalate_threshold(scored_rows):
    thresholds = [i / 100 for i in range(10, 51, 2)]

    results = [
        evaluate_escalate_threshold(scored_rows, threshold)
        for threshold in thresholds
    ]

    results = sorted(results, key=lambda x: x["f1"], reverse=True)

    print("\n===== FINAL ESCALATE THRESHOLD TUNING =====")
    for result in results:
        print(result)

    print("\n===== BEST ESCALATE THRESHOLD =====")
    print(results[0])

    return results[0]["threshold"]


def evaluate_block_threshold(scored_rows, block_threshold, escalate_threshold):
    block_tp = block_fp = block_fn = 0
    escalate_count = approve_count = block_count = 0

    for row in scored_rows:
        final_score = calculate_final_score(row)
        actual = row["actual"]

        if final_score >= block_threshold:
            decision = "BLOCK"
            block_count += 1
        elif final_score >= escalate_threshold:
            decision = "ESCALATE"
            escalate_count += 1
        else:
            decision = "APPROVE"
            approve_count += 1

        predicted_block = decision == "BLOCK"

        if actual == 1 and predicted_block:
            block_tp += 1
        elif actual == 0 and predicted_block:
            block_fp += 1
        elif actual == 1 and not predicted_block:
            block_fn += 1

    precision = block_tp / (block_tp + block_fp) if block_tp + block_fp else 0
    recall = block_tp / (block_tp + block_fn) if block_tp + block_fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0

    return {
        "block_threshold": block_threshold,
        "escalate_threshold": escalate_threshold,
        "block": block_count,
        "escalate": escalate_count,
        "approve": approve_count,
        "block_tp": block_tp,
        "block_fp": block_fp,
        "block_fn": block_fn,
        "block_precision": round(precision, 3),
        "block_recall": round(recall, 3),
        "block_f1": round(f1, 3),
    }


def tune_block_threshold(scored_rows, escalate_threshold):
    block_thresholds = [i / 100 for i in range(35, 81, 5)]

    results = [
        evaluate_block_threshold(
            scored_rows,
            block_threshold=threshold,
            escalate_threshold=escalate_threshold
        )
        for threshold in block_thresholds
        if threshold > escalate_threshold
    ]

    results = sorted(results, key=lambda x: x["block_f1"], reverse=True)

    print("\n===== FINAL BLOCK THRESHOLD TUNING =====")
    for result in results:
        print(result)

    print("\n===== BEST BLOCK THRESHOLD =====")
    print(results[0])

    return results[0]["block_threshold"]


if __name__ == "__main__":
    df = load_data()
    customer_profiles, merchant_profiles = load_profiles()

    sample_df = build_tuning_sample(df)

    print("\n===== TUNING SAMPLE =====")
    print(sample_df["isFraud"].value_counts())
    print("Final weights:", FINAL_AGENT_WEIGHTS)

    scored_rows = score_transactions(
        sample_df,
        customer_profiles,
        merchant_profiles
    )

    best_escalate = tune_escalate_threshold(scored_rows)
    best_block = tune_block_threshold(scored_rows, best_escalate)

    print("\n===== FINAL SYSTEM THRESHOLDS =====")
    print({
        "ESCALATE": best_escalate,
        "BLOCK": best_block
    })