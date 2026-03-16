def build_transaction_record(raw_transaction: dict) -> dict:
    return {
        "step": raw_transaction.get("step"),
        "type": raw_transaction.get("type"),
        "amount": raw_transaction.get("amount"),
        "nameOrig": raw_transaction.get("nameOrig"),
        "oldbalanceOrg": raw_transaction.get("oldbalanceOrg"),
        "newbalanceOrig": raw_transaction.get("newbalanceOrig"),
        "nameDest": raw_transaction.get("nameDest"),
        "oldbalanceDest": raw_transaction.get("oldbalanceDest"),
        "newbalanceDest": raw_transaction.get("newbalanceDest"),
        "isFraud": raw_transaction.get("isFraud"),
        "isFlaggedFraud": raw_transaction.get("isFlaggedFraud"),
    }