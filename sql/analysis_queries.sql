-- =============================================================================
-- sql/analysis_queries.sql
-- 10 Business Questions answered with SQL
-- Run against data/sales.db (SQLite)
-- =============================================================================


-- =============================================================================
-- Q1: Total Revenue, Profit, and Orders by Year
-- =============================================================================
SELECT
    strftime('%Y', o.order_date)   AS year,
    COUNT(DISTINCT o.order_id)     AS total_orders,
    ROUND(SUM(i.sales), 2)         AS total_revenue,
    ROUND(SUM(i.profit), 2)        AS total_profit,
    ROUND(SUM(i.profit) / SUM(i.sales) * 100, 2) AS profit_margin_pct
FROM orders o
JOIN order_items i ON o.order_id = i.order_id
GROUP BY year
ORDER BY year;


-- =============================================================================
-- Q2: Top 5 Product Categories by Revenue
-- =============================================================================
SELECT
    p.category,
    COUNT(DISTINCT i.order_id)  AS num_orders,
    ROUND(SUM(i.sales), 2)      AS revenue,
    ROUND(SUM(i.profit), 2)     AS profit,
    ROUND(AVG(i.discount)*100, 1) AS avg_discount_pct
FROM order_items i
JOIN products p ON i.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;


-- =============================================================================
-- Q3: Monthly Revenue Trend (2022–2024)
-- =============================================================================
SELECT
    strftime('%Y-%m', o.order_date) AS month,
    ROUND(SUM(i.sales), 2)          AS monthly_revenue,
    COUNT(DISTINCT o.order_id)       AS orders_count,
    ROUND(AVG(i.sales), 2)           AS avg_order_value
FROM orders o
JOIN order_items i ON o.order_id = i.order_id
GROUP BY month
ORDER BY month;


-- =============================================================================
-- Q4: Top 10 Best-Selling Products
-- =============================================================================
SELECT
    p.product_name,
    p.category,
    SUM(i.quantity)           AS units_sold,
    ROUND(SUM(i.sales), 2)   AS revenue,
    ROUND(SUM(i.profit), 2)  AS profit,
    ROUND(SUM(i.profit)/SUM(i.sales)*100, 1) AS margin_pct
FROM order_items i
JOIN products p ON i.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC
LIMIT 10;


-- =============================================================================
-- Q5: Revenue and Profit by Customer Segment
-- =============================================================================
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id) AS num_customers,
    COUNT(DISTINCT o.order_id)    AS num_orders,
    ROUND(SUM(i.sales), 2)        AS revenue,
    ROUND(SUM(i.profit), 2)       AS profit,
    ROUND(SUM(i.sales)/COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM order_items i
JOIN orders o    ON i.order_id    = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY revenue DESC;


-- =============================================================================
-- Q6: Regional Performance Analysis
-- =============================================================================
SELECT
    c.region,
    COUNT(DISTINCT c.customer_id) AS customers,
    COUNT(DISTINCT o.order_id)    AS orders,
    ROUND(SUM(i.sales), 2)        AS revenue,
    ROUND(SUM(i.profit), 2)       AS profit,
    ROUND(SUM(i.profit)/SUM(i.sales)*100, 2) AS margin_pct
FROM order_items i
JOIN orders o    ON i.order_id    = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.region
ORDER BY revenue DESC;


-- =============================================================================
-- Q7: Discount Impact on Profit Margin
-- =============================================================================
SELECT
    CASE
        WHEN i.discount = 0      THEN '0% (No Discount)'
        WHEN i.discount <= 0.10  THEN '1-10%'
        WHEN i.discount <= 0.20  THEN '11-20%'
        ELSE '21%+'
    END AS discount_band,
    COUNT(*)                     AS num_transactions,
    ROUND(SUM(i.sales), 2)       AS revenue,
    ROUND(SUM(i.profit), 2)      AS profit,
    ROUND(AVG(i.profit/i.sales)*100, 2) AS avg_margin_pct
FROM order_items i
GROUP BY discount_band
ORDER BY avg_margin_pct DESC;


-- =============================================================================
-- Q8: Shipping Mode Performance
-- =============================================================================
SELECT
    o.ship_mode,
    COUNT(DISTINCT o.order_id)                   AS orders,
    ROUND(AVG(julianday(o.ship_date)
              - julianday(o.order_date)), 1)      AS avg_ship_days,
    ROUND(SUM(i.sales), 2)                        AS revenue,
    ROUND(SUM(i.sales)/COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o
JOIN order_items i ON o.order_id = i.order_id
GROUP BY o.ship_mode
ORDER BY avg_order_value DESC;


-- =============================================================================
-- Q9: Top 10 Customers by Lifetime Value (CLV)
-- =============================================================================
SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    c.region,
    COUNT(DISTINCT o.order_id)  AS total_orders,
    ROUND(SUM(i.sales), 2)      AS lifetime_value,
    ROUND(SUM(i.profit), 2)     AS total_profit,
    MIN(o.order_date)            AS first_order,
    MAX(o.order_date)            AS last_order
FROM order_items i
JOIN orders o    ON i.order_id    = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.segment, c.region
ORDER BY lifetime_value DESC
LIMIT 10;


-- =============================================================================
-- Q10: Year-over-Year Growth Analysis
-- =============================================================================
WITH yearly AS (
    SELECT
        strftime('%Y', o.order_date) AS year,
        ROUND(SUM(i.sales), 2)       AS revenue,
        ROUND(SUM(i.profit), 2)      AS profit
    FROM orders o
    JOIN order_items i ON o.order_id = i.order_id
    GROUP BY year
)
SELECT
    y.year,
    y.revenue,
    y.profit,
    LAG(y.revenue) OVER (ORDER BY y.year) AS prev_year_revenue,
    ROUND((y.revenue - LAG(y.revenue) OVER (ORDER BY y.year))
          / LAG(y.revenue) OVER (ORDER BY y.year) * 100, 2) AS yoy_growth_pct
FROM yearly y
ORDER BY y.year;
