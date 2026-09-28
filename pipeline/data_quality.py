import os
import pandas as pd

RAW = "data/raw"
REPORT = "data/processed"

os.makedirs(REPORT, exist_ok=True)

FILES = {
    "smart_meter": "smart_meter.csv",
    "weather": "weather.csv",
    "generation": "generation.csv",
    "grid_events": "grid_events.csv",
    "grid_assets": "grid_assets.csv"
}


def profile_dataset(name, file_name):
    path = os.path.join(RAW, file_name)

    df = pd.read_csv(path)

    result = {
        "Dataset": name,
        "Rows": len(df),
        "Columns": len(df.columns),
        "Missing_Values": int(df.isna().sum().sum()),
        "Duplicate_Rows": int(df.duplicated().sum()),
        "Memory_MB": round(
            df.memory_usage(deep=True).sum() / 1024**2,
            2
        )
    }

    return result


def main():

    print("\n" + "=" * 65)
    print("GRIDMIND DATA QUALITY ENGINE")
    print("=" * 65)

    results = []

    for name, file_name in FILES.items():

        print(f"\nChecking: {name}")

        result = profile_dataset(
            name,
            file_name
        )

        results.append(result)

        print(f"Rows       : {result['Rows']:,}")
        print(f"Columns    : {result['Columns']}")
        print(f"Missing    : {result['Missing_Values']:,}")
        print(f"Duplicates : {result['Duplicate_Rows']:,}")
        print(f"Memory     : {result['Memory_MB']} MB")

    report = pd.DataFrame(results)

    report.to_csv(
        f"{REPORT}/data_quality_report.csv",
        index=False
    )

    print("\n" + "-" * 65)
    print("QUALITY REPORT")
    print("-" * 65)

    print(report.to_string(index=False))

    print("\nReport saved to:")
    print(
        os.path.abspath(
            f"{REPORT}/data_quality_report.csv"
        )
    )


if __name__ == "__main__":
    main()