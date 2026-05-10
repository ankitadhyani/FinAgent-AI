import itertools
import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.merchant_agent import analyze_merchant
from config import MERCHANT_AGENT_CONFIG
from data_loader import load_data, load_profiles

RANDOM_SEED = 42
NORMAL_SAMPLE_SIZE = 500
FRAUD_SAMPLE_SIZE = 500
EVALUATION_THRESHOLD = 0.35


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


def evaluate_config(df, merchant_profiles, config, threshold=EVALUATION_THRESHOLD):
    tp = fp = tn = fn = 0

    for _, row in df.iterrows():
        txn = row.to_dict()
        score = analyze_merchant(txn, merchant_profiles, config)["merchant_score"]

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

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    return {
        "config": config,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def tune_weights(df, merchant_profiles):
    results = []

    for rt, hv, dev, amt, bal in itertools.product(
        [0.08, 0.10, 0.12],
        [0.15, 0.18, 0.20],
        [0.01, 0.03, 0.05],
        [0.03, 0.05, 0.07],
        [0.03, 0.05, 0.07],
    ):
        config = MERCHANT_AGENT_CONFIG.copy()
        config.update({
            "risky_type_weight": rt,
            "high_value_customer_transfer_weight": hv,
            "device_risk_weight": dev,
            "amount_risk_weight": amt,
            "balance_risk_weight": bal,
        })

        results.append(evaluate_config(df, merchant_profiles, config))

    results = sorted(results, key=lambda x: x["f1"], reverse=True)

    print("\n===== TOP 5 MERCHANT CONFIGS =====")
    for result in results[:5]:
        print(result)

    print("\n===== BEST MERCHANT CONFIG =====")
    print(results[0])


if __name__ == "__main__":
    df = load_data()
    _, merchant_profiles = load_profiles()

    sample_df = build_tuning_sample(df)

    print("\n===== TUNING SAMPLE =====")
    print(sample_df["isFraud"].value_counts())
    print("Evaluation threshold:", EVALUATION_THRESHOLD)

    tune_weights(sample_df, merchant_profiles)