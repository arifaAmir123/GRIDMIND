import os
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# GRIDMIND — DEMAND FORECASTING ENGINE
# Time-Aware ML Forecasting
# ============================================================

BASE_DIR = r"D:\GridMind"

INPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "silver_energy_intelligence.csv"
)

MODEL_DIR = os.path.join(BASE_DIR, "models", "artifacts")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("GRIDMIND — DEMAND FORECASTING ENGINE")
print("=" * 70)


# ------------------------------------------------------------
# 1. LOAD SILVER DATA
# ------------------------------------------------------------

print("\n[1/7] Loading Silver intelligence data...")

df = pd.read_csv(INPUT_FILE)

df["Timestamp"] = pd.to_datetime(df["Timestamp"])

df = df.sort_values(
    ["Timestamp", "Region"]
).reset_index(drop=True)

print(f"Rows loaded: {len(df):,}")


# ------------------------------------------------------------
# 2. CREATE FORECAST TARGET
# ------------------------------------------------------------

print("\n[2/7] Creating forecasting target...")

# Predict demand one hour into the future
df["Target_Demand_MW"] = (
    df.groupby("Region")["Demand_MW"].shift(-1)
)

# Remove final unavailable target rows
df = df.dropna(
    subset=["Target_Demand_MW"]
).reset_index(drop=True)

print("Forecast horizon: 1 hour")


# ------------------------------------------------------------
# 3. FEATURE SELECTION
# ------------------------------------------------------------

print("\n[3/7] Preparing ML features...")

FEATURES = [
    "Hour",
    "DayOfWeek",
    "IsWeekend",
    "Month",
    "Quarter",
    "Is_Peak_Hour",

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
    "Rainfall_mm",
    "Cloud_Cover_pct",

    "Renewable_MW",
    "Renewable_Share_pct",
    "Generation_Demand_Ratio",

    "Avg_Voltage_V",
    "Avg_Current_A",
    "Avg_Power_Factor"
]

# Keep only existing features
FEATURES = [
    col for col in FEATURES
    if col in df.columns
]

X = df[FEATURES].copy()
y = df["Target_Demand_MW"].copy()


# ------------------------------------------------------------
# 4. TIME-BASED TRAIN / TEST SPLIT
# ------------------------------------------------------------

print("\n[4/7] Creating time-based train/test split...")

split_time = df["Timestamp"].quantile(0.80)

train_mask = df["Timestamp"] <= split_time
test_mask = df["Timestamp"] > split_time

X_train = X.loc[train_mask]
X_test = X.loc[test_mask]

y_train = y.loc[train_mask]
y_test = y.loc[test_mask]

print(f"Training rows: {len(X_train):,}")
print(f"Testing rows : {len(X_test):,}")
print(f"Split time   : {split_time}")


# ------------------------------------------------------------
# 5. TRAIN MODEL
# ------------------------------------------------------------

print("\n[5/7] Training demand forecasting model...")

model = RandomForestRegressor(
    n_estimators=150,
    max_depth=18,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

model.fit(
    X_train,
    y_train
)

print("✓ Model training complete")


# ------------------------------------------------------------
# 6. EVALUATE
# ------------------------------------------------------------

print("\n[6/7] Evaluating forecasting performance...")

predictions = model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

r2 = r2_score(
    y_test,
    predictions
)

print("\nMODEL PERFORMANCE")
print("-" * 40)
print(f"MAE  : {mae:.4f} MW")
print(f"RMSE : {rmse:.4f} MW")
print(f"R²   : {r2:.4f}")


# ------------------------------------------------------------
# 7. CREATE FORECAST OUTPUT
# ------------------------------------------------------------

print("\n[7/7] Creating forecast intelligence output...")

forecast = df.loc[
    test_mask,
    [
        "Timestamp",
        "Region",
        "Demand_MW",
        "Target_Demand_MW"
    ]
].copy()

forecast["Forecast_Demand_MW"] = predictions

forecast.rename(
    columns={
        "Demand_MW": "Current_Demand_MW",
        "Target_Demand_MW": "Actual_Demand_MW"
    },
    inplace=True
)

forecast["Forecast_Error_MW"] = (
    forecast["Actual_Demand_MW"]
    - forecast["Forecast_Demand_MW"]
)

forecast["Absolute_Error_MW"] = (
    forecast["Forecast_Error_MW"]
    .abs()
)

forecast["Forecast_Error_pct"] = np.where(
    forecast["Actual_Demand_MW"] != 0,
    (
        forecast["Forecast_Error_MW"]
        / forecast["Actual_Demand_MW"]
    ) * 100,
    0
)

forecast["Forecast_Accuracy_pct"] = (
    100
    - forecast["Forecast_Error_pct"].abs()
)

forecast["Forecast_Accuracy_pct"] = (
    forecast["Forecast_Accuracy_pct"]
    .clip(lower=0, upper=100)
)

# Peak classification
forecast["Peak_Risk"] = np.select(
    [
        forecast["Forecast_Demand_MW"]
        >= forecast["Forecast_Demand_MW"].quantile(0.90),

        forecast["Forecast_Demand_MW"]
        >= forecast["Forecast_Demand_MW"].quantile(0.75)
    ],
    [
        "HIGH",
        "MEDIUM"
    ],
    default="LOW"
)

# ------------------------------------------------------------
# SAVE FORECAST DATA
# ------------------------------------------------------------

forecast_file = os.path.join(
    OUTPUT_DIR,
    "demand_forecast_results.csv"
)

forecast.to_csv(
    forecast_file,
    index=False
)

# ------------------------------------------------------------
# SAVE MODEL
# ------------------------------------------------------------

model_file = os.path.join(
    MODEL_DIR,
    "demand_forecasting_model.joblib"
)

joblib.dump(
    {
        "model": model,
        "features": FEATURES,
        "mae": mae,
        "rmse": rmse,
        "r2": r2
    },
    model_file
)

# ------------------------------------------------------------
# FEATURE IMPORTANCE
# ------------------------------------------------------------

importance = pd.DataFrame({
    "Feature": FEATURES,
    "Importance": model.feature_importances_
}).sort_values(
    "Importance",
    ascending=False
)

importance_file = os.path.join(
    OUTPUT_DIR,
    "forecast_feature_importance.csv"
)

importance.to_csv(
    importance_file,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("DEMAND FORECASTING COMPLETE")
print("=" * 70)

print(f"\nForecast results:")
print(forecast_file)

print(f"\nModel artifact:")
print(model_file)

print(f"\nFeature importance:")
print(importance_file)

print("\nTop predictive features:")

for _, row in importance.head(10).iterrows():
    print(
        f"  {row['Feature']:<30}"
        f"{row['Importance']:.4f}"
    )

print("\n" + "=" * 70)