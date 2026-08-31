use custchurn;

CREATE TABLE dim_contract (
    contract_id INT AUTO_INCREMENT PRIMARY KEY,
    contract_name VARCHAR(50) UNIQUE NOT NULL
);

select distinct(contract) from stg_customer_raw;

INSERT INTO dim_contract (contract_name)
VALUES
    ('Month-to-month'),
    ('One year'),
    ('Two year');
    
SELECT * FROM dim_contract;


CREATE TABLE dim_payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    payment_method VARCHAR(100) UNIQUE NOT NULL
);

INSERT INTO dim_payment (payment_method)
SELECT DISTINCT PaymentMethod
FROM stg_customer_raw;

SELECT * FROM dim_payment;

CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    gender VARCHAR(20),
    senior_citizen TINYINT,
    partner TINYINT,
    dependents TINYINT
);


INSERT INTO customers (
    customer_id,
    gender,
    senior_citizen,
    partner,
    dependents
)
SELECT
    customerID,
    LOWER(TRIM(gender)),
    CAST(SeniorCitizen AS UNSIGNED),
    CASE
        WHEN Partner = 'Yes' THEN 1
        WHEN Partner = 'No' THEN 0
    END,
    CASE
        WHEN Dependents = 'Yes' THEN 1
        WHEN Dependents = 'No' THEN 0
    END
FROM stg_customer_raw;

SELECT * FROM customers LIMIT 5;

CREATE TABLE fact_customer_account (
    customer_id VARCHAR(50) PRIMARY KEY,
    contract_id INT,
    payment_id INT,
    tenure INT,
    monthly_charges DECIMAL(10,2),
    total_charges DECIMAL(10,2),
    churn TINYINT,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    FOREIGN KEY (contract_id)
        REFERENCES dim_contract(contract_id),

    FOREIGN KEY (payment_id)
        REFERENCES dim_payment(payment_id)
);

INSERT INTO fact_customer_account (
    customer_id,
    contract_id,
    payment_id,
    tenure,
    monthly_charges,
    total_charges,
    churn
)
SELECT
    s.customerID,
    c.contract_id,
    p.payment_id,
    s.tenure,
    s.MonthlyCharges,

    CAST(
        NULLIF(TRIM(s.TotalCharges), '')
        AS DECIMAL(10,2)
    ),

    CASE
        WHEN s.Churn = 'Yes' THEN 1
        WHEN s.Churn = 'No' THEN 0
    END

FROM stg_customer_raw s

JOIN dim_contract c
    ON s.Contract = c.contract_name

JOIN dim_payment p
    ON s.PaymentMethod = p.payment_method;
    
SELECT COUNT(*) FROM stg_customer_raw;


SELECT COUNT(*) FROM customers;


SELECT COUNT(*) FROM fact_customer_account;


SELECT COUNT(*) FROM dim_contract;


SELECT COUNT(*) FROM dim_payment;

SELECT COUNT(*)
FROM dim_payment;



SELECT
    c.customer_id,
    c.gender,
    c.partner,
    f.tenure,
    f.monthly_charges,
    f.total_charges,
    f.churn,
    d.contract_name
FROM customers c

JOIN fact_customer_account f
    ON c.customer_id = f.customer_id

JOIN dim_contract d
    ON f.contract_id = d.contract_id

LIMIT 10;


show tables;

select * from fact_customer_account;

describe fact_customer_account;
