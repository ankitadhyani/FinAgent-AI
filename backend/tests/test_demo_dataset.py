import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_PATH = os.path.join(BASE_DIR, "data", "paysim_demo.csv")

REQUIRED_COLUMNS = [
    "step", "type", "amount", "nameOrig", "nameDest",
    "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest",
    "isFraud", "isFlaggedFraud",
    "fraud_score", "behavior_score", "merchant_score", "location_score",
    "final_score", "risk_level", "decision"
]


def test_demo_dataset_exists():
    assert os.path.exists(DEMO_PATH), "paysim_demo.csv does not exist"


def test_shape():
    df = pd.read_csv(DEMO_PATH)
    assert len(df) == 600, f"Expected 600 rows, got {len(df)}"


def test_required_columns():
    df = pd.read_csv(DEMO_PATH)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    assert not missing, f"Missing columns: {missing}"


def test_no_nulls():
    df = pd.read_csv(DEMO_PATH)
    assert df[REQUIRED_COLUMNS].isnull().sum().sum() == 0, "Null values found"


def test_decision_distribution():
    df = pd.read_csv(DEMO_PATH)
    counts = df["decision"].value_counts()

    assert counts.get("APPROVE", 0) == 200
    assert counts.get("ESCALATE", 0) == 200
    assert counts.get("BLOCK", 0) == 200


def test_valid_decisions():
    df = pd.read_csv(DEMO_PATH)
    valid = {"APPROVE", "ESCALATE", "BLOCK"}
    assert df["decision"].isin(valid).all()


def test_valid_risk_levels():
    df = pd.read_csv(DEMO_PATH)
    valid = {"LOW", "MEDIUM", "HIGH"}
    assert df["risk_level"].isin(valid).all()


def test_no_negative_amounts():
    df = pd.read_csv(DEMO_PATH)
    assert (df["amount"] >= 0).all()


def test_unique_transaction_ids():
    df = pd.read_csv(DEMO_PATH)
    assert df["transaction_id"].duplicated().sum() == 0


def test_score_range():
    df = pd.read_csv(DEMO_PATH)
    for col in ["fraud_score", "behavior_score", "merchant_score", "location_score", "final_score"]:
        assert ((df[col] >= 0) & (df[col] <= 1)).all(), f"{col} out of range"