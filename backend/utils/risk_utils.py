from utils.config import AGENT_RISK_BANDS

def get_risk_level(score: float, agent_name: str) -> str:
    bands = AGENT_RISK_BANDS.get(agent_name)

    if score >= bands["HIGH"]:
        return "HIGH"
    elif score >= bands["MEDIUM"]:
        return "MEDIUM"
    return "LOW"