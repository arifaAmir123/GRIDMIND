import boto3
from botocore.client import Config

ENDPOINT = "http://localhost:8333"
BUCKET = "gridmind-energy-lake"

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id="",
    aws_secret_access_key="",
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)

s3.create_bucket(Bucket=BUCKET)

folders = [
    "bronze/smart_meter/",
    "bronze/weather/",
    "bronze/generation/",
    "bronze/grid_events/",
    "bronze/grid_assets/",
    "silver/",
    "gold/",
    "models/",
    "logs/",
]

for folder in folders:
    s3.put_object(Bucket=BUCKET, Key=folder)

print(f"Created bucket: {BUCKET}")
print("\nData Lake Structure:")

for folder in folders:
    print(f"  {folder}")

print("\nGridMind Energy Data Lake initialized successfully.")