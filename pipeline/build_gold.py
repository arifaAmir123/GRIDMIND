import os
import pandas as pd
import numpy as np


# ============================================================
# GRIDMIND — GOLD INTELLIGENCE LAYER
# ML + Risk + Renewable + Decision Intelligence
# ============================================================

BASE_DIR = r"D:\GridMind"

SILVER_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "silver_energy_intelligence.csv"
)

FORECAST_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "demand_forecast_results.csv"
)

ANOMALY_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "grid_anomaly_results.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("GRIDMIND — GOLD INTELLIGENCE BUILDER")
print("=" * 70)


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

print("\n[1/6] Loading intelligence layers...")

silver = pd.read_csv(
    SILVER_FILE,
    parse_dates=["Timestamp"]
)

forecast = pd.read_csv(
    FORECAST_FILE,
    parse_dates=["Timestamp"]
)

anomaly = pd.read_csv(
    ANOMALY_FILE,
    parse_dates=["Timestamp"]
)

print(f"Silver records   : {len(silver):,}")
print(f"Forecast records : {len(forecast):,}")
print(f"Anomaly records  : {len(anomaly):,}")


# ------------------------------------------------------------
# 2. PREPARE FORECAST DATA
# ------------------------------------------------------------

print("\n[2/6] Preparing forecast intelligence...")

forecast_cols = [
    "Timestamp",
    "Region",
    "Current_Demand_MW",
    "Actual_Demand_MW",
    "Forecast_Demand_MW",
    "Forecast_Error_MW",
    "Absolute_Error_MW",
    "Forecast_Error_pct",
    "Forecast_Accuracy_pct",
    "Peak_Risk"
]

forecast = forecast[
    [
        col for col in forecast_cols
        if col in forecast.columns
    ]
]


# ------------------------------------------------------------
# 3. PREPARE ANOMALY DATA
# ------------------------------------------------------------

print("\n[3/6] Preparing grid risk intelligence...")

anomaly_cols = [
    "Timestamp",
    "Region",
    "Anomaly_Score",
    "Anomaly_Flag",
    "Risk_Level",
    "Grid_Status",
    "Demand_vs_24H_Baseline_pct"
]

anomaly = anomaly[
    [
        col for col in anomaly_cols
        if col in anomaly.columns
    ]
]


# ------------------------------------------------------------
# 4. BUILD GOLD DATASET
# ------------------------------------------------------------

print("\n[4/6] Merging ML intelligence...")

# Start from Silver
gold = silver.copy()

# Forecast is only available for the test period.
gold = gold.merge(
    forecast,
    on=["Timestamp", "Region"],
    how="left"
)

gold = gold.merge(
    anomaly,
    on=["Timestamp", "Region"],
    how="left"
)


# ------------------------------------------------------------
# 5. DECISION INTELLIGENCE
# ------------------------------------------------------------

print("\n[5/6] Creating decision intelligence metrics...")

# Fill forecast values where unavailable
gold["Forecast_Demand_MW"] = gold[
    "Forecast_Demand_MW"
].fillna(gold["Demand_MW"])

gold["Current_Demand_MW"] = gold[
    "Current_Demand_MW"
].fillna(gold["Demand_MW"])

gold["Actual_Demand_MW"] = gold[
    "Actual_Demand_MW"
].fillna(gold["Demand_MW"])

gold["Forecast_Error_MW"] = gold[
    "Forecast_Error_MW"
].fillna(0)

gold["Forecast_Accuracy_pct"] = gold[
    "Forecast_Accuracy_pct"
].fillna(100)

gold["Peak_Risk"] = gold[
    "Peak_Risk"
].fillna("LOW")

gold["Anomaly_Score"] = gold[
    "Anomaly_Score"
].fillna(0)

gold["Anomaly_Flag"] = gold[
    "Anomaly_Flag"
].fillna(0)

gold["Risk_Level"] = gold[
    "Risk_Level"
].fillna("LOW")

gold["Grid_Status"] = gold[
    "Grid_Status"
].fillna("NORMAL")

gold["Demand_vs_24H_Baseline_pct"] = gold[
    "Demand_vs_24H_Baseline_pct"
].fillna(0)


# ------------------------------------------------------------
# COMPOSITE GRID RISK SCORE
# ------------------------------------------------------------

gold["Peak_Risk_Score"] = gold[
    "Peak_Risk"
].map({
    "LOW": 20,
    "MEDIUM": 50,
    "HIGH": 80
}).fillna(20)

gold["Risk_Level_Score"] = gold[
    "Risk_Level"
].map({
    "LOW": 10,
    "MEDIUM": 40,
    "HIGH": 70,
    "CRITICAL": 100
}).fillna(10)

gold["Demand_Deviation_Score"] = (
    gold["Demand_vs_24H_Baseline_pct"]
    .abs()
    .clip(upper=100)
)

gold["Grid_Risk_Score"] = (
    gold["Anomaly_Score"] * 0.50
    + gold["Peak_Risk_Score"] * 0.25
    + gold["Risk_Level_Score"] * 0.15
    + gold["Demand_Deviation_Score"] * 0.10
)

gold["Grid_Risk_Score"] = (
    gold["Grid_Risk_Score"]
    .clip(0, 100)
    .round(2)
)


# ------------------------------------------------------------
# DECISION PRIORITY
# ------------------------------------------------------------

gold["Decision_Priority"] = np.select(
    [
        gold["Grid_Risk_Score"] >= 80,
        gold["Grid_Risk_Score"] >= 60,
        gold["Grid_Risk_Score"] >= 40
    ],
    [
        "IMMEDIATE ACTION",
        "HIGH PRIORITY",
        "MONITOR"
    ],
    default="NORMAL"
)


# ------------------------------------------------------------
# OPERATIONAL RECOMMENDATION
# ------------------------------------------------------------

gold["Recommended_Action"] = np.select(
    [
        gold["Grid_Risk_Score"] >= 80,

        (
            (gold["Grid_Risk_Score"] >= 60)
            &
            (gold["Forecast_Demand_MW"]
             > gold["Current_Demand_MW"])
        ),

        gold["Anomaly_Flag"] == 1,

        gold["Peak_Risk"] == "HIGH"
    ],
    [
        "Investigate grid condition immediately",

        "Prepare additional capacity",

        "Investigate abnormal consumption",

        "Prepare for peak demand"
    ],
    default="Continue normal monitoring"
)


# ------------------------------------------------------------
# RENEWABLE OPPORTUNITY
# ------------------------------------------------------------

gold["Renewable_Opportunity"] = np.select(
    [
        gold["Renewable_Share_pct"] < 25,
        gold["Renewable_Share_pct"] < 50
    ],
    [
        "HIGH",
        "MEDIUM"
    ],
    default="LOW"
)


# ------------------------------------------------------------
# FINAL CLEANUP
# ------------------------------------------------------------

gold = gold.replace(
    [np.inf, -np.inf],
    np.nan
)

gold = gold.fillna(0)

# Restore categorical fields after blanket fill
if "Risk_Level" in gold.columns:
    gold["Risk_Level"] = gold["Risk_Level"].replace(
        0, "LOW"
    )

if "Peak_Risk" in gold.columns:
    gold["Peak_Risk"] = gold["Peak_Risk"].replace(
        0, "LOW"
    )

if "Grid_Status" in gold.columns:
    gold["Grid_Status"] = gold["Grid_Status"].replace(
        0, "NORMAL"
    )

if "Decision_Priority" in gold.columns:
    gold["Decision_Priority"] = gold[
        "Decision_Priority"
    ].replace(
        0,
        "NORMAL"
    )

if "Recommended_Action" in gold.columns:
    gold["Recommended_Action"] = gold[
        "Recommended_Action"
    ].replace(
        0,
        "Continue normal monitoring"
    )

if "Renewable_Opportunity" in gold.columns:
    gold["Renewable_Opportunity"] = gold[
        "Renewable_Opportunity"
    ].replace(
        0,
        "LOW"
    )


# Remove duplicates
gold = gold.drop_duplicates(
    subset=["Timestamp", "Region"]
)

gold = gold.sort_values(
    ["Timestamp", "Region"]
).reset_index(drop=True)


# ------------------------------------------------------------
# SAVE GOLD DATASET
# ------------------------------------------------------------

print("\n[6/6] Saving Gold intelligence dataset...")

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "gold_grid_intelligence.csv"
)

gold.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("GOLD INTELLIGENCE COMPLETE")
print("=" * 70)

print(f"\nOutput:")
print(OUTPUT_FILE)

print(f"\nRows    : {len(gold):,}")
print(f"Columns : {len(gold.columns)}")

print("\nDecision Priority:")
print(
    gold["Decision_Priority"]
    .value_counts()
    .to_string()
)

print("\nRisk Level:")
print(
    gold["Risk_Level"]
    .value_counts()
    .to_string()
)

print("\nGrid Status:")
print(
    gold["Grid_Status"]
    .value_counts()
    .to_string()
)

print("\n" + "=" * 70)