import os
import pandas as pd
import numpy as np

RAW = "data/raw"
PROCESSED = "data/processed"

os.makedirs(PROCESSED, exist_ok=True)

print("Loading datasets...")

meter = pd.read_csv(
    f"{RAW}/smart_meter.csv",
    parse_dates=["Timestamp"]
)

weather = pd.read_csv(
    f"{RAW}/weather.csv",
    parse_dates=["Timestamp"]
)

generation = pd.read_csv(
    f"{RAW}/generation.csv",
    parse_dates=["Timestamp"]
)

# =========================================================
# AGGREGATE SMART METER DATA
# =========================================================

print("Aggregating smart meter consumption...")

meter_hourly = (
    meter
    .groupby(["Timestamp", "Region"], as_index=False)
    .agg(
        Total_Consumption_kWh=(
            "Consumption_kWh",
            "sum"
        ),
        Avg_Voltage_V=(
            "Voltage_V",
            "mean"
        ),
        Avg_Current_A=(
            "Current_A",
            "mean"
        ),
        Avg_Power_Factor=(
            "Power_Factor",
            "mean"
        ),
        Customer_Count=(
            "Customer_Type",
            "count"
        )
    )
)

# =========================================================
# PREPARE WEATHER
# =========================================================

print("Preparing weather data...")

weather_hourly = (
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

# =========================================================
# GENERATION
# =========================================================

print("Preparing generation data...")

generation["Region"] = "Central"

generation_hourly = (
    generation
    .groupby(["Timestamp", "Region"], as_index=False)
    .agg(
        Solar_MW=("Solar_MW", "mean"),
        Wind_MW=("Wind_MW", "mean"),
        Hydro_MW=("Hydro_MW", "mean"),
        Thermal_MW=("Thermal_MW", "mean"),
        Total_Generation_MW=(
            "Total_Generation_MW",
            "mean"
        )
    )
)

# =========================================================
# MERGE
# =========================================================

print("Building integrated energy dataset...")

energy = meter_hourly.merge(
    weather_hourly,
    on=["Timestamp", "Region"],
    how="left"
)

energy = energy.merge(
    generation_hourly,
    on=["Timestamp", "Region"],
    how="left"
)

# =========================================================
# TIME FEATURES
# =========================================================

energy["Hour"] = energy["Timestamp"].dt.hour

energy["Day"] = (
    energy["Timestamp"].dt.day
)

energy["Month"] = (
    energy["Timestamp"].dt.month
)

energy["Day_of_Week"] = (
    energy["Timestamp"].dt.dayofweek
)

energy["Is_Weekend"] = (
    energy["Day_of_Week"] >= 5
).astype(int)

energy["Season"] = np.select(
    [
        energy["Month"].isin([12, 1, 2]),
        energy["Month"].isin([3, 4, 5]),
        energy["Month"].isin([6, 7, 8])
    ],
    [
        "Winter",
        "Spring",
        "Summer"
    ],
    default="Autumn"
)

# =========================================================
# DEMAND FEATURES
# =========================================================

energy["Demand_MW"] = (
    energy["Total_Consumption_kWh"] / 1000
)

energy["Renewable_MW"] = (
    energy["Solar_MW"]
    + energy["Wind_MW"]
    + energy["Hydro_MW"]
)

energy["Renewable_Share_pct"] = (
    energy["Renewable_MW"]
    / energy["Total_Generation_MW"]
    * 100
)

energy["Generation_Demand_Ratio"] = (
    energy["Total_Generation_MW"]
    / energy["Demand_MW"].replace(0, np.nan)
)

# =========================================================
# LAG FEATURES
# =========================================================

energy = energy.sort_values(
    ["Region", "Timestamp"]
)

energy["Demand_Lag_1H"] = (
    energy.groupby("Region")["Demand_MW"]
    .shift(1)
)

energy["Demand_Lag_24H"] = (
    energy.groupby("Region")["Demand_MW"]
    .shift(24)
)

energy["Demand_Rolling_24H"] = (
    energy.groupby("Region")["Demand_MW"]
    .transform(
        lambda x: x.rolling(24, min_periods=1).mean()
    )
)

# =========================================================
# SAVE
# =========================================================

output = (
    f"{PROCESSED}/energy_features.csv"
)

energy.to_csv(
    output,
    index=False
)

print("\n" + "=" * 65)
print("FEATURE ENGINEERING COMPLETE")
print("=" * 65)

print(f"Rows       : {len(energy):,}")
print(f"Columns    : {len(energy.columns)}")
print(f"Missing    : {energy.isna().sum().sum():,}")

print("\nSaved:")
print(os.path.abspath(output))