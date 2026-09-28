import os
import numpy as np
import pandas as pd

np.random.seed(42)

BASE = "data"
RAW = os.path.join(BASE, "raw")

os.makedirs(RAW, exist_ok=True)

# =========================================================
# CONFIGURATION
# =========================================================

START = "2024-01-01"
END = "2025-12-31 23:00"

timestamps = pd.date_range(
    start=START,
    end=END,
    freq="h"
)

regions = [
    "North",
    "Central",
    "South",
    "East",
    "West"
]

substations = [
    "SS-001",
    "SS-002",
    "SS-003",
    "SS-004",
    "SS-005",
    "SS-006",
    "SS-007",
    "SS-008",
    "SS-009",
    "SS-010"
]

customer_types = [
    "Residential",
    "Commercial",
    "Industrial"
]

# =========================================================
# 1. SMART METER DATA
# =========================================================

print("Generating smart meter data...")

meter_count = 500_000

meter_time = np.random.choice(timestamps, meter_count)
meter_region = np.random.choice(regions, meter_count)
meter_substation = np.random.choice(substations, meter_count)
meter_customer = np.random.choice(
    customer_types,
    meter_count,
    p=[0.65, 0.25, 0.10]
)

hour = pd.Series(meter_time).dt.hour.values
month = pd.Series(meter_time).dt.month.values

base_consumption = np.where(
    meter_customer == "Residential",
    np.random.normal(2.5, 0.8, meter_count),
    np.where(
        meter_customer == "Commercial",
        np.random.normal(7.0, 2.0, meter_count),
        np.random.normal(18.0, 5.0, meter_count)
    )
)

hour_factor = (
    1
    + 0.35 * np.sin((hour - 8) / 24 * 2 * np.pi)
    + 0.20 * np.sin((hour - 18) / 24 * 2 * np.pi)
)

season_factor = 1 + 0.15 * np.sin((month - 1) / 12 * 2 * np.pi)

consumption = (
    base_consumption
    * hour_factor
    * season_factor
    + np.random.normal(0, 0.4, meter_count)
)

consumption = np.maximum(consumption, 0.1)

temperature = (
    25
    + 10 * np.sin((month - 3) / 12 * 2 * np.pi)
    + np.random.normal(0, 4, meter_count)
)

voltage = np.random.normal(230, 5, meter_count)

current = consumption * 4.35 + np.random.normal(0, 1, meter_count)

power_factor = np.clip(
    np.random.normal(0.92, 0.04, meter_count),
    0.70,
    1.00
)

smart_meter = pd.DataFrame({
    "Timestamp": meter_time,
    "Region": meter_region,
    "Substation_ID": meter_substation,
    "Customer_Type": meter_customer,
    "Consumption_kWh": np.round(consumption, 3),
    "Temperature_C": np.round(temperature, 2),
    "Voltage_V": np.round(voltage, 2),
    "Current_A": np.round(current, 2),
    "Power_Factor": np.round(power_factor, 3)
})

smart_meter.sort_values("Timestamp", inplace=True)

smart_meter.to_csv(
    f"{RAW}/smart_meter.csv",
    index=False
)

print(f"Smart meters: {len(smart_meter):,}")

# =========================================================
# 2. WEATHER DATA
# =========================================================

print("Generating weather data...")

weather = pd.DataFrame({
    "Timestamp": timestamps,
    "Region": np.random.choice(regions, len(timestamps))
})

weather_month = weather["Timestamp"].dt.month
weather_hour = weather["Timestamp"].dt.hour

weather["Temperature_C"] = (
    25
    + 10 * np.sin((weather_month - 3) / 12 * 2 * np.pi)
    + 3 * np.sin((weather_hour - 12) / 24 * 2 * np.pi)
    + np.random.normal(0, 2, len(weather))
)

weather["Humidity_%"] = np.clip(
    65 - weather["Temperature_C"] * 0.3
    + np.random.normal(0, 8, len(weather)),
    20,
    100
)

weather["Wind_Speed_kmh"] = np.maximum(
    np.random.normal(18, 7, len(weather)),
    0
)

daylight = np.maximum(
    np.sin((weather_hour - 6) / 12 * np.pi),
    0
)

weather["Solar_Irradiance"] = np.maximum(
    daylight * np.random.normal(750, 150, len(weather)),
    0
)

weather["Rainfall_mm"] = np.maximum(
    np.random.exponential(0.5, len(weather)) - 0.3,
    0
)

weather["Cloud_Cover_%"] = np.clip(
    np.random.normal(45, 25, len(weather)),
    0,
    100
)

weather = weather.round(2)

weather.to_csv(
    f"{RAW}/weather.csv",
    index=False
)

print(f"Weather records: {len(weather):,}")

# =========================================================
# 3. GENERATION DATA
# =========================================================

print("Generating generation data...")

generation = pd.DataFrame({
    "Timestamp": timestamps
})

generation_hour = generation["Timestamp"].dt.hour
generation_month = generation["Timestamp"].dt.month

solar_factor = np.maximum(
    np.sin((generation_hour - 6) / 12 * np.pi),
    0
)

generation["Solar_MW"] = np.maximum(
    solar_factor * np.random.normal(
        850,
        120,
        len(generation)
    ),
    0
)

generation["Wind_MW"] = np.maximum(
    np.random.normal(500, 120, len(generation)),
    50
)

generation["Hydro_MW"] = np.maximum(
    700
    + 100 * np.sin(
        generation_month / 12 * 2 * np.pi
    )
    + np.random.normal(0, 60, len(generation)),
    300
)

generation["Thermal_MW"] = np.maximum(
    np.random.normal(1600, 250, len(generation)),
    700
)

generation["Total_Generation_MW"] = (
    generation["Solar_MW"]
    + generation["Wind_MW"]
    + generation["Hydro_MW"]
    + generation["Thermal_MW"]
)

generation = generation.round(2)

generation.to_csv(
    f"{RAW}/generation.csv",
    index=False
)

print(f"Generation records: {len(generation):,}")

# =========================================================
# 4. GRID EVENTS
# =========================================================

print("Generating grid events...")

event_count = 5_000

event_types = [
    "Normal",
    "Overload",
    "Voltage Anomaly",
    "Equipment Fault",
    "Outage",
    "Maintenance"
]

severity = [
    "Low",
    "Medium",
    "High",
    "Critical"
]

events = pd.DataFrame({
    "Event_ID": [
        f"EVT-{i:05d}"
        for i in range(1, event_count + 1)
    ],
    "Timestamp": np.random.choice(
        timestamps,
        event_count
    ),
    "Region": np.random.choice(
        regions,
        event_count
    ),
    "Substation_ID": np.random.choice(
        substations,
        event_count
    ),
    "Event_Type": np.random.choice(
        event_types,
        event_count,
        p=[0.45, 0.15, 0.12, 0.10, 0.10, 0.08]
    ),
    "Severity": np.random.choice(
        severity,
        event_count,
        p=[0.35, 0.35, 0.22, 0.08]
    ),
    "Duration_Minutes": np.random.randint(
        5,
        480,
        event_count
    )
})

events.sort_values(
    "Timestamp",
    inplace=True
)

events.to_csv(
    f"{RAW}/grid_events.csv",
    index=False
)

print(f"Grid events: {len(events):,}")

# =========================================================
# 5. GRID INFRASTRUCTURE
# =========================================================

print("Generating infrastructure data...")

asset_count = 1_000

assets = pd.DataFrame({
    "Asset_ID": [
        f"AST-{i:04d}"
        for i in range(1, asset_count + 1)
    ],
    "Region": np.random.choice(
        regions,
        asset_count
    ),
    "Substation_ID": np.random.choice(
        substations,
        asset_count
    ),
    "Asset_Type": np.random.choice(
        [
            "Transformer",
            "Circuit Breaker",
            "Transmission Line",
            "Distribution Line"
        ],
        asset_count
    ),
    "Capacity_MW": np.random.choice(
        [10, 25, 50, 100, 250, 500],
        asset_count
    ),
    "Installation_Year": np.random.randint(
        1995,
        2025,
        asset_count
    ),
    "Asset_Status": np.random.choice(
        [
            "Operational",
            "Maintenance",
            "Degraded"
        ],
        asset_count,
        p=[0.85, 0.10, 0.05]
    )
})

assets.to_csv(
    f"{RAW}/grid_assets.csv",
    index=False
)

print(f"Grid assets: {len(assets):,}")

# =========================================================
# SUMMARY
# =========================================================

print("\n" + "=" * 55)
print("GRIDMIND DATA GENERATION COMPLETE")
print("=" * 55)

print(f"Smart Meter : {len(smart_meter):,}")
print(f"Weather     : {len(weather):,}")
print(f"Generation  : {len(generation):,}")
print(f"Grid Events : {len(events):,}")
print(f"Grid Assets : {len(assets):,}")

print("\nFiles created in:")
print(os.path.abspath(RAW))