import pandas as pd
import pyarrow

# import raw data
headers = pd.read_csv(
    "00-data/10-raw_txt_only/origination_data_file_header.txt", sep="|", nrows=0
).columns.tolist()
df = pd.read_csv(
    "00-data/10-raw_txt_only/orig_2022Q1.txt", sep="|", header=None, names=headers
)

# subset for relevant columns
orig_cols = [
    "LOAN IDENTIFIER",
    "OCCUPANCY STATUS",
    "ORIGINAL DEBT-TO-INCOME (DTI) RATIO",
    "ORIGINAL LOAN-TO-VALUE (LTV)",
    "ORIGINAL COMBINED LOAN-TO-VALUE (CLTV)",
    "ORIGINAL INTEREST RATE",
    "PROPERTY TYPE",
    "LOAN PURPOSE",
]
subset_df = df[orig_cols]

# export data to .parquet
df.to_parquet(
    "00-data/20-to_parquet/orig_2022Q1.parquet",
    engine="pyarrow",
)

subset_df.to_parquet(
    "00-data/20-to_parquet/subset_orig_2022Q1.parquet",
    engine="pyarrow",
)
