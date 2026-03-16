import pandas as pd
from transaction_schema import build_transaction_record

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

DATA_PATH = "./data/paysim.csv"


def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def inspect_data(df):
    print("\n--- Dataset Shape ---")
    print(df.shape)

    print("\n--- Columns ---")
    print(df.columns.tolist())

    print("\n--- First 5 Rows ---")
    print(df.head(100))

    print("\n--- Missing Values ---")
    print(df.isnull().sum())


def get_sample_transaction(df, index=0):
    row = df.iloc[index]
    raw_transaction = row.to_dict()
    transaction = build_transaction_record(raw_transaction)

    print("\n--- Sample Transaction ---")
    for key, value in transaction.items():
        print(f"{key}: {value}")

    return transaction


def show_fraud_samples(df, n=5):
    fraud_df = df[df["isFraud"] == 1].head(n)

    print(f"\n--- First {n} Fraud Transactions ---")
    print(fraud_df)


def fraud_by_type(df):
    print("\n--- Fraud Count by Transaction Type ---")
    print(df.groupby("type")["isFraud"].sum())


if __name__ == "__main__":
    df = load_data()
    inspect_data(df)
    sample_txn = get_sample_transaction(df, index=0)
    show_fraud_samples(df, n=5)
    fraud_by_type(df)