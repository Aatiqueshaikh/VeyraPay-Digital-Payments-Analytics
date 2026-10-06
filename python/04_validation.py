import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEANED_FILE = PROJECT_ROOT / "data" / "cleaned" / "veyrapay_transactions_cleaned.csv"

print("Loading cleaned dataset...")

df = pd.read_csv(
    CLEANED_FILE,
    parse_dates=["transaction_datetime", "refund_datetime"]
)

print(f"Dataset shape: {df.shape}")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\n--- Validation Script Ready ---")
print("Cleaned dataset loaded successfully.")


# ============================================================
# 1. DATA INTEGRITY VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("1. DATA INTEGRITY VALIDATION")
print("=" * 60)

# Required columns
required_columns = [
    "transaction_id",
    "transaction_datetime",
    "amount",
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
    "refund_amount",
    "refund_datetime",
    "processing_time_seconds"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

print(f"\nRequired columns: {len(required_columns)}")
print(f"Actual columns:   {len(df.columns)}")

if missing_columns:
    print(f"❌ Missing columns: {missing_columns}")
else:
    print("✅ All required columns are present.")


# Transaction ID uniqueness
duplicate_transaction_ids = df["transaction_id"].duplicated().sum()

print(f"\nDuplicate transaction IDs: {duplicate_transaction_ids:,}")

if duplicate_transaction_ids == 0:
    print("✅ Transaction IDs are unique.")
else:
    print("❌ Duplicate transaction IDs found.")


# Exact duplicate rows
duplicate_rows = df.duplicated().sum()

print(f"\nExact duplicate rows: {duplicate_rows:,}")

if duplicate_rows == 0:
    print("✅ No exact duplicate rows found.")
else:
    print("❌ Exact duplicate rows found.")


# Row count
expected_rows = 200_000
actual_rows = len(df)

print(f"\nExpected rows: {expected_rows:,}")
print(f"Actual rows:   {actual_rows:,}")

if actual_rows == expected_rows:
    print("✅ Row count matches expected cleaned dataset.")
else:
    print("❌ Row count does not match expected value.")


# Transaction datetime validation
missing_transaction_datetime = df["transaction_datetime"].isna().sum()

print(
    f"\nMissing transaction timestamps: "
    f"{missing_transaction_datetime:,}"
)

if missing_transaction_datetime == 0:
    print("✅ All transactions have valid timestamps.")
else:
    print("❌ Missing transaction timestamps found.")


print("\n--- Data integrity validation completed ---")


# ============================================================
# 2. AMOUNT & PROCESSING-TIME VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("2. AMOUNT & PROCESSING-TIME VALIDATION")
print("=" * 60)

# Amount must be greater than zero
invalid_amounts = (df["amount"] <= 0).sum()

print(f"\nAmounts <= 0: {invalid_amounts:,}")

if invalid_amounts == 0:
    print("✅ All transaction amounts are greater than zero.")
else:
    print("❌ Invalid transaction amounts found.")


# Refund amount must not be negative
invalid_refund_amounts = (df["refund_amount"] < 0).sum()

print(f"\nNegative refund amounts: {invalid_refund_amounts:,}")

if invalid_refund_amounts == 0:
    print("✅ No negative refund amounts found.")
else:
    print("❌ Negative refund amounts found.")


# Refund amount must not exceed transaction amount
refund_exceeds_transaction = (
    df["refund_amount"] > df["amount"]
).sum()

print(
    f"\nRefund amount > transaction amount: "
    f"{refund_exceeds_transaction:,}"
)

if refund_exceeds_transaction == 0:
    print("✅ All refund amounts are within transaction amounts.")
else:
    print("❌ Refund amount exceeds transaction amount.")


# Processing time must not be negative
invalid_processing_times = (
    df["processing_time_seconds"] < 0
).sum()

print(
    f"\nNegative processing times: "
    f"{invalid_processing_times:,}"
)

if invalid_processing_times == 0:
    print("✅ No negative processing times found.")
else:
    print("❌ Negative processing times found.")


print("\n--- Amount & processing-time validation completed ---")


# ============================================================
# 3. TRANSACTION STATUS VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("3. TRANSACTION STATUS VALIDATION")
print("=" * 60)

# Allowed transaction statuses
allowed_statuses = {
    "Successful",
    "Failed",
    "Pending"
}

invalid_statuses = (
    ~df["transaction_status"].isin(allowed_statuses)
).sum()

print(f"\nInvalid transaction statuses: {invalid_statuses:,}")

if invalid_statuses == 0:
    print("✅ All transaction statuses are valid.")
else:
    print("❌ Invalid transaction statuses found.")


# Failed transactions must have a failure reason
failed_missing_reason = (
    (df["transaction_status"] == "Failed") &
    (df["failure_reason"].isna())
).sum()

print(
    f"\nFailed transactions missing failure reason: "
    f"{failed_missing_reason:,}"
)

if failed_missing_reason == 0:
    print("✅ All failed transactions have a failure reason.")
else:
    print("❌ Failed transactions missing failure reason found.")


# Successful transactions must not have a failure reason
successful_with_reason = (
    (df["transaction_status"] == "Successful") &
    (df["failure_reason"].notna())
).sum()

print(
    f"\nSuccessful transactions with failure reason: "
    f"{successful_with_reason:,}"
)

if successful_with_reason == 0:
    print("✅ Successful transactions have no failure reason.")
else:
    print("❌ Successful transactions with failure reason found.")


# Pending transactions must not have a failure reason
pending_with_reason = (
    (df["transaction_status"] == "Pending") &
    (df["failure_reason"].notna())
).sum()

print(
    f"\nPending transactions with failure reason: "
    f"{pending_with_reason:,}"
)

if pending_with_reason == 0:
    print("✅ Pending transactions have no failure reason.")
else:
    print("❌ Pending transactions with failure reason found.")


print("\n--- Transaction status validation completed ---")


# ============================================================
# 4. REFUND BUSINESS-RULE VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("4. REFUND BUSINESS-RULE VALIDATION")
print("=" * 60)

# Failed transactions must not have refunds
failed_with_refund = (
    (df["transaction_status"] == "Failed") &
    (df["refund_status"] != "No Refund")
).sum()

print(
    f"\nFailed transactions with refund: "
    f"{failed_with_refund:,}"
)

if failed_with_refund == 0:
    print("✅ Failed transactions have no refunds.")
else:
    print("❌ Failed transactions with refunds found.")


# Pending transactions must not have refunds
pending_with_refund = (
    (df["transaction_status"] == "Pending") &
    (df["refund_status"] != "No Refund")
).sum()

print(
    f"\nPending transactions with refund: "
    f"{pending_with_refund:,}"
)

if pending_with_refund == 0:
    print("✅ Pending transactions have no refunds.")
else:
    print("❌ Pending transactions with refunds found.")


# No Refund status must have zero refund amount
no_refund_with_amount = (
    (df["refund_status"] == "No Refund") &
    (df["refund_amount"] != 0)
).sum()

print(
    f"\nNo Refund transactions with refund amount: "
    f"{no_refund_with_amount:,}"
)

if no_refund_with_amount == 0:
    print("✅ No Refund transactions have zero refund amount.")
else:
    print("❌ No Refund transactions with refund amount found.")


# No Refund status must have no refund datetime
no_refund_with_datetime = (
    (df["refund_status"] == "No Refund") &
    (df["refund_datetime"].notna())
).sum()

print(
    f"\nNo Refund transactions with refund datetime: "
    f"{no_refund_with_datetime:,}"
)

if no_refund_with_datetime == 0:
    print("✅ No Refund transactions have no refund datetime.")
else:
    print("❌ No Refund transactions with refund datetime found.")


# Refunded transactions must have a refund datetime
refund_without_datetime = (
    (df["refund_status"] != "No Refund") &
    (df["refund_datetime"].isna())
).sum()

print(
    f"\nRefund transactions missing refund datetime: "
    f"{refund_without_datetime:,}"
)

if refund_without_datetime == 0:
    print("✅ All refund transactions have a refund datetime.")
else:
    print("❌ Refund transactions missing refund datetime found.")


# Refund datetime must be later than transaction datetime
invalid_refund_datetime = (
    df["refund_datetime"].notna() &
    (df["refund_datetime"] <= df["transaction_datetime"])
).sum()

print(
    f"\nRefund datetime <= transaction datetime: "
    f"{invalid_refund_datetime:,}"
)

if invalid_refund_datetime == 0:
    print("✅ All refund datetimes occur after transaction datetime.")
else:
    print("❌ Invalid refund datetime sequence found.")


print("\n--- Refund business-rule validation completed ---")


# ============================================================
# 4A. INVESTIGATE INVALID REFUND DATETIMES
# ============================================================

print("\n" + "=" * 60)
print("4A. INVALID REFUND DATETIME INVESTIGATION")
print("=" * 60)

invalid_refund_records = df[
    df["refund_datetime"].notna() &
    (df["refund_datetime"] <= df["transaction_datetime"])
].copy()

print(
    f"\nInvalid refund datetime records: "
    f"{len(invalid_refund_records):,}"
)

print("\nSample invalid records:")

print(
    invalid_refund_records[
        [
            "transaction_id",
            "transaction_datetime",
            "refund_status",
            "refund_amount",
            "refund_datetime"
        ]
    ].head(10).to_string(index=False)
)


# Calculate time difference
invalid_refund_records["refund_delay_seconds"] = (
    invalid_refund_records["refund_datetime"] -
    invalid_refund_records["transaction_datetime"]
).dt.total_seconds()

print("\nRefund delay statistics for invalid records:")

print(
    invalid_refund_records["refund_delay_seconds"]
    .describe()
)


print("\n--- Invalid refund datetime investigation completed ---")