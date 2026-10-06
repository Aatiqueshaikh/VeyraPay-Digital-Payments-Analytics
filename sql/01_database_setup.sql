-- ============================================================
-- VeyraPay — Digital Payments & Transaction Analytics
-- MySQL Database Setup
-- File: 01_database_setup.sql
-- ============================================================

-- Create database
CREATE DATABASE IF NOT EXISTS veyrapay_analytics;

USE veyrapay_analytics;


-- ============================================================
-- 1. Dimension: Date
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,
    date DATE NOT NULL,
    year SMALLINT NOT NULL,
    quarter TINYINT NOT NULL,
    month TINYINT NOT NULL,
    week TINYINT NOT NULL,
    day TINYINT NOT NULL,
    is_weekend BOOLEAN NOT NULL
);


-- ============================================================
-- 2. Dimension: Customer
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL UNIQUE
);


-- ============================================================
-- 3. Dimension: Merchant
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_merchant (
    merchant_key INT AUTO_INCREMENT PRIMARY KEY,
    merchant_id VARCHAR(20) NOT NULL UNIQUE,
    merchant_category VARCHAR(50) NULL
);


-- ============================================================
-- 4. Dimension: Payment Method
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_payment_method (
    payment_method_key TINYINT PRIMARY KEY,
    payment_method VARCHAR(30) NOT NULL UNIQUE
);


-- ============================================================
-- 5. Dimension: Geography
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_geography (
    geography_key INT AUTO_INCREMENT PRIMARY KEY,
    region VARCHAR(30) NOT NULL,
    state VARCHAR(50) NOT NULL,
    city VARCHAR(60) NULL,

    UNIQUE KEY uq_geography (region, state, city)
);


-- ============================================================
-- 6. Fact: Transactions
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id VARCHAR(30) PRIMARY KEY,
    transaction_datetime DATETIME NOT NULL,

    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    merchant_key INT NOT NULL,
    payment_method_key TINYINT NOT NULL,
    geography_key INT NOT NULL,

    amount DECIMAL(12,2) NOT NULL,
    customer_type VARCHAR(15) NOT NULL,
    transaction_status VARCHAR(15) NOT NULL,
    failure_reason VARCHAR(50) NULL,

    platform VARCHAR(15) NOT NULL,
    device_type VARCHAR(15) NOT NULL,

    refund_status VARCHAR(15) NOT NULL,
    refund_amount DECIMAL(12,2) NOT NULL,
    refund_datetime DATETIME NULL,

    processing_time_seconds INT NOT NULL,

    CONSTRAINT fk_transaction_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key),

    CONSTRAINT fk_transaction_customer
        FOREIGN KEY (customer_key)
        REFERENCES dim_customer(customer_key),

    CONSTRAINT fk_transaction_merchant
        FOREIGN KEY (merchant_key)
        REFERENCES dim_merchant(merchant_key),

    CONSTRAINT fk_transaction_payment_method
        FOREIGN KEY (payment_method_key)
        REFERENCES dim_payment_method(payment_method_key),

    CONSTRAINT fk_transaction_geography
        FOREIGN KEY (geography_key)
        REFERENCES dim_geography(geography_key)
);


-- ============================================================
-- Setup complete
-- ============================================================