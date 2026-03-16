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

import pandas as pd

def analyze_behavior(transaction: dict, df: pd.DataFrame) -> dict:
    score = 0.0
    reasons = []

    name_orig = transaction.get("nameOrig")
    current_amount = transaction.get("amount", 0)
    current_type = transaction.get("type")
    current_step = transaction.get("step", 0)

    # Only use past transaction of this sender
    customer_history = df[
        (df["nameOrig"] == name_orig) & 
        (df["step"] < current_step)
    ]

    history_count = len(customer_history)

    if history_count == 0:
        reasons.append("No prior transaction found for this customer.")
        return {
            "agent": "behavior_agent",
            "behavior_score": 0.1,
            "risk_level": "LOW",
            "reasons": reasons,
            "history_count": history_count
        }
    
    avg_amount = customer_history["amount"].mean()
    max_amount = customer_history["amount"].max()
    common_type = customer_history["type"].mode().iloc(0)

    # Rule 1: Current amount much higher than historical average
    if avg_amount > 0:
        ratio = current_amount / avg_amount

        if ratio > 10:
            score += 0.45
            reasons.append(
                f"Current amount is {ratio:.2f}x higher than customer's historical average ({avg_amount:.2f})."
            )
        elif ratio > 5:
            score += 0.30
            reasons.append(
                f"Current amount is {ratio:.2f}x higher than customer's historical average ({avg_amount:.2f})."
            )
        elif ratio > 2:
            score += 0.15
            reasons.append(
                f"Current amount is {ratio:.2f}x higher than customer's historical average ({avg_amount:.2f})."
            )

    # Rule 2: Current amount exceeds historical max
    if current_amount > max_amount:
        score += 0.20
        reasons.append(
            f"Current amount exceeds customer's previous maximum transaction amount ({max_amount:.2f})."
        )

    # Rule 3: Transaction type differs from usual behavior
    if current_type != common_type:
        score += 0.20
        reasons.append(
            f"Transaction type '{current_type}' differs from customer's most common historical type '{common_type}'."
        )

    score = min(score, 1.0)

    if score >= 0.75:
        risk_level = "HIGH"
    elif score >= 0.40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "agent": "behavior_agent",
        "behavior_score": round(score, 2),
        "risk_level": risk_level,
        "reasons": reasons,
        "history_count": history_count,
        "avg_amount": round(avg_amount, 2),
        "max_amount": round(max_amount, 2),
        "common_type": common_type
    }