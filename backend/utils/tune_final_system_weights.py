import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_loader import load_data, load_profiles
from agents.fraud_agent import analyze_fraud
from agents.behavior_agent import analyze_behavior
from agents.merchant_agent import analyze_merchant
from agents.location_agent import analyze_location

RANDOM_SEED = 42
NORMAL_SAMPLE_SIZE = 500
FRAUD_SAMPLE_SIZE = 500
EVALUATION_THRESHOLD = 0.22


WEIGHT_CONFIGS = [
    {"fraud": 0.45, "behavior": 0.25, "merchant": 0.20, "location": 0.10},
    {"fraud": 0.50, "behavior": 0.20, "merchant": 0.20, "location": 0.10},
    {"fraud": 0.40, "behavior": 0.30, "merchant": 0.20, "location": 0.10},
    {"fraud": 0.45, "behavior": 0.30, "merchant": 0.15, "location": 0.10},
    {"fraud": 0.40, "behavior": 0.25, "merchant": 0.20, "location": 0.15},
    {"fraud": 0.50, "behavior": 0.25, "merchant": 0.15, "location": 0.10},
    {"fraud": 0.35, "behavior": 0.35, "merchant": 0.20, "location": 0.10},
]


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


def evaluate_weights(scored_rows, weights, threshold=EVALUATION_THRESHOLD):
    tp = fp = tn = fn = 0

    for row in scored_rows:
        final_score = (
            weights["fraud"] * row["fraud_score"]
            + weights["behavior"] * row["behavior_score"]
            + weights["merchant"] * row["merchant_score"]
            + weights["location"] * row["location_score"]
        )

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

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    return {
        "weights": weights,
        "threshold": threshold,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
    }


def tune_weights(scored_rows):
    results = [
        evaluate_weights(scored_rows, weights)
        for weights in WEIGHT_CONFIGS
    ]

    results = sorted(results, key=lambda x: x["f1"], reverse=True)

    print("\n===== FINAL SYSTEM WEIGHT TUNING =====")
    for result in results:
        print(result)

    print("\n===== BEST FINAL WEIGHTS =====")
    print(results[0])


if __name__ == "__main__":
    df = load_data()
    customer_profiles, merchant_profiles = load_profiles()

    sample_df = build_tuning_sample(df)

    print("\n===== TUNING SAMPLE =====")
    print(sample_df["isFraud"].value_counts())
    print("Evaluation threshold:", EVALUATION_THRESHOLD)

    scored_rows = score_transactions(
        sample_df,
        customer_profiles,
        merchant_profiles
    )

    tune_weights(scored_rows)