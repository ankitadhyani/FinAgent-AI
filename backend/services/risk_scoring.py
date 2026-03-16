

def combine_agent_scores(fraud_result: dict, behavior_result: dict) -> dict:
    fraud_score = fraud_result.get("fraud_score", 0.0)
    behavior_score = behavior_result.get("behavior_score", 0.0)

    # Weighted combination
    # fraud agent = 70%
    # behavior agent = 30%
    # Right now fraud agent is stronger than behavior agent, 
    # since behavior history may often be missing.
    final_score = (0.7 * fraud_score) + (0.3 * behavior_score)

    # Merge reasons
    all_reasons = []
    all_reasons.extend(fraud_result.get("reasons", []))
    all_reasons.extend(behavior_result.get("reasons", []))

    # Final decision
    if final_score >= 0.75:
        decision = "BLOCK"
        risk_level = "HIGH"
    elif final_score >= 0.40:
        decision = "ESCALATE"
        risk_level = "MEDIUM"
    else:
        decision = "APPROVE"
        risk_level = "LOW"

    return {
        "final_score": round(final_score, 2),
        "risk_level": risk_level,
        "decision": decision,
        "reasons": all_reasons
    }