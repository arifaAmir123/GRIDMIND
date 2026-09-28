import os
import pandas as pd


# ============================================================
# GRIDMIND — AI ENERGY ANALYST
# Data-Grounded Decision Intelligence
# ============================================================

BASE_DIR = r"D:\GridMind"

GOLD_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "gold_grid_intelligence.csv"
)


def load_data():

    return pd.read_csv(
        GOLD_FILE,
        parse_dates=["Timestamp"]
    )


def analyze_question(question: str):

    df = load_data()

    q = question.lower().strip()

    # --------------------------------------------------------
    # ANOMALIES
    # --------------------------------------------------------

    if "anomal" in q:

        region_anomalies = (
            df.groupby("Region")["Anomaly_Flag"]
            .sum()
            .sort_values(ascending=False)
        )

        top_region = region_anomalies.index[0]
        top_count = int(region_anomalies.iloc[0])

        total = int(
            df["Anomaly_Flag"].sum()
        )

        return {
            "question": question,
            "answer": (
                f"{top_region} has the highest number of "
                f"detected anomalies with {top_count:,} "
                f"records. Across the dataset, "
                f"{total:,} anomalous records were detected."
            ),
            "type": "anomaly_analysis"
        }

    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    if "risk" in q:

        risk_counts = (
            df["Risk_Level"]
            .value_counts()
            .to_dict()
        )

        critical = int(
            risk_counts.get("CRITICAL", 0)
        )

        high = int(
            risk_counts.get("HIGH", 0)
        )

        return {
            "question": question,
            "answer": (
                f"Grid risk analysis identifies "
                f"{critical:,} critical-risk records and "
                f"{high:,} high-risk records. "
                f"These records should receive priority "
                f"for operational investigation."
            ),
            "type": "risk_analysis"
        }

    # --------------------------------------------------------
    # DEMAND
    # --------------------------------------------------------

    if (
        "demand" in q
        or "consumption" in q
    ):

        regional_demand = (
            df.groupby("Region")["Demand_MW"]
            .mean()
            .sort_values(ascending=False)
        )

        top_region = regional_demand.index[0]
        top_demand = float(
            regional_demand.iloc[0]
        )

        return {
            "question": question,
            "answer": (
                f"{top_region} has the highest average "
                f"recorded demand at approximately "
                f"{top_demand:.2f} MW."
            ),
            "type": "demand_analysis"
        }

    # --------------------------------------------------------
    # RENEWABLE
    # --------------------------------------------------------

    if "renewable" in q:

        regional_renewable = (
            df.groupby("Region")
            ["Renewable_Share_pct"]
            .mean()
            .sort_values(ascending=False)
        )

        top_region = regional_renewable.index[0]
        top_share = float(
            regional_renewable.iloc[0]
        )

        return {
            "question": question,
            "answer": (
                f"{top_region} has the highest average "
                f"renewable generation share at "
                f"{top_share:.2f}%."
            ),
            "type": "renewable_analysis"
        }

    # --------------------------------------------------------
    # PEAK
    # --------------------------------------------------------

    if "peak" in q:

        peak_records = df[
            df["Is_Peak_Hour"] == 1
        ]

        peak_demand = float(
            peak_records["Demand_MW"].mean()
        )

        return {
            "question": question,
            "answer": (
                f"Average demand during defined peak "
                f"hours is approximately "
                f"{peak_demand:.2f} MW."
            ),
            "type": "peak_analysis"
        }

    # --------------------------------------------------------
    # DEFAULT
    # --------------------------------------------------------

    return {
        "question": question,
        "answer": (
            "GridMind can currently analyze demand, "
            "consumption, anomalies, grid risk, "
            "renewable generation and peak demand."
        ),
        "type": "general"
    }