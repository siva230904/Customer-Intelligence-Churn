use custchurn;

SELECT
    dc.contract_name,
    AVG(fca.churn) AS churn_rate
FROM fact_customer_account AS fca
JOIN dim_contract AS dc
    ON fca.contract_id = dc.contract_id
GROUP BY dc.contract_name
ORDER BY churn_rate DESC;


DESCRIBE ingestion_log;

SELECT COUNT(*)
FROM stg_customer_raw;

select * from ingestion_log;
DESCRIBE customers;
DESCRIBE dim_contract;
DESCRIBE dim_payment;

ALTER TABLE ingestion_log
ADD COLUMN filename VARCHAR(255) AFTER ingestion_id,
ADD COLUMN status VARCHAR(20) AFTER filename,
ADD COLUMN reason VARCHAR(500) AFTER row_count;

DESCRIBE customer_ml_features;

SELECT COUNT(*) FROM cleaned_customers;
SELECT COUNT(*) FROM dim_contract;
SELECT COUNT(*) FROM dim_payment;
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM fact_customer_account;

SELECT *
FROM customer_ml_features
LIMIT 3;