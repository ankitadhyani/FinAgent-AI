import sys
import os
import itertools
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_loader import load_data
from agents.fraud_agent import analyze_fraud
from config import FRAUD_AGENT_CONFIG

RANDOM_SEED = 42
EVALUATION_THRESHOLD = 0.35
NORMAL_SAMPLE_SIZE = 500
FRAUD_SAMPLE_SIZE = 500


# =========================
# SAMPLE BUILDER
# =========================
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

    return concat_and_shuffle(normal_sample, fraud_sample)


def concat_and_shuffle(normal_sample, fraud_sample):
    return (
        pd.concat([normal_sample, fraud_sample])
        .sample(frac=1, random_state=RANDOM_SEED)
        .reset_index(drop=True)
    )


# =========================
# EVALUATION
# =========================
def evaluate_config(df, config, threshold=EVALUATION_THRESHOLD):
    tp = fp = tn = fn = 0

    for _, row in df.iterrows():
        txn = row.to_dict()
        score = analyze_fraud(txn, config)["fraud_score"]

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
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0

    return {
        "config": config,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "tp": tp,
        "fp": fp,
        "fn": fn
    }


# =========================
# WEIGHT TUNING
# =========================
def tune_weights(df):
    high_amount_vals = [0.08, 0.10]
    zero_balance_vals = [0.10, 0.15]
    dest_zero_vals = [0.15, 0.18]
    balance_emptied_vals = [0.25, 0.30]
    combined_vals = [0.25, 0.30]
    amount_risk_vals = [0.05, 0.07]
    velocity_risk_vals = [0.06, 0.08]
    device_risk_vals = [0.01, 0.02]
    balance_risk_vals = [0.03, 0.05]

    results = []

    for ha, zb, dz, be, cb, ar, vr, dr, br in itertools.product(
        high_amount_vals,
        zero_balance_vals,
        dest_zero_vals,
        balance_emptied_vals,
        combined_vals,
        amount_risk_vals,
        velocity_risk_vals,
        device_risk_vals,
        balance_risk_vals
    ):
        config = FRAUD_AGENT_CONFIG.copy()
        config.update({
            "high_amount_weight": ha,
            "zero_origin_balance_weight": zb,
            "destination_zero_balance_weight": dz,
            "balance_emptied_weight": be,
            "combined_pattern_weight": cb,
            "amount_risk_weight": ar,
            "velocity_risk_weight": vr,
            "device_risk_weight": dr,
            "balance_risk_weight": br,
        })

        metrics = evaluate_config(df, config)
        results.append(metrics)

    results = sorted(results, key=lambda x: x["f1"], reverse=True)

    print("\n===== TOP 5 CONFIGS =====")
    for r in results[:5]:
        print(r)

    print("\n===== BEST CONFIG =====")
    print(results[0])


# =========================
# RUN
# =========================
if __name__ == "__main__":
    df = load_data()

    sample_df = build_tuning_sample(
        df,
        normal_size=NORMAL_SAMPLE_SIZE,
        fraud_size=FRAUD_SAMPLE_SIZE
    )

    print("\n===== TUNING SAMPLE =====")
    print(sample_df["isFraud"].value_counts())
    print("Evaluation threshold:", EVALUATION_THRESHOLD)

    tune_weights(sample_df)