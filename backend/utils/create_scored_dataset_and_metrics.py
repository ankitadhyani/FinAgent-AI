import json
import os
import sys

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_loader import load_profiles
from orchestrator import investigate_transaction

RANDOM_SEED = 42
VALIDATION_FRAUD_SIZE = 5000
VALIDATION_NORMAL_SIZE = 5000


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_PATH = os.path.join(DATA_DIR, "paysim_enriched.csv")
SCORED_PATH = os.path.join(DATA_DIR, "paysim_scored.csv")
METRICS_PATH = os.path.join(DATA_DIR, "model_metrics.json")


customer_profiles, merchant_profiles = load_profiles()


def run_finagent(transaction):
    return investigate_transaction(
        transaction,
        customer_profiles,
        merchant_profiles,
    )


def score_dataset():
    df = pd.read_csv(INPUT_PATH)
    scored_rows = []

    print(f"[INFO] Loaded full enriched dataset for scoring: {len(df)} rows.")

    for idx, row in df.iterrows():
        txn = row.to_dict()
        result = run_finagent(txn)

        final_result = result.get("final_result") or result.get("final_decision") or result

        scored_row = txn.copy()
        scored_row["final_score"] = final_result.get("final_score", 0.0)
        scored_row["risk_level"] = final_result.get("risk_level", "LOW")
        scored_row["decision"] = final_result.get("decision", "APPROVE")

        scored_rows.append(scored_row)

        if (idx + 1) % 10000 == 0:
            print(f"Scored {idx + 1} rows...")

    scored_df = pd.DataFrame(scored_rows)
    scored_df.to_csv(SCORED_PATH, index=False)

    print(f"Saved scored dataset to: {SCORED_PATH}")
    return scored_df


def build_validation_sample(scored_df):
    fraud_df = scored_df[scored_df["isFraud"] == 1]
    normal_df = scored_df[scored_df["isFraud"] == 0]

    fraud_sample = fraud_df.sample(
        n=min(VALIDATION_FRAUD_SIZE, len(fraud_df)),
        random_state=RANDOM_SEED,
    )

    normal_sample = normal_df.sample(
        n=min(VALIDATION_NORMAL_SIZE, len(normal_df)),
        random_state=RANDOM_SEED,
    )

    return (
        pd.concat([fraud_sample, normal_sample])
        .sample(frac=1, random_state=RANDOM_SEED)
        .reset_index(drop=True)
    )


def calculate_metrics(validation_df):
    tp = fp = tn = fn = 0

    for _, row in validation_df.iterrows():
        actual = int(row.get("isFraud", 0))
        predicted = row.get("decision") in ["ESCALATE", "BLOCK"]

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
    accuracy = (
        (tp + tn) / (tp + tn + fp + fn)
        if (tp + tn + fp + fn)
        else 0
    )

    return {
        "evaluation_scope": "Balanced validation sample from paysim_scored.csv",
        "sample_size": int(len(validation_df)),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "accuracy": round(accuracy, 3),
    }


if __name__ == "__main__":
    if os.path.exists(SCORED_PATH):
        print(f"[INFO] Scored dataset already exists. Loading: {SCORED_PATH}")
        scored_df = pd.read_csv(SCORED_PATH)
    else:
        print("[INFO] Scored dataset not found. Creating it now...")
        scored_df = score_dataset()

    if os.path.exists(METRICS_PATH):
        print(f"[INFO] Model metrics already exist. Skipping metrics creation: {METRICS_PATH}")
        with open(METRICS_PATH, "r") as f:
            metrics = json.load(f)
    else:
        print("[INFO] Model metrics not found. Creating metrics now...")
        validation_df = build_validation_sample(scored_df)

        print("\n[INFO] Validation actual fraud distribution:")
        print(validation_df["isFraud"].value_counts())

        print("\n[INFO] Validation decision distribution:")
        print(validation_df["decision"].value_counts())

        metrics = calculate_metrics(validation_df)

        with open(METRICS_PATH, "w") as f:
            json.dump(metrics, f, indent=2)

    print("\n[INFO] Model metrics:")
    print(json.dumps(metrics, indent=2))