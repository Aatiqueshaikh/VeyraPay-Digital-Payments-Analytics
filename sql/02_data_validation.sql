-- ============================================================
-- VeyraPay — Data Validation
-- File: 02_data_validation.sql
-- Purpose: Validate the integrity and completeness of the
--          VeyraPay MySQL data model.
-- ============================================================


-- ============================================================
-- 1. FACT TABLE ROW COUNT & UNIQUE TRANSACTIONS
-- ============================================================

SELECT
    COUNT(*) AS fact_transaction_rows,
    COUNT(DISTINCT transaction_id) AS unique_transaction_ids
FROM veyrapay_analytics.fact_transactions;


-- ============================================================
-- 2. FACT TABLE NULL CHECKS FOR REQUIRED COLUMNS
-- ============================================================

SELECT
    COUNT(*) AS total_rows,
    SUM(transaction_id IS NULL) AS null_transaction_ids,
    SUM(transaction_datetime IS NULL) AS null_transaction_datetimes,
    SUM(date_key IS NULL) AS null_date_keys,
    SUM(customer_key IS NULL) AS null_customer_keys,
    SUM(merchant_key IS NULL) AS null_merchant_keys,
    SUM(payment_method_key IS NULL) AS null_payment_method_keys,
    SUM(geography_key IS NULL) AS null_geography_keys,
    SUM(amount IS NULL) AS null_amounts,
    SUM(customer_type IS NULL) AS null_customer_types,
    SUM(transaction_status IS NULL) AS null_transaction_statuses,
    SUM(platform IS NULL) AS null_platforms,
    SUM(device_type IS NULL) AS null_device_types,
    SUM(refund_status IS NULL) AS null_refund_statuses,
    SUM(refund_amount IS NULL) AS null_refund_amounts,
    SUM(processing_time_seconds IS NULL) AS null_processing_times
FROM veyrapay_analytics.fact_transactions;


-- ============================================================
-- 3. DUPLICATE TRANSACTION ID VALIDATION
-- ============================================================

SELECT
    COUNT(*) AS duplicate_transaction_id_groups
FROM (
    SELECT
        transaction_id
    FROM veyrapay_analytics.fact_transactions
    GROUP BY transaction_id
    HAVING COUNT(*) > 1
) AS duplicates;


-- ============================================================
-- 4. TRANSACTION AMOUNT VALIDATION
-- ============================================================

SELECT
    COUNT(*) AS invalid_amount_rows
FROM veyrapay_analytics.fact_transactions
WHERE amount <= 0;


-- ============================================================
-- 5. TRANSACTION STATUS & FAILURE-REASON VALIDATION
-- ============================================================

SELECT
    COUNT(*) AS invalid_status_reason_rows
FROM veyrapay_analytics.fact_transactions
WHERE
    (transaction_status = 'Failed' AND failure_reason IS NULL)
    OR
    (transaction_status IN ('Successful', 'Pending') AND failure_reason IS NOT NULL);


-- ============================================================
-- 6. REFUND VALIDATION
-- ============================================================

SELECT
    COUNT(*) AS invalid_refund_rows
FROM veyrapay_analytics.fact_transactions
WHERE
    (refund_status = 'No Refund'
        AND (refund_amount <> 0 OR refund_datetime IS NOT NULL))
    OR
    (refund_status IN ('Partial Refund', 'Full Refund')
        AND (refund_amount <= 0 OR refund_datetime IS NULL))
    OR
    (refund_amount > amount)
    OR
    (refund_datetime <= transaction_datetime);


-- ============================================================
-- 7. DIMENSION-KEY INTEGRITY VALIDATION
-- ============================================================

SELECT
    COUNT(*) AS invalid_dimension_key_rows
FROM veyrapay_analytics.fact_transactions ft
LEFT JOIN veyrapay_analytics.dim_customer dc
    ON ft.customer_key = dc.customer_key
LEFT JOIN veyrapay_analytics.dim_merchant dm
    ON ft.merchant_key = dm.merchant_key
LEFT JOIN veyrapay_analytics.dim_payment_method dpm
    ON ft.payment_method_key = dpm.payment_method_key
LEFT JOIN veyrapay_analytics.dim_geography dg
    ON ft.geography_key = dg.geography_key
LEFT JOIN veyrapay_analytics.dim_date dd
    ON ft.date_key = dd.date_key
WHERE
    dc.customer_key IS NULL
    OR dm.merchant_key IS NULL
    OR dpm.payment_method_key IS NULL
    OR dg.geography_key IS NULL
    OR dd.date_key IS NULL;


-- ============================================================
-- 8. DATE-KEY & TRANSACTION-DATE VALIDATION
-- ============================================================

SELECT
    COUNT(*) AS invalid_date_rows
FROM veyrapay_analytics.fact_transactions ft
LEFT JOIN veyrapay_analytics.dim_date dd
    ON ft.date_key = dd.date_key
WHERE
    dd.date_key IS NULL
    OR DATE(ft.transaction_datetime) <> dd.date;