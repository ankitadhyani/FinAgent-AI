from workflows.finagent_langgraph import run_fraud_graph


def investigate_transaction(
    transaction: dict,
    customer_profiles: dict | None = None,
    merchant_profiles: dict | None = None
) -> dict:
    try:
        return run_fraud_graph(
            transaction,
            customer_profiles=customer_profiles,
            merchant_profiles=merchant_profiles
        )

    except Exception as e:
        return {
            "error": str(e),
            "transaction_id": f"{transaction.get('nameOrig')}_{transaction.get('step')}",
            "transaction": transaction,
            "fraud_agent": {},
            "behavior_agent": {},
            "merchant_agent": {},
            "location_agent": {},
            "final_result": {
                "final_score": 0.0,
                "risk_level": "UNKNOWN",
                "decision": "REVIEW"
            },
            "report": "Workflow failed. Unable to generate investigation report."
        }

""" OLD file content
from agents.fraud_agent import analyze_fraud
from agents.behavior_agent import analyze_behavior
from agents.merchant_agent import analyze_merchant
from agents.location_agent import analyze_location
from services.risk_scoring import combine_agent_scores
from services.report_agent import generate_report


def investigate_transaction(
    transaction: dict,
    customer_profiles: dict,
    merchant_profiles: dict
) -> dict:
    try:
        fraud_result = analyze_fraud(transaction)
        behavior_result = analyze_behavior(transaction, customer_profiles)
        merchant_result = analyze_merchant(transaction, merchant_profiles)
        location_result = analyze_location(transaction)

        final_result = combine_agent_scores(
            fraud_result,
            behavior_result,
            merchant_result,
            location_result
        )

        investigation_result = {
            "transaction_id": f"{transaction.get('nameOrig')}_{transaction.get('step')}",
            "transaction": transaction,
            "fraud_agent": fraud_result,
            "behavior_agent": behavior_result,
            "merchant_agent": merchant_result,
            "location_agent": location_result,
            "final_result": final_result
        }

        investigation_result["report"] = generate_report(investigation_result)

        return investigation_result

    except Exception as e:
        return {
            "error": str(e),
            "transaction": transaction
        }
"""