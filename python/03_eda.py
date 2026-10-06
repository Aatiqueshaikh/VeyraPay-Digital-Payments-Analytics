import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ---------------------------------------------------------
# VeyraPay — Exploratory Data Analysis
# ---------------------------------------------------------

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

CLEANED_FILE = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "veyrapay_transactions_cleaned.csv"
)

EDA_OUTPUT_DIR = PROJECT_ROOT / "data" / "eda"


# ---------------------------------------------------------
# 1. Load cleaned dataset
# ---------------------------------------------------------

print("Loading cleaned dataset...")

df = pd.read_csv(
    CLEANED_FILE,
    parse_dates=["transaction_datetime", "refund_datetime"],
    low_memory=False
)

print(f"Dataset shape: {df.shape}")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


# ---------------------------------------------------------
# 2. Create analysis date fields
# ---------------------------------------------------------

df["transaction_date"] = df["transaction_datetime"].dt.date
df["year"] = df["transaction_datetime"].dt.year
df["month"] = df["transaction_datetime"].dt.month
df["year_month"] = df["transaction_datetime"].dt.to_period("M").astype(str)
df["day_of_week"] = df["transaction_datetime"].dt.day_name()
df["hour"] = df["transaction_datetime"].dt.hour


# ---------------------------------------------------------
# 3. Create EDA output directory
# ---------------------------------------------------------

EDA_OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# 4. Basic dataset overview
# ---------------------------------------------------------

print("\n--- Dataset Overview ---")
print(df.info())

print("\n--- Date Range ---")
print(f"Start: {df['transaction_datetime'].min()}")
print(f"End:   {df['transaction_datetime'].max()}")

print("\n--- Missing Values ---")
print(df.isna().sum())

print("\n--- Numeric Summary ---")
print(
    df[
        [
            "amount",
            "refund_amount",
            "processing_time_seconds"
        ]
    ].describe()
)


# ---------------------------------------------------------
# 5. Transaction performance
# ---------------------------------------------------------

print("\n--- Transaction Performance ---")

total_transactions = len(df)
total_transaction_value = df["amount"].sum()
average_transaction_value = df["amount"].mean()

successful_transactions = (
    df["transaction_status"] == "Successful"
).sum()

failed_transactions = (
    df["transaction_status"] == "Failed"
).sum()

pending_transactions = (
    df["transaction_status"] == "Pending"
).sum()

success_rate = (
    successful_transactions / total_transactions * 100
)

failure_rate = (
    failed_transactions / total_transactions * 100
)

print(f"Total Transactions: {total_transactions:,}")
print(f"Total Transaction Value: ₹{total_transaction_value:,.2f}")
print(f"Average Transaction Value: ₹{average_transaction_value:,.2f}")
print(f"Successful Transactions: {successful_transactions:,}")
print(f"Failed Transactions: {failed_transactions:,}")
print(f"Pending Transactions: {pending_transactions:,}")
print(f"Success Rate: {success_rate:.2f}%")
print(f"Failure Rate: {failure_rate:.2f}%")


# ---------------------------------------------------------
# 6. Payment method analysis
# ---------------------------------------------------------

print("\n--- Payment Method Analysis ---")

payment_analysis = (
    df.groupby("payment_method")
    .agg(
        transactions=("transaction_id", "count"),
        transaction_value=("amount", "sum"),
        average_transaction_value=("amount", "mean")
    )
    .sort_values(
        "transaction_value",
        ascending=False
    )
)

print(payment_analysis)


# ---------------------------------------------------------
# 7. Customer analysis
# ---------------------------------------------------------

print("\n--- Customer Analysis ---")

customer_analysis = (
    df.groupby("customer_type")
    .agg(
        transactions=("transaction_id", "count"),
        transaction_value=("amount", "sum"),
        customers=("customer_id", "nunique")
    )
)

print(customer_analysis)

active_customers = df["customer_id"].nunique()

print(f"\nActive Customers: {active_customers:,}")


# ---------------------------------------------------------
# 8. Platform analysis
# ---------------------------------------------------------

print("\n--- Platform Analysis ---")

platform_analysis = (
    df.groupby("platform")
    .agg(
        transactions=("transaction_id", "count"),
        transaction_value=("amount", "sum"),
        average_transaction_value=("amount", "mean")
    )
    .sort_values(
        "transaction_value",
        ascending=False
    )
)

print(platform_analysis)


# ---------------------------------------------------------
# 9. Refund analysis
# ---------------------------------------------------------

print("\n--- Refund Analysis ---")

refund_transactions = (
    df["refund_status"] != "No Refund"
).sum()

refund_amount = df["refund_amount"].sum()

refund_rate = (
    refund_transactions / total_transactions * 100
)

print(f"Refund Transactions: {refund_transactions:,}")
print(f"Refund Amount: ₹{refund_amount:,.2f}")
print(f"Refund Rate: {refund_rate:.2f}%")


# ---------------------------------------------------------
# 10. Failure reason analysis
# ---------------------------------------------------------

print("\n--- Failure Reason Analysis ---")

failure_analysis = (
    df.loc[
        df["transaction_status"] == "Failed"
    ]
    .groupby("failure_reason")
    .size()
    .sort_values(
        ascending=False
    )
)

print(failure_analysis)


# ---------------------------------------------------------
# 11. Regional analysis
# ---------------------------------------------------------

print("\n--- Regional Analysis ---")

region_analysis = (
    df.groupby("region")
    .agg(
        transactions=("transaction_id", "count"),
        transaction_value=("amount", "sum"),
        average_transaction_value=("amount", "mean")
    )
    .sort_values(
        "transaction_value",
        ascending=False
    )
)

print(region_analysis)


# ---------------------------------------------------------
# 12. Merchant category analysis
# ---------------------------------------------------------

print("\n--- Merchant Category Analysis ---")

merchant_category_analysis = (
    df.groupby("merchant_category", dropna=False)
    .agg(
        transactions=("transaction_id", "count"),
        transaction_value=("amount", "sum"),
        average_transaction_value=("amount", "mean")
    )
    .sort_values(
        "transaction_value",
        ascending=False
    )
)

print(merchant_category_analysis)


# ---------------------------------------------------------
# 13. Monthly transaction trend
# ---------------------------------------------------------

print("\n--- Monthly Transaction Trend ---")

monthly_analysis = (
    df.groupby("year_month")
    .agg(
        transactions=("transaction_id", "count"),
        transaction_value=("amount", "sum")
    )
    .reset_index()
)

print(monthly_analysis)


# ---------------------------------------------------------
# 14. Save analysis tables
# ---------------------------------------------------------

payment_analysis.to_csv(
    EDA_OUTPUT_DIR / "payment_method_analysis.csv"
)

customer_analysis.to_csv(
    EDA_OUTPUT_DIR / "customer_type_analysis.csv"
)

platform_analysis.to_csv(
    EDA_OUTPUT_DIR / "platform_analysis.csv"
)

failure_analysis.to_csv(
    EDA_OUTPUT_DIR / "failure_reason_analysis.csv"
)

region_analysis.to_csv(
    EDA_OUTPUT_DIR / "region_analysis.csv"
)

merchant_category_analysis.to_csv(
    EDA_OUTPUT_DIR / "merchant_category_analysis.csv"
)

monthly_analysis.to_csv(
    EDA_OUTPUT_DIR / "monthly_transaction_analysis.csv",
    index=False
)


# ---------------------------------------------------------
# 15. Monthly transaction value chart
# ---------------------------------------------------------

plt.figure(figsize=(12, 6))

plt.plot(
    monthly_analysis["year_month"],
    monthly_analysis["transaction_value"]
)

plt.title(
    "VeyraPay Monthly Transaction Value"
)

plt.xlabel("Month")
plt.ylabel("Transaction Value (INR)")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    EDA_OUTPUT_DIR / "monthly_transaction_value.png",
    dpi=150
)

plt.close()


# ---------------------------------------------------------
# 16. Payment method transaction value chart
# ---------------------------------------------------------

plt.figure(figsize=(10, 6))

payment_chart = payment_analysis.sort_values(
    "transaction_value"
)

plt.barh(
    payment_chart.index,
    payment_chart["transaction_value"]
)

plt.title(
    "Transaction Value by Payment Method"
)

plt.xlabel("Transaction Value (INR)")
plt.ylabel("Payment Method")

plt.tight_layout()

plt.savefig(
    EDA_OUTPUT_DIR / "payment_method_transaction_value.png",
    dpi=150
)

plt.close()


# ---------------------------------------------------------
# 17. Failure reason chart
# ---------------------------------------------------------

plt.figure(figsize=(10, 6))

failure_chart = failure_analysis.sort_values()

plt.barh(
    failure_chart.index,
    failure_chart.values
)

plt.title(
    "Failed Transactions by Failure Reason"
)

plt.xlabel("Failed Transactions")
plt.ylabel("Failure Reason")

plt.tight_layout()

plt.savefig(
    EDA_OUTPUT_DIR / "failure_reason_distribution.png",
    dpi=150
)

plt.close()


# ---------------------------------------------------------
# 18. Final EDA message
# ---------------------------------------------------------

print("\nEDA completed successfully.")

print(f"Analysis outputs saved to:")
print(EDA_OUTPUT_DIR)


# ---------------------------------------------------------
# 19. Day-of-week analysis
# ---------------------------------------------------------

print("\n--- Day-of-Week Analysis ---")

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

day_analysis = (
    df.groupby("day_of_week")
    .agg(
        transactions=("transaction_id", "count"),
        transaction_value=("amount", "sum"),
        average_transaction_value=("amount", "mean")
    )
    .reindex(weekday_order)
)

print(day_analysis)


# ---------------------------------------------------------
# 20. Hourly transaction analysis
# ---------------------------------------------------------

print("\n--- Hourly Transaction Analysis ---")

hour_analysis = (
    df.groupby("hour")
    .agg(
        transactions=("transaction_id", "count"),
        transaction_value=("amount", "sum")
    )
    .sort_index()
)

print(hour_analysis)


# ---------------------------------------------------------
# 21. Weekend vs weekday analysis
# ---------------------------------------------------------

print("\n--- Weekday vs Weekend Analysis ---")

df["day_type"] = df["day_of_week"].isin(
    ["Saturday", "Sunday"]
).map({
    True: "Weekend",
    False: "Weekday"
})

day_type_analysis = (
    df.groupby("day_type")
    .agg(
        transactions=("transaction_id", "count"),
        transaction_value=("amount", "sum"),
        average_transaction_value=("amount", "mean")
    )
)

print(day_type_analysis)


# ---------------------------------------------------------
# 22. Save time analysis tables
# ---------------------------------------------------------

day_analysis.to_csv(
    EDA_OUTPUT_DIR / "day_of_week_analysis.csv"
)

hour_analysis.to_csv(
    EDA_OUTPUT_DIR / "hourly_transaction_analysis.csv"
)

day_type_analysis.to_csv(
    EDA_OUTPUT_DIR / "weekday_vs_weekend_analysis.csv"
)


# ---------------------------------------------------------
# 23. Final EDA Validation
# ---------------------------------------------------------

print("\n--- Final EDA Validation ---")

print(f"Total transactions: {df['transaction_id'].nunique():,}")
print(f"Total transaction value: ₹{df['amount'].sum():,.2f}")
print(f"Successful transactions: {(df['transaction_status'] == 'Successful').sum():,}")
print(f"Failed transactions: {(df['transaction_status'] == 'Failed').sum():,}")
print(f"Pending transactions: {(df['transaction_status'] == 'Pending').sum():,}")

print(
    f"Payment method analysis transactions: "
    f"{payment_analysis['transactions'].sum():,}"
)

print(
    f"Monthly analysis transactions: "
    f"{monthly_analysis['transactions'].sum():,}"
)

print(
    f"Day-of-week analysis transactions: "
    f"{day_analysis['transactions'].sum():,}"
)

print(
    f"Hourly analysis transactions: "
    f"{hour_analysis['transactions'].sum():,}"
)

print(
    f"Weekday + weekend transactions: "
    f"{day_type_analysis['transactions'].sum():,}"
)

print("\nEDA validation completed.")