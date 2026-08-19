# 📦 Olist Brazilian E-Commerce Analytics Dashboard

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458.svg)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75.svg)](https://plotly.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)](https://streamlit.io/)

> An interactive e-commerce analytics dashboard built with **Python, Pandas, Plotly, and Streamlit**, analyzing 99K+ orders from the Olist Brazilian E-Commerce Public Dataset.

## 🚀 Live Demo

**Streamlit App:** Add your deployed Streamlit URL here

---

## 📌 Project Overview

This project analyzes the **Olist Brazilian E-Commerce Public Dataset** to understand marketplace performance across:

* Revenue and GMV
* Customers
* Products and categories
* Sellers
* Payments
* Delivery performance
* Customer reviews
* Geographic performance

The project combines **data cleaning, ETL, exploratory analysis, business analytics, statistical analysis, and interactive dashboard development** into a single application.

The dashboard is designed to answer practical business questions rather than simply display charts.

---

## 📊 Key Metrics

| Metric                     |         Value |
| -------------------------- | ------------: |
| Total GMV                  | **R$ 15.84M** |
| Product Revenue            | **R$ 13.59M** |
| Freight Revenue            |  **R$ 2.25M** |
| Total Orders               |    **99,441** |
| Order Items                |   **112,650** |
| Unique Customers           |    **96,096** |
| Active Sellers             |     **3,095** |
| Average Order Value        | **R$ 160.58** |
| Average Items / Order      |      **1.13** |
| Delivered Orders           |    **96,478** |
| On-Time Delivery Rate      |    **91.89%** |
| Average Delivery Lead Time | **12.1 days** |
| Average Review Score       |  **4.09 / 5** |

---

## 🔍 Key Business Findings

### 🚚 Delivery Performance Matters

Delivery performance has a strong relationship with customer satisfaction.

* On-time orders: **4.29★ average rating**
* Late orders: **2.57★ average rating**
* Difference: **-1.72 stars**
* 1-star reviews:

  * On-time: **6.6%**
  * Late: **46.2%**

This indicates that late delivery is strongly associated with poor customer reviews.

> Note: This is an observational relationship, so it should not be interpreted as proof that delivery delays alone cause lower ratings.

### 📈 Category Concentration

The analysis shows a strong concentration of revenue across product categories.

* **18 of 72 categories** account for approximately **80% of revenue**.
* This highlights the importance of focusing inventory, marketing, and seller strategy on high-performing categories.

### 🌎 Geographic Concentration

The Southeast region represents a large share of marketplace activity.

The top three states:

* São Paulo
* Rio de Janeiro
* Minas Gerais

together contribute approximately **62.5% of GMV**.

### 💳 Payment Behavior

Credit cards are the dominant payment method, representing approximately **78.3% of payment value**.

Installment payments also represent a significant portion of transactions, highlighting the importance of financing in the Brazilian e-commerce market.

---

# 📱 Dashboard Features

The Streamlit application contains multiple analytical sections.

### 🏠 Executive Overview

Provides a high-level view of marketplace performance:

* GMV
* Revenue
* Orders
* Customers
* Monthly revenue trends
* State performance
* Customer review distribution

### 💰 Revenue & Product Analytics

Analyzes:

* Revenue by category
* Revenue by sub-category
* Category Pareto analysis
* Payment method distribution
* Average order value
* Freight-to-product price ratio
* Seller concentration

### 🚚 Delivery & Customer Experience

Analyzes:

* On-time vs late deliveries
* Delivery lead time
* Late delivery rate
* Delivery performance by state
* Review score vs delivery performance
* Customer satisfaction

### 🗺️ Customer & Geographic Analytics

Includes:

* State-level performance
* Geographic sales analysis
* Customer purchasing patterns
* Order activity by day and hour
* Customer segments and cohorts

### 🔎 Interactive Data Explorer

Allows users to explore individual records using filters such as:

* Order ID
* City
* Product category
* State

The filtered data can also be exported for further analysis.

### 📚 KPI Glossary & Methodology

Documents:

* KPI definitions
* Business formulas
* Data transformations
* Data modeling decisions
* Analytical methodology

---

# 🛠️ Tech Stack

| Technology     | Purpose                                |
| -------------- | -------------------------------------- |
| **Python**     | Data processing and analytics          |
| **Pandas**     | Data manipulation and transformation   |
| **PyArrow**    | Parquet data processing                |
| **Plotly**     | Interactive visualizations             |
| **Streamlit**  | Dashboard application                  |
| **Parquet**    | Optimized analytical storage           |
| **Git/GitHub** | Version control and project management |

---

# 🏗️ Data Pipeline

The project follows an ETL-style workflow:

```text
Olist Raw CSV Files
        │
        ▼
   Data Cleaning
        │
        ▼
   Data Transformation
        │
        ▼
   Data Modeling
        │
        ▼
   Parquet Files
        │
        ▼
 Streamlit Dashboard
        │
        ▼
 Business Insights
```

The `prepare_data.py` script is responsible for transforming the raw Olist datasets into optimized analytical datasets used by the dashboard.

---

# 📁 Project Structure

```text
olist-ecommerce-analytics-dashboard/
│
├── .streamlit/
│   └── config.toml
│
├── data/
│   ├── olist_merged.parquet
│   └── olist_orders.parquet
│
├── app.py
├── prepare_data.py
├── requirements.txt
├── .gitignore
└── README.md
```

### File Description

**`app.py`**
Main Streamlit application containing the dashboard and interactive visualizations.

**`prepare_data.py`**
ETL pipeline used to clean, transform, join, and prepare the Olist datasets.

**`data/olist_merged.parquet`**
Item-level analytical dataset used for product, revenue, seller, and category analysis.

**`data/olist_orders.parquet`**
Order-level dataset used for customer, delivery, review, and order-level analysis.

**`requirements.txt`**
Python dependencies required to run the application.

**`.streamlit/config.toml`**
Streamlit application configuration and theme settings.

---

# 💻 Run Locally

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/olist-ecommerce-analytics-dashboard.git
cd olist-ecommerce-analytics-dashboard
```

## 2. Create a virtual environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the dashboard

```bash
streamlit run app.py
```

The application will open in your browser.

---

# ☁️ Deploy on Streamlit Community Cloud

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Connect your GitHub account.
4. Select this repository.
5. Set the main file to:

```text
app.py
```

6. Deploy the application.

After deployment, add your Streamlit URL to the **Live Demo** section at the top of this README.

---

# 📚 Dataset

This project uses the **Olist Brazilian E-Commerce Public Dataset**.

The dataset contains information about:

* Orders
* Customers
* Sellers
* Products
* Payments
* Reviews
* Order items
* Geolocation

The original dataset covers Brazilian e-commerce transactions from approximately **2016–2018**.

Dataset source:

[Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

---

# 📈 Analytical Methods

The project uses several data analytics techniques:

### Exploratory Data Analysis

* Descriptive statistics
* Distribution analysis
* Correlation analysis
* Outlier analysis
* Time-series analysis
* Categorical analysis

### Business Analytics

* Revenue analysis
* Customer analysis
* Product analysis
* Seller analysis
* Geographic analysis
* Delivery analysis
* Payment analysis

### Statistical Analysis

The project also evaluates the relationship between delivery performance and customer review scores using statistical testing.

The results are interpreted as **observational evidence**, not as a randomized experiment.

---

# 🎯 Business Questions

The dashboard was designed around questions such as:

* What is the total GMV generated by the marketplace?
* Which categories generate the most revenue?
* Which sellers contribute the most GMV?
* Which states generate the most sales?
* How does delivery performance vary by region?
* Does late delivery correspond with lower review scores?
* Which payment methods are most frequently used?
* How concentrated is revenue across categories and sellers?
* How does marketplace revenue change over time?
* Which customer segments contribute the most value?
---

# 👤 Author

**Vinay Chauhan**

Data Analyst | Python | SQL | Power BI | Excel | Data Analytics

---

## ⭐ If you found this project useful

Feel free to explore the repository and the live dashboard.
https://olist-app-dashboard-rvyuanhnkffmbavx3mypct.streamlit.app/
