-- ============================================================
-- LAB SQL6 — CREATE RULE-BASED HIGH-RISK VIEW
-- ============================================================

USE custchurn;


-- ============================================================
-- 83. BUSINESS RULE
-- ============================================================

-- A customer is considered HIGH RISK when:
--
-- 1. Contract is Month-to-month
-- 2. Tenure is less than 12 months
-- 3. Monthly charges are greater than the dataset average
--
-- ============================================================


-- ============================================================
-- 84. TEST THE SELECT QUERY FIRST
-- ============================================================

SELECT
    customer_id,
    tenure,
    monthly_charges,
    contract,

    CASE
        WHEN contract = 'Month-to-month'
         AND tenure < 12
         AND monthly_charges > (
             SELECT AVG(monthly_charges)
             FROM customer_ml_features
         )
        THEN 'Month-to-month + low tenure + above-average charges'
    END AS risk_reason

FROM customer_ml_features

WHERE contract = 'Month-to-month'
  AND tenure < 12
  AND monthly_charges > (
      SELECT AVG(monthly_charges)
      FROM customer_ml_features
  )

ORDER BY monthly_charges DESC;


-- ============================================================
-- 85. VERIFY COUNT
-- ============================================================

SELECT
    COUNT(*) AS high_risk_customer_count
FROM customer_ml_features

WHERE contract = 'Month-to-month'
  AND tenure < 12
  AND monthly_charges > (
      SELECT AVG(monthly_charges)
      FROM customer_ml_features
  );


-- ============================================================
-- 86. CREATE VIEW
-- ============================================================

DROP VIEW IF EXISTS v_high_risk_customers;


CREATE VIEW v_high_risk_customers AS

SELECT
    customer_id,
    tenure,
    monthly_charges,
    total_charges,
    contract,
    payment_method,
    churn,

    CASE
        WHEN contract = 'Month-to-month'
         AND tenure < 12
         AND monthly_charges > (
             SELECT AVG(monthly_charges)
             FROM customer_ml_features
         )
        THEN 'Month-to-month + low tenure + above-average charges'
    END AS risk_reason

FROM customer_ml_features

WHERE contract = 'Month-to-month'
  AND tenure < 12
  AND monthly_charges > (
      SELECT AVG(monthly_charges)
      FROM customer_ml_features
  );


-- ============================================================
-- 87. QUERY THE VIEW
-- ============================================================

SELECT *
FROM v_high_risk_customers
LIMIT 10;


-- ============================================================
-- 88. COUNT HIGH-RISK CUSTOMERS
-- ============================================================

SELECT
    COUNT(*) AS high_risk_customer_count
FROM v_high_risk_customers;


-- ============================================================
-- HIGH-RISK CUSTOMER PERCENTAGE
-- ============================================================

SELECT
    COUNT(*) AS high_risk_customer_count,

    (
        COUNT(*) * 100.0
        /
        (SELECT COUNT(*) FROM customer_ml_features)
    ) AS high_risk_percentage

FROM v_high_risk_customers;


-- ============================================================
-- ALTERNATIVE: COUNT + PERCENTAGE IN ONE QUERY
-- ============================================================

SELECT
    COUNT(*) AS high_risk_customer_count,

    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM customer_ml_features),
        2
    ) AS high_risk_percentage

FROM v_high_risk_customers;





/* 89. Rule-based vs ML-based
Rule-based risk scoring is simple, transparent, and easy to 
implement, but it can only identify customers who satisfy 
predefined conditions. ML-based scoring can learn complex 
relationships between many customer features and identify 
patterns that may not be obvious when manually defining rules. However, ML models require training data, validation, monitoring, and are generally more complex to explain and maintain.
*/


