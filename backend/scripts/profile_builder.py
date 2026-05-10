import os
import pickle
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

ENRICHED_DATA_PATH = os.path.join(BASE_DIR, "data", "paysim_enriched.csv")
CUSTOMER_PROFILE_PATH = os.path.join(BASE_DIR, "data", "customer_profiles.pkl")
MERCHANT_PROFILE_PATH = os.path.join(BASE_DIR, "data", "merchant_profiles.pkl")


def build_customer_profiles(df):
    customer_df = df.groupby("nameOrig").agg(
        avg_amount=("amount", "mean"),
        max_amount=("amount", "max"),
        txn_count=("amount", "count"),
        avg_customer_amount_ratio=("customer_amount_ratio", "mean"),
        max_customer_amount_ratio=("customer_amount_ratio", "max"),
        behavior_risk_rate=("behavior_risk", "mean"),
        velocity_risk_rate=("velocity_risk", "mean"),
        night_txn_rate=("is_night", "mean"),

        avg_home_distance_km=("home_distance_km", "mean"),
        max_home_distance_km=("home_distance_km", "max"),
        avg_travel_speed_kmh=("travel_speed_kmh", "mean"),
        max_travel_speed_kmh=("travel_speed_kmh", "max"),
        geo_risk_rate=("geo_risk", "mean"),
    )

    return customer_df.to_dict("index")


def build_merchant_profiles(df):
    merchant_df = df.groupby("nameDest").agg(
        txn_count=("amount", "count"),
        unique_senders=("nameOrig", "nunique"),
        avg_amount=("amount", "mean"),
        max_amount=("amount", "max"),
        amount_risk_rate=("amount_risk", "mean"),
        balance_risk_rate=("balance_risk", "mean"),
        device_risk_rate=("device_risk", "mean"),
    )

    return merchant_df.to_dict("index")


def save_profiles(customer_profiles, merchant_profiles):
    with open(CUSTOMER_PROFILE_PATH, "wb") as f:
        pickle.dump(customer_profiles, f)

    with open(MERCHANT_PROFILE_PATH, "wb") as f:
        pickle.dump(merchant_profiles, f)


if __name__ == "__main__":
    df = pd.read_csv(ENRICHED_DATA_PATH)

    print("\n[INFO] Building customer profiles from full enriched dataset...")
    customer_profiles = build_customer_profiles(df)

    print("[INFO] Building merchant profiles from full enriched dataset...")
    merchant_profiles = build_merchant_profiles(df)

    save_profiles(customer_profiles, merchant_profiles)

    print("\n[INFO] Profiles saved successfully")
    print("Customer profiles:", len(customer_profiles))
    print("Merchant profiles:", len(merchant_profiles))
    print("Saved to:")
    print(" -", CUSTOMER_PROFILE_PATH)
    print(" -", MERCHANT_PROFILE_PATH)