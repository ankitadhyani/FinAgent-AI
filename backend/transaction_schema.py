BASE_TRANSACTION_FIELDS = [
    "step",
    "type",
    "amount",
    "nameOrig",
    "oldbalanceOrg",
    "newbalanceOrig",
    "nameDest",
    "oldbalanceDest",
    "newbalanceDest",
    "isFraud",
    "isFlaggedFraud",
]

ENGINEERED_FEATURES = [
    "transaction_id",
    "timestamp",
    "time_diff",
    "hour",
    "is_night",
    "high_velocity",
    "txn_count_1hr",
    "velocity_risk",
    "home_lat",
    "home_long",
    "origin_lat",
    "origin_long",
    "geo_distance_km",
    "geo_risk",
    "device_type",
    "device_risk",
    "amt_zscore",
    "amt_log",
    "amt_deviation",
    "amount_risk",
    "balance_error",
    "balance_ratio",
    "balance_risk",
    "customer_txn_count",
    "customer_avg_amount",
    "customer_amount_ratio",
    "behavior_risk",
]

TRANSACTION_FIELDS = BASE_TRANSACTION_FIELDS + ENGINEERED_FEATURES


def build_transaction_record(raw_transaction: dict) -> dict:
    transaction = {}

    # Keep frontend-safe base fields always present
    for field in BASE_TRANSACTION_FIELDS:
        transaction[field] = raw_transaction.get(field)

    # Add new engineered fields only if they exist
    for field in ENGINEERED_FEATURES:
        if field in raw_transaction:
            transaction[field] = raw_transaction.get(field)

    return transaction