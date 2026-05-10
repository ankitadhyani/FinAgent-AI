import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from data_loader import (
    load_data,
    load_profiles
)

from orchestrator import investigate_transaction


SENDER_ID = "C633069844"
RECEIVER_ID = "C1718989078"


def get_transaction(df, sender_id, receiver_id):
    txn_df = df[
        (df["nameOrig"] == sender_id) &
        (df["nameDest"] == receiver_id)
    ]

    if txn_df.empty:
        raise ValueError(
            f"Transaction not found for {sender_id} -> {receiver_id}"
        )

    return txn_df.iloc[0].to_dict()


if __name__ == "__main__":

    df = load_data()

    customer_profiles, merchant_profiles = load_profiles()

    print(f"\n===== TRANSACTION =====")

    txn = get_transaction(
    df,
    SENDER_ID,
    RECEIVER_ID
)

    result = investigate_transaction(
        txn,
        customer_profiles,
        merchant_profiles
    )

    print("\n===== INVESTIGATION RESULT =====")
    print(result)