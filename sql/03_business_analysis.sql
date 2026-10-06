-- ============================================================
-- VeyraPay — Business Analysis
-- File: 03_business_analysis.sql
-- Purpose: Analyze transaction performance and business trends.
-- ============================================================


-- ============================================================
-- 1. MONTHLY TRANSACTION TREND
-- ============================================================

SELECT
    YEAR(transaction_datetime) AS year,
    MONTH(transaction_datetime) AS month,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS transaction_value
FROM veyrapay_analytics.fact_transactions
GROUP BY
    YEAR(transaction_datetime),
    MONTH(transaction_datetime)
ORDER BY
    year,
    month;


-- ============================================================
-- 2. PAYMENT METHOD PERFORMANCE
-- ============================================================

SELECT
    dpm.payment_method,
    COUNT(*) AS transaction_count,
    ROUND(SUM(ft.amount), 2) AS transaction_value,
    ROUND(
        100.0 * SUM(ft.transaction_status = 'Successful') / COUNT(*),
        2
    ) AS success_rate
FROM veyrapay_analytics.fact_transactions ft
JOIN veyrapay_analytics.dim_payment_method dpm
    ON ft.payment_method_key = dpm.payment_method_key
GROUP BY
    dpm.payment_method
ORDER BY
    transaction_value DESC;


-- ============================================================
-- 3. TRANSACTION STATUS DISTRIBUTION
-- ============================================================

SELECT
    transaction_status,
    COUNT(*) AS transaction_count,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS transaction_share,
    ROUND(SUM(amount), 2) AS transaction_value
FROM veyrapay_analytics.fact_transactions
GROUP BY
    transaction_status
ORDER BY
    transaction_count DESC;


-- ============================================================
-- 4. FAILURE REASON ANALYSIS
-- ============================================================

SELECT
    failure_reason,
    COUNT(*) AS failed_transaction_count,
    ROUND(SUM(amount), 2) AS failed_transaction_value,
    ROUND(
        100.0 * COUNT(*) /
        (SELECT COUNT(*)
         FROM veyrapay_analytics.fact_transactions
         WHERE transaction_status = 'Failed'),
        2
    ) AS failure_share
FROM veyrapay_analytics.fact_transactions
WHERE transaction_status = 'Failed'
GROUP BY
    failure_reason
ORDER BY
    failed_transaction_count DESC;


-- ============================================================
-- 5. CUSTOMER TYPE ANALYSIS
-- ============================================================

SELECT
    customer_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS transaction_value,
    COUNT(DISTINCT customer_key) AS unique_customers,
    ROUND(
        100.0 * SUM(transaction_status = 'Successful') / COUNT(*),
        2
    ) AS success_rate
FROM veyrapay_analytics.fact_transactions
GROUP BY
    customer_type
ORDER BY
    transaction_count DESC;


-- ============================================================
-- 6. REGIONAL PERFORMANCE
-- ============================================================

SELECT
    dg.region,
    COUNT(*) AS transaction_count,
    ROUND(SUM(ft.amount), 2) AS transaction_value,
    ROUND(
        100.0 * SUM(ft.transaction_status = 'Successful') / COUNT(*),
        2
    ) AS success_rate,
    COUNT(DISTINCT ft.customer_key) AS unique_customers
FROM veyrapay_analytics.fact_transactions ft
JOIN veyrapay_analytics.dim_geography dg
    ON ft.geography_key = dg.geography_key
GROUP BY
    dg.region
ORDER BY
    transaction_value DESC;


-- ============================================================
-- 7. PLATFORM & DEVICE PERFORMANCE
-- ============================================================

SELECT
    platform,
    device_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS transaction_value,
    ROUND(
        100.0 * SUM(transaction_status = 'Successful') / COUNT(*),
        2
    ) AS success_rate
FROM veyrapay_analytics.fact_transactions
GROUP BY
    platform,
    device_type
ORDER BY
    transaction_count DESC;


-- ============================================================
-- 8. REFUND ANALYSIS
-- ============================================================

SELECT
    refund_status,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS transaction_value,
    ROUND(SUM(refund_amount), 2) AS refund_amount,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS transaction_share
FROM veyrapay_analytics.fact_transactions
GROUP BY
    refund_status
ORDER BY
    transaction_count DESC;