import os
import pickle
import pandas as pd

from transaction_schema import ENGINEERED_FEATURES, build_transaction_record

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_DIR, "data", "paysim_demo.csv")
CUSTOMER_PROFILE_PATH = os.path.join(BASE_DIR, "data", "customer_profiles.pkl")
MERCHANT_PROFILE_PATH = os.path.join(BASE_DIR, "data", "merchant_profiles.pkl")


def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def load_profiles():
    with open(CUSTOMER_PROFILE_PATH, "rb") as f:
        customer_profiles = pickle.load(f)

    with open(MERCHANT_PROFILE_PATH, "rb") as f:
        merchant_profiles = pickle.load(f)

    return customer_profiles, merchant_profiles


def inspect_data(df):
    print("\n--- Dataset Shape ---")
    print(df.shape)

    print("\n--- Columns ---")
    print(df.columns.tolist())

    print("\n--- First 5 Rows ---")
    print(df.head())

    print("\n--- Missing Values ---")
    print(df.isnull().sum())

    if "isFraud" in df.columns:
        print("\n--- Fraud Distribution ---")
        print(df["isFraud"].value_counts())


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


def inspect_features(df):
    print("\n--- Engineered Features Check ---")

    missing_features = []

    for col in ENGINEERED_FEATURES:
        if col in df.columns:
            print(f"{col}: OK")
        else:
            missing_features.append(col)
            print(f"{col}: MISSING")

    if missing_features:
        print("\nMissing engineered features:", missing_features)
    else:
        print("\nAll engineered features are present.")


if __name__ == "__main__":
    df = load_data()

    inspect_data(df)
    inspect_features(df)

    sample_txn = get_sample_transaction(df, index=0)
    show_fraud_samples(df, n=5)
    fraud_by_type(df)