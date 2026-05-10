import os
import json
import time
import pickle
import pandas as pd

from dotenv import load_dotenv
from groq import Groq


# =========================
# PATH CONFIG
# =========================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

ENV_PATH = os.path.join(BASE_DIR, ".env")

DEMO_PATH = os.path.join(BASE_DIR, "data", "paysim_demo.csv")
CUSTOMER_PROFILE_PATH = os.path.join(BASE_DIR, "data", "customer_profiles.pkl")
MERCHANT_PROFILE_PATH = os.path.join(BASE_DIR, "data", "merchant_profiles.pkl")


# =========================
# API CONFIG
# =========================

load_dotenv(dotenv_path=ENV_PATH)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check backend/.env file.")

groq_client = Groq(api_key=api_key)


# =========================
# LOAD FILES
# =========================

def load_demo_data():
    df = pd.read_csv(DEMO_PATH)
    print("[INFO] Demo file loaded:", df.shape)
    return df


def load_pickle(path):
    with open(path, "rb") as f:
        return pickle.load(f)


# =========================
# LLM INPUT BUILDER
# =========================

def build_llm_input(transaction, customer_profile, merchant_profile):
    return {
        "txn": {
            "type": transaction.get("type"),
            "amount": transaction.get("amount"),

            "amount_risk": transaction.get("amount_risk", 0),
            "balance_risk": transaction.get("balance_risk", 0),
            "velocity_risk": transaction.get("velocity_risk", 0),
            "high_velocity": transaction.get("high_velocity", 0),
            "txn_count_1hr": transaction.get("txn_count_1hr", 1),

            "geo_risk": transaction.get("geo_risk", 0),
            "geo_distance_km": transaction.get("geo_distance_km", 0),
            "home_distance_km": transaction.get("home_distance_km", 0),
            "travel_speed_kmh": transaction.get("travel_speed_kmh", 0),
            "time_diff": transaction.get("time_diff", 0),

            "device_risk": transaction.get("device_risk", 0),
            "is_night": transaction.get("is_night", 0),
            "behavior_risk": transaction.get("behavior_risk", 0),

            "customer_amount_ratio": transaction.get(
                "customer_amount_ratio",
                0
            ),

            "fraud_score": transaction.get("fraud_score", 0),
            "behavior_score": transaction.get("behavior_score", 0),
            "merchant_score": transaction.get("merchant_score", 0),
            "location_score": transaction.get("location_score", 0),
            "final_score": transaction.get("final_score", 0),
            "risk_level": transaction.get("risk_level", "LOW")
        },

        "cust_profile": {
            "txn_count": customer_profile.get("txn_count", 0),
            "avg_amount": customer_profile.get("avg_amount", 0),
            "max_amount": customer_profile.get("max_amount", 0),

            "avg_amount_ratio": customer_profile.get(
                "avg_customer_amount_ratio",
                0
            ),

            "max_amount_ratio": customer_profile.get(
                "max_customer_amount_ratio",
                0
            ),

            "behavior_risk_rate": customer_profile.get(
                "behavior_risk_rate",
                0
            ),

            "velocity_risk_rate": customer_profile.get(
                "velocity_risk_rate",
                0
            ),

            "night_txn_rate": customer_profile.get(
                "night_txn_rate",
                0
            ),

            "avg_home_distance_km": customer_profile.get(
                "avg_home_distance_km",
                0
            ),

            "max_home_distance_km": customer_profile.get(
                "max_home_distance_km",
                0
            ),

            "avg_travel_speed_kmh": customer_profile.get(
                "avg_travel_speed_kmh",
                0
            ),

            "max_travel_speed_kmh": customer_profile.get(
                "max_travel_speed_kmh",
                0
            ),

            "geo_risk_rate": customer_profile.get(
                "geo_risk_rate",
                0
            )
        },

        "dest_profile": {
            "txn_count": merchant_profile.get("txn_count", 0),
            "unique_senders": merchant_profile.get("unique_senders", 0),
            "avg_amount": merchant_profile.get("avg_amount", 0),
            "max_amount": merchant_profile.get("max_amount", 0),

            "amount_risk_rate": merchant_profile.get(
                "amount_risk_rate",
                0
            ),

            "balance_risk_rate": merchant_profile.get(
                "balance_risk_rate",
                0
            ),

            "device_risk_rate": merchant_profile.get(
                "device_risk_rate",
                0
            )
        }
    }


# =========================
# LLM DECISION CALL
# =========================

def call_llm_decision(transaction, customer_profile, merchant_profile):

    llm_input = build_llm_input(
        transaction,
        customer_profile,
        merchant_profile
    )

    prompt = f"""
You are an AI fraud decision agent.

Input:
{json.dumps(llm_input, separators=(",", ":"))}

Return only valid JSON.

Format:
{{
  "score": 0.0,
  "decision": "APPROVE/ESCALATE/BLOCK",
  "reasoning": [
    "short reason 1",
    "short reason 2"
  ]
}}

Rules:
- Decide independently using transaction risk flags, agent scores, customer profile, and destination profile.
- Decision must be one of: APPROVE, ESCALATE, BLOCK.
- Score must be between 0 and 1.

APPROVE guidance:
- Strongly prefer APPROVE when risk_level is LOW, final_score < 0.20, amount_risk = 0, balance_risk = 0, velocity_risk = 0, high_velocity = 0, geo_risk = 0.
- For PAYMENT or CASH_IN with LOW risk_level and final_score < 0.20, choose APPROVE unless at least two strong fraud indicators exist.
- Do not escalate only because device_risk = 1.
- Do not escalate only because customer_amount_ratio is above average.
- Do not escalate only because transaction amount is high.
- Do not treat web/mobile/atm alone as fraud.

Velocity guidance:
- txn_count_1hr = 1, high_velocity = 0, and velocity_risk = 0 means normal current velocity.
- Low customer velocity_risk_rate means the customer does not have repeated velocity-risk history.
- Do not mention rapid, repeated, or multiple transactions unless velocity_risk = 1, high_velocity = 1, or txn_count_1hr >= 3.

Location guidance:
- travel_speed_kmh above 300 km/h indicates suspicious movement between consecutive transactions.
- geo_distance_km represents movement from previous transaction location to current transaction location.
- home_distance_km represents distance from customer home region.
- geo_risk = 1 means the location agent detected suspicious geographic behavior.
- Large distance alone is not fraud unless combined with unrealistic travel speed, geo_risk, or other fraud indicators.
- Do not mention impossible travel unless travel_speed_kmh is high.
- Low customer geo_risk_rate means the customer does not repeatedly show location-risk behavior.

Customer profile guidance:
- Recent transaction history is limited only when cust_profile.txn_count <= 1.
- If cust_profile.txn_count > 1, do not say "single transaction", "limited history", or "no context".
- behavior_risk_rate close to 0 means this customer has mostly normal historical behavior.
- A high customer_amount_ratio alone is not enough for ESCALATE unless combined with strong fraud indicators.

Merchant guidance:
- unique_senders alone is not fraud.
- High destination transaction volume is not fraud by itself.
- High merchant activity is suspicious only when combined with amount_risk, balance_risk, velocity_risk, geo_risk, or high destination risk rates.
- Low amount_risk_rate and low balance_risk_rate mean the destination has mostly normal historical activity.

Strong fraud indicators:
- balance_risk = 1
- velocity_risk = 1
- high_velocity = 1
- geo_risk = 1
- amount_risk = 1
- behavior_risk = 1
- TRANSFER or CASH_OUT combined with balance_risk or velocity_risk

Escalate/Block guidance:
- ESCALATE only when there are mixed or moderate suspicious signals.
- BLOCK only when multiple strong indicators appear together.
- TRANSFER or CASH_OUT with balance_risk + velocity_risk or geo_risk should be treated as high risk.
- PAYMENT or CASH_IN with no strong fraud indicators should usually be APPROVE.

Reasoning:
- Use only the provided input.
- Maximum 2 short reasoning lines.
- Do not invent missing history.
- Do not mention any signal that is not present in the input.
""".strip()

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "Return only valid JSON. No extra text."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(content)

    except json.JSONDecodeError:

        parsed = {
            "score": 0.5,
            "decision": "ESCALATE",
            "reasoning": [
                "LLM response could not be parsed.",
                "Defaulted to review-level decision."
            ]
        }

    try:
        score = float(parsed.get("score", 0.5))
    except:
        score = 0.5

    score = max(0.0, min(score, 1.0))

    decision = str(
        parsed.get("decision", "ESCALATE")
    ).upper()

    if decision not in [
        "APPROVE",
        "ESCALATE",
        "BLOCK"
    ]:
        decision = "ESCALATE"

    reasoning = parsed.get("reasoning", [])

    if isinstance(reasoning, str):
        reasoning = [reasoning]

    reasoning = reasoning[:2]

    return {
        "ai_score": round(score, 2),
        "ai_decision": decision,
        "ai_reasoning": " | ".join(reasoning)
    }


# =========================
# UPDATE DEMO FILE
# =========================

def update_demo_with_ai_decision(limit=6):

    df = load_demo_data()

    customer_profiles = load_pickle(CUSTOMER_PROFILE_PATH)
    merchant_profiles = load_pickle(MERCHANT_PROFILE_PATH)

    print("[INFO] Customer profiles loaded:", len(customer_profiles))
    print("[INFO] Merchant profiles loaded:", len(merchant_profiles))

    if "ai_score" not in df.columns:
        df["ai_score"] = ""

    if "ai_decision" not in df.columns:
        df["ai_decision"] = ""

    if "ai_reasoning" not in df.columns:
        df["ai_reasoning"] = ""

    updated_count = 0
    total_rows = len(df)

    for idx, row in df.iterrows():

        if updated_count >= limit:
            break

        existing_decision = str(
            row.get("ai_decision", "")
        ).strip().upper()

        if existing_decision in [
            "APPROVE",
            "ESCALATE",
            "BLOCK"
        ]:
            print(
                f"[SKIP] Row {idx + 1}/{total_rows}: already updated."
            )
            continue

        transaction = row.to_dict()

        customer_id = transaction.get("nameOrig")
        merchant_id = transaction.get("nameDest")

        customer_profile = customer_profiles.get(
            customer_id,
            {}
        )

        merchant_profile = merchant_profiles.get(
            merchant_id,
            {}
        )

        try:

            result = call_llm_decision(
                transaction,
                customer_profile,
                merchant_profile
            )

            df.at[idx, "ai_score"] = result["ai_score"]
            df.at[idx, "ai_decision"] = result["ai_decision"]
            df.at[idx, "ai_reasoning"] = result["ai_reasoning"]

            updated_count += 1

            print(
                f"[DONE] Updated {updated_count}/{limit} | "
                f"Row {idx + 1}/{total_rows} | "
                f"Decision: {result['ai_decision']} | "
                f"Score: {result['ai_score']}"
            )

            df.to_csv(DEMO_PATH, index=False)

            time.sleep(1)

        except Exception as e:

            error_text = str(e)

            if (
                "429" in error_text
                or "rate limit" in error_text.lower()
            ):

                print("[STOP] 429/rate limit detected.")
                print("[INFO] Saving progress and stopping.")

                df.to_csv(DEMO_PATH, index=False)

                break

            print(
                f"[ERROR] Row {idx + 1}/{total_rows}: "
                f"{error_text}"
            )

            print("[INFO] Continuing to next row.")

    df.to_csv(DEMO_PATH, index=False)

    print("\n[INFO] AI decision update completed.")
    print("[INFO] Updated same file:", DEMO_PATH)


if __name__ == "__main__":
    update_demo_with_ai_decision(limit=6)