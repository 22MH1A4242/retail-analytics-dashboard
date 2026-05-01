"""
generate_data.py
Creates a realistic retail sales SQLite database + CSV files
Run once: python generate_data.py
"""
import pandas as pd
import numpy as np
import sqlite3
import os

np.random.seed(42)
os.makedirs("data", exist_ok=True)

# ── Products ──────────────────────────────────────────────────────────────────
CATEGORIES = {
    "Technology":  ["Laptop", "Monitor", "Keyboard", "Mouse", "Headphones",
                    "Webcam", "SSD", "USB Hub", "Tablet", "Smartwatch"],
    "Furniture":   ["Office Chair", "Standing Desk", "Bookshelf", "Cabinet",
                    "Conference Table", "Sofa", "Filing Cabinet"],
    "Office Supplies": ["Pen Set", "Notebook", "Sticky Notes", "Stapler",
                        "Printer Paper", "Folders", "Highlighters", "Tape"],
}
SUB_CATS = {
    "Technology": ["Electronics", "Accessories", "Computers"],
    "Furniture": ["Chairs", "Tables", "Storage"],
    "Office Supplies": ["Paper", "Writing", "Binding"],
}

products = []
pid = 1
for cat, items in CATEGORIES.items():
    for item in items:
        sub = np.random.choice(SUB_CATS[cat])
        cost = np.random.uniform(5, 900)
        products.append({
            "product_id": f"P{pid:04d}", "product_name": item,
            "category": cat, "sub_category": sub,
            "cost_price": round(cost, 2),
            "list_price": round(cost * np.random.uniform(1.2, 2.0), 2),
        })
        pid += 1

products_df = pd.DataFrame(products)

# ── Customers ─────────────────────────────────────────────────────────────────
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
REGIONS  = ["North", "South", "East", "West", "Central"]
CITIES   = {
    "North":   ["Delhi", "Chandigarh", "Jaipur", "Lucknow"],
    "South":   ["Bangalore", "Chennai", "Hyderabad", "Kochi"],
    "East":    ["Kolkata", "Bhubaneswar", "Patna", "Guwahati"],
    "West":    ["Mumbai", "Ahmedabad", "Pune", "Surat"],
    "Central": ["Nagpur", "Indore", "Bhopal", "Raipur"],
}

n_customers = 500
regions = np.random.choice(REGIONS, n_customers)
customers_df = pd.DataFrame({
    "customer_id":   [f"C{i:04d}" for i in range(1, n_customers + 1)],
    "customer_name": [f"Customer {i}" for i in range(1, n_customers + 1)],
    "segment":       np.random.choice(SEGMENTS, n_customers, p=[0.50, 0.30, 0.20]),
    "region":        regions,
    "city":          [np.random.choice(CITIES[r]) for r in regions],
})

# ── Orders ────────────────────────────────────────────────────────────────────
n_orders  = 5000
date_range = pd.date_range("2022-01-01", "2024-12-31", freq="D")
order_dates = np.random.choice(date_range, n_orders)
ship_days   = np.random.choice([1, 2, 3, 4, 5, 6, 7], n_orders, p=[0.05, 0.25, 0.30, 0.20, 0.10, 0.07, 0.03])
ship_modes  = np.random.choice(["Standard Class", "Second Class", "First Class", "Same Day"],
                                 n_orders, p=[0.60, 0.20, 0.15, 0.05])

orders_df = pd.DataFrame({
    "order_id":    [f"ORD-{i:05d}" for i in range(1, n_orders + 1)],
    "order_date":  pd.to_datetime(order_dates),
    "ship_date":   pd.to_datetime(order_dates) + pd.to_timedelta(ship_days, unit="D"),
    "ship_mode":   ship_modes,
    "customer_id": np.random.choice(customers_df["customer_id"], n_orders),
})

# ── Order Items ───────────────────────────────────────────────────────────────
items_per_order = np.random.choice([1, 2, 3, 4], n_orders, p=[0.40, 0.35, 0.17, 0.08])
rows = []
for _, order in orders_df.iterrows():
    n_items = items_per_order[int(order.name)]
    selected_prods = products_df.sample(n_items)
    for _, prod in selected_prods.iterrows():
        qty      = np.random.choice([1, 2, 3, 4, 5], p=[0.50, 0.25, 0.13, 0.07, 0.05])
        discount = np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20, 0.30],
                                     p=[0.45, 0.15, 0.15, 0.10, 0.10, 0.05])
        sale_price = prod["list_price"] * (1 - discount)
        profit     = (sale_price - prod["cost_price"]) * qty
        rows.append({
            "item_id":     f"IT-{len(rows)+1:06d}",
            "order_id":    order["order_id"],
            "product_id":  prod["product_id"],
            "quantity":    qty,
            "discount":    discount,
            "unit_price":  round(sale_price, 2),
            "sales":       round(sale_price * qty, 2),
            "profit":      round(profit, 2),
        })

items_df = pd.DataFrame(rows)

# ── Save to SQLite ────────────────────────────────────────────────────────────
conn = sqlite3.connect("data/sales.db")
products_df.to_sql("products",   conn, if_exists="replace", index=False)
customers_df.to_sql("customers", conn, if_exists="replace", index=False)
orders_df.to_sql("orders",       conn, if_exists="replace", index=False)
items_df.to_sql("order_items",   conn, if_exists="replace", index=False)
conn.close()

# Save CSVs too
products_df.to_csv("data/products.csv",    index=False)
customers_df.to_csv("data/customers.csv",  index=False)
orders_df.to_csv("data/orders.csv",        index=False)
items_df.to_csv("data/order_items.csv",    index=False)

print(f"Database saved → data/sales.db")
print(f"Products: {len(products_df)} | Customers: {len(customers_df)}")
print(f"Orders: {len(orders_df)} | Line items: {len(items_df)}")
print(f"Total Revenue: ₹{items_df['sales'].sum():,.0f}")
