from data_loader import load_data, get_sample_transaction
from orchestrator import investigate_transaction
from services.report_agent import generate_report


def get_first_fraud_transaction(df):
    fraud_df = df[df["isFraud"] == 1]
    return fraud_df.iloc[0].to_dict()


if __name__ == "__main__":
    df = load_data()

    print("\n===== NORMAL TRANSACTION REPORT =====")
    normal_txn = get_sample_transaction(df, 0)
    normal_result = investigate_transaction(normal_txn, df)
    normal_report = generate_report(normal_result)
    print(normal_report["report_text"])

    print("\n===== FRAUD TRANSACTION REPORT =====")
    fraud_txn = get_first_fraud_transaction(df)
    fraud_result = investigate_transaction(fraud_txn, df)
    fraud_report = generate_report(fraud_result)
    print(fraud_report["report_text"])  