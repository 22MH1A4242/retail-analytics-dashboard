live Demo: https://retail-analytics-dashboard-pqewvuj9e5jxcun3v3t9pz.streamlit.app/

# 📊 Retail Business Analytics Dashboard

> **Skills demonstrated:** SQL (10 business queries) · SQLite · Python · Plotly · Streamlit · Data Storytelling

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate the database (SQLite + CSV files)
python generate_data.py

# 3. Launch the dashboard
streamlit run app.py
```

## Project Structure

```
project3_dashboard/
├── app.py                      ← Streamlit dashboard (main)
├── generate_data.py            ← Creates realistic retail dataset
├── requirements.txt
├── sql/
│   └── analysis_queries.sql   ← 10 business SQL questions (show this in interviews!)
└── data/
    ├── sales.db                ← SQLite database (4 tables)
    ├── products.csv
    ├── customers.csv
    ├── orders.csv
    └── order_items.csv
```

## Database Schema

```
customers   (customer_id, customer_name, segment, region, city)
products    (product_id, product_name, category, sub_category, cost_price, list_price)
orders      (order_id, order_date, ship_date, ship_mode, customer_id)
order_items (item_id, order_id, product_id, quantity, discount, unit_price, sales, profit)
```

## 10 SQL Business Questions Answered

1. Total Revenue, Profit and Orders by Year
2. Top 5 Product Categories by Revenue
3. Monthly Revenue Trend (2022–2024)
4. Top 10 Best-Selling Products
5. Revenue and Profit by Customer Segment
6. Regional Performance Analysis
7. Discount Impact on Profit Margin ← interviewers love this one
8. Shipping Mode Performance
9. Top 10 Customers by Lifetime Value (CLV)
10. Year-over-Year Growth Analysis (with LAG window function)

## Resume Bullet Points (copy these!)

- Designed a 4-table normalised SQLite database for retail transactions (5,000+ orders, 500+ customers)
- Wrote 10 advanced SQL queries including window functions (LAG, PARTITION BY) for YoY growth analysis
- Built an interactive Streamlit dashboard with live SQL filtering across year, category, and customer segment
- Identified discount band vs. profit margin correlation — showing 21%+ discounts reduce margins by ~40%
