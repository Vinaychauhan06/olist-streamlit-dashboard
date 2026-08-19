"""
Olist Brazilian E-Commerce Pipeline
Extracts, cleans, transforms, and validates the 9 Olist CSV datasets into
an optimized, star-schema analytics parquet file for high-performance Streamlit dashboards.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np

RAW_DIRS = [
    Path("D:/O-list dashboard/data"),
    Path("D:/Git Hub/E-Commerce-Analytics-Dashboard-Python-SQL-Power-BI-"),
    Path("raw_data"),
    Path("data/raw")
]

def find_raw_dir():
    for d in RAW_DIRS:
        if d.exists() and (d / "olist_orders_dataset.csv").exists():
            return d
    raise FileNotFoundError("Could not locate raw CSV data directory.")

raw_path = find_raw_dir()
print(f"Loading raw files from: {raw_path}")

orders = pd.read_csv(raw_path / "olist_orders_dataset.csv", parse_dates=[
    "order_purchase_timestamp", "order_approved_at",
    "order_delivered_carrier_date", "order_delivered_customer_date",
    "order_estimated_delivery_date"
])
items = pd.read_csv(raw_path / "olist_order_items_dataset.csv")
payments = pd.read_csv(raw_path / "olist_order_payments_dataset.csv")
reviews = pd.read_csv(raw_path / "olist_order_reviews_dataset.csv")
customers = pd.read_csv(raw_path / "olist_customers_dataset.csv")
products = pd.read_csv(raw_path / "olist_products_dataset.csv")
translation = pd.read_csv(raw_path / "product_category_name_translation.csv")
sellers = pd.read_csv(raw_path / "olist_sellers_dataset.csv")

print(f"Loaded: {len(orders):,} orders, {len(items):,} items, {len(payments):,} payments, {len(reviews):,} reviews, {len(customers):,} customers, {len(sellers):,} sellers, {len(products):,} products.")

# 1. Deduplicate reviews (latest response timestamp per order)
reviews_sorted = reviews.sort_values(by=["order_id", "review_answer_timestamp"], ascending=[True, False])
reviews_dedup = reviews_sorted.drop_duplicates(subset=["order_id"])[["order_id", "review_score", "review_id", "review_comment_message"]]

# 2. Payments aggregation at order grain
payments_agg = payments.groupby("order_id").agg(
    total_payment_value=("payment_value", "sum"),
    max_installments=("payment_installments", "max"),
    payment_count=("payment_sequential", "max")
).reset_index()

primary_pay = (
    payments.sort_values(by=["order_id", "payment_value"], ascending=[True, False])
    .drop_duplicates(subset=["order_id"])[["order_id", "payment_type"]]
    .rename(columns={"payment_type": "primary_payment_type"})
)
payments_agg = payments_agg.merge(primary_pay, on="order_id", how="left")

# 3. Category translations
products = products.merge(translation, on="product_category_name", how="left")
products["category_english"] = products["product_category_name_english"].fillna("uncategorized")
products["category_english"] = products["category_english"].str.replace("_", " ").str.title()

# 4. Customer order count for repeat rate
customer_order_counts = orders.merge(customers[["customer_id", "customer_unique_id"]], on="customer_id", how="left")
order_per_unique_cust = customer_order_counts.groupby("customer_unique_id")["order_id"].nunique().reset_index()
order_per_unique_cust.rename(columns={"order_id": "customer_total_orders"}, inplace=True)
customers = customers.merge(order_per_unique_cust, on="customer_unique_id", how="left")
customers["is_repeat_customer"] = customers["customer_total_orders"] > 1

# 5. Build full fact table at item grain
fact = (
    items
    .merge(orders, on="order_id", how="left")
    .merge(customers[["customer_id", "customer_unique_id", "customer_city", "customer_state", "customer_zip_code_prefix", "is_repeat_customer", "customer_total_orders"]], on="customer_id", how="left")
    .merge(products[["product_id", "category_english", "product_weight_g", "product_photos_qty"]], on="product_id", how="left")
    .merge(sellers[["seller_id", "seller_city", "seller_state", "seller_zip_code_prefix"]], on="seller_id", how="left")
    .merge(payments_agg, on="order_id", how="left")
    .merge(reviews_dedup[["order_id", "review_score"]], on="order_id", how="left")
)

fact["category_english"] = fact["category_english"].fillna("Uncategorized")
fact["item_total"] = fact["price"] + fact["freight_value"]
fact["order_purchase_timestamp"] = pd.to_datetime(fact["order_purchase_timestamp"])
fact["order_date"] = fact["order_purchase_timestamp"].dt.date
fact["order_year"] = fact["order_purchase_timestamp"].dt.year
fact["order_month"] = fact["order_purchase_timestamp"].dt.to_period("M").astype(str)
fact["order_year_month"] = fact["order_purchase_timestamp"].dt.strftime("%Y-%m")
fact["order_weekday"] = fact["order_purchase_timestamp"].dt.day_name()
fact["order_hour"] = fact["order_purchase_timestamp"].dt.hour

# Delivery metrics
fact["delivery_days"] = (fact["order_delivered_customer_date"] - fact["order_purchase_timestamp"]).dt.total_seconds() / 86400.0
fact["estimated_days"] = (fact["order_estimated_delivery_date"] - fact["order_purchase_timestamp"]).dt.total_seconds() / 86400.0
fact["days_early_vs_promise"] = (fact["order_estimated_delivery_date"] - fact["order_delivered_customer_date"]).dt.total_seconds() / 86400.0
fact["is_late"] = fact["order_delivered_customer_date"] > fact["order_estimated_delivery_date"]
fact["is_late"] = fact["is_late"].where(fact["order_delivered_customer_date"].notna())

# Trend completeness flag (2017-01-01 to 2018-08-31)
fact["is_complete_month"] = (fact["order_purchase_timestamp"] >= "2017-01-01") & (fact["order_purchase_timestamp"] <= "2018-08-31 23:59:59")

# Clean zip prefixes to 5-digit strings
fact["customer_zip_code_prefix"] = fact["customer_zip_code_prefix"].fillna(0).astype(int).astype(str).str.zfill(5)
fact["seller_zip_code_prefix"] = fact["seller_zip_code_prefix"].fillna(0).astype(int).astype(str).str.zfill(5)

# Save to output
out_dir = Path("C:/Users/Vinay Chauhan/olist_ecommerce_analytics_dashboard/data")
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "olist_merged.parquet"

# Select and optimize columns
keep_cols = [
    "order_id", "order_item_id", "product_id", "seller_id", "customer_id",
    "customer_unique_id", "customer_city", "customer_state", "customer_zip_code_prefix",
    "seller_city", "seller_state", "seller_zip_code_prefix",
    "category_english", "price", "freight_value", "item_total",
    "order_status", "order_purchase_timestamp", "order_date", "order_year",
    "order_month", "order_year_month", "order_weekday", "order_hour",
    "order_delivered_customer_date", "order_estimated_delivery_date",
    "delivery_days", "estimated_days", "days_early_vs_promise", "is_late", "is_complete_month",
    "total_payment_value", "max_installments", "primary_payment_type",
    "review_score", "is_repeat_customer", "customer_total_orders"
]

fact_out = fact[keep_cols]
fact_out.to_parquet(out_file, index=False, compression="snappy")
print(f"Clean fact parquet dataset saved: {out_file} ({out_file.stat().st_size / (1024*1024):.2f} MB)")

# Also create orders level table for 100% accurate macro order stats
orders_enriched = orders.merge(customers[["customer_id", "customer_unique_id", "customer_city", "customer_state", "customer_zip_code_prefix", "is_repeat_customer", "customer_total_orders"]], on="customer_id", how="left")
orders_enriched = orders_enriched.merge(payments_agg, on="order_id", how="left")
orders_enriched = orders_enriched.merge(reviews_dedup[["order_id", "review_score"]], on="order_id", how="left")

orders_items_summary = fact.groupby("order_id").agg(
    total_gmv=("item_total", "sum"),
    total_price=("price", "sum"),
    total_freight=("freight_value", "sum"),
    total_items=("order_item_id", "count"),
    categories=("category_english", lambda x: ", ".join(x.unique()))
).reset_index()

orders_enriched = orders_enriched.merge(orders_items_summary, on="order_id", how="left")
orders_enriched["total_gmv"] = orders_enriched["total_gmv"].fillna(0)
orders_enriched["total_price"] = orders_enriched["total_price"].fillna(0)
orders_enriched["total_freight"] = orders_enriched["total_freight"].fillna(0)
orders_enriched["total_items"] = orders_enriched["total_items"].fillna(0)
orders_enriched["order_purchase_timestamp"] = pd.to_datetime(orders_enriched["order_purchase_timestamp"])
orders_enriched["order_year"] = orders_enriched["order_purchase_timestamp"].dt.year
orders_enriched["order_month"] = orders_enriched["order_purchase_timestamp"].dt.to_period("M").astype(str)
orders_enriched["order_year_month"] = orders_enriched["order_purchase_timestamp"].dt.strftime("%Y-%m")
orders_enriched["delivery_days"] = (orders_enriched["order_delivered_customer_date"] - orders_enriched["order_purchase_timestamp"]).dt.total_seconds() / 86400.0
orders_enriched["is_late"] = orders_enriched["order_delivered_customer_date"] > orders_enriched["order_estimated_delivery_date"]
orders_enriched["is_late"] = orders_enriched["is_late"].where(orders_enriched["order_delivered_customer_date"].notna())
orders_enriched["is_complete_month"] = (orders_enriched["order_purchase_timestamp"] >= "2017-01-01") & (orders_enriched["order_purchase_timestamp"] <= "2018-08-31 23:59:59")

orders_file = out_dir / "olist_orders.parquet"
orders_enriched.to_parquet(orders_file, index=False, compression="snappy")
print(f"Orders parquet dataset saved: {orders_file} ({orders_file.stat().st_size / (1024*1024):.2f} MB)")
