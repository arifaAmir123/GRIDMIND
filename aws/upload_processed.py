import os
import boto3
from botocore.client import Config

# ============================================================
# GRIDMIND — PROCESSED DATA LAKE SYNC
# Silver + Gold → S3-Compatible Data Lake
# ============================================================

ENDPOINT = "http://localhost:8333"
BUCKET = "gridmind-energy-lake"

ACCESS_KEY = "gridmindadmin"
SECRET_KEY = "GridMind@2026Secure"

BASE_DIR = r"D:\GridMind"

FILES = {
    os.path.join(
        BASE_DIR,
        "data",
        "processed",
        "silver_energy_intelligence.csv"
    ): "silver/energy_intelligence/silver_energy_intelligence.csv",

    os.path.join(
        BASE_DIR,
        "data",
        "processed",
        "gold_grid_intelligence.csv"
    ): "gold/grid_intelligence/gold_grid_intelligence.csv",

    os.path.join(
        BASE_DIR,
        "data",
        "processed",
        "demand_forecast_results.csv"
    ): "gold/forecast/demand_forecast_results.csv",

    os.path.join(
        BASE_DIR,
        "data",
        "processed",
        "grid_anomaly_results.csv"
    ): "gold/anomaly/grid_anomaly_results.csv",

    os.path.join(
        BASE_DIR,
        "data",
        "processed",
        "forecast_feature_importance.csv"
    ): "gold/forecast/forecast_feature_importance.csv",
}


s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)


print("=" * 70)
print("GRIDMIND — PROCESSED DATA LAKE SYNC")
print("=" * 70)


for local_file, s3_key in FILES.items():

    if not os.path.exists(local_file):
        print(f"\n[ERROR] Missing: {local_file}")
        continue

    size_mb = os.path.getsize(local_file) / (
        1024 * 1024
    )

    print(f"\nUploading: {os.path.basename(local_file)}")
    print(f"Size    : {size_mb:.2f} MB")
    print(f"Target  : s3://{BUCKET}/{s3_key}")

    s3.upload_file(
        local_file,
        BUCKET,
        s3_key
    )

    print("✓ Uploaded successfully")


print("\n" + "=" * 70)
print("PROCESSED DATA LAKE SYNC COMPLETE")
print("=" * 70)