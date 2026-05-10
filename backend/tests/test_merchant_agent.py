from data_loader import load_data,get_sample_transaction
from agents.merchant_agent import analyze_merchant


def get_first_fraud_transaction(df):
    fraud_df = df[df["isFraud"] == 1]
    row = fraud_df.iloc[0]
    return row.to_dict()


if __name__ == "__main__":
    df = load_data()

    print("\n===== NORMAL SAMPLE TRANSACTION =====")
    normal_txn = get_sample_transaction(df, index=0)
    normal_result = analyze_merchant(normal_txn, df)
    print(normal_result)

    print("\n===== FIRST FRAUD TRANSACTION =====")
    fraud_txn = get_first_fraud_transaction(df)
    fraud_result = analyze_merchant(fraud_txn, df)
    print(fraud_result)