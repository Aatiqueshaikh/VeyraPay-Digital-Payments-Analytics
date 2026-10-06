-- ============================================================
-- VeyraPay — KPI Validation
-- File: 04_kpi_validation.sql
-- Purpose: Validate core KPIs used across Python, MySQL and Power BI.
-- ============================================================


-- ============================================================
-- 1. CORE TRANSACTION KPIs
-- ============================================================

SELECT
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_transaction_value,
    ROUND(AVG(amount), 2) AS average_transaction_value,
    SUM(transaction_status = 'Successful') AS successful_transactions,
    ROUND(
        100.0 * SUM(transaction_status = 'Successful') / COUNT(*),
        2
    ) AS success_rate,
    COUNT(DISTINCT customer_key) AS active_customers
FROM veyrapay_analytics.fact_transactions;


-- ============================================================
-- 2. REFUND KPIs
-- ============================================================

SELECT
    SUM(refund_status IN ('Partial Refund', 'Full Refund'))
        AS refund_transactions,
    ROUND(SUM(refund_amount), 2)
        AS total_refund_amount,
    ROUND(
        100.0 * SUM(refund_status IN ('Partial Refund', 'Full Refund'))
        / COUNT(*),
        2
    ) AS refund_rate
FROM veyrapay_analytics.fact_transactions;


-- ============================================================
-- 3. TRANSACTION STATUS RECONCILIATION
-- ============================================================

SELECT
    transaction_status,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS transaction_value,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS transaction_share
FROM veyrapay_analytics.fact_transactions
GROUP BY
    transaction_status
ORDER BY
    transaction_count DESC;


-- ============================================================
-- 4. PAYMENT METHOD RECONCILIATION
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
    transaction_count DESC;


-- ============================================================
-- 5. CUSTOMER TYPE RECONCILIATION
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
-- 6. REGIONAL RECONCILIATION
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
    transaction_count DESC;


-- ============================================================
-- 7. PLATFORM & DEVICE RECONCILIATION
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
-- 8. FAILURE REASON RECONCILIATION
-- ============================================================

SELECT
    failure_reason,
    COUNT(*) AS failed_transaction_count,
    ROUND(SUM(amount), 2) AS failed_transaction_value,
    ROUND(
        100.0 * COUNT(*) /
        (
            SELECT COUNT(*)
            FROM veyrapay_analytics.fact_transactions
            WHERE transaction_status = 'Failed'
        ),
        2
    ) AS failure_share
FROM veyrapay_analytics.fact_transactions
WHERE transaction_status = 'Failed'
GROUP BY
    failure_reason
ORDER BY
    failed_transaction_count DESC;