import pandas as pd
import numpy as np
import os

# =========================
# PATH CONFIG
# =========================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

DATA_PATH = os.path.join(BASE_DIR, "data", "paysim.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "paysim_enriched.csv")

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


# NOTE:
# PaySim does not include device, location, or real-time velocity context.
# For this project, those fields are synthetic enrichment features created to
# support the fraud-agent workflow. Some synthetic signals are intentionally
# aligned with the existing isFraud label so the enriched demo data contains
# plausible high-risk patterns for fraud transactions.

 
# =========================
# 1. CLEANING
# =========================
def clean_data(df):
    df = df.drop_duplicates()
    df["transaction_id"] = df.index.astype(str)
    df = df.fillna(0)
    df = df[df["amount"] >= 0].copy()

    df["balance_error"] = (
        df["oldbalanceOrg"] - df["amount"] - df["newbalanceOrig"]
    ).abs()

    return df


# =========================
# 2. TIME FEATURES
# =========================
def add_time_features(df):
    df["timestamp"] = pd.to_datetime("2020-01-01") + pd.to_timedelta(df["step"], unit="h")

    df = df.sort_values(["nameOrig", "timestamp"]).copy()

    df["time_diff"] = df.groupby("nameOrig")["timestamp"].diff().dt.total_seconds()
    df["time_diff"] = df["time_diff"].fillna(999999)

    df["hour"] = df["timestamp"].dt.hour
    df["is_night"] = ((df["hour"] < 6) | (df["hour"] > 22)).astype(int)

    return df


# =========================
# 3. VELOCITY FEATURES
# =========================
def add_velocity_features(df):
    df = df.sort_values(["nameOrig", "timestamp"]).copy()

    # Basic velocity from time difference
    df["high_velocity"] = (df["time_diff"] < 300).astype(int)

    # Synthetic enrichment:
    # Since many PaySim customers appear only once, add label-aligned velocity
    # variation so fraud examples have realistic repeated-transaction signals.
    fraud_idx = df["isFraud"] == 1
    normal_idx = df["isFraud"] == 0

    df["txn_count_1hr"] = 1

    df.loc[normal_idx, "txn_count_1hr"] = np.random.choice(
        [1, 2],
        size=normal_idx.sum(),
        p=[0.92, 0.08]
    )

    df.loc[fraud_idx, "txn_count_1hr"] = np.random.choice(
        [1, 2, 3, 4, 5],
        size=fraud_idx.sum(),
        p=[0.25, 0.20, 0.25, 0.20, 0.10]
    )

    df["velocity_risk"] = (df["txn_count_1hr"] >= 3).astype(int)

    return df
# =========================
# 4. BEHAVIORAL FEATURES
# =========================

def add_behavior_simulation_features(df):
    fraud_idx = df["isFraud"] == 1
    normal_idx = df["isFraud"] == 0

    # Simulated customer history count
    df.loc[normal_idx, "customer_txn_count"] = np.random.choice(
        [1, 2, 3, 4, 5, 10],
        size=normal_idx.sum(),
        p=[0.20, 0.25, 0.20, 0.15, 0.15, 0.05]
    )

    df.loc[fraud_idx, "customer_txn_count"] = np.random.choice(
        [5, 10, 15, 20, 30],
        size=fraud_idx.sum(),
        p=[0.15, 0.20, 0.25, 0.25, 0.15]
    )

    # Simulated customer average amount
    df["customer_avg_amount"] = df["amount"] / np.random.uniform(1.5, 6.0, len(df))

    # Fraud rows look more unusual compared with customer history
    df.loc[fraud_idx, "customer_avg_amount"] = (
        df.loc[fraud_idx, "amount"] / np.random.uniform(5.0, 15.0, fraud_idx.sum())
    )

    df["customer_amount_ratio"] = df["amount"] / (df["customer_avg_amount"] + 1)

    df["behavior_risk"] = (
        (df["customer_amount_ratio"] >= 5) |
        (df["velocity_risk"] == 1)
    ).astype(int)

    return df

# =========================
# 5. LOCATION FEATURES
# =========================
def add_location_features(df):
    rng = np.random.default_rng(42)

    users = df["nameOrig"].unique()

    base_lat = dict(zip(users, rng.uniform(25, 45, len(users))))
    base_long = dict(zip(users, rng.uniform(-120, -70, len(users))))

    df["home_lat"] = df["nameOrig"].map(base_lat)
    df["home_long"] = df["nameOrig"].map(base_long)

    normal_idx = df["isFraud"] == 0
    fraud_idx = df["isFraud"] == 1

    df["origin_lat"] = df["home_lat"]
    df["origin_long"] = df["home_long"]

    df.loc[normal_idx, "origin_lat"] += rng.normal(
        0, 0.05, normal_idx.sum()
    )
    df.loc[normal_idx, "origin_long"] += rng.normal(
        0, 0.05, normal_idx.sum()
    )

    df.loc[fraud_idx, "origin_lat"] += rng.uniform(
        5, 20, fraud_idx.sum()
    )
    df.loc[fraud_idx, "origin_long"] += rng.uniform(
        5, 20, fraud_idx.sum()
    )

    return df


# =========================
# 6. GEO DISTANCE FEATURES
# =========================
def haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))
    return r * c


def add_geo_features(df):
    df = df.sort_values(["nameOrig", "timestamp"]).copy()

    df["prev_origin_lat"] = df.groupby("nameOrig")["origin_lat"].shift(1)
    df["prev_origin_long"] = df.groupby("nameOrig")["origin_long"].shift(1)

    df["home_distance_km"] = haversine_distance(
        df["home_lat"],
        df["home_long"],
        df["origin_lat"],
        df["origin_long"]
    )

    df["geo_distance_km"] = haversine_distance(
        df["prev_origin_lat"],
        df["prev_origin_long"],
        df["origin_lat"],
        df["origin_long"]
    )

    df["geo_distance_km"] = df["geo_distance_km"].fillna(0)

    valid_time = (
        (df["time_diff"] > 0)
        & (df["time_diff"] < 999999)
    )

    df["travel_speed_kmh"] = 0.0

    df.loc[valid_time, "travel_speed_kmh"] = (
        df.loc[valid_time, "geo_distance_km"]
        / (df.loc[valid_time, "time_diff"] / 3600)
    )

    df["travel_speed_kmh"] = (
        df["travel_speed_kmh"]
        .replace([np.inf, -np.inf], 0)
        .fillna(0)
    )

    df["geo_risk"] = (
        (df["travel_speed_kmh"] >= 300)
        | (df["home_distance_km"] > 500)
    ).astype(int)

    return df


# =========================
# 7. DEVICE FEATURES
# =========================
def add_device_features(df):
    fraud_idx = df["isFraud"] == 1
    normal_idx = df["isFraud"] == 0

    # Synthetic enrichment:
    # Device type is generated because PaySim does not provide device context.
    # Fraud rows are more likely to receive higher-risk access channels.
    df.loc[normal_idx, "device_type"] = np.random.choice(
        ["mobile", "web"],
        size=normal_idx.sum(),
        p=[0.50, 0.50]
    )

    df.loc[fraud_idx, "device_type"] = np.random.choice(
        ["mobile", "web", "atm"],
        size=fraud_idx.sum(),
        p=[0.25, 0.35, 0.40]
    )

    df["device_risk"] = df["device_type"].isin(["atm", "web"]).astype(int)

    return df


# =========================
# 8. AMOUNT FEATURES
# =========================
def add_amount_features(df):
    global_mean = df["amount"].mean()
    global_std = df["amount"].std() + 1e-6

    df["amt_zscore"] = (df["amount"] - global_mean) / global_std
    df["amt_log"] = np.log1p(df["amount"])

    # Synthetic enrichment:
    # Amplify fraud amount deviation to create a stronger demo signal for the
    # downstream risk agents.
    fraud_idx = df["isFraud"] == 1
    df.loc[fraud_idx, "amt_zscore"] *= np.random.uniform(
        1.5, 3.0, fraud_idx.sum()
    )

    df["amt_deviation"] = df["amt_zscore"]
    df["amount_risk"] = (df["amt_zscore"] > 1.5).astype(int)

    return df


# =========================
# 9. BALANCE FEATURES
# =========================
def add_balance_features(df):
    df["balance_error"] = (
        df["oldbalanceOrg"] - df["amount"] - df["newbalanceOrig"]
    ).abs()

    df["balance_ratio"] = df["amount"] / (df["oldbalanceOrg"] + 1)

    df["balance_risk"] = (
        df["type"].isin(["TRANSFER", "CASH_OUT"]) &
        (df["balance_ratio"] > 0.995)
    ).astype(int)

    return df


# =========================
# 10. PIPELINE
# =========================
def feature_engineering_pipeline(df):
    df = clean_data(df)

    df = add_time_features(df)
    df = add_velocity_features(df)
    df = add_behavior_simulation_features(df) 
    df = add_location_features(df)
    df = add_geo_features(df)
    df = add_device_features(df)
    df = add_amount_features(df)
    df = add_balance_features(df)

    return df


# =========================
# RUN
# =========================
if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)

    print("\n[INFO] Raw PaySim loaded")
    print("Raw shape:", df.shape)

    df = feature_engineering_pipeline(df)

    df.to_csv(OUTPUT_PATH, index=False)

    print("\n[INFO] Enriched PaySim saved successfully")
    print("Saved to:", OUTPUT_PATH)
    print("Final shape:", df.shape)

    print("\n--- Preview ---")
    print(df.head())

    print("\n--- Columns ---")
    print(df.columns.tolist())

    print("\n--- Device Distribution by Fraud Flag ---")
    print(pd.crosstab(df["isFraud"], df["device_type"], normalize="index") * 100)

    print("\n--- Risk Feature Distribution by Fraud Flag ---")
    print(df.groupby("isFraud")[
        [
            "amount_risk",
            "geo_risk",
            "velocity_risk",
            "device_risk",
            "balance_risk"
        ]
    ].mean())

    print("\n--- Fraud Sample Check ---")
    print(df[df["isFraud"] == 1][
        [
            "type",
            "amount",
            "device_type",
            "amt_zscore",
            "amount_risk",
            "geo_distance_km",
            "geo_risk",
            "txn_count_1hr",
            "velocity_risk",
            "balance_ratio",
            "balance_risk"
        ]
    ].head(10))
