from utils.config import LOCATION_AGENT_CONFIG
from utils.risk_utils import get_risk_level


def _is_enabled(value) -> bool:
    return value in [1, "1", True]


def analyze_location(transaction: dict,
                     config: dict = LOCATION_AGENT_CONFIG) -> dict:

    score = 0.0
    reasons = []

    geo_risk = transaction.get("geo_risk", 0)

    geo_distance = float(
        transaction.get("geo_distance_km", 0)
    )

    home_distance = float(
        transaction.get("home_distance_km", 0)
    )

    travel_speed = float(
        transaction.get("travel_speed_kmh", 0)
    )

    time_diff = float(
        transaction.get("time_diff", 999999)
    )

    is_night = _is_enabled(
        transaction.get("is_night", 0)
    )

    origin_lat = transaction.get("origin_lat")
    origin_long = transaction.get("origin_long")
    home_lat = transaction.get("home_lat")
    home_long = transaction.get("home_long")

    # ---------------------------------
    # IMPOSSIBLE / HIGH TRAVEL SPEED
    # ---------------------------------
    if travel_speed >= config["impossible_speed_threshold"]:

        score += config["impossible_speed_weight"]

        reasons.append(
            f"Impossible travel speed detected: "
            f"{travel_speed:.2f} km/h."
        )

    elif travel_speed >= config["high_speed_threshold"]:

        score += config["high_speed_weight"]

        reasons.append(
            f"Very high travel speed detected: "
            f"{travel_speed:.2f} km/h."
        )

    elif travel_speed >= config["medium_speed_threshold"]:

        score += config["medium_speed_weight"]

        reasons.append(
            f"Elevated travel speed detected: "
            f"{travel_speed:.2f} km/h."
        )

    # ---------------------------------
    # HOME DISTANCE CHECK
    # ---------------------------------
    if home_distance >= config["extreme_distance_threshold"]:

        score += config["extreme_distance_weight"]

        reasons.append(
            f"Transaction far from home location: "
            f"{home_distance:.2f} km."
        )

    elif home_distance >= config["moderate_distance_threshold"]:

        score += config["moderate_distance_weight"]

        reasons.append(
            f"Moderate distance from home detected: "
            f"{home_distance:.2f} km."
        )

    # ---------------------------------
    # GEO RISK FLAG
    # ---------------------------------
    if _is_enabled(geo_risk):

        score += config["geo_risk_weight"]

        reasons.append(
            "Geographic anomaly risk flag detected."
        )

    # ---------------------------------
    # NIGHT + HIGH MOVEMENT
    # ---------------------------------
    if (
        is_night
        and travel_speed >= config["high_speed_threshold"]
    ):

        score += config["night_speed_combo_weight"]

        reasons.append(
            "High geographic movement during night hours."
        )

    # ---------------------------------
    # MISSING LOCATION DATA
    # ---------------------------------
    if None in [
        origin_lat,
        origin_long,
        home_lat,
        home_long
    ]:

        score += config["missing_location_weight"]

        reasons.append(
            "Location fields are incomplete."
        )

    score = min(score, 1.0)

    risk_level = get_risk_level(
        score,
        "location_agent"
    )

    return {
        "agent": "location_agent",
        "location_score": round(score, 2),
        "risk_level": risk_level,
        "travel_speed_kmh": round(travel_speed, 2),
        "geo_distance_km": round(geo_distance, 2),
        "home_distance_km": round(home_distance, 2),
        "time_diff_seconds": round(time_diff, 2),
        "reasons": reasons
    }