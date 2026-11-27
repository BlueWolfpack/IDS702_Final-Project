import pandas as pd
import pyarrow
from pathlib import Path

# define directory paths
raw_dir = Path("00-data/10-raw_txt_only")
out_dir = Path("00-data/20-to_parquet")
out_dir.mkdir(parents=True, exist_ok=True)
subset_dir = Path("00-data/30-subsetted")
subset_dir.mkdir(parents=True, exist_ok=True)

# raw data headers
orig_headers = pd.read_csv(
    raw_dir / "origination_data_file_header.txt", sep="|", nrows=0
).columns.tolist()

perf_headers = pd.read_csv(
    raw_dir / "performance_data_file_header.txt", sep="|", nrows=0
).columns.tolist()

# define relevant columns
orig_cols = [
    "LOAN IDENTIFIER",  # can get origination_year from this (first 4 characters)
    "CLASSIC FICO",  # credit_score
    "OCCUPANCY STATUS",  # occupancy_status
    "ORIGINAL DEBT-TO-INCOME (DTI) RATIO",  # dti
    "ORIGINAL LOAN-TO-VALUE (LTV)",  # ltv
    "ORIGINAL INTEREST RATE",  # interest_rate
    "ORIGINAL UPB",  # original_loan_amount
    "PROPERTY TYPE",  # property_type
    "LOAN PURPOSE",  # loan_purpose
]

perf_cols = [
    "LOAN IDENTIFIER",
    "CURRENT LOAN DELINQUENCY STATUS",  # early_delinquency (work will need to be done on this. If this is positive for any of the performance files then it should be marked as true)
]

mixed_cols = [
    "CURRENT LOAN DELINQUENCY STATUS",
    "MODIFICATION FLAG",
    "INTEREST RATE STEP INDICATOR",
    "PAYMENT DEFERRAL FLAG",
    "DELINQUENCY DUE TO DISASTER",
]

for path in sorted(raw_dir.glob("orig_*.txt")):
    stem = path.stem
    print(f"Processing {path.name}...")

    df = pd.read_csv(path, sep="|", header=None, names=orig_headers)
    subset_df = df[orig_cols]

    df.to_parquet(out_dir / f"{stem}.parquet", engine="pyarrow")
    subset_df.to_parquet(out_dir / f"subset_{stem}.parquet", engine="pyarrow")

print("Completed origination files.")

for path in sorted(raw_dir.glob("perf_*.txt")):
    stem = path.stem
    print(f"Processing {path.name}...")

    df = pd.read_csv(
        path,
        sep="|",
        header=None,
        names=perf_headers,
        dtype={col: str for col in mixed_cols},
    )
    subset_df = df[perf_cols]

    df.to_parquet(out_dir / f"{stem}.parquet", engine="pyarrow")
    subset_df.to_parquet(subset_dir / f"subset_{stem}.parquet", engine="pyarrow")

print("Completed performance files.")
