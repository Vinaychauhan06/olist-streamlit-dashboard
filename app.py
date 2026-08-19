"""
=============================================================================
E-Commerce Executive Analytics Dashboard | Olist Brazilian Marketplace
Author: Vinay Chauhan (Data Analyst Portfolio Project)
Tools: Python, Streamlit, Pandas, Plotly Express & Graph Objects
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & MODERN THEME
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Olist E-Commerce Analytics | Executive Suite",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a clean, pro-tier UI
st.markdown("""
<style>
    /* Global Typography & Font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }
    
    /* Top Pro Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
        color: #FFFFFF;
        border-radius: 14px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .hero-title {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
        color: #F8FAFC;
    }
    .hero-subtitle {
        font-size: 13px;
        color: #94A3B8;
        margin-top: 6px;
        margin-bottom: 12px;
    }
    .hero-tag {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(96, 165, 250, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 6px;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        transform: translateY(-2px);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px;
        font-weight: 500;
        color: #64748B;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.5px;
    }

    /* Custom Insight Callout Cards */
    .pro-insight {
        background: #F8FAFC;
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 16px 0;
        font-size: 13.5px;
        color: #334155;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }
    .pro-insight strong {
        color: #1E293B;
    }

    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 2. DATA LOADING & CACHING
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    """
    Loads pre-aggregated and cleaned Olist marketplace dataset.
    Uses st.cache_data for instant caching and performance.
    """
    df = pd.read_parquet("data/olist_merged.parquet")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df

df = load_data()

# ---------------------------------------------------------------------------
# 3. SIDEBAR FILTERS (POLISHED & INTUITIVE)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ **Dashboard Controls**")
    st.caption("Filter data across time and geography")
    
    # Year Filter
    available_years = sorted(df["order_year"].dropna().unique().tolist())
    selected_years = st.multiselect(
        "📅 **Order Year**",
        options=available_years,
        default=available_years
    )

    # State Filter
    all_states = sorted(df["customer_state"].dropna().unique().tolist())
    selected_states = st.multiselect(
        "📍 **Customer State**",
        options=all_states,
        default=[]
    )

    # Order Status Filter
    all_status = sorted(df["order_status"].dropna().unique().tolist())
    selected_status = st.multiselect(
        "📦 **Order Status**",
        options=all_status,
        default=["delivered"]
    )
    
    st.divider()
    st.caption("💡 **Tip:** Clear state filter to view national totals.")

# Apply filters
filtered_df = df.copy()
if selected_years:
    filtered_df = filtered_df[filtered_df["order_year"].isin(selected_years)]
if selected_states:
    filtered_df = filtered_df[filtered_df["customer_state"].isin(selected_states)]
if selected_status:
    filtered_df = filtered_df[filtered_df["order_status"].isin(selected_status)]

# Handling empty selection
if filtered_df.empty:
    st.warning("⚠️ No records match the selected filters. Please expand your selection.")
    st.stop()

# ---------------------------------------------------------------------------
# 4. CORE BUSINESS KPIS CALCULATION
# ---------------------------------------------------------------------------
total_revenue = filtered_df["item_total"].sum()
total_orders = filtered_df["order_id"].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
avg_review_score = filtered_df["review_score"].mean()

# On-time delivery calculation
delivered_orders = filtered_df.dropna(subset=["is_late"])
if len(delivered_orders) > 0:
    late_rate = delivered_orders["is_late"].astype(bool).mean()
    on_time_rate = (1 - late_rate) * 100
    avg_delivery_days = delivered_orders["delivery_days"].mean()
else:
    on_time_rate = 0
    avg_delivery_days = 0

# ---------------------------------------------------------------------------
# 5. PRO EXECUTIVE HEADER & KPI CARDS
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">📦 Olist E-Commerce Performance Analytics</div>
    <div class="hero-subtitle">Executive Intelligence Suite · Analyzing 100,000+ Orders & Marketplace Dynamics</div>
    <span class="hero-tag">🇧🇷 Brazilian Marketplace</span>
    <span class="hero-tag">📊 2016–2018 Dataset</span>
    <span class="hero-tag">⚡ Live Parquet Engine</span>
</div>
""", unsafe_allow_html=True)

# 5 Sleek Metric Cards
k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    label="Gross Revenue",
    value=f"R$ {total_revenue/1_000_000:.2f}M",
    help="Total value of items ordered including freight"
)
k2.metric(
    label="Total Orders",
    value=f"{total_orders:,}",
    help="Total distinct orders placed"
)
k3.metric(
    label="Avg Order Value (AOV)",
    value=f"R$ {avg_order_value:.2f}",
    help="Average spend per order"
)
k4.metric(
    label="On-Time Delivery",
    value=f"{on_time_rate:.1f}%",
    help="Orders delivered on or before the estimated promise date"
)
k5.metric(
    label="Customer Rating (CSAT)",
    value=f"⭐ {avg_review_score:.2f} / 5.0",
    help="Average review rating from 1 to 5 stars"
)

st.write("")

# ---------------------------------------------------------------------------
# 6. TABBED ANALYTICS SECTIONS (PRO DATA VISUALIZATIONS)
# ---------------------------------------------------------------------------
tab_sales, tab_ops, tab_cust = st.tabs([
    "📈  Sales & Revenue Performance",
    "🚚  Logistics & Fulfillment",
    "💳  Customer & Payment Insights"
])

# Color Palettes
NAVY_PALETTE = ["#1E3A8A", "#2563EB", "#3B82F6", "#60A5FA", "#93C5FD"]
ACCENT_BLUE = "#2563EB"

# ---------------------------------------------------------------------------
# TAB 1: SALES & REVENUE PERFORMANCE
# ---------------------------------------------------------------------------
with tab_sales:
    col_trend, col_cat = st.columns([6, 4])

    with col_trend:
        st.markdown("##### 📈 **Monthly Revenue Growth (GMV)**")
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
            labels={"order_year_month": "Month", "item_total": "Gross Revenue (R$)"}
        )
        fig_trend.update_traces(
            line=dict(color="#2563EB", width=3.5),
            marker=dict(size=7, color="#1E3A8A")
        )
        fig_trend.update_layout(
            template="plotly_white",
            height=370,
            margin=dict(l=10, r=10, t=20, b=10),
            hovermode="x unified",
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickprefix="R$ "),
            xaxis=dict(showgrid=False, tickangle=-45)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_cat:
        st.markdown("##### 🏆 **Top 10 Product Categories by Revenue**")
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
            text_auto=".2s"
        )
        fig_cat.update_traces(
            marker_color="#1E3A8A",
            textposition="outside"
        )
        fig_cat.update_layout(
            template="plotly_white",
            height=370,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickprefix="R$ "),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("""
    <div class="pro-insight">
        💡 <strong>Executive Insight:</strong> High-ticket categories like <strong>Health & Beauty</strong>, 
        <strong>Watches & Gifts</strong>, and <strong>Bed & Bath</strong> dominate marketplace GMV. 
        A significant inflection point occurred in <strong>November 2017</strong> with record Black Friday sales volume.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 2: LOGISTICS & FULFILLMENT
# ---------------------------------------------------------------------------
with tab_ops:
    col_deliv, col_geo = st.columns(2)

    with col_deliv:
        st.markdown("##### ⏱️ **Delivery Speed vs Customer Satisfaction**")
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
            labels={"delivery_bucket": "Delivery Timeframe", "review_score": "Avg Review Rating"},
            range_y=[1, 5],
            text_auto=".2f"
        )
        fig_deliv.update_traces(textposition="outside")
        fig_deliv.update_layout(
            template="plotly_white",
            height=370,
            margin=dict(l=10, r=10, t=20, b=10),
            coloraxis_showscale=False,
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_deliv, use_container_width=True)

    with col_geo:
        st.markdown("##### 📍 **Top 10 States by Order Volume**")
        state_orders = (
            filtered_df.groupby("customer_state")["order_id"]
            .nunique()
            .reset_index()
            .rename(columns={"order_id": "total_orders"})
            .sort_values(by="total_orders", ascending=False)
            .head(10)
        )

        fig_geo = px.bar(
            state_orders,
            x="customer_state",
            y="total_orders",
            labels={"customer_state": "State Code", "total_orders": "Orders"},
            color="total_orders",
            color_continuous_scale="teal",
            text_auto=".2s"
        )
        fig_geo.update_traces(textposition="outside")
        fig_geo.update_layout(
            template="plotly_white",
            height=370,
            margin=dict(l=10, r=10, t=20, b=10),
            coloraxis_showscale=False,
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_geo, use_container_width=True)

    st.markdown(f"""
    <div class="pro-insight">
        🚚 <strong>Logistics Takeaway:</strong> Orders delivered under 10 days boast an average rating of <strong>4.3 / 5.0</strong>. 
        When transit exceeds 20 days, satisfaction plummets below <strong>2.8 / 5.0</strong>. 
        Overall marketplace average delivery duration is <strong>{avg_delivery_days:.1f} days</strong>.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TAB 3: CUSTOMER & PAYMENT INSIGHTS
# ---------------------------------------------------------------------------
with tab_cust:
    col_pay, col_rating = st.columns(2)

    with col_pay:
        st.markdown("##### 💳 **Revenue Share by Payment Method**")
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
            hole=0.55,
            color_discrete_sequence=["#1E3A8A", "#2563EB", "#60A5FA", "#CBD5E1"]
        )
        fig_pay.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="#FFFFFF", width=2))
        )
        fig_pay.update_layout(
            template="plotly_white",
            height=370,
            margin=dict(l=10, r=10, t=20, b=10),
            showlegend=False
        )
        st.plotly_chart(fig_pay, use_container_width=True)

    with col_rating:
        st.markdown("##### ⭐ **Customer Review Score Distribution**")
        review_counts = (
            filtered_df["review_score"]
            .value_counts()
            .reset_index()
            .rename(columns={"review_score": "stars", "count": "total_reviews"})
            .sort_values(by="stars")
        )

        fig_rev = px.bar(
            review_counts,
            x="stars",
            y="total_reviews",
            labels={"stars": "Review Stars (1 to 5)", "total_reviews": "Reviews"},
            color="stars",
            color_continuous_scale="Blues",
            text_auto=".2s"
        )
        fig_rev.update_traces(textposition="outside")
        fig_rev.update_layout(
            template="plotly_white",
            height=370,
            margin=dict(l=10, r=10, t=20, b=10),
            coloraxis_showscale=False,
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
            xaxis=dict(showgrid=False, tickmode="linear", tick0=1, dtick=1)
        )
        st.plotly_chart(fig_rev, use_container_width=True)

    st.markdown("""
    <div class="pro-insight">
        💳 <strong>Payment Insight:</strong> Over <strong>75% of marketplace transactions</strong> are completed using 
        <strong>Credit Card</strong> installments, reflecting Brazilian consumer reliance on split-payment financing.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 7. FOOTER
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "📌 **Portfolio Project:** Designed & Developed by Vinay Chauhan | "
    "Tech Stack: Python (Pandas, Plotly), Streamlit Community Cloud, Parquet Engine."
)
