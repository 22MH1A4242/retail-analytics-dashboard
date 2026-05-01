"""
app.py — Retail Business Analytics Dashboard
Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.kpi-card {
    background: white; border: 1px solid #e0e0e0; border-radius: 12px;
    padding: 1.2rem 1.5rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.kpi-value { font-size: 1.8rem; font-weight: 700; color: #1a237e; }
.kpi-label { font-size: 0.8rem; color: #666; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-delta { font-size: 0.85rem; font-weight: 600; margin-top: 4px; }
.positive  { color: #2e7d32; }
.negative  { color: #c62828; }
</style>
""", unsafe_allow_html=True)

# ── DB Connection ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_connection():
    return sqlite3.connect("data/sales.db", check_same_thread=False)

@st.cache_data(ttl=300)
def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql_query(sql, conn)

try:
    _ = run_query("SELECT 1 FROM orders LIMIT 1")
    DB_OK = True
except Exception:
    DB_OK = False

if not DB_OK:
    st.error("⚠️ Database not found. Run `python generate_data.py` first.")
    st.stop()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("🔧 Filters")

years_avail = run_query("SELECT DISTINCT strftime('%Y',order_date) AS yr FROM orders ORDER BY yr")["yr"].tolist()
sel_years   = st.sidebar.multiselect("Year", years_avail, default=years_avail)

cats_avail  = run_query("SELECT DISTINCT category FROM products ORDER BY category")["category"].tolist()
sel_cats    = st.sidebar.multiselect("Category", cats_avail, default=cats_avail)

segs_avail  = run_query("SELECT DISTINCT segment FROM customers ORDER BY segment")["segment"].tolist()
sel_segs    = st.sidebar.multiselect("Customer Segment", segs_avail, default=segs_avail)

yr_filter  = "(" + ",".join(f"'{y}'" for y in sel_years)  + ")"
cat_filter = "(" + ",".join(f"'{c}'" for c in sel_cats)   + ")"
seg_filter = "(" + ",".join(f"'{s}'" for s in sel_segs)   + ")"

BASE = f"""
    FROM order_items i
    JOIN orders o    ON i.order_id    = o.order_id
    JOIN products p  ON i.product_id  = p.product_id
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE strftime('%Y', o.order_date) IN {yr_filter}
      AND p.category IN {cat_filter}
      AND c.segment  IN {seg_filter}
"""

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.title("📊 Retail Business Analytics Dashboard")
st.markdown("Live SQL-powered dashboard. All charts update based on sidebar filters.")

kpi_df = run_query(f"""
    SELECT
        ROUND(SUM(i.sales), 0)                              AS revenue,
        ROUND(SUM(i.profit), 0)                             AS profit,
        COUNT(DISTINCT o.order_id)                          AS orders,
        COUNT(DISTINCT c.customer_id)                       AS customers,
        ROUND(SUM(i.profit)/SUM(i.sales)*100, 1)            AS margin,
        ROUND(SUM(i.sales)/COUNT(DISTINCT o.order_id), 2)   AS aov
    {BASE}
""")

k = kpi_df.iloc[0]
col1, col2, col3, col4, col5, col6 = st.columns(6)
kpis = [
    ("💰 Total Revenue",   f"₹{k['revenue']:,.0f}",   ""),
    ("📈 Total Profit",    f"₹{k['profit']:,.0f}",    ""),
    ("🛒 Total Orders",    f"{k['orders']:,.0f}",      ""),
    ("👥 Customers",       f"{k['customers']:,.0f}",   ""),
    ("📊 Profit Margin",   f"{k['margin']}%",          ""),
    ("🛍 Avg Order Value", f"₹{k['aov']:,.2f}",       ""),
]
for col, (label, value, delta) in zip([col1, col2, col3, col4, col5, col6], kpis):
    with col:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value'>{value}</div>
            <div class='kpi-label'>{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Row 1: Revenue Trend + Category Breakdown ─────────────────────────────────
col_a, col_b = st.columns([2, 1])

with col_a:
    monthly = run_query(f"""
        SELECT strftime('%Y-%m', o.order_date) AS month,
               ROUND(SUM(i.sales), 0)          AS revenue,
               ROUND(SUM(i.profit), 0)         AS profit
        {BASE}
        GROUP BY month ORDER BY month
    """)
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=monthly["month"], y=monthly["revenue"],
        name="Revenue", line=dict(color="#1565C0", width=2.5), fill="tozeroy",
        fillcolor="rgba(21,101,192,0.08)"))
    fig_trend.add_trace(go.Scatter(x=monthly["month"], y=monthly["profit"],
        name="Profit", line=dict(color="#2E7D32", width=2, dash="dot")))
    fig_trend.update_layout(title="📅 Monthly Revenue & Profit Trend",
                            height=360, legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_trend, use_container_width=True)

with col_b:
    cat_df = run_query(f"""
        SELECT p.category, ROUND(SUM(i.sales),0) AS revenue {BASE}
        GROUP BY p.category ORDER BY revenue DESC
    """)
    fig_pie = px.pie(cat_df, values="revenue", names="category",
                     title="🗂 Revenue by Category",
                     color_discrete_sequence=px.colors.qualitative.Set2)
    fig_pie.update_layout(height=360)
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Row 2: Top Products + Regional Map ────────────────────────────────────────
col_c, col_d = st.columns([1, 1])

with col_c:
    top_prods = run_query(f"""
        SELECT p.product_name, ROUND(SUM(i.sales),0) AS revenue,
               ROUND(SUM(i.profit),0) AS profit
        {BASE}
        GROUP BY p.product_name ORDER BY revenue DESC LIMIT 10
    """)
    fig_top = px.bar(top_prods, x="revenue", y="product_name", orientation="h",
                     color="profit", color_continuous_scale="RdYlGn",
                     title="🏆 Top 10 Products by Revenue",
                     labels={"revenue": "Revenue (₹)", "product_name": ""})
    fig_top.update_layout(height=400, yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig_top, use_container_width=True)

with col_d:
    region_df = run_query(f"""
        SELECT c.region,
               ROUND(SUM(i.sales),0)  AS revenue,
               ROUND(SUM(i.profit),0) AS profit,
               COUNT(DISTINCT o.order_id) AS orders
        {BASE}
        GROUP BY c.region ORDER BY revenue DESC
    """)
    fig_reg = px.bar(region_df, x="region", y=["revenue", "profit"],
                     barmode="group", title="🗺 Revenue & Profit by Region",
                     color_discrete_map={"revenue": "#1565C0", "profit": "#2E7D32"},
                     labels={"value": "Amount (₹)", "region": "Region"})
    fig_reg.update_layout(height=400, legend=dict(orientation="h", y=1.05))
    st.plotly_chart(fig_reg, use_container_width=True)

# ── Row 3: Discount Impact + Ship Mode ────────────────────────────────────────
col_e, col_f = st.columns(2)

with col_e:
    disc_df = run_query(f"""
        SELECT
            CASE WHEN i.discount = 0     THEN '0% No Discount'
                 WHEN i.discount <= 0.10 THEN '1-10%'
                 WHEN i.discount <= 0.20 THEN '11-20%'
                 ELSE '21%+' END AS discount_band,
            ROUND(AVG(i.profit/i.sales)*100,1) AS avg_margin
        {BASE}
        GROUP BY discount_band ORDER BY avg_margin DESC
    """)
    fig_disc = px.bar(disc_df, x="discount_band", y="avg_margin",
                      color="avg_margin", color_continuous_scale="RdYlGn",
                      title="💸 Discount Band vs Profit Margin",
                      labels={"avg_margin": "Avg Margin %", "discount_band": "Discount"})
    fig_disc.update_layout(height=340)
    st.plotly_chart(fig_disc, use_container_width=True)

with col_f:
    ship_df = run_query(f"""
        SELECT o.ship_mode,
               COUNT(DISTINCT o.order_id) AS orders,
               ROUND(AVG(julianday(o.ship_date)-julianday(o.order_date)),1) AS avg_days
        {BASE}
        GROUP BY o.ship_mode ORDER BY orders DESC
    """)
    fig_ship = px.scatter(ship_df, x="avg_days", y="orders", size="orders",
                          text="ship_mode", color="ship_mode",
                          title="🚚 Shipping Mode: Volume vs Speed",
                          labels={"avg_days": "Avg Ship Days", "orders": "Order Count"})
    fig_ship.update_traces(textposition="top center")
    fig_ship.update_layout(height=340, showlegend=False)
    st.plotly_chart(fig_ship, use_container_width=True)

# ── Row 4: Customer Segment + SQL Query Explorer ───────────────────────────────
st.markdown("---")
col_g, col_h = st.columns([1, 1])

with col_g:
    seg_df = run_query(f"""
        SELECT c.segment,
               COUNT(DISTINCT c.customer_id) AS customers,
               ROUND(SUM(i.sales),0)         AS revenue,
               ROUND(SUM(i.profit),0)        AS profit
        {BASE} GROUP BY c.segment ORDER BY revenue DESC
    """)
    fig_seg = px.bar(seg_df, x="segment", y="revenue", color="segment",
                     title="👥 Performance by Customer Segment",
                     text="revenue",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_seg.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig_seg.update_layout(height=360, showlegend=False)
    st.plotly_chart(fig_seg, use_container_width=True)

with col_h:
    st.subheader("🔍 SQL Query Explorer")
    st.markdown("Run any SQL query against the sales database:")
    default_q = """SELECT p.category, ROUND(SUM(i.sales),2) AS revenue,
       ROUND(SUM(i.profit),2) AS profit
FROM order_items i
JOIN products p ON i.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC"""
    user_sql = st.text_area("SQL Query", value=default_q, height=150)
    if st.button("▶ Run Query"):
        try:
            result = run_query(user_sql)
            st.dataframe(result, use_container_width=True, height=180)
            st.caption(f"✅ {len(result)} rows returned")
        except Exception as e:
            st.error(f"SQL Error: {e}")

# ── Top Customers Table ───────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🏅 Top 10 Customers by Lifetime Value")
top_cust = run_query(f"""
    SELECT c.customer_name, c.segment, c.region, c.city,
           COUNT(DISTINCT o.order_id)  AS orders,
           ROUND(SUM(i.sales), 0)      AS lifetime_value,
           ROUND(SUM(i.profit), 0)     AS total_profit
    {BASE}
    GROUP BY c.customer_id, c.customer_name, c.segment, c.region, c.city
    ORDER BY lifetime_value DESC LIMIT 10
""")
top_cust.index = range(1, len(top_cust) + 1)
st.dataframe(top_cust.style.background_gradient(subset=["lifetime_value"], cmap="Blues"),
             use_container_width=True)

st.markdown("---")
st.caption("Built with Streamlit · SQLite · Plotly  |  Data: Synthetic retail sales 2022–2024")