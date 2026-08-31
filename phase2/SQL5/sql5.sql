-- ============================================================
-- LAB SQL5 — CREATE ML FEATURE TABLE
-- ============================================================




-- ============================================================
-- 1. DROP EXISTING ML FEATURE TABLE
-- ============================================================

DROP TABLE IF EXISTS customer_ml_features;


-- ============================================================
-- 2. CREATE CUSTOMER ML FEATURE TABLE
-- ============================================================

CREATE TABLE customer_ml_features (

    -- ========================================================
    -- Customer information
    -- ========================================================

    customer_id VARCHAR(50) PRIMARY KEY,

    gender VARCHAR(20),

    senior_citizen INT,

    partner INT,

    dependents INT,


    -- ========================================================
    -- Original numeric features
    -- ========================================================

    tenure INT,

    monthly_charges FLOAT,

    total_charges FLOAT,

    churn INT,


    -- ========================================================
    -- Service features
    -- ========================================================

    phone_service INT,

    multiple_lines VARCHAR(50),

    internet_service VARCHAR(50),

    online_security INT,

    online_backup INT,

    device_protection INT,

    tech_support INT,

    streaming_tv INT,

    streaming_movies INT,


    -- ========================================================
    -- Other original features
    -- ========================================================

    contract VARCHAR(50),

    paperless_billing INT,

    payment_method VARCHAR(100),


    -- ========================================================
    -- Engineered features
    -- ========================================================

    tenure_bucket VARCHAR(20),

    high_charge_flag INT,

    service_count INT,

    is_long_term_customer INT,

    has_streaming_bundle INT,

    auto_pay_flag INT

);


-- ============================================================
-- 3. POPULATE CUSTOMER ML FEATURE TABLE
-- ============================================================

INSERT INTO customer_ml_features (

    customer_id,
    gender,
    senior_citizen,
    partner,
    dependents,

    tenure,
    monthly_charges,
    total_charges,
    churn,

    phone_service,
    multiple_lines,
    internet_service,

    online_security,
    online_backup,
    device_protection,
    tech_support,
    streaming_tv,
    streaming_movies,

    contract,
    paperless_billing,
    payment_method,

    tenure_bucket,
    high_charge_flag,
    service_count,
    is_long_term_customer,
    has_streaming_bundle,
    auto_pay_flag
)

SELECT

    -- ========================================================
    -- CUSTOMER INFORMATION
    -- ========================================================

    c.customer_id,

    c.gender,

    c.senior_citizen,

    c.partner,

    c.dependents,


    -- ========================================================
    -- ORIGINAL NUMERIC FEATURES
    -- ========================================================

    fca.tenure,

    fca.monthly_charges,

    -- Convert the 11 NULL total charges to 0
    COALESCE(fca.total_charges, 0) AS total_charges,

    fca.churn,


    -- ========================================================
    -- PHONE SERVICE
    --
    -- Yes = 1
    -- No  = 0
    -- ========================================================

    CASE
        WHEN LOWER(s.PhoneService) = 'yes' THEN 1
        ELSE 0
    END AS phone_service,


    -- ========================================================
    -- MULTIPLE LINES
    -- ========================================================

    s.MultipleLines AS multiple_lines,


    -- ========================================================
    -- INTERNET SERVICE
    -- ========================================================

    s.InternetService AS internet_service,


    -- ========================================================
    -- ONLINE SECURITY
    -- Yes = 1
    -- No / No internet service = 0
    -- ========================================================

    CASE
        WHEN LOWER(s.OnlineSecurity) = 'yes' THEN 1
        ELSE 0
    END AS online_security,


    -- ========================================================
    -- ONLINE BACKUP
    -- ========================================================

    CASE
        WHEN LOWER(s.OnlineBackup) = 'yes' THEN 1
        ELSE 0
    END AS online_backup,


    -- ========================================================
    -- DEVICE PROTECTION
    -- ========================================================

    CASE
        WHEN LOWER(s.DeviceProtection) = 'yes' THEN 1
        ELSE 0
    END AS device_protection,


    -- ========================================================
    -- TECH SUPPORT
    -- ========================================================

    CASE
        WHEN LOWER(s.TechSupport) = 'yes' THEN 1
        ELSE 0
    END AS tech_support,


    -- ========================================================
    -- STREAMING TV
    -- ========================================================

    CASE
        WHEN LOWER(s.StreamingTV) = 'yes' THEN 1
        ELSE 0
    END AS streaming_tv,


    -- ========================================================
    -- STREAMING MOVIES
    -- ========================================================

    CASE
        WHEN LOWER(s.StreamingMovies) = 'yes' THEN 1
        ELSE 0
    END AS streaming_movies,


    -- ========================================================
    -- CONTRACT
    -- ========================================================

    dc.contract_name AS contract,


    -- ========================================================
    -- PAPERLESS BILLING
    --
    -- Yes = 1
    -- No  = 0
    -- ========================================================

    CASE
        WHEN LOWER(s.PaperlessBilling) = 'yes' THEN 1
        ELSE 0
    END AS paperless_billing,


    -- ========================================================
    -- PAYMENT METHOD
    -- ========================================================

    dp.payment_method,


    -- ========================================================
    -- FEATURE 1 — TENURE BUCKET
    --
    -- CP4 bins:
    -- [0, 12, 24, 48, 72]
    -- ========================================================

    CASE
        WHEN fca.tenure <= 12 THEN '0-12'
        WHEN fca.tenure <= 24 THEN '12-24'
        WHEN fca.tenure <= 48 THEN '24-48'
        WHEN fca.tenure <= 72 THEN '48-72'
        ELSE '48-72'
    END AS tenure_bucket,


    -- ========================================================
    -- FEATURE 2 — HIGH CHARGE FLAG
    --
    -- SQL5 specification:
    -- monthly_charges > average monthly charges
    --
    -- 1 = above average
    -- 0 = average or below average
    -- ========================================================

    CASE
        WHEN fca.monthly_charges > (
            SELECT AVG(monthly_charges)
            FROM fact_customer_account
        )
        THEN 1
        ELSE 0
    END AS high_charge_flag,


    -- ========================================================
    -- FEATURE 3 — SERVICE COUNT
    --
    -- Count the six service columns that equal 1
    --
    -- 1. online_security
    -- 2. online_backup
    -- 3. device_protection
    -- 4. tech_support
    -- 5. streaming_tv
    -- 6. streaming_movies
    -- ========================================================

    (
        CASE
            WHEN LOWER(s.OnlineSecurity) = 'yes' THEN 1
            ELSE 0
        END

        +

        CASE
            WHEN LOWER(s.OnlineBackup) = 'yes' THEN 1
            ELSE 0
        END

        +

        CASE
            WHEN LOWER(s.DeviceProtection) = 'yes' THEN 1
            ELSE 0
        END

        +

        CASE
            WHEN LOWER(s.TechSupport) = 'yes' THEN 1
            ELSE 0
        END

        +

        CASE
            WHEN LOWER(s.StreamingTV) = 'yes' THEN 1
            ELSE 0
        END

        +

        CASE
            WHEN LOWER(s.StreamingMovies) = 'yes' THEN 1
            ELSE 0
        END

    ) AS service_count,


    -- ========================================================
    -- FEATURE 4 — LONG-TERM CUSTOMER
    --
    -- tenure >= 24 → 1
    -- tenure < 24  → 0
    -- ========================================================

    CASE
        WHEN fca.tenure >= 24 THEN 1
        ELSE 0
    END AS is_long_term_customer,


    -- ========================================================
    -- FEATURE 5 — STREAMING BUNDLE
    --
    -- Both StreamingTV AND StreamingMovies must be Yes
    -- ========================================================

    CASE
        WHEN LOWER(s.StreamingTV) = 'yes'
         AND LOWER(s.StreamingMovies) = 'yes'
        THEN 1
        ELSE 0
    END AS has_streaming_bundle,


    -- ========================================================
    -- FEATURE 6 — AUTO PAY FLAG
    --
    -- Payment method contains "automatic"
    -- ========================================================

    CASE
        WHEN LOWER(dp.payment_method) LIKE '%automatic%'
        THEN 1
        ELSE 0
    END AS auto_pay_flag


-- ============================================================
-- SOURCE TABLES
-- ============================================================

FROM fact_customer_account AS fca

JOIN customers AS c
    ON fca.customer_id = c.customer_id

JOIN dim_contract AS dc
    ON fca.contract_id = dc.contract_id

JOIN dim_payment AS dp
    ON fca.payment_id = dp.payment_id

JOIN stg_customer_raw AS s
    ON fca.customer_id = s.customerID;


-- ============================================================
-- 4. VERIFY ROW COUNT
-- ============================================================

SELECT
    COUNT(*) AS total_rows
FROM customer_ml_features;

-- Expected:
-- 7043


-- ============================================================
-- 5. VERIFY NULL MONTHLY CHARGES
-- ============================================================

SELECT
    COUNT(*) AS null_monthly_charges
FROM customer_ml_features
WHERE monthly_charges IS NULL;

-- Expected:
-- 0


-- ============================================================
-- 6. VERIFY NULL TOTAL CHARGES
-- ============================================================

SELECT
    COUNT(*) AS null_total_charges
FROM customer_ml_features
WHERE total_charges IS NULL;

-- Expected:
-- 0


-- ============================================================
-- 7. FINAL NULL CHECK
-- ============================================================

SELECT
    COUNT(*) AS invalid_rows
FROM customer_ml_features
WHERE customer_id IS NULL
   OR tenure IS NULL
   OR monthly_charges IS NULL
   OR total_charges IS NULL
   OR churn IS NULL;

-- Expected:
-- 0


-- ============================================================
-- 8. CHURN CLASS DISTRIBUTION
-- ============================================================

SELECT
    churn,
    COUNT(*) AS customer_count
FROM customer_ml_features
GROUP BY churn
ORDER BY churn;


-- ============================================================
-- 9. CHECK TENURE BUCKET
-- ============================================================

SELECT
    tenure_bucket,
    COUNT(*) AS customer_count
FROM customer_ml_features
GROUP BY tenure_bucket
ORDER BY tenure_bucket;


-- ============================================================
-- 10. CHECK HIGH CHARGE FLAG
-- ============================================================

SELECT
    high_charge_flag,
    COUNT(*) AS customer_count
FROM customer_ml_features
GROUP BY high_charge_flag
ORDER BY high_charge_flag;


-- ============================================================
-- 11. CHECK SERVICE COUNT
-- ============================================================

SELECT
    service_count,
    COUNT(*) AS customer_count
FROM customer_ml_features
GROUP BY service_count
ORDER BY service_count;


-- ============================================================
-- 12. CHECK LONG-TERM CUSTOMER FLAG
-- ============================================================

SELECT
    is_long_term_customer,
    COUNT(*) AS customer_count
FROM customer_ml_features
GROUP BY is_long_term_customer
ORDER BY is_long_term_customer;


-- ============================================================
-- 13. CHECK STREAMING BUNDLE
-- ============================================================

SELECT
    has_streaming_bundle,
    COUNT(*) AS customer_count
FROM customer_ml_features
GROUP BY has_streaming_bundle
ORDER BY has_streaming_bundle;


-- ============================================================
-- 14. CHECK AUTO PAY FLAG
-- ============================================================

SELECT
    auto_pay_flag,
    COUNT(*) AS customer_count
FROM customer_ml_features
GROUP BY auto_pay_flag
ORDER BY auto_pay_flag;


-- ============================================================
-- 15. FINAL TABLE CHECK
-- ============================================================

SELECT *
FROM customer_ml_features
LIMIT 10;