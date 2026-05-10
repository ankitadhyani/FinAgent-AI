import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_loader import load_data
from agents.fraud_agent import analyze_fraud

RANDOM_SEED = 42
NORMAL_SAMPLE_SIZE = 500
FRAUD_SAMPLE_SIZE = 500


def build_tuning_sample(df, normal_size=NORMAL_SAMPLE_SIZE, fraud_size=FRAUD_SAMPLE_SIZE):
    fraud_df = df[df["isFraud"] == 1]
    normal_df = df[df["isFraud"] == 0]

    fraud_sample = fraud_df.sample(
        n=min(fraud_size, len(fraud_df)),
        random_state=RANDOM_SEED
    )
    normal_sample = normal_df.sample(
        n=min(normal_size, len(normal_df)),
        random_state=RANDOM_SEED
    )

    return (
        pd.concat([normal_sample, fraud_sample])
        .sample(frac=1, random_state=RANDOM_SEED)
        .reset_index(drop=True)
    )


def score_transactions(df):
    scored_rows = []

    for _, row in df.iterrows():
        txn = row.to_dict()
        result = analyze_fraud(txn)

        scored_rows.append({
            "actual": txn.get("isFraud", 0),
            "score": result["fraud_score"]
        })

    return scored_rows


def evaluate_binary(scored_rows, threshold):
    tp = fp = tn = fn = 0

    for row in scored_rows:
        actual = row["actual"]
        predicted = row["score"] >= threshold

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
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0
    )

    return {
        "threshold": threshold,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3)
    }


def tune_high_threshold(scored_rows):
    thresholds = [i / 100 for i in range(10, 81, 5)]
    results = [evaluate_binary(scored_rows, t) for t in thresholds]
    results = sorted(results, key=lambda x: x["f1"], reverse=True)

    print("\n===== FRAUD AGENT HIGH THRESHOLD TUNING =====")
    for r in results:
        print(r)

    print("\n===== BEST HIGH THRESHOLD BY F1 =====")
    print(results[0])

    return results[0]["threshold"]


def evaluate_medium_threshold(scored_rows, medium_threshold, high_threshold):
    suspicious = 0
    high_count = 0
    medium_count = 0
    low_count = 0

    tp = fp = fn = 0

    for row in scored_rows:
        actual = row["actual"]
        score = row["score"]

        if score >= high_threshold:
            level = "HIGH"
            high_count += 1
        elif score >= medium_threshold:
            level = "MEDIUM"
            medium_count += 1
        else:
            level = "LOW"
            low_count += 1

        predicted_suspicious = level in ["HIGH", "MEDIUM"]

        if predicted_suspicious:
            suspicious += 1

        if actual == 1 and predicted_suspicious:
            tp += 1
        elif actual == 0 and predicted_suspicious:
            fp += 1
        elif actual == 1 and not predicted_suspicious:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0
    )

    return {
        "medium_threshold": medium_threshold,
        "high_threshold": high_threshold,
        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": low_count,
        "suspicious_total": suspicious,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3)
    }


def tune_medium_threshold(scored_rows, high_threshold):
    medium_candidates = [0.10, 0.15, 0.20, 0.25, 0.30]

    results = []

    for medium in medium_candidates:
        if medium >= high_threshold:
            continue

        results.append(
            evaluate_medium_threshold(
                scored_rows,
                medium_threshold=medium,
                high_threshold=high_threshold
            )
        )

    results = sorted(results, key=lambda x: x["f1"], reverse=True)

    print("\n===== FRAUD AGENT MEDIUM THRESHOLD TUNING =====")
    for r in results:
        print(r)

    print("\n===== BEST MEDIUM THRESHOLD =====")
    print(results[0])

    return results[0]["medium_threshold"]


if __name__ == "__main__":
    df = load_data()
    sample_df = build_tuning_sample(df)

    print("\n===== TUNING SAMPLE =====")
    print(sample_df["isFraud"].value_counts())

    scored_rows = score_transactions(sample_df)

    best_high = tune_high_threshold(scored_rows)
    best_medium = tune_medium_threshold(scored_rows, best_high)

    print("\n===== FINAL FRAUD AGENT RISK BANDS =====")
    print({
        "fraud_agent": {
            "HIGH": best_high,
            "MEDIUM": best_medium
        }
    })