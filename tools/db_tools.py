import json
from db.connection import get_db_connection

# --- 1. Python Execution Functions ---

def get_order_details(order_id: str) -> str:
    """Reads order details and notification state from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Note: PostgreSQL uses %s for parameter substitution
    cursor.execute(
        "SELECT order_id, status, carrier, eta, notification_sent FROM orders WHERE order_id = %s",
        (order_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return json.dumps({
            "order_id": row["order_id"],
            "status": row["status"],
            "carrier": row["carrier"],
            "eta": row["eta"],
            "notification_sent": bool(row["notification_sent"])
        })
    return json.dumps({"error": f"Order {order_id} not found."})

def search_customers(name: str = None, email: str = None, phone: str = None):
    """
    Searches for customers by name, email, or phone.
    Returns a dictionary indicating whether a single match, multiple matches, or no match was found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    result = None

    try:
        if email:
            cursor.execute("SELECT customer_id, name, email, phone FROM customers WHERE email = %s", (email,))
        elif phone:
            cursor.execute("SELECT customer_id, name, email, phone FROM customers WHERE phone = %s", (phone,))
        elif name:
            # Using ILIKE for case-insensitive partial/full matching
            cursor.execute("SELECT customer_id, name, email, phone FROM customers WHERE name ILIKE %s", (f"%{name}%",))
        else:
            result = {"status": "error", "message": "No search parameters provided."}

        rows = cursor.fetchall()
        
        if not rows:
            result = {"status": "not_found", "message": "No customer record found."}
        
        if len(rows) > 1:
            # Multiple matches found! Return options so the LLM can ask for clarification
            matches = [{"customer_id": r["customer_id"], "name": r["name"], "email": r["email"]} for r in rows]
            result = {
                "status": "ambiguous_match",
                "count": len(rows),
                "matches": matches,
                "message": f"Found {len(rows)} customers matching that criteria."
            }

        # Single match found
        r = rows[0]
        result = {
            "status": "success",
            "customer": {
                "customer_id": r["customer_id"],
                "name": r["name"],
                "email": r["email"],
                "phone": r["phone"]
            }
        }

        return json.dumps(result)

    finally:
        cursor.close()
        conn.close()

def get_orders_by_customer(customer_id: str):
    """
    Retrieves all orders associated with a specific customer ID, sorted by latest first.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    result = None

    try:
        cursor.execute("""
            SELECT order_id, customer_id, status, carrier, eta, notification_sent, notification_time 
            FROM orders 
            WHERE customer_id = %s
            ORDER BY notification_time DESC NULLS LAST;
        """, (customer_id,))
        
        rows = cursor.fetchall()
        if not rows:
            result = {"status": "not_found", "message": f"No orders found for customer ID {customer_id}."}

        orders = [{
            "order_id": r["order_id"],
            "status": r["status"],
            "carrier": r["carrier"],
            "eta": r["eta"],
            "notification_sent": r["notification_sent"]
        } for r in rows]

        result = {"status": "success", "orders": orders}

        return json.dumps(result)

    finally:
        cursor.close()
        conn.close()

def send_notification(order_id: str) -> str:
    """Dispatches notification and updates DB state deterministically."""
    print(f"\n  [SERVER ENGINE]: Sending email notification for {order_id}...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE orders 
        SET notification_sent = 1, notification_time = CURRENT_TIMESTAMP
        WHERE order_id = %s
    """, (order_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return json.dumps({"status": "success", "message": f"Notification sent for {order_id}"})


# --- 2. Tool Definitions & Router ---

DB_TOOLS_DEFINITION = [
    {
        "name": "get_order_details",
        "description": "Fetch order status, courier, ETA, and notification delivery state.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Order ID, e.g., ORD-1234"}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "search_customers",
        "description": "Searches for customers by name, email, or phone number. If multiple customers match a name, it returns multiple records so you can ask the user for clarification.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The full or partial name of the customer to search for."
                },
                "email": {
                    "type": "string",
                    "description": "The exact email address of the customer."
                },
                "phone": {
                    "type": "string",
                    "description": "The exact phone number of the customer."
                }
            },
            "required": []
        }
    },
    {
        "name": "get_orders_by_customer",
        "description": "Retrieves all orders associated with a specific customer ID, sorted by the most recent first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The unique customer identifier (e.g., CUST-001)."
                }
            },
            "required": ["customer_id"]
        }
    },
    {
        "name": "send_notification",
        "description": "Triggers email notification dispatch and updates order state in database.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Order ID, e.g., ORD-1234"}
            },
            "required": ["order_id"]
        }
    }
]

DB_TOOL_ROUTER = {
    "get_order_details": get_order_details,
    "send_notification": send_notification,
    "search_customers": search_customers,
    "get_orders_by_customer": get_orders_by_customer
}