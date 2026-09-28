import os
import boto3
from botocore.client import Config

ENDPOINT = "http://localhost:8333"
BUCKET = "gridmind-energy-lake"

ACCESS_KEY = "gridmindadmin"
SECRET_KEY = "GridMind@2026Secure"

RAW_DIR = r"D:\GridMind\data\raw"

DATASETS = {
    "smart_meter.csv": "bronze/smart_meter/smart_meter.csv",
    "weather.csv": "bronze/weather/weather.csv",
    "generation.csv": "bronze/generation/generation.csv",
    "grid_events.csv": "bronze/grid_events/grid_events.csv",
    "grid_assets.csv": "bronze/grid_assets/grid_assets.csv",
}

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)

print("=" * 60)
print("GRIDMIND — BRONZE DATA INGESTION")
print("=" * 60)

for filename, s3_key in DATASETS.items():

    local_file = os.path.join(RAW_DIR, filename)

    if not os.path.exists(local_file):
        print(f"[ERROR] Missing: {filename}")
        continue

    size_mb = os.path.getsize(local_file) / (1024 * 1024)

    print(f"\nUploading: {filename}")
    print(f"Size: {size_mb:.2f} MB")
    print(f"Target: s3://{BUCKET}/{s3_key}")

    s3.upload_file(local_file, BUCKET, s3_key)

    print("✓ Uploaded successfully")

print("\n" + "=" * 60)
print("BRONZE INGESTION COMPLETE")
print("=" * 60)