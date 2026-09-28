import os
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# ============================================================
# GRIDMIND — GRID ANOMALY DETECTION ENGINE
# Unsupervised Detection using Isolation Forest
# ============================================================

BASE_DIR = r"D:\GridMind"

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "silver_energy_intelligence.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models",
    "artifacts"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


print("=" * 70)
print("GRIDMIND — GRID ANOMALY DETECTION ENGINE")
print("=" * 70)


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

print("\n[1/6] Loading Silver intelligence data...")

df = pd.read_csv(INPUT_FILE)

df["Timestamp"] = pd.to_datetime(
    df["Timestamp"]
)

df = df.sort_values(
    ["Region", "Timestamp"]
).reset_index(drop=True)

print(f"Rows loaded: {len(df):,}")


# ------------------------------------------------------------
# 2. SELECT ANOMALY FEATURES
# ------------------------------------------------------------

print("\n[2/6] Preparing anomaly features...")

FEATURES = [
    "Demand_MW",
    "Demand_Lag_1H",
    "Demand_Lag_24H",
    "Demand_Lag_168H",
    "Demand_Rolling_24H",
    "Demand_Rolling_168H",

    "Temperature_C",
    "Humidity_pct",
    "Wind_Speed_kmh",
    "Solar_Irradiance",

    "Voltage_V",
    "Avg_Voltage_V",
    "Avg_Current_A",
    "Avg_Power_Factor",

    "Renewable_MW",
    "Renewable_Share_pct",
    "Generation_Demand_Ratio",

    "Is_Peak_Hour",
    "IsWeekend"
]

FEATURES = [
    feature
    for feature in FEATURES
    if feature in df.columns
]

X = df[FEATURES].copy()

X = X.replace(
    [np.inf, -np.inf],
    np.nan
)

X = X.fillna(
    X.median(numeric_only=True)
)

print(f"Features used: {len(FEATURES)}")


# ------------------------------------------------------------
# 3. STANDARDIZE
# ------------------------------------------------------------

print("\n[3/6] Standardizing anomaly signals...")

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ------------------------------------------------------------
# 4. TRAIN ISOLATION FOREST
# ------------------------------------------------------------

print("\n[4/6] Training Isolation Forest...")

model = IsolationForest(
    n_estimators=200,
    contamination=0.02,
    random_state=42,
    n_jobs=-1
)

model.fit(X_scaled)

print("✓ Anomaly detection model trained")


# ------------------------------------------------------------
# 5. GENERATE ANOMALY SCORES
# ------------------------------------------------------------

print("\n[5/6] Detecting abnormal grid behavior...")

predictions = model.predict(X_scaled)

raw_scores = model.decision_function(
    X_scaled
)

# Convert score so higher = more anomalous
anomaly_score = -raw_scores

# Normalize 0–100
score_min = anomaly_score.min()
score_max = anomaly_score.max()

df["Anomaly_Score"] = (
    (anomaly_score - score_min)
    / (score_max - score_min)
) * 100

df["Anomaly_Flag"] = np.where(
    predictions == -1,
    1,
    0
)

# ------------------------------------------------------------
# RISK CLASSIFICATION
# ------------------------------------------------------------

df["Risk_Level"] = np.select(
    [
        df["Anomaly_Score"] >= 80,
        df["Anomaly_Score"] >= 60,
        df["Anomaly_Score"] >= 40
    ],
    [
        "CRITICAL",
        "HIGH",
        "MEDIUM"
    ],
    default="LOW"
)


# ------------------------------------------------------------
# BUSINESS INTERPRETATION
# ------------------------------------------------------------

df["Grid_Status"] = np.where(
    df["Anomaly_Flag"] == 1,
    "ABNORMAL",
    "NORMAL"
)

# Demand deviation from rolling baseline
df["Demand_vs_24H_Baseline_pct"] = np.where(
    df["Demand_Rolling_24H"] != 0,
    (
        (
            df["Demand_MW"]
            - df["Demand_Rolling_24H"]
        )
        / df["Demand_Rolling_24H"]
    ) * 100,
    0
)


# ------------------------------------------------------------
# 6. SAVE OUTPUTS
# ------------------------------------------------------------

print("\n[6/6] Saving anomaly intelligence...")

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "grid_anomaly_results.csv"
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "grid_anomaly_model.joblib"
)

joblib.dump(
    {
        "model": model,
        "scaler": scaler,
        "features": FEATURES
    },
    MODEL_FILE
)


# ============================================================
# SUMMARY
# ============================================================

total_anomalies = int(
    df["Anomaly_Flag"].sum()
)

anomaly_rate = (
    total_anomalies
    / len(df)
) * 100

print("\n" + "=" * 70)
print("ANOMALY DETECTION COMPLETE")
print("=" * 70)

print(f"\nTotal records : {len(df):,}")
print(f"Anomalies     : {total_anomalies:,}")
print(f"Anomaly rate  : {anomaly_rate:.2f}%")

print("\nRisk distribution:")

print(
    df["Risk_Level"]
    .value_counts()
    .to_string()
)

print(f"\nResults:")
print(OUTPUT_FILE)

print(f"\nModel:")
print(MODEL_FILE)

print("\n" + "=" * 70)