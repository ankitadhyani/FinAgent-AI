"""
Behavior Agent:
Does this transaction look unusual for this customer compared to their past behavior?
Unlike fraud_agent.py, the behavior agent cannot work on just one transaction alone.
It needs:
- the current transaction
- the full dataset, or at least the sender’s past transactions
What Behavior agent (version 1) does:-
For a given transaction, it should check:
1. how many past transactions this sender has
2. average past amount for this sender
3. whether current amount is much larger than usual
4. whether the transaction type is unusual for that sender
"""

from utils.config import BEHAVIOR_AGENT_CONFIG
from utils.risk_utils import get_risk_level

def analyze_behavior(transaction, customer_profiles, config=BEHAVIOR_AGENT_CONFIG):
    score = 0.0
    reasons = []

    user = transaction.get("nameOrig")
    profile = customer_profiles.get(user, {})

    amount_ratio = transaction.get("customer_amount_ratio", 0)
    txn_count = profile.get("txn_count", transaction.get("customer_txn_count", 0))
    max_amount = profile.get("max_amount", 0)

    if amount_ratio >= config["amount_ratio_high_threshold"]:
        score += config["amount_ratio_high_weight"]
        reasons.append(f"Transaction amount is highly unusual for customer: {amount_ratio:.2f}x average.")
    elif amount_ratio >= config["amount_ratio_medium_threshold"]:
        score += config["amount_ratio_medium_weight"]
        reasons.append(f"Transaction amount is moderately unusual: {amount_ratio:.2f}x average.")
    elif amount_ratio >= config["amount_ratio_low_threshold"]:
        score += config["amount_ratio_low_weight"]
        reasons.append(f"Transaction amount is slightly above customer pattern: {amount_ratio:.2f}x average.")

    if transaction.get("amount", 0) > max_amount and max_amount > 0:
        score += config["exceeds_history_max_weight"]
        reasons.append("Transaction exceeds customer historical maximum amount.")

    if transaction.get("velocity_risk", 0) == 1:
        score += config["velocity_risk_weight"]
        reasons.append("High transaction velocity detected.")

    if transaction.get("is_night", 0) == 1:
        score += config["night_risk_weight"]
        reasons.append("Transaction occurred during night hours.")

    if transaction.get("amount_risk", 0) == 1:
        score += config["amount_risk_weight"]
        reasons.append("Amount risk signal is active.")

    if txn_count <= 1:
        reasons.append("Limited customer history available.")

    score = min(score, 1.0)

    return {
        "agent": "behavior_agent",
        "behavior_score": round(score, 2),
        "score": round(score, 2),
        "reasons": reasons,
        "history_count": txn_count,
        "risk_level": get_risk_level(score, "behavior_agent")
    }