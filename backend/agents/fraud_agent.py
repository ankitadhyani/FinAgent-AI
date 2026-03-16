
def analyze_fraud(transaction: dict) -> dict:
    score = 0.0
    reasons = []

    txn_type = transaction.get("type")
    amount = transaction.get("amount", 0)
    oldbalance_org = transaction.get("oldbalanceOrg", 0)
    newbalance_orig = transaction.get("newbalanceOrig", 0)
    name_dest = transaction.get("nameDest", "")
    oldbalance_dest = transaction.get("oldbalanceDest", 0)
    newbalance_dest = transaction.get("newbalanceDest", 0)

    #Rule 1: Fraud in PaySim is mostly in TRANSFER and CASH_OUT
    if txn_type in ["TRANSFER", "CASH_OUT"]:
        score += 0.30
        reasons.append(f"Transaction type '{txn_type}' is commonly associated with fraud in PaySim.")

    # Rule 2: Large amount can be suspecious
    if amount > 200000:
        score += 0.30
        reasons.append(f"High transaction amount detected: {amount}.")
    elif amount > 50000:
        score += 0.15
        reasons.append(f"Moderately high transaction amount detected: {amount}.")
    
    # Rule 3: Sender has zero and near-zero balance but transaction still happened
    if oldbalance_org == 0 and amount > 0:
        score += 0.20
        reasons.append("Origin account has zero balance before transaction, which is suspecious.")
    
    # Rule 4: Balance inconsistency at sender side
    expected_newbalance_orig = oldbalance_org - amount
    if abs(expected_newbalance_orig - newbalance_orig) > 1:
        score += 0.15
        reasons.append(f"Origin balance mismatch: expected {expected_newbalance_orig}, got {newbalance_orig}.")

    # Rule 5: For 'Customer' destination accounts, zero balances may be suspecious
    if str(name_dest).startswith("C"):
        if oldbalance_dest == 0 and newbalance_dest == 0 and amount > 0:
            score += 0.20
            reasons.append("Destination is a customer account but destination balances remain zero.")
    
    # Cap score at 1.0
    score = min(score, 1.0)

    #Convert score into label
    if score >= 0.75:
        risk_level = "HIGH"
    elif score >= 0.40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    return {
        "agent": "fraud_agent",
        "fraud_score": round(score, 2),
        "risk_level": risk_level,
        "reasons": reasons
    }