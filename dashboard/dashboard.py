import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Afficionado Coffee Roasters Analytics",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .main {
        padding-top: 1rem;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1 {
        font-weight: 700;
    }

    h2 {
        font-weight: 600;
    }

    h3 {
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        font-size: 28px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "Coffee Shop Sales New.xlsx"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_column(df, possible_names):
    """
    Finds a column from a list of possible column names.
    Comparison is case-insensitive and ignores spaces,
    underscores and hyphens.
    """

    normalized_columns = {}

    for col in df.columns:
        normalized = (
            str(col)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )

        normalized_columns[normalized] = col

    for name in possible_names:
        normalized_name = (
            name.strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )

        if normalized_name in normalized_columns:
            return normalized_columns[normalized_name]

    return None


def format_number(value):
    """
    Formats large numbers using full units instead of
    unexplained k/M notation.
    """

    if pd.isna(value):
        return "0"

    return f"{value:,.0f}"


def format_currency(value):
    """
    Formats revenue values using Indian Rupee notation.
    """

    if pd.isna(value):
        return "₹0"

    return f"₹{value:,.2f}"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data(path):

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at: {path}"
        )

    df = pd.read_excel(path)

    return df


# ============================================================
# LOAD DATASET
# ============================================================

try:

    df = load_data(DATA_PATH)

except FileNotFoundError:

    st.error(
        "❌ Dataset not found."
    )

    st.info(
        f"Expected dataset location:\n\n{DATA_PATH}"
    )

    st.stop()

except Exception as e:

    st.error(
        "❌ An error occurred while loading the dataset."
    )

    st.exception(e)

    st.stop()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)


# ============================================================
# IDENTIFY IMPORTANT COLUMNS
# ============================================================

transaction_id_col = find_column(
    df,
    [
        "transaction_id",
        "transaction id",
        "transactionid"
    ]
)

date_col = find_column(
    df,
    [
        "transaction_date",
        "transaction date",
        "transactiondate",
        "date"
    ]
)

time_col = find_column(
    df,
    [
        "transaction_time",
        "transaction time",
        "transactiontime",
        "time"
    ]
)

quantity_col = find_column(
    df,
    [
        "transaction_qty",
        "transaction qty",
        "transaction quantity",
        "quantity",
        "qty"
    ]
)

price_col = find_column(
    df,
    [
        "unit_price",
        "unit price",
        "unitprice",
        "price"
    ]
)

store_location_col = find_column(
    df,
    [
        "store_location",
        "store location",
        "storelocation",
        "location"
    ]
)

store_id_col = find_column(
    df,
    [
        "store_id",
        "store id",
        "storeid"
    ]
)

product_category_col = find_column(
    df,
    [
        "product_category",
        "product category",
        "productcategory"
    ]
)

product_type_col = find_column(
    df,
    [
        "product_type",
        "product type",
        "producttype"
    ]
)


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

missing_columns = []

if date_col is None:
    missing_columns.append("Date")

if time_col is None:
    missing_columns.append("Time")

if quantity_col is None:
    missing_columns.append("Transaction Quantity")

if price_col is None:
    missing_columns.append("Unit Price")

if store_location_col is None:
    missing_columns.append("Store Location")


if missing_columns:

    st.error(
        "❌ Required columns are missing from the dataset."
    )

    st.write(
        "Missing columns:"
    )

    for column in missing_columns:
        st.write(f"- {column}")

    st.write(
        "Available columns:"
    )

    st.write(
        list(df.columns)
    )

    st.stop()


# ============================================================
# DATA TYPE CONVERSION
# ============================================================

df[date_col] = pd.to_datetime(
    df[date_col],
    errors="coerce"
)

df[quantity_col] = pd.to_numeric(
    df[quantity_col],
    errors="coerce"
)

df[price_col] = pd.to_numeric(
    df[price_col],
    errors="coerce"
)


# ============================================================
# REMOVE INVALID ROWS
# ============================================================

df = df.dropna(
    subset=[
        date_col,
        time_col,
        quantity_col,
        price_col,
        store_location_col
    ]
).copy()


# ============================================================
# CONVERT TIME
# ============================================================

def extract_hour(value):

    try:

        if isinstance(value, pd.Timestamp):
            return value.hour

        if hasattr(value, "hour"):
            return value.hour

        time_string = str(value)

        parsed = pd.to_datetime(
            time_string,
            errors="coerce"
        )

        if pd.notna(parsed):
            return parsed.hour

    except Exception:
        pass

    return np.nan


df["hour"] = df[time_col].apply(
    extract_hour
)


df = df.dropna(
    subset=["hour"]
).copy()


df["hour"] = df["hour"].astype(int)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

df["revenue"] = (
    df[quantity_col] *
    df[price_col]
)


df["day_of_week"] = (
    df[date_col]
    .dt.day_name()
)


df["day_number"] = (
    df[date_col]
    .dt.dayofweek
)


df["year"] = (
    df[date_col]
    .dt.year
)


df["month"] = (
    df[date_col]
    .dt.month
)


df["month_name"] = (
    df[date_col]
    .dt.month_name()
)


df["date_only"] = (
    df[date_col]
    .dt.date
)


# ============================================================
# TIME BUCKET
# ============================================================

def get_time_bucket(hour):

    if 6 <= hour <= 11:
        return "Morning"

    elif 12 <= hour <= 16:
        return "Afternoon"

    elif 17 <= hour <= 21:
        return "Evening"

    else:
        return "Late Hours"


df["time_bucket"] = df["hour"].apply(
    get_time_bucket
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "☕ Dashboard Controls"
)

st.sidebar.markdown(
    "---"
)


# ============================================================
# STORE FILTER
# ============================================================

store_options = sorted(
    df[store_location_col]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


selected_stores = st.sidebar.multiselect(
    "🏪 Select Store Location",
    options=store_options,
    default=store_options
)


# ============================================================
# DAY OF WEEK FILTER
# ============================================================

day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


available_days = [
    day for day in day_order
    if day in df["day_of_week"].unique()
]


selected_days = st.sidebar.multiselect(
    "📅 Select Day of Week",
    options=available_days,
    default=available_days
)


# ============================================================
# HOUR RANGE FILTER
# ============================================================

selected_hour_range = st.sidebar.slider(
    "⏰ Select Hour Range",
    min_value=0,
    max_value=23,
    value=(0, 23),
    step=1
)


# ============================================================
# METRIC SELECTOR
# ============================================================

metric_option = st.sidebar.radio(
    "📊 Select Metric",
    [
        "Revenue",
        "Transaction Quantity"
    ]
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    df[store_location_col]
    .astype(str)
    .isin(selected_stores)
].copy()


filtered_df = filtered_df[
    filtered_df["day_of_week"]
    .isin(selected_days)
].copy()


filtered_df = filtered_df[
    (filtered_df["hour"] >= selected_hour_range[0]) &
    (filtered_df["hour"] <= selected_hour_range[1])
].copy()


# ============================================================
# HEADER
# ============================================================

st.title(
    "☕ Afficionado Coffee Roasters"
)

st.subheader(
    "Sales Trend and Time-Based Performance Analysis"
)

st.markdown(
    """
    This interactive dashboard analyses coffee shop transaction
    data to uncover sales trends, customer demand patterns,
    peak hours, day-of-week performance, and store-level behaviour.
    """
)


st.markdown("---")


# ============================================================
# NO DATA WARNING
# ============================================================

if filtered_df.empty:

    st.warning(
        "⚠️ No data available for the selected filters."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_revenue = filtered_df["revenue"].sum()

total_quantity = filtered_df[quantity_col].sum()

total_transactions = (
    filtered_df[transaction_id_col].nunique()
    if transaction_id_col is not None
    else len(filtered_df)
)

average_transaction_value = (
    total_revenue /
    total_transactions
    if total_transactions > 0
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "💰 Total Revenue",
        format_currency(total_revenue)
    )


with col2:

    st.metric(
        "📦 Total Quantity",
        format_number(total_quantity)
    )


with col3:

    st.metric(
        "🧾 Total Transactions",
        format_number(total_transactions)
    )


with col4:

    st.metric(
        "💳 Avg. Transaction Value",
        format_currency(
            average_transaction_value
        )
    )


st.markdown("---")


# ============================================================
# SALES TREND
# ============================================================

st.header(
    "📈 Overall Sales Trend"
)


daily_sales = (
    filtered_df
    .groupby("date_only")
    .agg(
        revenue=("revenue", "sum"),
        quantity=(quantity_col, "sum")
    )
    .reset_index()
)


if metric_option == "Revenue":

    fig = px.line(
        daily_sales,
        x="date_only",
        y="revenue",
        markers=True,
        title="Daily Revenue Trend",
        labels={
            "date_only": "Date",
            "revenue": "Revenue (£)"
        }
    )

    fig.update_yaxes(
        tickprefix="£",
        separatethousands=True
    )

else:

    fig = px.line(
        daily_sales,
        x="date_only",
        y="quantity",
        markers=True,
        title="Daily Transaction Quantity Trend",
        labels={
            "date_only": "Date",
            "quantity": "Transaction Quantity"
        }
    )

    fig.update_yaxes(
        separatethousands=True
    )


fig.update_layout(
    hovermode="x unified"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# DAY OF WEEK ANALYSIS
# ============================================================

st.header(
    "📅 Day-of-Week Performance"
)


day_summary = (
    filtered_df
    .groupby(
        ["day_of_week", "day_number"]
    )
    .agg(
        revenue=("revenue", "sum"),
        quantity=(quantity_col, "sum"),
        transactions=(
            transaction_id_col,
            "nunique"
        ) if transaction_id_col else (
            quantity_col,
            "count"
        )
    )
    .reset_index()
)


day_summary = day_summary.sort_values(
    "day_number"
)


col1, col2 = st.columns(2)


with col1:

    if metric_option == "Revenue":

        fig_day = px.bar(
            day_summary,
            x="day_of_week",
            y="revenue",
            title="Revenue by Day of Week",
            labels={
                "day_of_week": "Day",
                "revenue": "Revenue (£)"
            },
            text_auto=".2s"
        )

        fig_day.update_yaxes(
            tickprefix="£",
            separatethousands=True
        )

    else:

        fig_day = px.bar(
            day_summary,
            x="day_of_week",
            y="quantity",
            title="Transaction Quantity by Day of Week",
            labels={
                "day_of_week": "Day",
                "quantity": "Transaction Quantity"
            },
            text_auto=".2s"
        )


    st.plotly_chart(
        fig_day,
        use_container_width=True
    )


with col2:

    fig_transactions = px.bar(
        day_summary,
        x="day_of_week",
        y="transactions",
        title="Transactions by Day of Week",
        labels={
            "day_of_week": "Day",
            "transactions": "Number of Transactions"
        },
        text_auto=".2s"
    )


    st.plotly_chart(
        fig_transactions,
        use_container_width=True
    )


# ============================================================
# HOURLY DEMAND
# ============================================================

st.header(
    "⏰ Time-of-Day Demand Analysis"
)


hour_summary = (
    filtered_df
    .groupby("hour")
    .agg(
        revenue=("revenue", "sum"),
        quantity=(quantity_col, "sum"),
        transactions=(
            transaction_id_col,
            "nunique"
        ) if transaction_id_col else (
            quantity_col,
            "count"
        )
    )
    .reset_index()
)


col1, col2 = st.columns(2)


with col1:

    if metric_option == "Revenue":

        fig_hour = px.bar(
            hour_summary,
            x="hour",
            y="revenue",
            title="Hourly Revenue Distribution",
            labels={
                "hour": "Hour of Day",
                "revenue": "Revenue (£)"
            }
        )

        fig_hour.update_yaxes(
            tickprefix="£",
            separatethousands=True
        )

    else:

        fig_hour = px.bar(
            hour_summary,
            x="hour",
            y="quantity",
            title="Hourly Transaction Quantity",
            labels={
                "hour": "Hour of Day",
                "quantity": "Transaction Quantity"
            }
        )


    st.plotly_chart(
        fig_hour,
        use_container_width=True
    )


with col2:

    fig_transaction_hour = px.line(
        hour_summary,
        x="hour",
        y="transactions",
        markers=True,
        title="Hourly Transaction Volume",
        labels={
            "hour": "Hour of Day",
            "transactions": "Number of Transactions"
        }
    )


    st.plotly_chart(
        fig_transaction_hour,
        use_container_width=True
    )


# ============================================================
# PEAK HOUR ANALYSIS
# ============================================================

st.subheader(
    "🔥 Peak and Off-Peak Hours"
)


if not hour_summary.empty:

    peak_row = hour_summary.loc[
        hour_summary["transactions"].idxmax()
    ]

    slow_row = hour_summary.loc[
        hour_summary["transactions"].idxmin()
    ]


    col1, col2 = st.columns(2)


    with col1:

        st.success(
            f"🔥 Peak Hour: {int(peak_row['hour']):02d}:00 "
            f"with {format_number(peak_row['transactions'])} transactions."
        )


    with col2:

        st.info(
            f"📉 Lowest Activity Hour: "
            f"{int(slow_row['hour']):02d}:00 "
            f"with {format_number(slow_row['transactions'])} transactions."
        )


# ============================================================
# TIME BUCKET ANALYSIS
# ============================================================

st.header(
    "🕐 Demand by Time Period"
)


bucket_order = [
    "Morning",
    "Afternoon",
    "Evening",
    "Late Hours"
]


bucket_summary = (
    filtered_df
    .groupby("time_bucket")
    .agg(
        revenue=("revenue", "sum"),
        quantity=(quantity_col, "sum"),
        transactions=(
            transaction_id_col,
            "nunique"
        ) if transaction_id_col else (
            quantity_col,
            "count"
        )
    )
    .reset_index()
)


bucket_summary["time_bucket"] = pd.Categorical(
    bucket_summary["time_bucket"],
    categories=bucket_order,
    ordered=True
)


bucket_summary = bucket_summary.sort_values(
    "time_bucket"
)


if metric_option == "Revenue":

    fig_bucket = px.bar(
        bucket_summary,
        x="time_bucket",
        y="revenue",
        title="Revenue by Time Period",
        labels={
            "time_bucket": "Time Period",
            "revenue": "Revenue (£)"
        },
        text_auto=".2s"
    )

    fig_bucket.update_yaxes(
        tickprefix="£",
        separatethousands=True
    )

else:

    fig_bucket = px.bar(
        bucket_summary,
        x="time_bucket",
        y="quantity",
        title="Transaction Quantity by Time Period",
        labels={
            "time_bucket": "Time Period",
            "quantity": "Transaction Quantity"
        },
        text_auto=".2s"
    )


st.plotly_chart(
    fig_bucket,
    use_container_width=True
)


# ============================================================
# STORE COMPARISON
# ============================================================

st.header(
    "🏪 Store Location Comparison"
)


store_summary = (
    filtered_df
    .groupby(store_location_col)
    .agg(
        revenue=("revenue", "sum"),
        quantity=(quantity_col, "sum"),
        transactions=(
            transaction_id_col,
            "nunique"
        ) if transaction_id_col else (
            quantity_col,
            "count"
        )
    )
    .reset_index()
)


if metric_option == "Revenue":

    fig_store = px.bar(
        store_summary,
        x=store_location_col,
        y="revenue",
        title="Revenue by Store Location",
        labels={
            store_location_col: "Store Location",
            "revenue": "Revenue (£)"
        },
        text_auto=".2s"
    )

    fig_store.update_yaxes(
        tickprefix="£",
        separatethousands=True
    )

else:

    fig_store = px.bar(
        store_summary,
        x=store_location_col,
        y="quantity",
        title="Transaction Quantity by Store Location",
        labels={
            store_location_col: "Store Location",
            "quantity": "Transaction Quantity"
        },
        text_auto=".2s"
    )


st.plotly_chart(
    fig_store,
    use_container_width=True
)


# ============================================================
# STORE × HOUR HEATMAP
# ============================================================

st.header(
    "🔥 Store-Level Hourly Demand Heatmap"
)


heatmap_data = (
    filtered_df
    .pivot_table(
        index=store_location_col,
        columns="hour",
        values=(
            "revenue"
            if metric_option == "Revenue"
            else quantity_col
        ),
        aggfunc="sum",
        fill_value=0
    )
)


if not heatmap_data.empty:

    if metric_option == "Revenue":

        heatmap_title = (
            "Revenue Heatmap by Store and Hour"
        )

        colorbar_title = "Revenue (£)"

    else:

        heatmap_title = (
            "Transaction Quantity Heatmap by Store and Hour"
        )

        colorbar_title = "Quantity"


    fig_heatmap = px.imshow(
        heatmap_data,
        aspect="auto",
        title=heatmap_title,
        labels={
            "x": "Hour of Day",
            "y": "Store Location",
            "color": colorbar_title
        }
    )


    st.plotly_chart(
        fig_heatmap,
        use_container_width=True
    )


# ============================================================
# STORE × DAY ANALYSIS
# ============================================================

st.header(
    "📊 Store and Day-of-Week Comparison"
)


store_day = (
    filtered_df
    .groupby(
        [
            store_location_col,
            "day_of_week",
            "day_number"
        ]
    )
    .agg(
        revenue=("revenue", "sum"),
        quantity=(quantity_col, "sum"),
        transactions=(
            transaction_id_col,
            "nunique"
        ) if transaction_id_col else (
            quantity_col,
            "count"
        )
    )
    .reset_index()
)


store_day = store_day.sort_values(
    "day_number"
)


if metric_option == "Revenue":

    fig_store_day = px.bar(
        store_day,
        x="day_of_week",
        y="revenue",
        color=store_location_col,
        barmode="group",
        title="Revenue by Day and Store Location",
        labels={
            "day_of_week": "Day",
            "revenue": "Revenue (£)",
            store_location_col: "Store"
        }
    )

    fig_store_day.update_yaxes(
        tickprefix="£",
        separatethousands=True
    )

else:

    fig_store_day = px.bar(
        store_day,
        x="day_of_week",
        y="quantity",
        color=store_location_col,
        barmode="group",
        title="Transaction Quantity by Day and Store Location",
        labels={
            "day_of_week": "Day",
            "quantity": "Transaction Quantity",
            store_location_col: "Store"
        }
    )


st.plotly_chart(
    fig_store_day,
    use_container_width=True
)


# ============================================================
# PRODUCT CATEGORY ANALYSIS
# ============================================================

if product_category_col is not None:

    st.header(
        "☕ Product Category Performance"
    )


    product_summary = (
        filtered_df
        .groupby(product_category_col)
        .agg(
            revenue=("revenue", "sum"),
            quantity=(quantity_col, "sum")
        )
        .reset_index()
        .sort_values(
            "revenue",
            ascending=False
        )
    )


    col1, col2 = st.columns(2)


    with col1:

        fig_product_revenue = px.bar(
            product_summary.head(15),
            x="revenue",
            y=product_category_col,
            orientation="h",
            title="Top Product Categories by Revenue",
            labels={
                "revenue": "Revenue (£)",
                product_category_col: "Product Category"
            }
        )

        fig_product_revenue.update_xaxes(
            tickprefix="£",
            separatethousands=True
        )


        st.plotly_chart(
            fig_product_revenue,
            use_container_width=True
        )


    with col2:

        fig_product_quantity = px.bar(
            product_summary.head(15),
            x="quantity",
            y=product_category_col,
            orientation="h",
            title="Top Product Categories by Quantity",
            labels={
                "quantity": "Transaction Quantity",
                product_category_col: "Product Category"
            }
        )


        st.plotly_chart(
            fig_product_quantity,
            use_container_width=True
        )


# ============================================================
# DATA SUMMARY
# ============================================================

st.header(
    "📋 Filtered Data Summary"
)


summary_col1, summary_col2, summary_col3 = st.columns(3)


with summary_col1:

    st.write(
        f"**Rows Analysed:** "
        f"{format_number(len(filtered_df))}"
    )


with summary_col2:

    st.write(
        f"**Stores Selected:** "
        f"{filtered_df[store_location_col].nunique()}"
    )


with summary_col3:

    st.write(
        f"**Date Range:** "
        f"{filtered_df['date_only'].min()} "
        f"to "
        f"{filtered_df['date_only'].max()}"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align: center;">
        <p>
        ☕ <b>Afficionado Coffee Roasters</b>
        — Sales Trend and Time-Based Performance Analysis
        </p>
        <p>
        Built with Python, Pandas, Plotly and Streamlit
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
