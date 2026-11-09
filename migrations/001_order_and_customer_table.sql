CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(50),
    address VARCHAR (200),
    status INT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    status INT NOT NULL,
    carrier VARCHAR(50),
    eta VARCHAR(50),
    notification_sent INT DEFAULT 0,
    notification_time TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);