from utils.config import (
    FINAL_AGENT_WEIGHTS,
    FINAL_SYSTEM_THRESHOLDS
)


def combine_agent_scores(
    fraud_result: dict,
    behavior_result: dict,
    merchant_result: dict,
    location_result: dict,
    ai_analyst_result: dict = None
) -> dict:

    fraud_score = fraud_result.get("fraud_score", 0.0)
    behavior_score = behavior_result.get("behavior_score", 0.0)
    merchant_score = merchant_result.get("merchant_score", 0.0)
    location_score = location_result.get("location_score", 0.0)
    ai_score = (
        ai_analyst_result.get("ai_score", 0.0)
        if ai_analyst_result else 0.0
    )

    final_score = (
        FINAL_AGENT_WEIGHTS["fraud"] * fraud_score
        + FINAL_AGENT_WEIGHTS["behavior"] * behavior_score
        + FINAL_AGENT_WEIGHTS["merchant"] * merchant_score
        + FINAL_AGENT_WEIGHTS["location"] * location_score
        + FINAL_AGENT_WEIGHTS.get("ai_analyst", 0.0) * ai_score
    )

    all_reasons = []

    all_reasons.extend(fraud_result.get("reasons", []))
    all_reasons.extend(behavior_result.get("reasons", []))
    all_reasons.extend(merchant_result.get("reasons", []))
    all_reasons.extend(location_result.get("reasons", []))

    if ai_analyst_result:
        all_reasons.extend(ai_analyst_result.get("reasons", []))

    unique_reasons = list(dict.fromkeys(all_reasons))

    if final_score >= FINAL_SYSTEM_THRESHOLDS["BLOCK"]:
        decision = "BLOCK"
        risk_level = "HIGH"
    elif final_score >= FINAL_SYSTEM_THRESHOLDS["ESCALATE"]:
        decision = "ESCALATE"
        risk_level = "MEDIUM"
    else:
        decision = "APPROVE"
        risk_level = "LOW"

    return {
        "final_score": round(final_score, 2),
        "risk_level": risk_level,
        "decision": decision,
        "reasons": unique_reasons,
        "component_scores": {
            "fraud_score": fraud_score,
            "behavior_score": behavior_score,
            "merchant_score": merchant_score,
            "location_score": location_score,
            "ai_score": ai_score
        }
    }