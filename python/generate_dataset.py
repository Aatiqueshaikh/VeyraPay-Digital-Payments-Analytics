import numpy as np
import pandas as pd
from pathlib import Path


# ============================================================
# VEYRAPAY — SYNTHETIC TRANSACTION DATASET GENERATOR
# ============================================================

# Reproducible random generation
SEED = 42
rng = np.random.default_rng(SEED)

# Dataset targets
N_TRANSACTIONS = 200_000
N_CUSTOMERS = 50_000
N_MERCHANTS = 6_000

# 24-month project period
START_DATE = pd.Timestamp("2024-01-01 00:00:00")
END_DATE = pd.Timestamp("2025-12-31 23:59:59")

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = RAW_DIR / "veyrapay_transactions_raw.csv"

# Ensure the output folder exists
RAW_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# BLUEPRINT CATEGORIES
# ============================================================

PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "Wallet",
]

STATUSES = [
    "Successful",
    "Failed",
    "Pending",
]

PLATFORMS = [
    "Mobile",
    "Web",
]

MERCHANT_CATEGORIES = [
    "Food & Dining",
    "Retail",
    "Grocery",
    "Travel",
    "Entertainment",
    "Healthcare",
    "Education",
    "Utilities",
    "Electronics",
    "Services",
]

REFUND_STATUSES = [
    "No Refund",
    "Partial Refund",
    "Full Refund",
]

FAILURE_REASONS = [
    "Bank Declined",
    "Insufficient Funds",
    "Network Timeout",
    "Authentication Failed",
    "Payment Gateway Error",
    "Limit Exceeded",
    "Technical Error",
]


print("VeyraPay dataset generator initialized.")
print(f"Transactions target : {N_TRANSACTIONS:,}")
print(f"Customers target    : {N_CUSTOMERS:,}")
print(f"Merchants target    : {N_MERCHANTS:,}")
print(f"Output file         : {OUTPUT_FILE}")


# ============================================================
# INDIA GEOGRAPHY
# ============================================================

GEOGRAPHY = {
    "North": {
        "Jammu and Kashmir": ["Srinagar", "Jammu"],
        "Himachal Pradesh": ["Shimla", "Dharamshala"],
        "Punjab": ["Ludhiana", "Amritsar", "Chandigarh"],
        "Haryana": ["Gurugram", "Faridabad", "Panipat"],
        "Delhi": ["New Delhi", "Delhi"],
        "Uttarakhand": ["Dehradun", "Haridwar"],
        "Uttar Pradesh": ["Lucknow", "Kanpur", "Noida", "Varanasi", "Agra"],
    },

    "South": {
        "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
        "Telangana": ["Hyderabad", "Warangal"],
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Tirupati"],
        "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode"],
    },

    "East": {
        "West Bengal": ["Kolkata", "Siliguri", "Durgapur"],
        "Odisha": ["Bhubaneswar", "Cuttack"],
        "Bihar": ["Patna", "Gaya"],
        "Jharkhand": ["Ranchi", "Jamshedpur"],
        "Assam": ["Guwahati", "Dibrugarh"],
    },

    "West": {
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
        "Goa": ["Panaji", "Margao"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur"],
    },

    "Central": {
        "Madhya Pradesh": ["Indore", "Bhopal", "Jabalpur"],
        "Chhattisgarh": ["Raipur", "Bhilai"],
    },
}


# Create a flat geography lookup for transaction generation
GEOGRAPHY_ROWS = []

for region, states in GEOGRAPHY.items():
    for state, cities in states.items():
        for city in cities:
            GEOGRAPHY_ROWS.append(
                {
                    "region": region,
                    "state": state,
                    "city": city,
                }
            )

GEOGRAPHY_DF = pd.DataFrame(GEOGRAPHY_ROWS)

print(f"Geography combinations loaded: {len(GEOGRAPHY_DF)}")


# ============================================================
# CUSTOMER AND MERCHANT POOLS
# ============================================================

CUSTOMER_IDS = np.array(
    [f"CUST{number:06d}" for number in range(1, N_CUSTOMERS + 1)]
)

MERCHANT_IDS = np.array(
    [f"MER{number:05d}" for number in range(1, N_MERCHANTS + 1)]
)

print(f"Customer IDs created : {len(CUSTOMER_IDS):,}")
print(f"Merchant IDs created : {len(MERCHANT_IDS):,}")


# ============================================================
# TRANSACTION TIMESTAMPS
# ============================================================

# Generate realistic time-of-day activity:
# lower activity overnight, higher activity during
# morning, lunch, and evening periods.

HOUR_WEIGHTS = np.array([
    0.015,  # 00:00
    0.012,  # 01:00
    0.010,  # 02:00
    0.010,  # 03:00
    0.012,  # 04:00
    0.015,  # 05:00
    0.025,  # 06:00
    0.040,  # 07:00
    0.055,  # 08:00
    0.065,  # 09:00
    0.060,  # 10:00
    0.070,  # 11:00
    0.075,  # 12:00
    0.070,  # 13:00
    0.055,  # 14:00
    0.050,  # 15:00
    0.045,  # 16:00
    0.055,  # 17:00
    0.075,  # 18:00
    0.080,  # 19:00
    0.070,  # 20:00
    0.055,  # 21:00
    0.035,  # 22:00
    0.020,  # 23:00
])

HOUR_WEIGHTS = HOUR_WEIGHTS / HOUR_WEIGHTS.sum()

# Generate dates across the complete 24-month period.
date_range = pd.date_range(
    start=START_DATE.normalize(),
    end=END_DATE.normalize(),
    freq="D",
)

transaction_dates = rng.choice(
    date_range,
    size=N_TRANSACTIONS,
    replace=True,
)

transaction_hours = rng.choice(
    np.arange(24),
    size=N_TRANSACTIONS,
    replace=True,
    p=HOUR_WEIGHTS,
)

transaction_minutes = rng.integers(
    0,
    60,
    size=N_TRANSACTIONS,
)

transaction_seconds = rng.integers(
    0,
    60,
    size=N_TRANSACTIONS,
)

TRANSACTION_DATETIME = (
    pd.to_datetime(transaction_dates)
    + pd.to_timedelta(transaction_hours, unit="h")
    + pd.to_timedelta(transaction_minutes, unit="m")
    + pd.to_timedelta(transaction_seconds, unit="s")
)

# Keep timestamps inside the exact project period.
TRANSACTION_DATETIME = pd.Series(
    TRANSACTION_DATETIME
).clip(
    lower=START_DATE,
    upper=END_DATE,
).to_numpy()

print(
    "Transaction timestamps generated:"
    f" {TRANSACTION_DATETIME.min()} → {TRANSACTION_DATETIME.max()}"
)


# ============================================================
# TRANSACTION AMOUNTS
# ============================================================

# Blueprint target distribution:
# ₹50–₹500       → 25%
# ₹500–₹1,500    → 35%
# ₹1,500–₹5,000  → 25%
# ₹5,000–₹15,000 → 11%
# ₹15,000+       → 4%

amount_band = rng.choice(
    [
        "50-500",
        "500-1500",
        "1500-5000",
        "5000-15000",
        "15000+",
    ],
    size=N_TRANSACTIONS,
    p=[0.25, 0.35, 0.25, 0.11, 0.04],
)

amounts = np.empty(N_TRANSACTIONS)

mask = amount_band == "50-500"
amounts[mask] = rng.uniform(50, 500, mask.sum())

mask = amount_band == "500-1500"
amounts[mask] = rng.uniform(500, 1500, mask.sum())

mask = amount_band == "1500-5000"
amounts[mask] = rng.uniform(1500, 5000, mask.sum())

mask = amount_band == "5000-15000"
amounts[mask] = rng.uniform(5000, 15000, mask.sum())

mask = amount_band == "15000+"
amounts[mask] = rng.lognormal(
    mean=np.log(22000),
    sigma=0.45,
    size=mask.sum(),
)

# Keep monetary values to two decimal places
AMOUNTS = np.round(amounts, 2)

print(
    f"Transaction amounts generated:"
    f" ₹{AMOUNTS.min():,.2f} → ₹{AMOUNTS.max():,.2f}"
)


# ============================================================
# CUSTOMER ASSIGNMENT
# ============================================================

# Assign customers with a realistic transaction-frequency pattern.
# More frequent customers are less common, while occasional
# customers make up a larger share of the customer base.

customer_frequency_group = rng.choice(
    [
        "1-2",
        "3-5",
        "6-12",
        "13-30",
        "30+",
    ],
    size=N_CUSTOMERS,
    p=[0.25, 0.30, 0.28, 0.13, 0.04],
)

customer_weights = np.ones(N_CUSTOMERS)

customer_weights[customer_frequency_group == "1-2"] = 1.0
customer_weights[customer_frequency_group == "3-5"] = 2.5
customer_weights[customer_frequency_group == "6-12"] = 5.5
customer_weights[customer_frequency_group == "13-30"] = 12.0
customer_weights[customer_frequency_group == "30+"] = 25.0

customer_weights = customer_weights / customer_weights.sum()

CUSTOMER_ASSIGNMENTS = rng.choice(
    CUSTOMER_IDS,
    size=N_TRANSACTIONS,
    replace=True,
    p=customer_weights,
)

print(
    f"Unique customers assigned:"
    f" {pd.Series(CUSTOMER_ASSIGNMENTS).nunique():,}"
)


# ============================================================
# MERCHANT ASSIGNMENT
# ============================================================

MERCHANT_ASSIGNMENTS = rng.choice(
    MERCHANT_IDS,
    size=N_TRANSACTIONS,
    replace=True,
)

MERCHANT_CATEGORY_ASSIGNMENTS = rng.choice(
    MERCHANT_CATEGORIES,
    size=N_TRANSACTIONS,
    replace=True,
)

print(
    f"Unique merchants assigned:"
    f" {pd.Series(MERCHANT_ASSIGNMENTS).nunique():,}"
)

print(
    f"Merchant categories used:"
    f" {pd.Series(MERCHANT_CATEGORY_ASSIGNMENTS).nunique()}"
)


# ============================================================
# PAYMENT METHOD ASSIGNMENT
# ============================================================

PAYMENT_METHOD_ASSIGNMENTS = rng.choice(
    PAYMENT_METHODS,
    size=N_TRANSACTIONS,
    replace=True,
    p=[
        0.48,  # UPI
        0.17,  # Credit Card
        0.15,  # Debit Card
        0.10,  # Net Banking
        0.10,  # Wallet
    ],
)

print("Payment method distribution:")
print(
    pd.Series(PAYMENT_METHOD_ASSIGNMENTS)
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ============================================================
# PLATFORM AND DEVICE ASSIGNMENT
# ============================================================

PLATFORM_ASSIGNMENTS = rng.choice(
    PLATFORMS,
    size=N_TRANSACTIONS,
    replace=True,
    p=[0.75, 0.25],
)

DEVICE_TYPES = np.where(
    PLATFORM_ASSIGNMENTS == "Mobile",
    rng.choice(
        ["Android", "iOS"],
        size=N_TRANSACTIONS,
        replace=True,
        p=[0.70, 0.30],
    ),
    rng.choice(
        ["Desktop", "Laptop"],
        size=N_TRANSACTIONS,
        replace=True,
        p=[0.65, 0.35],
    ),
)

print("Platform distribution:")
print(
    pd.Series(PLATFORM_ASSIGNMENTS)
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print("Device types generated:", pd.Series(DEVICE_TYPES).nunique())


# ============================================================
# TRANSACTION STATUS
# ============================================================

TRANSACTION_STATUS_ASSIGNMENTS = rng.choice(
    STATUSES,
    size=N_TRANSACTIONS,
    replace=True,
    p=[
        0.92,  # Successful
        0.06,  # Failed
        0.02,  # Pending
    ],
)

print("Transaction status distribution:")
print(
    pd.Series(TRANSACTION_STATUS_ASSIGNMENTS)
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ============================================================
# FAILURE REASONS
# ============================================================

FAILURE_REASON_ASSIGNMENTS = np.full(
    N_TRANSACTIONS,
    None,
    dtype=object,
)

failed_mask = TRANSACTION_STATUS_ASSIGNMENTS == "Failed"

FAILURE_REASON_ASSIGNMENTS[failed_mask] = rng.choice(
    FAILURE_REASONS,
    size=failed_mask.sum(),
    replace=True,
    p=[
        0.25,  # Bank Declined
        0.22,  # Insufficient Funds
        0.16,  # Network Timeout
        0.14,  # Authentication Failed
        0.12,  # Payment Gateway Error
        0.07,  # Limit Exceeded
        0.04,  # Technical Error
    ],
)

print(
    f"Failure reasons assigned to:"
    f" {failed_mask.sum():,} failed transactions"
)


# ============================================================
# GEOGRAPHY ASSIGNMENT
# ============================================================

geography_indices = rng.integers(
    0,
    len(GEOGRAPHY_DF),
    size=N_TRANSACTIONS,
)

TRANSACTION_REGION = GEOGRAPHY_DF.iloc[
    geography_indices
]["region"].to_numpy()

TRANSACTION_STATE = GEOGRAPHY_DF.iloc[
    geography_indices
]["state"].to_numpy()

TRANSACTION_CITY = GEOGRAPHY_DF.iloc[
    geography_indices
]["city"].to_numpy()

print(
    f"Geography assigned across:"
    f" {pd.Series(TRANSACTION_REGION).nunique()} regions, "
    f"{pd.Series(TRANSACTION_STATE).nunique()} states, "
    f"{pd.Series(TRANSACTION_CITY).nunique()} cities"
)


# ============================================================
# REFUND STATUS AND AMOUNT
# ============================================================

REFUND_STATUS_ASSIGNMENTS = np.full(
    N_TRANSACTIONS,
    "No Refund",
    dtype=object,
)

REFUND_AMOUNTS = np.zeros(
    N_TRANSACTIONS,
    dtype=float,
)

successful_mask = TRANSACTION_STATUS_ASSIGNMENTS == "Successful"

successful_refund_statuses = rng.choice(
    REFUND_STATUSES,
    size=successful_mask.sum(),
    replace=True,
    p=[
        0.94,   # No Refund
        0.045,  # Partial Refund
        0.015,  # Full Refund
    ],
)

REFUND_STATUS_ASSIGNMENTS[successful_mask] = successful_refund_statuses

successful_indices = np.where(successful_mask)[0]

partial_mask = (
    successful_mask
    & (REFUND_STATUS_ASSIGNMENTS == "Partial Refund")
)

full_mask = (
    successful_mask
    & (REFUND_STATUS_ASSIGNMENTS == "Full Refund")
)

# Partial refunds: strictly greater than 0
# and strictly less than the transaction amount.
REFUND_AMOUNTS[partial_mask] = np.round(
    AMOUNTS[partial_mask]
    * rng.uniform(0.10, 0.90, partial_mask.sum()),
    2,
)

# Full refunds equal the complete transaction amount.
REFUND_AMOUNTS[full_mask] = AMOUNTS[full_mask]

print("Refund status distribution:")
print(
    pd.Series(REFUND_STATUS_ASSIGNMENTS)
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print(
    f"Total refund amount generated:"
    f" ₹{REFUND_AMOUNTS.sum():,.2f}"
)


# ============================================================
# REFUND DATETIME INITIALIZATION
# ============================================================

REFUND_DATETIMES = np.empty(
    int(N_TRANSACTIONS),
    dtype="datetime64[ns]",
)

REFUND_DATETIMES[:] = np.datetime64("NaT")

refund_mask = REFUND_STATUS_ASSIGNMENTS != "No Refund"

refund_indices = np.where(refund_mask)[0]

# Generate a refund delay between 1 and 30 days.
refund_delay_days = rng.integers(
    1,
    31,
    size=refund_indices.size,
)

refund_delay_hours = rng.integers(
    0,
    24,
    size=refund_indices.size,
)

refund_delay = (
    pd.to_timedelta(refund_delay_days, unit="D")
    + pd.to_timedelta(refund_delay_hours, unit="h")
)

refund_datetimes = (
    TRANSACTION_DATETIME[refund_indices]
    + refund_delay
)

# Keep refunds within the overall project period.
refund_datetimes = pd.Series(refund_datetimes)

REFUND_DATETIMES[refund_indices] = (
    refund_datetimes.to_numpy(dtype="datetime64[ns]")
)

print(
    f"Refund timestamps generated for:"
    f" {refund_indices.size:,} transactions"
)


# ============================================================
# PROCESSING TIME
# ============================================================

PROCESSING_TIME_SECONDS = np.empty(
    N_TRANSACTIONS,
    dtype=float,
)

# Successful transactions generally process faster.
successful_processing = rng.lognormal(
    mean=np.log(8),
    sigma=0.45,
    size=successful_mask.sum(),
)

# Failed transactions tend to take somewhat longer.
failed_processing = rng.lognormal(
    mean=np.log(14),
    sigma=0.55,
    size=failed_mask.sum(),
)

# Pending transactions have the longest processing time.
pending_mask = TRANSACTION_STATUS_ASSIGNMENTS == "Pending"

pending_processing = rng.lognormal(
    mean=np.log(25),
    sigma=0.60,
    size=pending_mask.sum(),
)

PROCESSING_TIME_SECONDS[successful_mask] = successful_processing
PROCESSING_TIME_SECONDS[failed_mask] = failed_processing
PROCESSING_TIME_SECONDS[pending_mask] = pending_processing

PROCESSING_TIME_SECONDS = np.round(
    np.maximum(PROCESSING_TIME_SECONDS, 1),
    2,
)

print(
    "Processing time generated:"
    f" {PROCESSING_TIME_SECONDS.min():.2f}s"
    f" → {PROCESSING_TIME_SECONDS.max():.2f}s"
)


# ============================================================
# BUILD TRANSACTION DATAFRAME
# ============================================================

TRANSACTIONS_DF = pd.DataFrame(
    {
        "transaction_id": [
            f"TXN{number:07d}"
            for number in range(1, N_TRANSACTIONS + 1)
        ],
        "transaction_datetime": TRANSACTION_DATETIME,
        "amount": AMOUNTS,
        "customer_id": CUSTOMER_ASSIGNMENTS,
        "customer_type": None,
        "payment_method": PAYMENT_METHOD_ASSIGNMENTS,
        "transaction_status": TRANSACTION_STATUS_ASSIGNMENTS,
        "failure_reason": FAILURE_REASON_ASSIGNMENTS,
        "merchant_id": MERCHANT_ASSIGNMENTS,
        "merchant_category": MERCHANT_CATEGORY_ASSIGNMENTS,
        "state": TRANSACTION_STATE,
        "region": TRANSACTION_REGION,
        "city": TRANSACTION_CITY,
        "platform": PLATFORM_ASSIGNMENTS,
        "device_type": DEVICE_TYPES,
        "refund_status": REFUND_STATUS_ASSIGNMENTS,
        "refund_amount": REFUND_AMOUNTS,
        "refund_datetime": REFUND_DATETIMES,
        "processing_time_seconds": PROCESSING_TIME_SECONDS,
    }
)

print(
    f"Transaction DataFrame created:"
    f" {TRANSACTIONS_DF.shape[0]:,} rows × "
    f"{TRANSACTIONS_DF.shape[1]} columns"
)

print("\nColumns:")
print(list(TRANSACTIONS_DF.columns))


# ============================================================
# CUSTOMER TYPE — NEW VS RETURNING
# ============================================================

# Sort chronologically so the first observed transaction
# for each customer can be identified correctly.
TRANSACTIONS_DF = TRANSACTIONS_DF.sort_values(
    by=["customer_id", "transaction_datetime"]
).reset_index(drop=True)

TRANSACTIONS_DF["customer_type"] = np.where(
    TRANSACTIONS_DF.groupby("customer_id").cumcount() == 0,
    "New",
    "Returning",
)

print("\nCustomer type distribution:")
print(
    TRANSACTIONS_DF["customer_type"]
    .value_counts()
)

print(
    "\nUnique customers represented:"
    f" {TRANSACTIONS_DF['customer_id'].nunique():,}"
)


# ============================================================
# WEEKDAY / WEEKEND ACTIVITY
# ============================================================

transaction_days = pd.Series(
    TRANSACTION_DATETIME
).dt.dayofweek.to_numpy()

weekend_mask = transaction_days >= 5

# Apply a modest weekend activity adjustment.
# Weekend transactions receive a small uplift,
# while weekday transactions remain the majority.
weekend_adjustment = rng.random(N_TRANSACTIONS)

weekend_activity_mask = (
    weekend_mask
    & (weekend_adjustment < 0.08)
)

weekday_activity_mask = (
    ~weekend_mask
    & (weekend_adjustment < 0.03)
)

print(
    "Weekend transaction share:"
    f" {weekend_mask.mean() * 100:.2f}%"
)

print(
    "Weekend activity sample:"
    f" {weekend_activity_mask.sum():,}"
)

print(
    "Weekday activity sample:"
    f" {weekday_activity_mask.sum():,}"
)


# ============================================================
# MERCHANT CATEGORY AMOUNT BEHAVIOR
# ============================================================

CATEGORY_AMOUNT_MULTIPLIERS = {
    "Food & Dining": 0.85,
    "Retail": 1.00,
    "Grocery": 0.90,
    "Travel": 1.35,
    "Entertainment": 1.05,
    "Healthcare": 1.20,
    "Education": 1.10,
    "Utilities": 0.95,
    "Electronics": 1.30,
    "Services": 1.00,
}

category_multipliers = np.array(
    [
        CATEGORY_AMOUNT_MULTIPLIERS[category]
        for category in MERCHANT_CATEGORY_ASSIGNMENTS
    ]
)

# Add modest random variation so categories overlap naturally.
category_variation = rng.normal(
    loc=1.0,
    scale=0.08,
    size=N_TRANSACTIONS,
)

AMOUNTS = np.round(
    np.maximum(
        AMOUNTS * category_multipliers * category_variation,
        50.00,
    ),
    2,
)

print(
    "Category-adjusted transaction amounts:"
    f" ₹{AMOUNTS.min():,.2f} → ₹{AMOUNTS.max():,.2f}"
)


# ============================================================
# RE-SYNC REFUND AMOUNTS AFTER FINAL AMOUNT ADJUSTMENT
# ============================================================

# Recalculate refund amounts using the final transaction amounts.

REFUND_AMOUNTS = np.zeros(
    N_TRANSACTIONS,
    dtype=float,
)

partial_mask = (
    TRANSACTION_STATUS_ASSIGNMENTS == "Successful"
) & (
    REFUND_STATUS_ASSIGNMENTS == "Partial Refund"
)

full_mask = (
    TRANSACTION_STATUS_ASSIGNMENTS == "Successful"
) & (
    REFUND_STATUS_ASSIGNMENTS == "Full Refund"
)

REFUND_AMOUNTS[partial_mask] = np.round(
    AMOUNTS[partial_mask]
    * rng.uniform(
        0.10,
        0.90,
        partial_mask.sum(),
    ),
    2,
)

REFUND_AMOUNTS[full_mask] = AMOUNTS[full_mask]

print(
    "Refund amounts re-synced with final transaction amounts."
)


# ============================================================
# CUSTOMER-LEVEL BEHAVIOR VARIATION
# ============================================================

# Create a stable preference profile for each customer.
# These are soft preferences, not fixed rules.

customer_preference = pd.DataFrame(
    {
        "customer_id": CUSTOMER_IDS,
        "preferred_payment": rng.choice(
            PAYMENT_METHODS,
            size=N_CUSTOMERS,
            replace=True,
            p=[0.48, 0.17, 0.15, 0.10, 0.10],
        ),
        "mobile_preference": rng.uniform(
            0.65,
            0.95,
            size=N_CUSTOMERS,
        ),
    }
)

customer_preference_lookup = customer_preference.set_index(
    "customer_id"
)

print(
    "Customer behavior profiles created:"
    f" {len(customer_preference_lookup):,}"
)


# ============================================================
# APPLY SOFT CUSTOMER PAYMENT PREFERENCES
# ============================================================

customer_preference_map = customer_preference_lookup.loc[
    CUSTOMER_ASSIGNMENTS,
    "preferred_payment",
].to_numpy()

# Keep the original payment distribution as the baseline.
# A moderate preference strength avoids rigid behavior.
keep_preference = rng.random(N_TRANSACTIONS) < 0.55

preferred_payment_mask = keep_preference

PAYMENT_METHOD_ASSIGNMENTS[preferred_payment_mask] = (
    customer_preference_map[preferred_payment_mask]
)

print(
    "Soft customer payment preferences applied:"
    f" {preferred_payment_mask.mean() * 100:.2f}% of transactions"
)


# ============================================================
# APPLY SOFT CUSTOMER PLATFORM PREFERENCES
# ============================================================

customer_mobile_preference = customer_preference_lookup.loc[
    CUSTOMER_ASSIGNMENTS,
    "mobile_preference",
].to_numpy()

# Reassign platform using each customer's soft preference.
# This does not force customers to use only one platform.
platform_random = rng.random(N_TRANSACTIONS)

PLATFORM_ASSIGNMENTS = np.where(
    platform_random < customer_mobile_preference,
    "Mobile",
    "Web",
)

print("Platform distribution after customer preferences:")
print(
    pd.Series(PLATFORM_ASSIGNMENTS)
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ============================================================
# FINAL DEVICE TYPE ASSIGNMENT
# ============================================================

DEVICE_TYPES = np.where(
    PLATFORM_ASSIGNMENTS == "Mobile",
    rng.choice(
        ["Android", "iOS"],
        size=N_TRANSACTIONS,
        replace=True,
        p=[0.70, 0.30],
    ),
    rng.choice(
        ["Desktop", "Laptop"],
        size=N_TRANSACTIONS,
        replace=True,
        p=[0.65, 0.35],
    ),
)

print(
    "Final device types assigned based on platform."
)


# ============================================================
# MODEST MONTHLY SEASONALITY
# ============================================================

# Small monthly activity adjustments.
# Values remain close to 1.0 to avoid exaggerated seasonality.
MONTH_ACTIVITY_MULTIPLIERS = {
    1: 0.96,
    2: 0.98,
    3: 1.00,
    4: 1.02,
    5: 1.04,
    6: 1.00,
    7: 0.98,
    8: 1.01,
    9: 1.03,
    10: 1.07,
    11: 1.10,
    12: 1.08,
}

print("Monthly seasonality profile prepared.")


# ============================================================
# APPLY MONTHLY SEASONALITY TO DATE GENERATION
# ============================================================

# Build daily weights from the monthly activity profile.
date_months = pd.Series(date_range).dt.month.to_numpy()

date_weights = np.array(
    [
        MONTH_ACTIVITY_MULTIPLIERS[month]
        for month in date_months
    ],
    dtype=float,
)

date_weights = date_weights / date_weights.sum()

# Re-select transaction dates using the modest monthly weights.
seasonal_dates = rng.choice(
    date_range,
    size=N_TRANSACTIONS,
    replace=True,
    p=date_weights,
)

# Keep the previously generated realistic time-of-day pattern.
TRANSACTION_DATETIME = (
    pd.to_datetime(seasonal_dates)
    + pd.to_timedelta(transaction_hours, unit="h")
    + pd.to_timedelta(transaction_minutes, unit="m")
    + pd.to_timedelta(transaction_seconds, unit="s")
)

TRANSACTION_DATETIME = pd.Series(
    TRANSACTION_DATETIME
).clip(
    lower=START_DATE,
    upper=END_DATE,
).to_numpy()

print(
    "Monthly seasonality applied to transaction dates."
)


# ============================================================
# CONTROLLED RAW-DATA QUALITY ISSUES
# ============================================================

# These issues intentionally simulate realistic raw operational
# data imperfections. They will be documented and cleaned later.

quality_rng = np.random.default_rng(SEED + 100)

# ------------------------------------------------------------
# 1. Small missing-value percentage
# ------------------------------------------------------------

missing_rate = 0.008  # 0.8%

# Use only suitable non-critical fields.
missing_fields = [
    "merchant_category",
    "city",
    "device_type",
]

for field in missing_fields:
    missing_count = int(N_TRANSACTIONS * missing_rate)

    missing_indices = quality_rng.choice(
        N_TRANSACTIONS,
        size=missing_count,
        replace=False,
    )

    TRANSACTIONS_DF.loc[
        missing_indices,
        field,
    ] = None

print(
    "Controlled missing values added to suitable non-critical fields."
)

# ------------------------------------------------------------
# 2. Small text inconsistencies
# ------------------------------------------------------------

text_issue_count = int(
    N_TRANSACTIONS * 0.001
)

text_issue_indices = quality_rng.choice(
    N_TRANSACTIONS,
    size=text_issue_count,
    replace=False,
)

for index in text_issue_indices:
    category = TRANSACTIONS_DF.loc[
        index,
        "merchant_category",
    ]

    if pd.notna(category):
        TRANSACTIONS_DF.loc[
            index,
            "merchant_category",
        ] = f" {category} "

print(
    f"Text inconsistencies added: {text_issue_count:,}"
)

# ------------------------------------------------------------
# 3. Small number of plausible amount outliers
# ------------------------------------------------------------

outlier_count = max(
    1,
    int(N_TRANSACTIONS * 0.0005),
)

outlier_indices = quality_rng.choice(
    N_TRANSACTIONS,
    size=outlier_count,
    replace=False,
)

TRANSACTIONS_DF.loc[
    outlier_indices,
    "amount",
] = np.round(
    TRANSACTIONS_DF.loc[
        outlier_indices,
        "amount",
    ]
    * quality_rng.uniform(2.0, 4.0, outlier_count),
    2,
)

print(
    f"Amount outliers added: {outlier_count:,}"
)


# ============================================================
# SYNCHRONIZE FINAL TRANSACTION ATTRIBUTES
# ============================================================

# Update the transaction DataFrame with the final generated
# values after all behavioral adjustments.

TRANSACTIONS_DF["amount"] = AMOUNTS
TRANSACTIONS_DF["payment_method"] = PAYMENT_METHOD_ASSIGNMENTS
TRANSACTIONS_DF["platform"] = PLATFORM_ASSIGNMENTS
TRANSACTIONS_DF["device_type"] = DEVICE_TYPES
TRANSACTIONS_DF["transaction_datetime"] = TRANSACTION_DATETIME

TRANSACTIONS_DF["refund_status"] = REFUND_STATUS_ASSIGNMENTS
TRANSACTIONS_DF["refund_amount"] = REFUND_AMOUNTS

# Recalculate refund timestamps using the final transaction timestamps.
# Refunds must occur after the transaction and remain within the
# overall project period.

REFUND_DATETIMES = np.full(
    N_TRANSACTIONS,
    np.datetime64("NaT"),
    dtype="datetime64[ns]"
)

final_transaction_times = pd.to_datetime(
    TRANSACTION_DATETIME[refund_indices]
)

remaining_seconds = (
    END_DATE - final_transaction_times
).total_seconds().astype(np.int64)

# Target a realistic refund delay of up to 30 days.
max_delay_seconds = np.minimum(
    remaining_seconds,
    30 * 24 * 60 * 60
)

# Use at least 1 hour when enough time remains.
# For transactions near the project end, use the available
# remaining time while still keeping the refund timestamp later.
min_delay_seconds = np.where(
    max_delay_seconds >= 3600,
    3600,
    1
)

refund_delay_seconds = np.array([
    rng.integers(
        int(minimum),
        int(maximum) + 1
    )
    for minimum, maximum in zip(
        min_delay_seconds,
        max_delay_seconds
    )
])

refund_delay = pd.to_timedelta(
    refund_delay_seconds,
    unit="s"
)

REFUND_DATETIMES[refund_indices] = (
    final_transaction_times + refund_delay
).to_numpy(dtype="datetime64[ns]")

print(
    "Refund timestamps synchronized with final transaction timestamps."
)

TRANSACTIONS_DF["refund_datetime"] = REFUND_DATETIMES

TRANSACTIONS_DF["processing_time_seconds"] = (
    PROCESSING_TIME_SECONDS
)

print(
    "Final transaction attributes synchronized."
)


# ============================================================
# FINAL CUSTOMER TYPE RECALCULATION
# ============================================================

# Recalculate New vs Returning using the final transaction
# timestamps after all date-generation adjustments.

TRANSACTIONS_DF = TRANSACTIONS_DF.sort_values(
    by=["customer_id", "transaction_datetime"]
).reset_index(drop=True)

TRANSACTIONS_DF["customer_type"] = np.where(
    TRANSACTIONS_DF.groupby("customer_id").cumcount() == 0,
    "New",
    "Returning",
)

print("\nFinal customer type distribution:")
print(
    TRANSACTIONS_DF["customer_type"]
    .value_counts()
)

print(
    "\nFinal unique customers:"
    f" {TRANSACTIONS_DF['customer_id'].nunique():,}"
)


# ============================================================
# CONTROLLED DUPLICATE ROWS
# ============================================================

duplicate_rate = 0.0008  # 0.08%

duplicate_count = int(
    N_TRANSACTIONS * duplicate_rate
)

duplicate_indices = quality_rng.choice(
    len(TRANSACTIONS_DF),
    size=duplicate_count,
    replace=False,
)

duplicate_rows = TRANSACTIONS_DF.iloc[
    duplicate_indices
].copy()

TRANSACTIONS_DF = pd.concat(
    [
        TRANSACTIONS_DF,
        duplicate_rows,
    ],
    ignore_index=True,
)

print(
    f"Controlled duplicate rows added:"
    f" {duplicate_count:,}"
)

print(
    f"Raw dataset rows after duplicates:"
    f" {len(TRANSACTIONS_DF):,}"
)


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

FINAL_COLUMNS = [
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
    "processing_time_seconds",
]

TRANSACTIONS_DF = TRANSACTIONS_DF[
    FINAL_COLUMNS
]

print("\nFinal column order:")
print(
    TRANSACTIONS_DF.columns.tolist()
)


# ============================================================
# FINAL DATA TYPES
# ============================================================

TRANSACTIONS_DF["transaction_id"] = (
    TRANSACTIONS_DF["transaction_id"].astype(str)
)

TRANSACTIONS_DF["customer_id"] = (
    TRANSACTIONS_DF["customer_id"].astype(str)
)

TRANSACTIONS_DF["merchant_id"] = (
    TRANSACTIONS_DF["merchant_id"].astype(str)
)

TRANSACTIONS_DF["transaction_datetime"] = pd.to_datetime(
    TRANSACTIONS_DF["transaction_datetime"]
)

TRANSACTIONS_DF["refund_datetime"] = pd.to_datetime(
    TRANSACTIONS_DF["refund_datetime"]
)

TRANSACTIONS_DF["amount"] = pd.to_numeric(
    TRANSACTIONS_DF["amount"],
    errors="coerce",
).round(2)

TRANSACTIONS_DF["refund_amount"] = pd.to_numeric(
    TRANSACTIONS_DF["refund_amount"],
    errors="coerce",
).round(2)

TRANSACTIONS_DF["processing_time_seconds"] = pd.to_numeric(
    TRANSACTIONS_DF["processing_time_seconds"],
    errors="coerce",
).round(2)

print("\nFinal data types prepared.")
print(TRANSACTIONS_DF.dtypes)


# ============================================================
# FINAL REFUND BUSINESS-RULE SAFEGUARD
# ============================================================

# Failed and Pending transactions cannot have refunds.
no_refund_mask = TRANSACTIONS_DF["transaction_status"].isin(
    ["Failed", "Pending"]
)

TRANSACTIONS_DF.loc[no_refund_mask, "refund_status"] = "No Refund"
TRANSACTIONS_DF.loc[no_refund_mask, "refund_amount"] = 0.00
TRANSACTIONS_DF.loc[no_refund_mask, "refund_datetime"] = pd.NaT

print(
    "Final refund safeguard applied to "
    f"{no_refund_mask.sum():,} Failed/Pending transactions."
)


# ============================================================
# FINAL RAW-DATA VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("FINAL RAW-DATA VALIDATION")
print("=" * 60)

# Basic structure
print(f"Rows              : {len(TRANSACTIONS_DF):,}")
print(f"Columns           : {len(TRANSACTIONS_DF.columns)}")
print(
    f"Unique IDs        : "
    f"{TRANSACTIONS_DF['transaction_id'].nunique():,}"
)

# Critical value checks
positive_amounts = (
    TRANSACTIONS_DF["amount"].dropna() > 0
).all()

valid_statuses = (
    TRANSACTIONS_DF["transaction_status"]
    .isin(STATUSES)
).all()

valid_payment_methods = (
    TRANSACTIONS_DF["payment_method"]
    .isin(PAYMENT_METHODS)
).all()

valid_platforms = (
    TRANSACTIONS_DF["platform"]
    .isin(PLATFORMS)
).all()

refund_amount_valid = (
    TRANSACTIONS_DF["refund_amount"].fillna(0)
    <= TRANSACTIONS_DF["amount"]
).all()

# Failed transactions must have a failure reason.
failed_reason_valid = (
    TRANSACTIONS_DF.loc[
        TRANSACTIONS_DF["transaction_status"] == "Failed",
        "failure_reason",
    ]
    .notna()
    .all()
)

# Successful/Pending transactions must not have a failure reason.
non_failed_reason_valid = (
    TRANSACTIONS_DF.loc[
        TRANSACTIONS_DF["transaction_status"].isin(
            ["Successful", "Pending"]
        ),
        "failure_reason",
    ]
    .isna()
    .all()
)

# Failed/Pending transactions cannot have refunds.
failed_pending_no_refund = (
    TRANSACTIONS_DF.loc[
        TRANSACTIONS_DF["transaction_status"].isin(
            ["Failed", "Pending"]
        ),
        "refund_status",
    ]
    .eq("No Refund")
    .all()
)

# Refund timestamps must exist only when a refund exists.
refund_datetime_valid = (
    TRANSACTIONS_DF.loc[
        TRANSACTIONS_DF["refund_status"] == "No Refund",
        "refund_datetime",
    ]
    .isna()
    .all()
)

print(f"Positive amounts              : {positive_amounts}")
print(f"Valid transaction statuses    : {valid_statuses}")
print(f"Valid payment methods         : {valid_payment_methods}")
print(f"Valid platforms               : {valid_platforms}")
print(f"Refund amount <= amount       : {refund_amount_valid}")
print(f"Failed rows have reason       : {failed_reason_valid}")
print(
    f"Successful/Pending reason NULL: "
    f"{non_failed_reason_valid}"
)
print(
    f"Failed/Pending have no refund : "
    f"{failed_pending_no_refund}"
)
print(
    f"No-refund datetime is NULL    : "
    f"{refund_datetime_valid}"
)


# ============================================================
# SAVE RAW DATASET
# ============================================================

TRANSACTIONS_DF.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\n" + "=" * 60)
print("VEYRAPAY RAW DATASET GENERATED")
print("=" * 60)

print(f"Output file : {OUTPUT_FILE}")
print(f"Rows        : {len(TRANSACTIONS_DF):,}")
print(f"Columns     : {len(TRANSACTIONS_DF.columns)}")
print(
    f"File size   : "
    f"{OUTPUT_FILE.stat().st_size / (1024 * 1024):.2f} MB"
)

print("\nDataset generation completed successfully.")


# ============================================================
# DISTRIBUTION AUDIT
# ============================================================

print("\n" + "=" * 60)
print("DISTRIBUTION AUDIT")
print("=" * 60)

# ------------------------------------------------------------
# PAYMENT METHOD DISTRIBUTION
# ------------------------------------------------------------

print("\nPayment Method Distribution (%):")
print(
    (TRANSACTIONS_DF["payment_method"].value_counts(normalize=True) * 100)
    .round(2)
)

# ------------------------------------------------------------
# TRANSACTION STATUS DISTRIBUTION
# ------------------------------------------------------------

print("\nTransaction Status Distribution (%):")
print(
    (TRANSACTIONS_DF["transaction_status"].value_counts(normalize=True) * 100)
    .round(2)
)

# ------------------------------------------------------------
# PLATFORM DISTRIBUTION
# ------------------------------------------------------------

print("\nPlatform Distribution (%):")
print(
    (TRANSACTIONS_DF["platform"].value_counts(normalize=True) * 100)
    .round(2)
)

# ------------------------------------------------------------
# REFUND DISTRIBUTION
# ------------------------------------------------------------

print("\nRefund Status Distribution (%):")
print(
    (TRANSACTIONS_DF["refund_status"].value_counts(normalize=True) * 100)
    .round(2)
)

# ------------------------------------------------------------
# CUSTOMER TRANSACTION FREQUENCY
# ------------------------------------------------------------

customer_transaction_counts = (
    TRANSACTIONS_DF
    .drop_duplicates("transaction_id")
    .groupby("customer_id")
    .size()
)

frequency_bands = pd.cut(
    customer_transaction_counts,
    bins=[0, 2, 5, 12, 30, float("inf")],
    labels=["1-2", "3-5", "6-12", "13-30", "30+"],
)

print("\nCustomer Transaction Frequency:")
print(
    frequency_bands.value_counts(normalize=True)
    .sort_index()
    .mul(100)
    .round(2)
)

# ------------------------------------------------------------
# AMOUNT BANDS
# ------------------------------------------------------------

amount_bands = pd.cut(
    TRANSACTIONS_DF["amount"],
    bins=[0, 500, 1500, 5000, 15000, float("inf")],
    labels=[
        "₹50-₹500",
        "₹500-₹1,500",
        "₹1,500-₹5,000",
        "₹5,000-₹15,000",
        "₹15,000+",
    ],
    include_lowest=True,
)

print("\nTransaction Amount Distribution:")
print(
    amount_bands.value_counts(normalize=True)
    .sort_index()
    .mul(100)
    .round(2)
)

# ------------------------------------------------------------
# DATE COVERAGE
# ------------------------------------------------------------

print("\nDate Coverage:")
print(
    f"Minimum : "
    f"{TRANSACTIONS_DF['transaction_datetime'].min()}"
)

print(
    f"Maximum : "
    f"{TRANSACTIONS_DF['transaction_datetime'].max()}"
)

print(
    f"Months  : "
    f"{TRANSACTIONS_DF['transaction_datetime'].dt.to_period('M').nunique()}"
)

# ------------------------------------------------------------
# DUPLICATES
# ------------------------------------------------------------

duplicate_rows = TRANSACTIONS_DF.duplicated().sum()

duplicate_transaction_ids = (
    TRANSACTIONS_DF["transaction_id"].duplicated().sum()
)

print("\nDuplicate Audit:")
print(f"Exact duplicate rows     : {duplicate_rows:,}")
print(f"Duplicate transaction IDs: {duplicate_transaction_ids:,}")

# ------------------------------------------------------------
# MISSING VALUES
# ------------------------------------------------------------

print("\nMissing Values:")
print(
    TRANSACTIONS_DF.isna()
    .sum()
    .sort_values(ascending=False)
    .loc[lambda x: x > 0]
)

print("\nDistribution audit completed.")