def generate_report(investigation_result: dict) -> dict:
    transaction = investigation_result.get("transaction", {})

    fraud_agent = investigation_result.get("fraud_agent", {})
    behavior_agent = investigation_result.get("behavior_agent", {})
    merchant_agent = investigation_result.get("merchant_agent", {})
    location_agent = investigation_result.get("location_agent", {})
    ai_score = investigation_result.get(
        "ai_analyst_agent",
        {}
    ).get("ai_score", 0.0)

    final_result = investigation_result.get("final_result", {})

    txn_type = transaction.get("type", "UNKNOWN")
    amount = transaction.get("amount", 0)
    name_orig = transaction.get("nameOrig", "UNKNOWN")
    name_dest = transaction.get("nameDest", "UNKNOWN")

    final_score = final_result.get("final_score", 0.0)
    risk_level = final_result.get("risk_level", "LOW")
    decision = final_result.get("decision", "APPROVE")
    reasons = final_result.get("reasons", [])

    fraud_score = fraud_agent.get("fraud_score", 0.0)
    behavior_score = behavior_agent.get("behavior_score", 0.0)
    merchant_score = merchant_agent.get("merchant_score", 0.0)
    location_score = location_agent.get("location_score", 0.0)

    summary_lines = [
        "=== FRAUD INVESTIGATION REPORT ===",
        "",
        "Transaction Summary:",
        f"- Type: {txn_type}",
        f"- Amount: ${amount:,.2f}",
        f"- Sender: {name_orig}",
        f"- Receiver: {name_dest}",
        "",
        "Agent Findings:",
        f"- Fraud Agent Score: {fraud_score}",
        f"- Behavior Agent Score: {behavior_score}",
        f"- Receiver Agent Score: {merchant_score}",
        f"- Location Agent Score: {location_score}",
        f"- AI Risk Analyst Score: {ai_score} (independent contextual review)",
        "",
        "Final Assessment:",
        f"- Final Rule-Based Risk Score: {final_score}",
        f"- Risk Level: {risk_level}",
        f"- Decision: {decision}",
        f"- Agents Triggered: {len(reasons)}",
        ""
    ]

    if reasons:
        summary_lines.append("Key Reasons:")
        for reason in reasons:
            summary_lines.append(f"- {reason}")
    else:
        summary_lines.append("Key Reasons:")
        summary_lines.append("- No major suspicious indicators were detected.")

    summary_lines.extend([
        "",
        "Recommendation:"
    ])

    if decision == "BLOCK":
        summary_lines.append(
            "- Block this transaction immediately and trigger fraud response workflow."
        )
    elif decision == "ESCALATE":
        summary_lines.append(
            "- Escalate this transaction for manual analyst review."
        )
    else:
        summary_lines.append(
            "- Approve transaction. No immediate action required."
        )

    report_text = "\n".join(summary_lines)

    return {
        "report_text": report_text,
        "report_metadata": {
            "final_score": final_score,
            "risk_level": risk_level,
            "decision": decision,
            "fraud_score": fraud_score,
            "behavior_score": behavior_score,
            "merchant_score": merchant_score,
            "location_score": location_score,
            "ai_score": ai_score,
            "agents_triggered": len(reasons)
        }
    }
