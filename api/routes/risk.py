import os
import pandas as pd

from fastapi import APIRouter, Query


router = APIRouter()

BASE_DIR = r"D:\GridMind"

ANOMALY_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "grid_anomaly_results.csv"
)


@router.get("/summary")
def risk_summary():

    df = pd.read_csv(
        ANOMALY_FILE
    )

    risk_counts = (
        df["Risk_Level"]
        .value_counts()
        .to_dict()
    )

    return {
        "total_records": int(len(df)),
        "anomalies": int(
            df["Anomaly_Flag"].sum()
        ),
        "anomaly_rate_pct": round(
            float(
                df["Anomaly_Flag"].mean()
                * 100
            ),
            2
        ),
        "risk_distribution": {
            key: int(value)
            for key, value
            in risk_counts.items()
        }
    }


@router.get("/anomalies")
def get_anomalies(
    limit: int = Query(
        50,
        ge=1,
        le=500
    )
):

    df = pd.read_csv(
        ANOMALY_FILE,
        parse_dates=["Timestamp"]
    )

    anomalies = df[
        df["Anomaly_Flag"] == 1
    ].sort_values(
        "Anomaly_Score",
        ascending=False
    ).head(limit)

    records = []

    for _, row in anomalies.iterrows():

        records.append({
            "timestamp": str(
                row["Timestamp"]
            ),
            "region": row["Region"],
            "demand_mw": round(
                float(row["Demand_MW"]),
                2
            ),
            "anomaly_score": round(
                float(row["Anomaly_Score"]),
                2
            ),
            "risk_level": row["Risk_Level"],
            "grid_status": row["Grid_Status"],
            "demand_deviation_pct": round(
                float(
                    row[
                        "Demand_vs_24H_Baseline_pct"
                    ]
                ),
                2
            )
        })

    return {
        "count": len(records),
        "anomalies": records
    }