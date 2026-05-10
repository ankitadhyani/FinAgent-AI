from data_loader import load_data
from agents.fraud_agent import analyze_fraud
from agents.behavior_agent import analyze_behavior
from services.risk_scoring import combine_agent_scores


if __name__ == "__main__":
    df = load_data()

    safe_txn = {
        "step": 500,
        "type": "PAYMENT",
        "amount": 1000.0,
        "nameOrig": "C111",
        "oldbalanceOrg": 5000.0,
        "newbalanceOrig": 4000.0,
        "nameDest": "M222",
        "oldbalanceDest": 0.0,
        "newbalanceDest": 0.0
    }
    moderate_suspicious_txn = {
        "step": 500,
        "type": "CASH_OUT",
        "amount": 60000.0,
        "nameOrig": "C333",
        "oldbalanceOrg": 70000.0,
        "newbalanceOrig": 10000.0,
        "nameDest": "C444",
        "oldbalanceDest": 0.0,
        "newbalanceDest": 0.0
    }
    suspicious_txn = {
        "step": 500,
        "type": "TRANSFER",
        "amount": 750000.0,
        "nameOrig": "C999999999",
        "oldbalanceOrg": 0.0,
        "newbalanceOrig": 0.0,
        "nameDest": "C888888888",
        "oldbalanceDest": 0.0,
        "newbalanceDest": 0.0
    }

    print("\n===== MANUAL HIGH-RISK TRANSACTION =====")
    print(suspicious_txn)

    fraud_result = analyze_fraud(suspicious_txn)
    behavior_result = analyze_behavior(suspicious_txn, df)
    final_result = combine_agent_scores(fraud_result, behavior_result)

    print("\nFraud Agent Output:")
    print(fraud_result)

    print("\nBehavior Agent Output:")
    print(behavior_result)

    print("\nFinal Combined Result:")
    print(final_result)
