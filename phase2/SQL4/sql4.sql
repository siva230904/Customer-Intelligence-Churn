use custchurn;
show tables;
DESCRIBE customers;
DESCRIBE dim_contract;
DESCRIBE dim_payment;
DESCRIBE fact_customer_account;

-- Query 1:
-- Churn rate by contract:
SELECT
    dc.contract_name,
    AVG(fca.churn) * 100 AS churn_rate_percentage
FROM fact_customer_account AS fca
JOIN dim_contract AS dc
    ON fca.contract_id = dc.contract_id
GROUP BY dc.contract_name
ORDER BY churn_rate_percentage DESC;
-- The contract type with the highest churn rate is the contract
-- segment where customers are most likely to leave.

-- Query 2:
-- Churn rate by payment method
SELECT
    dp.payment_method,
    AVG(fca.churn) * 100 AS churn_rate_percentage
FROM fact_customer_account AS fca
JOIN dim_payment AS dp
    ON fca.payment_id = dp.payment_id
GROUP BY dp.payment_method
ORDER BY churn_rate_percentage DESC;
-- The payment method with the highest churn rate identifies the
-- payment segment associated with greater customer churn.

-- Query 3:
-- Average monthly charges by churn status:
SELECT
    churn,
    AVG(monthly_charges) AS avg_monthly_charges
FROM fact_customer_account
GROUP BY churn
ORDER BY churn;
-- Comparing average monthly charges between churned and retained
-- customers shows whether higher monthly charges are associated
-- with churn.

-- Query 4:
-- Top risky segments: customers with month-to-month contract AND 
-- tenure < 12 AND monthly_charges > average — count and list 
SELECT
    fca.customer_id,
    dc.contract_name,
    fca.tenure,
    fca.monthly_charges
FROM fact_customer_account AS fca

JOIN dim_contract AS dc
    ON fca.contract_id = dc.contract_id

WHERE dc.contract_name = 'Month-to-month'
  AND fca.tenure < 12
  AND fca.monthly_charges > (
      SELECT AVG(monthly_charges)
      FROM fact_customer_account
  )
ORDER BY fca.monthly_charges DESC;
-- The identified customers are high-risk because they have a
-- month-to-month contract, less than 12 months of tenure, and
-- above-average monthly charges.


-- Query 5:
-- High-value churned customers: churned customers with 
-- total_charges > 2000 — how many and what is their average 
-- tenure? 
SELECT
    COUNT(*) AS risky_customer_count
FROM fact_customer_account AS fca

JOIN dim_contract AS dc
    ON fca.contract_id = dc.contract_id

WHERE dc.contract_name = 'Month-to-month'
  AND fca.tenure < 12
  AND fca.monthly_charges > (
      SELECT AVG(monthly_charges)
      FROM fact_customer_account
  );
  
-- This identifies high-value customers who have already churned
-- and shows their average tenure.

-- Bonus :
-- For each contract type, what are the average monthly charges, 
-- average tenure, and churn rate?

SELECT
    dc.contract_name,
    AVG(fca.monthly_charges) AS avg_monthly_charges,
    AVG(fca.tenure) AS avg_tenure,
    AVG(fca.churn) * 100 AS churn_rate_percentage
FROM fact_customer_account AS fca

JOIN dim_contract AS dc
    ON fca.contract_id = dc.contract_id

GROUP BY dc.contract_name

ORDER BY churn_rate_percentage DESC;
  
SELECT
    COUNT(*) AS high_value_churned_customers,
    AVG(tenure) AS average_tenure
FROM fact_customer_account
WHERE churn = 1
  AND total_charges > 2000;