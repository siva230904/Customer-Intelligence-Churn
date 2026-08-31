create database custchurn;

use custchurn;

CREATE TABLE stg_customer_raw (
    customerID VARCHAR(50),
    gender VARCHAR(20),
    SeniorCitizen INT,
    Partner VARCHAR(20),
    Dependents VARCHAR(20),
    tenure INT,
    PhoneService VARCHAR(20),
    MultipleLines VARCHAR(50),
    InternetService VARCHAR(50),
    OnlineSecurity VARCHAR(50),
    OnlineBackup VARCHAR(50),
    DeviceProtection VARCHAR(50),
    TechSupport VARCHAR(50),
    StreamingTV VARCHAR(50),
    StreamingMovies VARCHAR(50),
    Contract VARCHAR(50),
    PaperlessBilling VARCHAR(20),
    PaymentMethod VARCHAR(100),
    MonthlyCharges DECIMAL(10,2),
    TotalCharges VARCHAR(50),
    Churn VARCHAR(20)
);

describe stg_customer_raw;


select count(*) from stg_customer_raw;

select TotalCharges from stg_customer_raw 
where TotalCharges="" LIMIT 5;

select count(*) from stg_customer_raw
where TotalCharges="";

DESCRIBE stg_customer_raw;

CREATE TABLE ingestion_log (
    ingestion_id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100),
    load_time DATETIME,
    row_count INT
);

INSERT INTO ingestion_log
    (table_name, load_time, row_count)
VALUES
    ('stg_customer_raw', NOW(), 7043);


SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT customerID) AS distinct_customers
FROM stg_customer_raw;
