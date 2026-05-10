from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph, END

from agents.fraud_agent import analyze_fraud
from agents.behavior_agent import analyze_behavior
from agents.merchant_agent import analyze_merchant
from agents.location_agent import analyze_location
from services.risk_scoring import combine_agent_scores
from services.report_agent import generate_report


class FraudGraphState(TypedDict, total=False):
    transaction: Dict[str, Any]
    customer_profiles: Dict[str, Any]
    merchant_profiles: Dict[str, Any]

    suspicious: bool

    fraud_result: Dict[str, Any]
    behavior_result: Dict[str, Any]
    merchant_result: Dict[str, Any]
    location_result: Dict[str, Any]
    ai_analyst_result: Dict[str, Any]

    final_result: Dict[str, Any]
    report: str
    final_response: Dict[str, Any]


def ingest_transaction_node(state: FraudGraphState) -> FraudGraphState:
    return state


def suspicious_check_node(state: FraudGraphState) -> FraudGraphState:
    transaction = state["transaction"]

    amount = float(transaction.get("amount", 0))
    tx_type = transaction.get("type", "")

    state["suspicious"] = (
        amount > 100000
        or tx_type in ["TRANSFER", "CASH_OUT"]
    )

    return state


def route_suspicious(state: FraudGraphState) -> str:
    if state.get("suspicious"):
        return "suspicious"
    return "low_risk"


def low_risk_no_action_node(state: FraudGraphState) -> FraudGraphState:
    transaction = state["transaction"]

    final_result = {
        "final_score": 0.0,
        "risk_level": "LOW",
        "decision": "APPROVE",
        "reasons": ["Transaction did not trigger suspicious-rule checks."]
    }

    investigation_result = {
        "transaction_id": f"{transaction.get('nameOrig')}_{transaction.get('step')}",
        "transaction": transaction,
        "fraud_agent": {},
        "behavior_agent": {},
        "merchant_agent": {},
        "location_agent": {},
        "ai_analyst_agent": {},
        "final_result": final_result
    }

    investigation_result["report"] = generate_report(investigation_result)
    state["final_response"] = investigation_result

    return state


def fraud_analysis_node(state: FraudGraphState) -> FraudGraphState:
    state["fraud_result"] = analyze_fraud(state["transaction"])
    return state


def customer_behavior_node(state: FraudGraphState) -> FraudGraphState:
    state["behavior_result"] = analyze_behavior(
        state["transaction"],
        state.get("customer_profiles", {})
    )
    return state


def merchant_risk_node(state: FraudGraphState) -> FraudGraphState:
    state["merchant_result"] = analyze_merchant(
        state["transaction"],
        state.get("merchant_profiles", {})
    )
    return state


def location_analysis_node(state: FraudGraphState) -> FraudGraphState:
    state["location_result"] = analyze_location(state["transaction"])
    return state


def ai_risk_analyst_node(state: FraudGraphState) -> FraudGraphState:
    transaction = state["transaction"]

    ai_score = float(transaction.get("ai_score", 0) or 0)
    ai_reasoning = transaction.get("ai_reasoning") or "No AI analyst reasoning available."
    ai_decision = transaction.get("ai_decision") or "LOW"

    state["ai_analyst_result"] = {
        "ai_score": ai_score,
        "rag_score": ai_score,
        "score": ai_score,
        "risk_level": ai_decision,
        "decision": ai_decision,
        "reasons": [ai_reasoning],
    }

    return state


def risk_scoring_node(state: FraudGraphState) -> FraudGraphState:
    state["final_result"] = combine_agent_scores(
        state.get("fraud_result", {}),
        state.get("behavior_result", {}),
        state.get("merchant_result", {}),
        state.get("location_result", {}),
        state.get("ai_analyst_result", {})
    )
    return state


def report_generation_node(state: FraudGraphState) -> FraudGraphState:
    transaction = state["transaction"]

    investigation_result = {
        "transaction_id": f"{transaction.get('nameOrig')}_{transaction.get('step')}",
        "transaction": transaction,
        "fraud_agent": state.get("fraud_result", {}),
        "behavior_agent": state.get("behavior_result", {}),
        "merchant_agent": state.get("merchant_result", {}),
        "location_agent": state.get("location_result", {}),
        "ai_analyst_agent": state.get("ai_analyst_result", {}),
        "final_result": state.get("final_result", {})
    }

    investigation_result["report"] = generate_report(investigation_result)

    state["final_response"] = investigation_result
    return state


def build_fraud_graph():
    graph = StateGraph(FraudGraphState)

    graph.add_node("ingest_transaction", ingest_transaction_node)
    graph.add_node("suspicious_check", suspicious_check_node)
    graph.add_node("low_risk_no_action", low_risk_no_action_node)

    graph.add_node("fraud_analysis_agent", fraud_analysis_node)
    graph.add_node("customer_behavior_agent", customer_behavior_node)
    graph.add_node("merchant_risk_agent", merchant_risk_node)
    graph.add_node("location_analysis_agent", location_analysis_node)
    graph.add_node("ai_risk_analyst_agent", ai_risk_analyst_node)

    graph.add_node("risk_scoring_agent", risk_scoring_node)
    graph.add_node("report_generation_agent", report_generation_node)

    graph.set_entry_point("ingest_transaction")

    graph.add_edge("ingest_transaction", "suspicious_check")

    graph.add_conditional_edges(
        "suspicious_check",
        route_suspicious,
        {
            "low_risk": "low_risk_no_action",
            "suspicious": "fraud_analysis_agent"
        }
    )

    graph.add_edge("low_risk_no_action", END)

    graph.add_edge("fraud_analysis_agent", "customer_behavior_agent")
    graph.add_edge("customer_behavior_agent", "merchant_risk_agent")
    graph.add_edge("merchant_risk_agent", "location_analysis_agent")
    graph.add_edge("location_analysis_agent", "ai_risk_analyst_agent")
    graph.add_edge("ai_risk_analyst_agent", "risk_scoring_agent")
    graph.add_edge("risk_scoring_agent", "report_generation_agent")
    graph.add_edge("report_generation_agent", END)

    return graph.compile()


fraud_graph = build_fraud_graph()


def run_fraud_graph(
    transaction: Dict[str, Any],
    customer_profiles: Dict[str, Any] | None = None,
    merchant_profiles: Dict[str, Any] | None = None
) -> Dict[str, Any]:

    initial_state = {
        "transaction": transaction,
        "customer_profiles": customer_profiles or {},
        "merchant_profiles": merchant_profiles or {}
    }

    result = fraud_graph.invoke(initial_state)
    return result["final_response"]