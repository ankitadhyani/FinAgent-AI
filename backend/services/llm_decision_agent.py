import os
import json
import time
import pickle
import pandas as pd

from dotenv import load_dotenv
from google import genai


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

ENV_PATH = os.path.join(BASE_DIR, ".env")

DEMO_PATH = os.path.join(BASE_DIR, "data", "paysim_demo.csv")
CUSTOMER_PROFILE_PATH = os.path.join(BASE_DIR, "data", "customer_profiles.pkl")
MERCHANT_PROFILE_PATH = os.path.join(BASE_DIR, "data", "merchant_profiles.pkl")

load_dotenv(dotenv_path=ENV_PATH)

api_key = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

GEMINI_ENABLED = bool(api_key)

if GEMINI_ENABLED:
    client = genai.Client(api_key=api_key)
    print("[INFO] Gemini AI Risk Analyst enabled.")
else:
    client = None
    print("[WARNING] GEMINI_API_KEY not found. AI Risk Analyst disabled.")


def extract_json_from_response(content):
    content = content.strip()

    content = content.replace("```json", "")
    content = content.replace("```JSON", "")
    content = content.replace("```", "")
    content = content.strip()

    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1:
        raise json.JSONDecodeError("No JSON object found", content, 0)

    return json.loads(content[start:end + 1])


def load_demo_data():
    df = pd.read_csv(DEMO_PATH)
    print("[INFO] Demo file loaded:", df.shape)
    return df


def load_pickle(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def build_llm_input(transaction, customer_profile, merchant_profile):

    return {
        "txn": {
            "type": transaction.get("type"),
            "amount": transaction.get("amount"),
            "hour": transaction.get("hour", 0),
            "is_night": transaction.get("is_night", 0),

            "amount_risk": transaction.get("amount_risk", 0),
            "balance_risk": transaction.get("balance_risk", 0),
            "balance_error": transaction.get("balance_error", 0),
            "balance_ratio": transaction.get("balance_ratio", 0),

            "velocity_risk": transaction.get("velocity_risk", 0),
            "high_velocity": transaction.get("high_velocity", 0),
            "txn_count_1hr": transaction.get("txn_count_1hr", 1),
            "time_diff": transaction.get("time_diff", 0),

            "geo_risk": transaction.get("geo_risk", 0),
            "geo_distance_km": transaction.get("geo_distance_km", 0),
            "home_distance_km": transaction.get("home_distance_km", 0),
            "travel_speed_kmh": transaction.get("travel_speed_kmh", 0),

            "device_type": transaction.get("device_type", ""),
            "device_risk": transaction.get("device_risk", 0),

            "behavior_risk": transaction.get("behavior_risk", 0),
            "customer_amount_ratio": transaction.get(
                "customer_amount_ratio",
                0
            )
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
            ),

            "historical_clean_behavior": 1
            if customer_profile.get("behavior_risk_rate", 0) < 0.1
            else 0,

            "historical_velocity_stability": 1
            if customer_profile.get("velocity_risk_rate", 0) < 0.1
            else 0,

            "historical_geo_stability": 1
            if customer_profile.get("geo_risk_rate", 0) < 0.1
            else 0
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
            ),

            "destination_low_amount_balance_risk": 1
            if (
                merchant_profile.get("amount_risk_rate", 0) < 0.1
                and merchant_profile.get("balance_risk_rate", 0) < 0.1
            )
            else 0
        }
    }


def ai_decision_agent(transaction, customer_profile, merchant_profile):
    if not GEMINI_ENABLED:
        return {
            "ai_final_score": 0.0,
            "ai_final_decision": "ESCALATE",
            "ai_final_reasoning": "AI reasoning unavailable. Gemini API key not configured."
        }

    llm_input = build_llm_input(
        transaction,
        customer_profile,
        merchant_profile
    )

    prompt = f"""
You are the AI Decision Agent for a banking fraud monitoring system.

Upstream rule-based specialist agents generate only structured evidence.
They do not make the final AI decision.

Your role is to review the evidence signals, customer profile, and
destination profile, then make the final AI decision.

Do not copy or assume the old rule-based decision.
The old rule-based decision is used only outside this prompt as a
validation baseline.

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

Evidence Signal Meaning:

- amount_risk means the transaction amount was unusual compared with
  the overall amount distribution.

- balance_risk means the transaction nearly drained the available
  origin balance during a TRANSFER or CASH_OUT transaction.

- balance_error shows the absolute mismatch in expected origin balance
  after the transaction.

- velocity_risk means the generated one-hour transaction count was high.

- high_velocity means the same customer had very rapid repeat activity
  based on short time difference.

- geo_risk means the transaction location was suspicious because of
  high travel speed or large distance from home.

- behavior_risk means the transaction deviated from the customer's
  normal amount behavior or velocity behavior.

- device_risk means the device channel may support risk, but it should
  not determine the final decision alone.

- customer_amount_ratio compares the current amount with the customer's
  simulated historical average amount.

- historical_clean_behavior means the customer historically has a low
  behavioral anomaly rate.

- historical_velocity_stability means the customer historically has a
  low velocity-risk rate.

- historical_geo_stability means the customer historically has a low
  geographic-risk rate.

- destination_low_amount_balance_risk means the destination historically
  has low amount-risk and balance-risk rates.

Decision Workflow:

1. Transaction Review
- TRANSFER and CASH_OUT require closer review only when supported by
  suspicious evidence.
- CASH_IN and PAYMENT are generally low-risk transaction types.
- Do not call CASH_IN a high-risk transaction type.
- Do not say CASH_IN requires closer review unless multiple strong
  risk flags are active.

2. Customer Review
- Compare the transaction with customer profile history.
- Stable customer history should reduce concern unless strong current
  evidence exists.
- Repeated abnormal customer behavior should increase concern.

3. Balance and Velocity Review
- Balance risk is important when it appears with amount risk,
  behavior risk, velocity risk, or geo risk.
- A single weak signal should not automatically decide the outcome.

4. Location, Device, and Time Review
- Location, device, and night activity are supporting signals.
- Large distance alone is not enough for BLOCK.
- Device risk alone is not enough for ESCALATE or BLOCK.

5. Destination Review
- High destination transaction count alone is not fraud.
- Many unique senders alone is not fraud.
- Destination risk matters more when combined with abnormal transaction,
  balance, velocity, customer, or location evidence.

Final Decision Calibration:

- APPROVE when evidence is normal, weak, isolated, or explainable by
  customer or destination history.

- APPROVE does not mean zero risk. It means the evidence is not strong
  enough for manual review or blocking.

- ESCALATE when suspicious evidence exists but is not strong enough to
  stop the transaction immediately.

- BLOCK only when multiple severe fraud indicators strongly align and
  the overall evidence clearly suggests high fraud likelihood.

- Strong BLOCK decisions usually involve:
    - TRANSFER or CASH_OUT
    - amount_risk = 1
    - balance_risk = 1
    - at least one strong supporting signal such as behavior_risk,
      geo_risk, velocity_risk, or high_velocity.

- PAYMENT and CASH_IN should rarely become BLOCK unless extremely strong
  evidence exists.

- If amount_risk = 0 and balance_risk = 0, BLOCK is usually not
  appropriate.

- If amount_risk = 0, balance_risk = 0, behavior_risk = 0,
  geo_risk = 0, velocity_risk = 0, and high_velocity = 0,
  the decision should usually be APPROVE.

- Do not choose BLOCK when the reasoning itself says the risk flags are 0.

- Do not use ESCALATE as a safe default.

Reasoning Rules:

- Use only the provided input.
- Maximum 2 short reasoning lines.
- Do not invent missing history.
- Mention only visible evidence signals.
- Do not describe a risk flag as active when its value is 0.
- Do not say "multiple severe indicators" unless multiple risk flags
  are actually 1.
- Do not mention the old rule-based decision.
- Do not mention thresholds.

Score Guidance:

- The score is confidence in the selected AI decision.
- Use different scores based on evidence strength.
- APPROVE can have moderate confidence when the transaction appears normal.
- ESCALATE should have middle confidence only when evidence is uncertain.
- BLOCK should have high confidence only when strong signals align.
""".strip()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "temperature": 0,
            "response_mime_type": "application/json"
        }
    )

    content = response.text.strip()



    try:
        parsed = extract_json_from_response(content)
    except json.JSONDecodeError:
        parsed = {
            "score": 0.5,
            "decision": "ESCALATE",
            "reasoning": [
                "AI response could not be parsed.",
                "Defaulted to review-level decision."
            ]
        }

    try:
        score = float(parsed.get("score", 0.5))
    except Exception:
        score = 0.5

    score = max(0.0, min(score, 1.0))

    decision = str(parsed.get("decision", "ESCALATE")).upper()

    if decision not in ["APPROVE", "ESCALATE", "BLOCK"]:
        decision = "ESCALATE"

    reasoning = parsed.get("reasoning", [])

    if isinstance(reasoning, str):
        reasoning = [reasoning]

    reasoning = reasoning[:2]

    return {
        "ai_final_score": round(score, 2),
        "ai_final_decision": decision,
        "ai_final_reasoning": " | ".join(reasoning)
    }


def print_decision_mismatch_summary(df):

    if "ai_decision" not in df.columns:
        print("[INFO] No AI decision column found.")
        return

    updated_df = df[
        df["ai_decision"].astype(str).str.upper().isin(
            ["APPROVE", "ESCALATE", "BLOCK"]
        )
    ].copy()

    if updated_df.empty:
        print("[INFO] No AI-updated rows found for mismatch check.")
        return

    updated_df["decision"] = updated_df["decision"].astype(str).str.upper()
    updated_df["ai_decision"] = updated_df["ai_decision"].astype(str).str.upper()

    mismatch_df = updated_df[
        updated_df["decision"] != updated_df["ai_decision"]
    ]

    print(
        f"[INFO] AI/system decision mismatches: "
        f"{len(mismatch_df)}/{len(updated_df)}"
    )

    print("\n[INFO] Rule-based decision distribution:")
    print(updated_df["decision"].value_counts().to_string())

    print("\n[INFO] AI decision distribution:")
    print(updated_df["ai_decision"].value_counts().to_string())

    if not mismatch_df.empty:
        print("\n[INFO] Mismatch breakdown:")
        print(
            mismatch_df
            .groupby(["decision", "ai_decision"])
            .size()
            .reset_index(name="count")
            .to_string(index=False)
        )

        preview_cols = [
            "nameOrig",
            "nameDest",
            "type",
            "amount",
            "decision",
            "ai_decision",
            "ai_score",
            "ai_reasoning"
        ]

        available_cols = [
            col for col in preview_cols
            if col in mismatch_df.columns
        ]

        print("\n[INFO] Sample mismatches:")
        print(
            mismatch_df[available_cols]
            .head(10)
            .to_string(index=False)
        )


def reset_ai_columns(df):
    df["ai_score"] = ""
    df["ai_decision"] = ""
    df["ai_reasoning"] = ""
    return df


def update_demo_with_ai_decision(limit=20, reset_existing=False):

    df = load_demo_data()

    if reset_existing:
        df = reset_ai_columns(df)
        df.to_csv(DEMO_PATH, index=False)
        print("[INFO] Existing AI columns cleared.")

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

    df["ai_score"] = df["ai_score"].astype(object)
    df["ai_decision"] = df["ai_decision"].astype(object)
    df["ai_reasoning"] = df["ai_reasoning"].astype(object)

    updated_count = 0
    total_rows = len(df)

    for idx, row in df.iterrows():

        if updated_count >= limit:
            break

        existing_decision = str(
            row.get("ai_decision", "")
        ).strip().upper()

        if existing_decision in ["APPROVE", "ESCALATE", "BLOCK"]:
            print(f"[SKIP] Row {idx + 1}/{total_rows}: already updated.")
            continue

        transaction = row.to_dict()

        customer_id = transaction.get("nameOrig")
        merchant_id = transaction.get("nameDest")

        customer_profile = customer_profiles.get(customer_id, {})
        merchant_profile = merchant_profiles.get(merchant_id, {})

        try:
            result = ai_decision_agent(
                transaction,
                customer_profile,
                merchant_profile
            )

            df.at[idx, "ai_score"] = result["ai_final_score"]
            df.at[idx, "ai_decision"] = result["ai_final_decision"]
            df.at[idx, "ai_reasoning"] = result["ai_final_reasoning"]

            updated_count += 1

            print(
                f"[DONE] Updated {updated_count}/{limit} | "
                f"Row {idx + 1}/{total_rows} | "
                f"Decision: {result['ai_final_decision']} | "
                f"Score: {result['ai_final_score']}"
            )

            df.to_csv(DEMO_PATH, index=False)
            time.sleep(4)

        except Exception as e:
            error_text = str(e)

            if "404" in error_text or "NOT_FOUND" in error_text:
                print("[STOP] Gemini model not found. Check MODEL_NAME.")
                df.to_csv(DEMO_PATH, index=False)
                break

            if "503" in error_text or "UNAVAILABLE" in error_text:
                print("[STOP] 503 temporary Gemini overload detected.")
                print("[INFO] Saving progress and stopping.")
                df.to_csv(DEMO_PATH, index=False)
                break

            if (
                "429" in error_text
                or "rate limit" in error_text.lower()
            ):
                print("[STOP] 429/rate limit detected.")
                print("[INFO] Saving progress and stopping.")
                df.to_csv(DEMO_PATH, index=False)
                break

            print(f"[ERROR] Row {idx + 1}/{total_rows}: {error_text}")
            print("[INFO] Continuing to next row.")

    df.to_csv(DEMO_PATH, index=False)

    print_decision_mismatch_summary(df)

    print("\n[INFO] AI decision update completed.")
    print("[INFO] Updated same file:", DEMO_PATH)


if __name__ == "__main__":
    update_demo_with_ai_decision(
        limit=10,
        reset_existing=False
    )
