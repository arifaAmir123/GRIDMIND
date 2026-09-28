import os
import pandas as pd

from fastapi import APIRouter


router = APIRouter()

BASE_DIR = r"D:\GridMind"

GOLD_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "gold_grid_intelligence.csv"
)


@router.get("/summary")
def dashboard_summary():

    df = pd.read_csv(
        GOLD_FILE,
        usecols=[
            "Timestamp",
            "Region",
            "Demand_MW",
            "Renewable_MW",
            "Renewable_Share_pct",
            "Anomaly_Flag",
            "Risk_Level",
            "Grid_Status",
            "Grid_Risk_Score"
        ]
    )

    return {
        "total_records": int(len(df)),
        "regions": int(df["Region"].nunique()),
        "total_demand_mw": round(
            float(df["Demand_MW"].sum()),
            2
        ),
        "average_demand_mw": round(
            float(df["Demand_MW"].mean()),
            2
        ),
        "average_renewable_share_pct": round(
            float(df["Renewable_Share_pct"].mean()),
            2
        ),
        "anomalies": int(
            df["Anomaly_Flag"].sum()
        ),
        "critical_risk": int(
            (df["Risk_Level"] == "CRITICAL").sum()
        ),
        "abnormal_records": int(
            (df["Grid_Status"] == "ABNORMAL").sum()
        ),
        "average_grid_risk_score": round(
            float(df["Grid_Risk_Score"].mean()),
            2
        )
    }