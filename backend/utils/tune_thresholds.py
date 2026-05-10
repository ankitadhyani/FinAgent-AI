import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_loader import load_data
from agents.fraud_agent import analyze_fraud
from agents.behavior_agent import analyze_behavior
from agents.merchant_agent import analyze_merchant


def get_final_score(fraud_result, behavior_result, merchant_result):
    fraud_score = fraud_result.get("fraud_score", 0.0)
    behavior_score = behavior_result.get("behavior_score", 0.0)
    merchant_score = merchant_result.get("merchant_score", 0.0)

    return (0.5 * fraud_score) + (0.2 * behavior_score) + (0.3 * merchant_score)


def tune_thresholds(df):
    df = df.sort_values("step").reset_index(drop=True)

    scored_rows = []

    for idx, row in df.iterrows():
        txn = row.to_dict()
        past_df = df.loc[:idx]

        fraud_result = analyze_fraud(txn)
        behavior_result = analyze_behavior(txn, past_df)
        merchant_result = analyze_merchant(txn, past_df)

        final_score = get_final_score(
            fraud_result,
            behavior_result,
            merchant_result
        )

        scored_rows.append({
            "actual": txn.get("isFraud", 0),
            "final_score": final_score,
        })

        # Optional: progress print (VERY useful)
        if idx % 5000 == 0:
            print(f"Processed {idx} rows...")

    print("\n===== THRESHOLD TUNING RESULTS =====")
    print("threshold | TP | FP | FN | Precision | Recall | F1")
    print("-" * 60)

    best_result = None

    for threshold in [0.15, 0.18, 0.20, 0.22, 0.24, 0.26, 0.28, 0.30, 0.35, 0.40, 0.45, 0.50]:
        tp = fp = fn = 0

        for row in scored_rows:
            actual = row["actual"]
            predicted = row["final_score"] >= threshold

            if actual == 1 and predicted:
                tp += 1
            elif actual == 0 and predicted:
                fp += 1
            elif actual == 1 and not predicted:
                fn += 1

        precision = tp / (tp + fp) if (tp + fp) else 0
        recall = tp / (tp + fn) if (tp + fn) else 0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0

        print(
            f"{threshold:>8.2f} | "
            f"{tp:>2} | {fp:>2} | {fn:>2} | "
            f"{precision:>9.3f} | {recall:>6.3f} | {f1:>5.3f}"
        )

        if best_result is None or f1 > best_result["f1"]:
            best_result = {
                "threshold": threshold,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }

    print("\n===== BEST THRESHOLD BY F1 =====")
    print(best_result)


if __name__ == "__main__":
    df = load_data()
    tune_thresholds(df)