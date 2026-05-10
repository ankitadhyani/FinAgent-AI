import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_loader import load_data, load_profiles
from orchestrator import investigate_transaction


def evaluate_system(df, customer_profiles, merchant_profiles, sample_size=500):
    sample_df = df.head(sample_size)

    total = 0
    actual_fraud = 0
    predicted_suspicious = 0

    tp = fp = fn = tn = 0

    for _, row in sample_df.iterrows():
        txn = row.to_dict()

        result = investigate_transaction(
            txn,
            customer_profiles,
            merchant_profiles
        )

        actual = txn.get("isFraud", 0)
        predicted = result["final_result"]["decision"] in ["ESCALATE", "BLOCK"]

        total += 1
        actual_fraud += actual

        if predicted:
            predicted_suspicious += 1

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

    print("\n===== FULL SYSTEM EVALUATION =====")
    print("Total transactions:", total)
    print("Actual fraud:", actual_fraud)
    print("Predicted suspicious:", predicted_suspicious)
    print("True positives:", tp)
    print("False positives:", fp)
    print("True negatives:", tn)
    print("False negatives:", fn)
    print("Precision:", round(precision, 3))
    print("Recall:", round(recall, 3))
    print("F1:", round(f1, 3))


if __name__ == "__main__":
    df = load_data()
    customer_profiles, merchant_profiles = load_profiles()

    evaluate_system(
        df,
        customer_profiles,
        merchant_profiles,
        sample_size=500
    )