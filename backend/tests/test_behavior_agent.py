from data_loader import load_data, get_sample_transaction
from agents.behavior_agent import analyze_behavior


def get_first_fraud_transaction(df):
    fraud_df = df[df["isFraud"] == 1]
    row = fraud_df.iloc[0]
    return row.to_dict()

# Get last 5 fraud transactions
def get_last_five_fraud_transaction(df):
    fraud_df = df[df["isFraud"] == 1].tail(5)
    return fraud_df


if __name__ == "__main__":
    df = load_data()

    print("\n===== NORMAL SAMPLE TRANSACTION =====")
    normal_txn = get_sample_transaction(df, index=0)
    normal_result = analyze_behavior(normal_txn, df)
    print(normal_result)

    print("\n===== FIRST FRAUD TRANSACTION =====")
    fraud_txn = get_first_fraud_transaction(df)
    fraud_result = analyze_behavior(fraud_txn, df)
    print(fraud_result)

    print("\n===== Last 5 FRAUD TRANSACTION =====")
    fraud_txns = get_last_five_fraud_transaction(df)
    for index, row in fraud_txns.iterrows():
        fraud_result = analyze_behavior(row, df)
        print("transaction #", index, " ", fraud_result)