FRAUD_AGENT_CONFIG = {
    "transfer_weight": 0.03,
    "cashout_weight": 0.05,

    "high_amount_threshold": 200000,
    "moderate_amount_threshold": 50000,

    "high_amount_weight": 0.08,
    "moderate_amount_weight": 0.05,

    "zero_origin_balance_weight": 0.10,
    "destination_zero_balance_weight": 0.15,
    "balance_emptied_weight": 0.25,
    "combined_pattern_weight": 0.25,

    "amount_risk_weight": 0.05,
    "velocity_risk_weight": 0.06,
    "device_risk_weight": 0.02,
    "balance_risk_weight": 0.05,
}


BEHAVIOR_AGENT_CONFIG = {
    "amount_ratio_high_threshold": 10,
    "amount_ratio_medium_threshold": 5,
    "amount_ratio_low_threshold": 2,

    "amount_ratio_high_weight": 0.3,
    "amount_ratio_medium_weight": 0.25,
    "amount_ratio_low_weight": 0.08,

    "exceeds_history_max_weight": 0.1,
    "velocity_risk_weight": 0.1,
    "night_risk_weight": 0.05,
    "amount_risk_weight": 0.06,
}

MERCHANT_AGENT_CONFIG = {
    "customer_destination_weight": 0.08,
    "risky_type_weight": 0.12,
    "high_value_customer_transfer_weight": 0.18,

    "many_unique_senders_high_weight": 0.25,
    "many_unique_senders_medium_weight": 0.15,
    "high_txn_count_weight": 0.15,
    "medium_txn_count_weight": 0.08,

    "device_risk_weight": 0.01,
    "amount_risk_weight": 0.05,
    "balance_risk_weight": 0.07,

    "unique_senders_high_threshold": 10,
    "unique_senders_medium_threshold": 5,
    "txn_count_high_threshold": 15,
    "txn_count_medium_threshold": 8,
    "high_value_threshold": 200000,
}


LOCATION_AGENT_CONFIG = {

    # ---------------------------------
    # Travel speed thresholds (km/h)
    # ---------------------------------
    "medium_speed_threshold": 120,
    "high_speed_threshold": 300,
    "impossible_speed_threshold": 900,

    # ---------------------------------
    # Travel speed weights
    # ---------------------------------
    "medium_speed_weight": 0.08,
    "high_speed_weight": 0.25,
    "impossible_speed_weight": 0.40,

    # ---------------------------------
    # Distance from home thresholds
    # ---------------------------------
    "moderate_distance_threshold": 100,
    "extreme_distance_threshold": 500,

    # ---------------------------------
    # Distance from home weights
    # ---------------------------------
    "moderate_distance_weight": 0.05,
    "extreme_distance_weight": 0.15,

    # ---------------------------------
    # Geo anomaly flag
    # ---------------------------------
    "geo_risk_weight": 0.30,

    # ---------------------------------
    # Night + high movement
    # ---------------------------------
    "night_speed_combo_weight": 0.05,

    # ---------------------------------
    # Missing location fields
    # ---------------------------------
    "missing_location_weight": 0.03,
}
AGENT_RISK_BANDS = {
    "fraud_agent": {"HIGH": 0.35, "MEDIUM": 0.30},
    "behavior_agent": {"HIGH": 0.30, "MEDIUM": 0.20},
    "merchant_agent": {"HIGH": 0.15, "MEDIUM": 0.10},
  "location_agent": {"HIGH": 0.30,"MEDIUM": 0.15},  
  "ai_analyst_agent": {"HIGH": 0.50, "MEDIUM": 0.30},
}
FINAL_AGENT_WEIGHTS = {
    "fraud": 0.40,
    "behavior": 0.25,
    "merchant": 0.15,
    "location": 0.10,
    "ai_analyst": 0.10,
}
FINAL_SYSTEM_THRESHOLDS = {
    "ESCALATE": 0.30,
    "BLOCK": 0.50
}