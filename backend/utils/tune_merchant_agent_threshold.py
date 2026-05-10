import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.merchant_agent import analyze_merchant
from data_loader import load_data, load_profiles

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


def evaluate_threshold(df, merchant_profiles, threshold):
    tp = fp = tn = fn = 0

    for _, row in df.iterrows():
        txn = row.to_dict()
        score = analyze_merchant(txn, merchant_profiles)["merchant_score"]

        actual = txn.get("isFraud", 0)
        predicted = score >= threshold

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


if __name__ == "__main__":
    df = load_data()
    _, merchant_profiles = load_profiles()

    sample_df = build_tuning_sample(df)

    print("\n===== TUNING SAMPLE =====")
    print(sample_df["isFraud"].value_counts())

    results = [
        evaluate_threshold(sample_df, merchant_profiles, i / 100)
        for i in range(10, 81, 5)
    ]

    results = sorted(results, key=lambda x: x["f1"], reverse=True)

    print("\n===== MERCHANT THRESHOLD TUNING =====")
    for result in results:
        print(result)

    print("\n===== BEST MERCHANT THRESHOLD =====")
    print(results[0])