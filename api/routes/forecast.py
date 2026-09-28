import os
import pandas as pd

from fastapi import APIRouter


router = APIRouter()

BASE_DIR = r"D:\GridMind"

FORECAST_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "demand_forecast_results.csv"
)


@router.get("/latest")
def latest_forecast():

    df = pd.read_csv(
        FORECAST_FILE,
        parse_dates=["Timestamp"]
    )

    latest_time = df["Timestamp"].max()

    latest = df[
        df["Timestamp"] == latest_time
    ].copy()

    records = []

    for _, row in latest.iterrows():

        records.append({
            "timestamp": str(row["Timestamp"]),
            "region": row["Region"],
            "current_demand_mw": round(
                float(row["Current_Demand_MW"]),
                2
            ),
            "forecast_demand_mw": round(
                float(row["Forecast_Demand_MW"]),
                2
            ),
            "forecast_error_mw": round(
                float(row["Forecast_Error_MW"]),
                2
            ),
            "forecast_accuracy_pct": round(
                float(row["Forecast_Accuracy_pct"]),
                2
            ),
            "peak_risk": row["Peak_Risk"]
        })

    return {
        "forecast_timestamp": str(latest_time),
        "regions": records
    }