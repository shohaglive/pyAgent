CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    carrier TEXT NOT NULL,
    eta TEXT NOT NULL,
    notification_sent INTEGER DEFAULT 0,
    notification_time TIMESTAMP
);

-- PostgreSQL Upsert Syntax (ON CONFLICT)
INSERT INTO orders (order_id, status, carrier, eta, notification_sent)
VALUES ('ORD-1234', 'Shipped', 'DHL', 'Tomorrow', 0)
ON CONFLICT (order_id) DO NOTHING;

INSERT INTO orders (order_id, status, carrier, eta, notification_sent)
VALUES ('ORD-5678', 'Processing', 'FedEx', '3 days', 1)
ON CONFLICT (order_id) DO NOTHING;