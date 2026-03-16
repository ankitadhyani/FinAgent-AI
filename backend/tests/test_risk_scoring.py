from data_loader import load_data, get_sample_transaction
from agents.fraud_agent import analyze_fraud
from agents.behavior_agent import analyze_behavior
from services.risk_scoring import combine_agent_scores


def get_first_fraud_transaction(df):
    fraud_df = df[df["isFraud"] == 1]
    row = fraud_df.iloc[0]
    return row.to_dict()


if __name__ == "__main__":
    df = load_data()

    print("\n===== NORMAL SAMPLE TRANSACTION =====")
    normal_txn = get_sample_transaction(df, index=0)

    fraud_result_normal = analyze_fraud(normal_txn)
    behavior_result_normal = analyze_behavior(normal_txn, df)
    final_result_normal = combine_agent_scores(fraud_result_normal, behavior_result_normal)

    print("\nFraud Agent Output:")
    print(fraud_result_normal)

    print("\nBehavior Agent Output:")
    print(behavior_result_normal)

    print("\nFinal Combined Result:")
    print(final_result_normal)

    print("\n===== FIRST FRAUD TRANSACTION =====")
    fraud_txn = get_first_fraud_transaction(df)

    fraud_result_fraud = analyze_fraud(fraud_txn)
    behavior_result_fraud = analyze_behavior(fraud_txn, df)
    final_result_fraud = combine_agent_scores(fraud_result_fraud, behavior_result_fraud)

    print("\nFraud Agent Output:")
    print(fraud_result_fraud)

    print("\nBehavior Agent Output:")
    print(behavior_result_fraud)

    print("\nFinal Combined Result:")
    print(final_result_fraud)