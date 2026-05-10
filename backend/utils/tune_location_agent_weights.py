import os
import sys
import itertools
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_loader import load_data
from agents.location_agent import analyze_location
from config import LOCATION_AGENT_CONFIG

RANDOM_SEED = 42
NORMAL_SAMPLE_SIZE = 500
FRAUD_SAMPLE_SIZE = 500
EVALUATION_THRESHOLD = 0.30


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


def evaluate_config(df, config, threshold=EVALUATION_THRESHOLD):
    tp = fp = tn = fn = 0

    for _, row in df.iterrows():
        txn = row.to_dict()
        result = analyze_location(txn, config)

        # Use whichever key your current location agent returns
        score = result.get("location_score", result.get("geo_score", 0))

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


def tune_weights(df):
    results = []

    for geo, extreme, moderate, missing in itertools.product(
        [0.20, 0.25, 0.30],
        [0.15, 0.20, 0.25],
        [0.08, 0.10, 0.12],
        [0.03, 0.05, 0.07],
    ):
        config = LOCATION_AGENT_CONFIG.copy()
        config.update({
            "geo_risk_weight": geo,
            "extreme_distance_weight": extreme,
            "moderate_distance_weight": moderate,
            "missing_location_weight": missing,
        })

        results.append(evaluate_config(df, config))

    results = sorted(results, key=lambda x: x["f1"], reverse=True)

    print("\n===== TOP 5 LOCATION CONFIGS =====")
    for result in results[:5]:
        print(result)

    print("\n===== BEST LOCATION CONFIG =====")
    print(results[0])


if __name__ == "__main__":
    df = load_data()
    sample_df = build_tuning_sample(df)

    print("\n===== TUNING SAMPLE =====")
    print(sample_df["isFraud"].value_counts())
    print("Evaluation threshold:", EVALUATION_THRESHOLD)

    tune_weights(sample_df)