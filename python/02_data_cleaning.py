import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# VeyraPay — Data Cleaning
# ---------------------------------------------------------

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "veyrapay_transactions_raw.csv"
CLEANED_FILE = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "veyrapay_transactions_cleaned.csv"
)


# ---------------------------------------------------------
# 1. Load raw dataset
# ---------------------------------------------------------

print("Loading raw dataset...")

df = pd.read_csv(RAW_FILE)

print(f"Raw dataset shape: {df.shape}")
print(f"Raw columns: {df.shape[1]}")
print(f"Raw rows: {df.shape[0]}")


# ---------------------------------------------------------
# 2. Standardize column names
# ---------------------------------------------------------

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

print("\nColumn names standardized.")


# ---------------------------------------------------------
# 3. Convert data types
# ---------------------------------------------------------

df["transaction_datetime"] = pd.to_datetime(
    df["transaction_datetime"],
    errors="coerce"
)

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="coerce"
)

df["refund_amount"] = pd.to_numeric(
    df["refund_amount"],
    errors="coerce"
)

df["refund_datetime"] = pd.to_datetime(
    df["refund_datetime"],
    errors="coerce"
)

df["processing_time_seconds"] = pd.to_numeric(
    df["processing_time_seconds"],
    errors="coerce"
)

print("Data types converted.")


# ---------------------------------------------------------
# 4. Standardize text fields
# ---------------------------------------------------------

text_columns = [
    "transaction_id",
    "customer_id",
    "customer_type",
    "payment_method",
    "transaction_status",
    "failure_reason",
    "merchant_id",
    "merchant_category",
    "state",
    "region",
    "city",
    "platform",
    "device_type",
    "refund_status",
]

for column in text_columns:
    df[column] = df[column].astype("string").str.strip()

print("Text fields standardized.")


# ---------------------------------------------------------
# 6. Cleaning diagnostics
# ---------------------------------------------------------

print("\n--- Cleaning Diagnostics ---")

print(f"Duplicate rows: {df.duplicated().sum()}")
print(f"Duplicate transaction IDs: {df['transaction_id'].duplicated().sum()}")

print("\nMissing values:")
print(df.isna().sum())

print("\nData types:")
print(df.dtypes)

print("\nDate range:")
print(f"Start: {df['transaction_datetime'].min()}")
print(f"End:   {df['transaction_datetime'].max()}")


# ---------------------------------------------------------
# 7. Diagnose missing merchant categories
# ---------------------------------------------------------

print("\n--- Merchant Category Diagnostic ---")

merchant_category_mapping = (
    df.dropna(subset=["merchant_category"])
    .groupby("merchant_id")["merchant_category"]
    .nunique()
)

missing_category_merchants = df.loc[
    df["merchant_category"].isna(),
    "merchant_id"
].unique()

recoverable_merchants = [
    merchant_id
    for merchant_id in missing_category_merchants
    if merchant_category_mapping.get(merchant_id, 0) == 1
]

print(f"Rows with missing merchant_category: {df['merchant_category'].isna().sum()}")
print(f"Unique merchants affected: {len(missing_category_merchants)}")
print(f"Merchants with one consistent known category: {len(recoverable_merchants)}")


# ---------------------------------------------------------
# 8. Diagnose missing cities
# ---------------------------------------------------------

print("\n--- City Diagnostic ---")

missing_city_states = df.loc[
    df["city"].isna(),
    "state"
].unique()

print(f"Rows with missing city: {df['city'].isna().sum()}")
print(f"Unique states affected: {len(missing_city_states)}")
print(f"States with missing city: {list(missing_city_states)}")


# ---------------------------------------------------------
# 9. Remove duplicate transactions
# ---------------------------------------------------------

before_dedup = len(df)

df = df.drop_duplicates(
    subset=["transaction_id"],
    keep="first"
).copy()

after_dedup = len(df)

print("\n--- Duplicate Removal ---")
print(f"Rows before deduplication: {before_dedup}")
print(f"Rows after deduplication: {after_dedup}")
print(f"Duplicate rows removed: {before_dedup - after_dedup}")


# ---------------------------------------------------------
# 10. Save cleaned dataset
# ---------------------------------------------------------

CLEANED_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    CLEANED_FILE,
    index=False
)

print("\nCleaned dataset saved successfully.")
print(f"Output: {CLEANED_FILE}")
print(f"Final shape: {df.shape}")


# ---------------------------------------------------------
# 11. Final cleaned-file verification
# ---------------------------------------------------------

cleaned_check = pd.read_csv(
    CLEANED_FILE,
    low_memory=False
)

print("\n--- Final Cleaned File Verification ---")
print(f"Saved rows: {len(cleaned_check)}")
print(f"Saved columns: {len(cleaned_check.columns)}")
print(
    f"Duplicate transaction IDs: "
    f"{cleaned_check['transaction_id'].duplicated().sum()}"
)
print(
    f"Duplicate rows: "
    f"{cleaned_check.duplicated().sum()}"
)