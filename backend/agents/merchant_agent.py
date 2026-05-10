from utils.risk_utils import get_risk_level
from utils.config import MERCHANT_AGENT_CONFIG


def analyze_merchant(transaction, merchant_profiles, config=MERCHANT_AGENT_CONFIG):
    score = 0.0
    reasons = []

    dest = transaction.get("nameDest")
    profile = merchant_profiles.get(dest, {})

    txn_count = profile.get("txn_count", 0)
    unique_senders = profile.get("unique_senders", 0)
    amount = transaction.get("amount", 0)
    txn_type = transaction.get("type", "")

    if txn_type in ["TRANSFER", "CASH_OUT"]:
        score += config["risky_type_weight"]
        reasons.append(f"Risky destination transaction type: {txn_type}.")

    if amount >= config["high_value_threshold"] and txn_type in ["TRANSFER", "CASH_OUT"]:
        score += config["high_value_customer_transfer_weight"]
        reasons.append("High-value risky transfer/cash-out transaction.")

    if unique_senders >= config["unique_senders_high_threshold"]:
        score += config["many_unique_senders_high_weight"]
        reasons.append(f"Destination has many unique senders: {unique_senders}.")
    elif unique_senders >= config["unique_senders_medium_threshold"]:
        score += config["many_unique_senders_medium_weight"]
        reasons.append(f"Destination has moderate sender diversity: {unique_senders}.")

    if txn_count >= config["txn_count_high_threshold"]:
        score += config["high_txn_count_weight"]
        reasons.append(f"Destination has high transaction volume: {txn_count}.")
    elif txn_count >= config["txn_count_medium_threshold"]:
        score += config["medium_txn_count_weight"]
        reasons.append(f"Destination has moderate transaction volume: {txn_count}.")

    if transaction.get("device_risk", 0) == 1:
        score += config["device_risk_weight"]
        reasons.append("Device risk signal is active.")

    if transaction.get("amount_risk", 0) == 1:
        score += config["amount_risk_weight"]
        reasons.append("Amount risk signal is active.")

    if transaction.get("balance_risk", 0) == 1:
        score += config["balance_risk_weight"]
        reasons.append("Balance risk signal is active.")

    score = min(score, 1.0)
    
    return {
        "agent": "merchant_agent",
        "merchant_score": round(score, 2),
        "score": round(score, 2),
        "reasons": reasons,
        "destination_txn_count": txn_count,
        "risk_level": get_risk_level(score, "merchant_agent"),
        "unique_senders_to_dest": unique_senders
    }
