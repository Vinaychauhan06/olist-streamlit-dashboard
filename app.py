"""
=============================================================================
E-Commerce Business Performance Dashboard (Olist Brazilian Marketplace)
Author: Vinay Chauhan (Data Analyst Portfolio Project)
Tools: Python, Streamlit, Pandas, Plotly Express
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard | Olist",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# 2. DATA LOADING & CACHING
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    """
    Loads and prepares the cleaned Olist marketplace dataset.
    Uses st.cache_data to prevent reloading the dataset on every user interaction.
    """
    df = pd.read_parquet("data/olist_merged.parquet")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df

df = load_data()

# ---------------------------------------------------------------------------
# 3. SIDEBAR FILTERS
# ---------------------------------------------------------------------------
st.sidebar.header("🔍 Filter Dashboard")

# Year Filter
available_years = sorted(df["order_year"].dropna().unique().tolist())
selected_years = st.sidebar.multiselect(
    "Select Year(s):",
    options=available_years,
    default=available_years
)

# State Filter
all_states = sorted(df["customer_state"].dropna().unique().tolist())
selected_states = st.sidebar.multiselect(
    "Select Customer State(s):",
    options=all_states,
    default=[]
)

# Order Status Filter
all_status = sorted(df["order_status"].dropna().unique().tolist())
selected_status = st.sidebar.multiselect(
    "Select Order Status:",
    options=all_status,
    default=["delivered"]
)

# Apply filters
filtered_df = df.copy()
if selected_years:
    filtered_df = filtered_df[filtered_df["order_year"].isin(selected_years)]
if selected_states:
    filtered_df = filtered_df[filtered_df["customer_state"].isin(selected_states)]
if selected_status:
    filtered_df = filtered_df[filtered_df["order_status"].isin(selected_status)]

# Handling empty filter state
if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters. Please adjust your selections.")
    st.stop()

# ---------------------------------------------------------------------------
# 4. CORE BUSINESS KPIS CALCULATION
# ---------------------------------------------------------------------------
total_revenue = filtered_df["item_total"].sum()
total_orders = filtered_df["order_id"].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
avg_review_score = filtered_df["review_score"].mean()

# On-time delivery percentage
delivered_orders = filtered_df.dropna(subset=["is_late"])
if len(delivered_orders) > 0:
    late_rate = delivered_orders["is_late"].astype(bool).mean()
    on_time_rate = (1 - late_rate) * 100
    avg_delivery_days = delivered_orders["delivery_days"].mean()
else:
    on_time_rate = 0
    avg_delivery_days = 0

# ---------------------------------------------------------------------------
# 5. DASHBOARD HEADER & KPI CARDS
# ---------------------------------------------------------------------------
st.title("📊 E-Commerce Business Performance Dashboard")
st.markdown(
    "Interactive analytics dashboard evaluating **Sales Performance**, **Logistics Efficiency**, "
    "and **Customer Feedback** for ~100,000 orders on the Olist Marketplace (2016–2018)."
)
st.divider()

# KPI Metric Row
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric(
    label="Total Revenue",
    value=f"R$ {total_revenue:,.0f}",
    help="Total value of items ordered including freight"
)
kpi2.metric(
    label="Total Orders",
    value=f"{total_orders:,}",
    help="Count of unique orders placed"
)
kpi3.metric(
    label="Avg Order Value (AOV)",
    value=f"R$ {avg_order_value:.2f}",
    help="Average revenue generated per order"
)
kpi4.metric(
    label="On-Time Delivery Rate",
    value=f"{on_time_rate:.1f}%",
    help="Percentage of orders delivered on or before the estimated date"
)
kpi5.metric(
    label="Avg Customer Rating",
    value=f"⭐ {avg_review_score:.2f} / 5.0",
    help="Average review rating from 1 to 5 stars"
)

st.write("")

# ---------------------------------------------------------------------------
# 6. TABBED ANALYTICS SECTIONS
# ---------------------------------------------------------------------------
tab_sales, tab_ops, tab_cust = st.tabs([
    "📈 Sales & Revenue",
    "🚚 Logistics & Operations",
    "👥 Customer & Payments"
])

# ---------------------------------------------------------------------------
# TAB 1: SALES & REVENUE PERFORMANCE
# ---------------------------------------------------------------------------
with tab_sales:
    col_left, col_right = st.columns([6, 4])

    with col_left:
        st.subheader("Monthly Revenue Trend")
        monthly_sales = (
            filtered_df[filtered_df["is_complete_month"] == True]
            .groupby("order_year_month")["item_total"]
            .sum()
            .reset_index()
        )
        
        fig_trend = px.line(
            monthly_sales,
            x="order_year_month",
            y="item_total",
            markers=True,
            labels={"order_year_month": "Year-Month", "item_total": "Revenue (R$)"},
            title="Monthly Gross Merchandise Value (GMV)"
        )
        fig_trend.update_traces(line_color="#1E88E5", line_width=3)
        fig_trend.update_layout(xaxis_tickangle=-45, height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        st.subheader("Top 10 Product Categories")
        top_cats = (
            filtered_df.groupby("category_english")["item_total"]
            .sum()
            .reset_index()
            .sort_values(by="item_total", ascending=True)
            .tail(10)
        )
        
        fig_cat = px.bar(
            top_cats,
            x="item_total",
            y="category_english",
            orientation="h",
            labels={"item_total": "Revenue (R$)", "category_english": "Category"},
            title="Top 10 Categories by Revenue",
            text_auto=".2s"
        )
        fig_cat.update_traces(marker_color="#3949AB")
        fig_cat.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_cat, use_container_width=True)

    st.info(
        "💡 **Analyst Finding:** Health & Beauty, Watches & Gifts, and Bed & Bath drive the highest marketplace revenue. "
        "November 2017 recorded a major revenue spike attributed to Black Friday promotions."
    )

# ---------------------------------------------------------------------------
# TAB 2: LOGISTICS & OPERATIONS PERFORMANCE
# ---------------------------------------------------------------------------
with tab_ops:
    col_ops1, col_ops2 = st.columns(2)

    with col_ops1:
        st.subheader("Delivery Speed vs Customer Rating")
        delivered_subset = filtered_df.dropna(subset=["delivery_days", "review_score"]).copy()
        delivered_subset["delivery_bucket"] = pd.cut(
            delivered_subset["delivery_days"],
            bins=[0, 5, 10, 15, 20, 30, 100],
            labels=["1-5 days", "6-10 days", "11-15 days", "16-20 days", "21-30 days", "30+ days"]
        )
        bucket_score = (
            delivered_subset.groupby("delivery_bucket", observed=False)["review_score"]
            .mean()
            .reset_index()
        )

        fig_deliv = px.bar(
            bucket_score,
            x="delivery_bucket",
            y="review_score",
            color="review_score",
            color_continuous_scale="Blues",
            labels={"delivery_bucket": "Delivery Timeframe", "review_score": "Avg Review Score"},
            title="Customer Satisfaction by Delivery Speed",
            range_y=[1, 5]
        )
        fig_deliv.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_deliv, use_container_width=True)

    with col_ops2:
        st.subheader("Top 10 States by Order Volume")
        state_orders = (
            filtered_df.groupby("customer_state")["order_id"]
            .nunique()
            .reset_index()
            .rename(columns={"order_id": "total_orders"})
            .sort_values(by="total_orders", ascending=False)
            .head(10)
        )

        fig_states = px.bar(
            state_orders,
            x="customer_state",
            y="total_orders",
            labels={"customer_state": "State", "total_orders": "Orders"},
            title="Order Volume by State (Top 10)",
            color="total_orders",
            color_continuous_scale="Teal"
        )
        fig_states.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_states, use_container_width=True)

    st.warning(
        f"🚚 **Operations Insight:** Orders delivered within 10 days maintain high customer satisfaction (~4.3/5). "
        f"However, orders taking 20+ days see rating drops below 3.0. Current average delivery time is **{avg_delivery_days:.1f} days**."
    )

# ---------------------------------------------------------------------------
# TAB 3: CUSTOMER & PAYMENT INSIGHTS
# ---------------------------------------------------------------------------
with tab_cust:
    col_cust1, col_cust2 = st.columns(2)

    with col_cust1:
        st.subheader("Payment Method Breakdown")
        payment_dist = (
            filtered_df.groupby("primary_payment_type")["item_total"]
            .sum()
            .reset_index()
            .rename(columns={"item_total": "revenue", "primary_payment_type": "payment_type"})
            .sort_values(by="revenue", ascending=False)
        )

        fig_pay = px.pie(
            payment_dist,
            names="payment_type",
            values="revenue",
            title="Revenue Share by Payment Method",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_pay.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_pay, use_container_width=True)

    with col_cust2:
        st.subheader("Customer Review Score Distribution")
        review_counts = (
            filtered_df["review_score"]
            .value_counts()
            .reset_index()
            .rename(columns={"review_score": "review_stars", "count": "total_reviews"})
            .sort_values(by="review_stars")
        )

        fig_rev = px.bar(
            review_counts,
            x="review_stars",
            y="total_reviews",
            labels={"review_stars": "Review Stars (1 to 5)", "total_reviews": "Total Reviews"},
            title="Distribution of Customer Ratings",
            color="review_stars",
            color_continuous_scale="Viridis"
        )
        fig_rev.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_rev, use_container_width=True)

    st.success(
        "💳 **Payment Insight:** Over 75% of marketplace revenue is processed through **Credit Card** installments, "
        "highlighting the importance of seamless installment checkout options for Brazilian consumers."
    )

# ---------------------------------------------------------------------------
# 7. FOOTER / PROJECT SUMMARY
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "📌 **Portfolio Project Details:** Built by Vinay Chauhan | Dataset: Brazilian E-Commerce public dataset by Olist on Kaggle | "
    "Tech Stack: Python (Pandas, Plotly), Streamlit Cloud, Parquet storage."
)
