from data_loader import load_data
from screener import screen_transactions


if __name__ == "__main__":
    df = load_data()

    results = screen_transactions(df, limit=10, suspicious_only=False)

    total = len(results)
    actual_fraud = sum(1 for r in results if r["isFraud_actual"] == 1)
    predicted_suspicious = sum(1 for r in results if r["decision"] in ["ESCALATE", "BLOCK"])
    true_positives = sum(
        1 for r in results
        if r["isFraud_actual"] == 1 and r["decision"] in ["ESCALATE", "BLOCK"]
    )
    false_positives = sum(
        1 for r in results
        if r["isFraud_actual"] == 0 and r["decision"] in ["ESCALATE", "BLOCK"]
    )

    print("\n===== SCREENING EVALUATION =====")
    print(f"Total transactions checked: {total}")
    print(f"Actual fraud transactions: {actual_fraud}")
    print(f"Predicted suspicious transactions: {predicted_suspicious}")
    print(f"True positives: {true_positives}")
    print(f"False positives: {false_positives}")

    if predicted_suspicious > 0:
        precision = true_positives / predicted_suspicious
        print(f"Precision: {precision:.2f}")

    if actual_fraud > 0:
        recall = true_positives / actual_fraud
        print(f"Recall: {recall:.2f}")

    print("\n===== TOP 10 BY SCORE =====")
    top_10 = sorted(results, key=lambda x: x["final_score"], reverse=True)[:10]
    for row in top_10:
        print(row)