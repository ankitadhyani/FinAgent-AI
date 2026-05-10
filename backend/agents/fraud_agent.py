import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.config import FRAUD_AGENT_CONFIG
from utils.risk_utils import get_risk_level


def _is_enabled(value) -> bool:
    return value in [1, "1", True]


def analyze_fraud(transaction: dict, config: dict = FRAUD_AGENT_CONFIG) -> dict:
    score = 0.0
    reasons = []

    txn_type = transaction.get("type")
    amount = transaction.get("amount", 0)
    oldbalance_org = transaction.get("oldbalanceOrg", 0)
    newbalance_orig = transaction.get("newbalanceOrig", 0)
    name_dest = transaction.get("nameDest", "")
    oldbalance_dest = transaction.get("oldbalanceDest", 0)
    newbalance_dest = transaction.get("newbalanceDest", 0)

    amount_risk = transaction.get("amount_risk", 0)
    velocity_risk = transaction.get("velocity_risk", 0)
    device_risk = transaction.get("device_risk", 0)
    balance_risk = transaction.get("balance_risk", 0)

    if txn_type == "TRANSFER":
        score += config["transfer_weight"]
        reasons.append("TRANSFER type is commonly associated with fraud.")
    elif txn_type == "CASH_OUT":
        score += config["cashout_weight"]
        reasons.append("CASH_OUT type is commonly associated with fraud.")

    if amount > config["high_amount_threshold"]:
        score += config["high_amount_weight"]
        reasons.append(f"High transaction amount detected: {amount}.")
    elif amount > config["moderate_amount_threshold"]:
        score += config["moderate_amount_weight"]
        reasons.append(f"Moderately high transaction amount detected: {amount}.")

    if oldbalance_org == 0 and amount > 0:
        score += config["zero_origin_balance_weight"]
        reasons.append("Origin account has zero balance before transaction.")

    if (
        str(name_dest).startswith("C")
        and oldbalance_dest == 0
        and newbalance_dest == 0
        and amount > 0
    ):
        score += config["destination_zero_balance_weight"]
        reasons.append("Destination account remains zero after transaction.")

    if (
        txn_type in ["TRANSFER", "CASH_OUT"]
        and oldbalance_org > 0
        and abs(oldbalance_org - amount) <= 1
        and newbalance_orig == 0
    ):
        score += config["balance_emptied_weight"]
        reasons.append("Sender balance fully emptied by transaction.")

    if (
        txn_type == "TRANSFER"
        and amount > config["high_amount_threshold"]
        and str(name_dest).startswith("C")
        and oldbalance_dest == 0
        and newbalance_dest == 0
    ):
        score += config["combined_pattern_weight"]
        reasons.append("High-risk combined fraud pattern detected.")

    if _is_enabled(amount_risk):
        score += config["amount_risk_weight"]
        reasons.append("Transaction amount is unusually high compared to the dataset baseline.")

    if _is_enabled(velocity_risk):
        score += config["velocity_risk_weight"]
        txn_count = transaction.get("txn_count_1hr")
        reasons.append(f"High transaction velocity detected: {txn_count} transactions in 1 hour.")

    if _is_enabled(device_risk):
        score += config["device_risk_weight"]
        device_type = transaction.get("device_type")
        reasons.append(f"Transaction used a higher-risk device channel: {device_type}.")

    if _is_enabled(balance_risk):
        score += config["balance_risk_weight"]
        reasons.append("Engineered balance-risk pattern detected.")

    score = min(score, 1.0)

    return {
        "agent": "fraud_agent",
        "fraud_score": round(score, 2),
        "score": round(score, 2),
        "risk_level": get_risk_level(score, "fraud_agent"),
        "reasons": reasons
    }
    