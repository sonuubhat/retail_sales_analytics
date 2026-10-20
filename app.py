from __future__ import annotations

import io
import zipfile
from urllib.request import Request, urlopen

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Retail Sales Analytics",
    page_icon="🛍️",
    layout="wide",
)

DATA_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"


@st.cache_data(show_spinner="Downloading and preparing the public UCI dataset…")
def load_data() -> pd.DataFrame:
    """Download the UCI Online Retail ZIP and return a cleaned dataframe."""
    request = Request(DATA_URL, headers={"User-Agent": "Mozilla/5.0 RetailAnalytics/1.0"})
    with urlopen(request, timeout=60) as response:
        payload = response.read()

    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        excel_name = next(
            (name for name in archive.namelist()
             if name.lower().endswith((".xlsx", ".xls")) and not name.startswith("__MACOSX")),
            None,
        )
        if not excel_name:
            raise ValueError("The downloaded ZIP did not contain an Excel dataset.")
        with archive.open(excel_name) as excel_file:
            df = pd.read_excel(excel_file)

    # Normalize column names in case the source file uses slightly different casing.
    df.columns = [str(column).strip() for column in df.columns]
    required = {"InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "Country"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing expected columns: {', '.join(sorted(missing))}")

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df = df.dropna(subset=["InvoiceDate", "Quantity", "UnitPrice", "Country", "InvoiceNo"])
    df["Country"] = df["Country"].astype(str).str.strip()
    df["Description"] = df["Description"].fillna("Unknown product").astype(str).str.strip()
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["InvoiceNo"] = df["InvoiceNo"].astype(str)

    # Exclude cancelled invoices and non-positive sales from the sales dashboard.
    df = df[~df["InvoiceNo"].str.startswith("C", na=False)]
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df = df[df["Revenue"] > 0]
    df["YearMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["Date"] = df["InvoiceDate"].dt.date
    return df


st.title("🛍️ Big Data Retail Sales Analytics")
st.caption(
    "Interactive analysis of the UCI Online Retail transaction dataset. "
    "Use the filters to explore revenue, products, customers, and countries."
)

with st.sidebar:
    st.header("Filters")
    if st.button("Refresh dataset"):
        load_data.clear()
        st.rerun()

try:
    raw = load_data()
except Exception as exc:
    st.error("The public dataset could not be loaded. Check your internet connection and try again.")
    st.exception(exc)
    st.stop()

min_date = pd.to_datetime(raw["InvoiceDate"].min()).date()
max_date = pd.to_datetime(raw["InvoiceDate"].max()).date()

with st.sidebar:
    date_range = st.date_input(
        "Invoice date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    countries = sorted(raw["Country"].dropna().unique().tolist())
    default_countries = ["United Kingdom"] if "United Kingdom" in countries else countries
    selected_countries = st.multiselect("Countries", countries, default=default_countries)
    min_revenue = float(raw["Revenue"].min())
    max_revenue = float(raw["Revenue"].quantile(0.99))
    revenue_floor = st.slider(
        "Minimum line-item revenue (£)",
        min_value=0.0,
        max_value=max(1.0, round(max_revenue, 2)),
        value=0.0,
        step=1.0,
    )

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = raw[
    (raw["InvoiceDate"].dt.date >= start_date)
    & (raw["InvoiceDate"].dt.date <= end_date)
    & (raw["Country"].isin(selected_countries) if selected_countries else False)
    & (raw["Revenue"] >= revenue_floor)
].copy()

if filtered.empty:
    st.warning("No transactions match these filters. Change the date, country, or revenue filters.")
    st.stop()

total_revenue = filtered["Revenue"].sum()
orders = filtered["InvoiceNo"].nunique()
customers = filtered["CustomerID"].nunique() if "CustomerID" in filtered.columns else 0
units = filtered["Quantity"].sum()
average_order = total_revenue / orders if orders else 0.0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Revenue", f"£{total_revenue:,.2f}")
m2.metric("Orders", f"{orders:,}")
m3.metric("Customers", f"{customers:,}")
m4.metric("Units sold", f"{units:,.0f}")
m5.metric("Average order value", f"£{average_order:,.2f}")

st.divider()
left, right = st.columns(2)

monthly = (
    filtered.groupby("YearMonth", as_index=False)
    .agg(Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique"))
    .sort_values("YearMonth")
)
with left:
    st.subheader("Monthly revenue")
    fig = px.line(monthly, x="YearMonth", y="Revenue", markers=True,
                  labels={"YearMonth": "Month", "Revenue": "Revenue (£)"})
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

top_products = (
    filtered.groupby("Description", as_index=False)
    .agg(Revenue=("Revenue", "sum"), Units=("Quantity", "sum"))
    .sort_values("Revenue", ascending=False)
    .head(10)
)
with right:
    st.subheader("Top 10 products by revenue")
    fig = px.bar(top_products.sort_values("Revenue"), x="Revenue", y="Description",
                 orientation="h", labels={"Revenue": "Revenue (£)", "Description": "Product"})
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
left, right = st.columns(2)

country_sales = (
    filtered.groupby("Country", as_index=False)
    .agg(Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique"))
    .sort_values("Revenue", ascending=False)
    .head(15)
)
with left:
    st.subheader("Top countries by revenue")
    fig = px.bar(country_sales.sort_values("Revenue"), x="Revenue", y="Country",
                 orientation="h", labels={"Revenue": "Revenue (£)"})
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

weekday = filtered.copy()
weekday["Weekday"] = weekday["InvoiceDate"].dt.day_name()
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday_sales = weekday.groupby("Weekday", as_index=False)["Revenue"].sum()
weekday_sales["Weekday"] = pd.Categorical(weekday_sales["Weekday"], categories=weekday_order, ordered=True)
weekday_sales = weekday_sales.sort_values("Weekday")
with right:
    st.subheader("Revenue by day of week")
    fig = px.bar(weekday_sales, x="Weekday", y="Revenue",
                 labels={"Weekday": "Day", "Revenue": "Revenue (£)"})
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Explore transaction records")
display_columns = [
    column for column in
    ["InvoiceDate", "InvoiceNo", "StockCode", "Description", "Quantity", "UnitPrice", "Revenue", "CustomerID", "Country"]
    if column in filtered.columns
]
st.dataframe(
    filtered[display_columns].sort_values("InvoiceDate", ascending=False).head(1000),
    use_container_width=True,
    hide_index=True,
)
csv = filtered[display_columns].to_csv(index=False).encode("utf-8")
st.download_button("Download filtered transactions as CSV", csv,
                   file_name="filtered_retail_transactions.csv", mime="text/csv")

with st.expander("Data cleaning and definitions"):
    st.markdown(
        """
        - **Revenue** = `Quantity × UnitPrice` for each line item.
        - Cancelled invoices (invoice numbers starting with `C`) are excluded.
        - Rows with missing dates, quantity, unit price, country, or invoice number are excluded.
        - Non-positive quantities and prices are excluded from the sales analysis.
        - Customer count uses distinct `CustomerID` values when that column is present.
        - This dashboard is exploratory; the dataset's original currency and business context are retained.
        """
    )

st.caption(
    "Dataset: UCI Machine Learning Repository, Online Retail. "
    "This student project is not affiliated with or endorsed by UCI."
)
