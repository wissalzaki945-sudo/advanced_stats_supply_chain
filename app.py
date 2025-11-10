import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import StringIO
import requests

st.set_page_config(page_title="Supply Chain Analytics", layout="wide")

# -------------------- Sidebar: Data Loading --------------------
st.sidebar.title("📦 Data Loader")
use_local = st.sidebar.checkbox("Use local file at ./data/DataCoSupplyChainDataset.csv", value=False)

default_url = ""
data_url = st.sidebar.text_input("Or paste a public CSV URL:", value=default_url, placeholder="https://.../DataCoSupplyChainDataset.csv")

uploaded = st.sidebar.file_uploader("...or upload CSV", type=["csv"])

@st.cache_data(show_spinner=False)
def load_csv_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_csv(StringIO(file_bytes.decode("utf-8", errors="ignore")))

@st.cache_data(show_spinner=False)
def load_csv_from_url(url: str) -> pd.DataFrame:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return pd.read_csv(StringIO(r.text))

@st.cache_data(show_spinner=False)
def load_local() -> pd.DataFrame:
    return pd.read_csv("data/DataCoSupplyChainDataset.csv")

df = None
load_btn = st.sidebar.button("Load data")

if load_btn:
    try:
        if use_local:
            df = load_local()
        elif uploaded is not None:
            df = load_csv_from_bytes(uploaded.read())
        elif data_url:
            df = load_csv_from_url(data_url)
        else:
            st.sidebar.warning("Please upload a file or paste a URL.")
    except Exception as e:
        st.sidebar.error(f"Could not load data: {e}")

# -------------------- Helper functions --------------------
def safe_col(df, *names):
    for n in names:
        if n in df.columns:
            return n
    return None

def currency(x):
    try:
        return f"${x:,.2f}"
    except Exception:
        return str(x)

# -------------------- Navigation --------------------
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to page:", [
    "Home",
    "Dashboard",
    "Data Overview",
    "Products (RQ1)",
    "Suppliers (RQ2)",
    "Logistics (RQ3)",
    "Customers (RQ4)",
    "Diagnostics"
])

if page == "Home":
    st.title("Advanced Statistics — Supply Chain Dashboard")
    st.write("Use the sidebar to **load your dataset** and navigate the pages.")
    st.markdown("""
    **Research Questions**
    - RQ1: Which product categories or SKUs contribute most to total revenue?
    - RQ2: Which suppliers deliver poor quality or have the longest delays?
    - RQ3: How do logistics decisions (mode, route, carrier) influence cost and time?
    - RQ4: Which customer segments bring the highest recurring sales?
    """)

    st.info("Once your data loads, go to **Dashboard** to see KPIs and a quick overview.")

if df is None and page != "Home":
    st.warning("Load the dataset from the sidebar first.")
    st.stop()

# Pre-compute "best effort" column guesses
rev_col = safe_col(df, "Revenue", "Revenue generated", "Benefit per order", "Benefit", "Profit")
price_col = safe_col(df, "Price", "Unit price", "Price per unit")
qty_col = safe_col(df, "Quantity", "Order Item Quantity", "Number of products sold")
prod_col = safe_col(df, "Product Name", "SKU", "Product", "Product type", "Product Category")
supp_col = safe_col(df, "Supplier Name", "Supplier name")
lead_col = safe_col(df, "Lead time", "Shipment Days", "Shipping Time", "Shipping days")
defect_col = safe_col(df, "Defect rates", "Defects")
carrier_col = safe_col(df, "Shipping carriers", "Shipping Mode", "Carrier")
ship_cost_col = safe_col(df, "Shipping costs", "Freight Cost")
cust_seg_col = safe_col(df, "Customer Segment", "Customer demographics", "Segment")
region_col = safe_col(df, "Region", "Customer Country", "Market")

# -------------------- Dashboard --------------------
if page == "Dashboard":
    st.header("📊 Executive Summary")
    c1, c2, c3, c4 = st.columns(4)
    total_rows = len(df)
    total_products = df[prod_col].nunique() if prod_col else None
    total_rev = df[rev_col].sum() if rev_col else np.nan
    total_orders = df["Order ID"].nunique() if "Order ID" in df.columns else total_rows

    c1.metric("Rows", f"{total_rows:,}")
    c2.metric("Unique Products", f"{total_products:,}" if total_products else "—")
    c3.metric("Total Revenue", currency(total_rev) if pd.notna(total_rev) else "—")
    c4.metric("Orders", f"{total_orders:,}" if total_orders else "—")

    st.subheader("Revenue by Product Type / Category")
    if prod_col and rev_col:
        rev_by_prod = df.groupby(prod_col)[rev_col].sum().reset_index().sort_values(rev_col, ascending=False).head(20)
        st.plotly_chart(px.bar(rev_by_prod, x=prod_col, y=rev_col), use_container_width=True)
    else:
        st.info("Columns for product or revenue not found.")

    st.subheader("Shipping Carrier Distribution")
    if carrier_col:
        carrier_counts = df[carrier_col].value_counts().reset_index()
        carrier_counts.columns = [carrier_col, "Count"]
        st.plotly_chart(px.pie(carrier_counts, names=carrier_col, values="Count", hole=0.4), use_container_width=True)
    else:
        st.info("Carrier column not found.")

# -------------------- Data Overview --------------------
if page == "Data Overview":
    st.header("🧾 Data Overview")
    st.dataframe(df.head(1000), use_container_width=True)

    st.markdown("#### Missing Values (Top 25)")
    mv = df.isna().sum().sort_values(ascending=False)
    mv = mv[mv > 0].head(25)
    if len(mv) > 0:
        st.dataframe(mv.to_frame("Missing"), use_container_width=True)
    else:
        st.info("No missing values detected.")

    st.markdown("#### Correlation Heatmap (numeric columns)")
    num = df.select_dtypes(include=["number"])
    if num.shape[1] >= 2:
        corr = num.corr(numeric_only=True)
        fig = px.imshow(corr, aspect="auto")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough numeric columns to compute correlation.")

# -------------------- RQ1 --------------------
if page == "Products (RQ1)":
    st.header("🏷️ Products — Top Revenue Drivers")
    if prod_col and rev_col:
        top_n = st.slider("Top N", 5, 30, 10)
        grouped = df.groupby(prod_col).agg(
            total_revenue=(rev_col, "sum"),
            items_sold=(qty_col, "sum") if qty_col else (rev_col, "count")
        ).sort_values("total_revenue", ascending=False).head(top_n).reset_index()
        st.dataframe(grouped, use_container_width=True)
        st.plotly_chart(px.bar(grouped, x=prod_col, y="total_revenue"), use_container_width=True)

        if price_col:
            st.markdown("#### Price Distribution (Top SKUs)")
            focus = grouped[prod_col].head(10).tolist()
            sub = df[df[prod_col].isin(focus)]
            st.plotly_chart(px.box(sub, x=prod_col, y=price_col), use_container_width=True)
    else:
        st.warning("Required columns not found.")

# -------------------- RQ2 --------------------
if page == "Suppliers (RQ2)":
    st.header("🏭 Suppliers — Lead Time & Defects")
    if supp_col:
        stats = df.groupby(supp_col).agg(
            avg_lead=(lead_col, "mean") if lead_col else (supp_col, "count"),
            avg_defect=(defect_col, "mean") if defect_col else (supp_col, "count"),
            count=("__dummy__", "size")
        ).reset_index()
        st.dataframe(stats.sort_values("avg_lead", ascending=False), use_container_width=True)

        if lead_col:
            st.subheader("Average Lead Time by Supplier")
            st.plotly_chart(px.bar(stats, x=supp_col, y="avg_lead"), use_container_width=True)
        if defect_col:
            st.subheader("Avg Defect Rate by Supplier")
            st.plotly_chart(px.bar(stats, x=supp_col, y="avg_defect"), use_container_width=True)
    else:
        st.warning("Supplier column not found.")

# -------------------- RQ3 --------------------
if page == "Logistics (RQ3)":
    st.header("🚚 Logistics — Modes, Carriers & Costs")
    if carrier_col:
        ship = df.groupby(carrier_col).agg(
            avg_time=(lead_col, "mean") if lead_col else (carrier_col, "count"),
            avg_cost=(ship_cost_col, "mean") if ship_cost_col else (carrier_col, "count"),
            count=("__dummy__", "size")
        ).reset_index()
        st.dataframe(ship, use_container_width=True)
        st.plotly_chart(px.bar(ship, x=carrier_col, y="avg_time", title="Avg Shipping Time"), use_container_width=True)
        if ship_cost_col:
            st.plotly_chart(px.bar(ship, x=carrier_col, y="avg_cost", title="Avg Shipping Cost"), use_container_width=True)
    else:
        st.warning("Carrier column not found.")

# -------------------- RQ4 --------------------
if page == "Customers (RQ4)":
    st.header("🧑‍🤝‍🧑 Customers — Segments & Revenue")
    if cust_seg_col and rev_col:
        seg = df.groupby(cust_seg_col)[rev_col].sum().reset_index().sort_values(by=rev_col, ascending=False)
        st.dataframe(seg, use_container_width=True)
        st.plotly_chart(px.bar(seg, x=cust_seg_col, y=rev_col), use_container_width=True)
    else:
        st.warning("Customer segment or revenue column not found.")

# -------------------- Diagnostics --------------------
if page == "Diagnostics":
    st.header("🛠️ Diagnostics")
    st.write("Preview column names and dtypes.")
    st.write(df.dtypes.to_frame("dtype"))

    st.download_button("Download full dataset as CSV", data=df.to_csv(index=False), file_name="dataset_export.csv")
