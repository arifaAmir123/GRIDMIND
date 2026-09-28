import os
import pandas as pd
import numpy as np

# ============================================================
# GRIDMIND — SILVER DATA PROCESSING
# Bronze → Clean → Validate → Analytics-Ready Silver
# ============================================================

BASE_DIR = r"D:\GridMind"
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)

print("=" * 70)
print("GRIDMIND — SILVER DATA PROCESSING")
print("=" * 70)

# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

print("\n[1/7] Loading source datasets...")

smart = pd.read_csv(os.path.join(RAW_DIR, "smart_meter.csv"))
weather = pd.read_csv(os.path.join(RAW_DIR, "weather.csv"))
generation = pd.read_csv(os.path.join(RAW_DIR, "generation.csv"))

print(f"Smart Meter : {len(smart):,} rows")
print(f"Weather     : {len(weather):,} rows")
print(f"Generation  : {len(generation):,} rows")

# ------------------------------------------------------------
# 2. STANDARDIZE TIMESTAMPS
# ------------------------------------------------------------

print("\n[2/7] Standardizing timestamps...")

smart["Timestamp"] = pd.to_datetime(smart["Timestamp"], errors="coerce")
weather["Timestamp"] = pd.to_datetime(weather["Timestamp"], errors="coerce")
generation["Timestamp"] = pd.to_datetime(generation["Timestamp"], errors="coerce")

# Remove invalid timestamps
smart = smart.dropna(subset=["Timestamp"])
weather = weather.dropna(subset=["Timestamp"])
generation = generation.dropna(subset=["Timestamp"])

# ------------------------------------------------------------
# 3. CLEAN NUMERIC DATA
# ------------------------------------------------------------

print("\n[3/7] Cleaning numeric fields...")

smart_numeric = [
    "Consumption_kWh",
    "Temperature_C",
    "Voltage_V",
    "Current_A",
    "Power_Factor"
]

weather_numeric = [
    "Temperature_C",
    "Humidity_%",
    "Wind_Speed_kmh",
    "Solar_Irradiance",
    "Rainfall_mm",
    "Cloud_Cover_%"
]

generation_numeric = [
    "Solar_MW",
    "Wind_MW",
    "Hydro_MW",
    "Thermal_MW",
    "Total_Generation_MW"
]

for col in smart_numeric:
    smart[col] = pd.to_numeric(smart[col], errors="coerce")

for col in weather_numeric:
    weather[col] = pd.to_numeric(weather[col], errors="coerce")

for col in generation_numeric:
    generation[col] = pd.to_numeric(generation[col], errors="coerce")

# ------------------------------------------------------------
# 4. AGGREGATE SMART METER DATA
# ------------------------------------------------------------

print("\n[4/7] Building regional demand intelligence...")

demand = (
    smart
    .groupby(["Timestamp", "Region"], as_index=False)
    .agg(
        Demand_kWh=("Consumption_kWh", "sum"),
        Avg_Temperature_C=("Temperature_C", "mean"),
        Avg_Voltage_V=("Voltage_V", "mean"),
        Avg_Current_A=("Current_A", "mean"),
        Avg_Power_Factor=("Power_Factor", "mean")
    )
)

# Convert hourly kWh to approximate MW
demand["Demand_MW"] = demand["Demand_kWh"] / 1000

# ------------------------------------------------------------
# 5. PREPARE WEATHER
# ------------------------------------------------------------

print("\n[5/7] Preparing weather intelligence...")

weather_clean = (
    weather
    .groupby(["Timestamp", "Region"], as_index=False)
    .agg(
        Temperature_C=("Temperature_C", "mean"),
        Humidity_pct=("Humidity_%", "mean"),
        Wind_Speed_kmh=("Wind_Speed_kmh", "mean"),
        Solar_Irradiance=("Solar_Irradiance", "mean"),
        Rainfall_mm=("Rainfall_mm", "sum"),
        Cloud_Cover_pct=("Cloud_Cover_%", "mean")
    )
)

# ------------------------------------------------------------
# 6. PREPARE GENERATION
# ------------------------------------------------------------

print("\n[6/7] Preparing generation intelligence...")

generation_clean = (
    generation
    .groupby("Timestamp", as_index=False)
    .agg(
        Solar_MW=("Solar_MW", "sum"),
        Wind_MW=("Wind_MW", "sum"),
        Hydro_MW=("Hydro_MW", "sum"),
        Thermal_MW=("Thermal_MW", "sum"),
        Total_Generation_MW=("Total_Generation_MW", "sum")
    )
)

# ------------------------------------------------------------
# 7. MERGE + FEATURE ENGINEERING
# ------------------------------------------------------------

print("\n[7/7] Creating Silver analytics layer...")

silver = demand.merge(
    weather_clean,
    on=["Timestamp", "Region"],
    how="left"
)

silver = silver.merge(
    generation_clean,
    on="Timestamp",
    how="left"
)

# ------------------------------------------------------------
# TIME FEATURES
# ------------------------------------------------------------

silver["Year"] = silver["Timestamp"].dt.year
silver["Month"] = silver["Timestamp"].dt.month
silver["Day"] = silver["Timestamp"].dt.day
silver["Hour"] = silver["Timestamp"].dt.hour
silver["DayOfWeek"] = silver["Timestamp"].dt.dayofweek
silver["DayName"] = silver["Timestamp"].dt.day_name()
silver["IsWeekend"] = silver["DayOfWeek"].isin([5, 6]).astype(int)
silver["Quarter"] = silver["Timestamp"].dt.quarter

# Peak hour flag
silver["Is_Peak_Hour"] = silver["Hour"].isin(
    [17, 18, 19, 20, 21]
).astype(int)

# ------------------------------------------------------------
# RENEWABLE ENERGY METRICS
# ------------------------------------------------------------

silver["Renewable_MW"] = (
    silver["Solar_MW"]
    + silver["Wind_MW"]
    + silver["Hydro_MW"]
)

silver["Renewable_Share_pct"] = np.where(
    silver["Total_Generation_MW"] > 0,
    (silver["Renewable_MW"] /
     silver["Total_Generation_MW"]) * 100,
    0
)

silver["Generation_Demand_Ratio"] = np.where(
    silver["Demand_MW"] > 0,
    silver["Total_Generation_MW"] /
    silver["Demand_MW"],
    0
)

# ------------------------------------------------------------
# DEMAND LAG FEATURES
# ------------------------------------------------------------

silver = silver.sort_values(
    ["Region", "Timestamp"]
).reset_index(drop=True)

silver["Demand_Lag_1H"] = (
    silver.groupby("Region")["Demand_MW"].shift(1)
)

silver["Demand_Lag_24H"] = (
    silver.groupby("Region")["Demand_MW"].shift(24)
)

silver["Demand_Lag_168H"] = (
    silver.groupby("Region")["Demand_MW"].shift(168)
)

# ------------------------------------------------------------
# ROLLING DEMAND
# ------------------------------------------------------------

silver["Demand_Rolling_24H"] = (
    silver.groupby("Region")["Demand_MW"]
    .transform(lambda x: x.rolling(24, min_periods=1).mean())
)

silver["Demand_Rolling_168H"] = (
    silver.groupby("Region")["Demand_MW"]
    .transform(lambda x: x.rolling(168, min_periods=1).mean())
)

# ------------------------------------------------------------
# DEMAND CHANGE
# ------------------------------------------------------------

silver["Demand_Change_pct"] = (
    silver.groupby("Region")["Demand_MW"]
    .pct_change()
    .replace([np.inf, -np.inf], np.nan)
    * 100
)

# ------------------------------------------------------------
# CLEAN FINAL DATA
# ------------------------------------------------------------

silver = silver.replace(
    [np.inf, -np.inf],
    np.nan
)

# Keep numeric missing values manageable
numeric_columns = silver.select_dtypes(
    include=[np.number]
).columns

silver[numeric_columns] = silver[numeric_columns].fillna(0)

# Remove duplicate records
silver = silver.drop_duplicates(
    subset=["Timestamp", "Region"]
)

# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

output_file = os.path.join(
    PROCESSED_DIR,
    "silver_energy_intelligence.csv"
)

silver.to_csv(
    output_file,
    index=False
)

# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("SILVER PROCESSING COMPLETE")
print("=" * 70)

print(f"\nOutput file:")
print(output_file)

print(f"\nRows       : {len(silver):,}")
print(f"Columns    : {len(silver.columns)}")
print(f"Regions    : {silver['Region'].nunique()}")
print(
    f"Date range : "
    f"{silver['Timestamp'].min()} → "
    f"{silver['Timestamp'].max()}"
)

print(
    f"\nMissing values: "
    f"{silver.isna().sum().sum():,}"
)

print(
    f"Duplicate records: "
    f"{silver.duplicated(subset=['Timestamp', 'Region']).sum():,}"
)

print("\nSilver columns:")
print(list(silver.columns))

print("\n" + "=" * 70)