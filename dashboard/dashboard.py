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
    page_title="Afficionado Coffee Roasters | Sales Analytics",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# TITLE
# ============================================================

st.title("☕ Afficionado Coffee Roasters")
st.subheader("Sales Trend and Time-Based Performance Analysis")

st.markdown(
    """
    This interactive dashboard analyses sales patterns across dates, 
    days of the week, hours of the day, time periods, and store locations.
    
    The objective is to support evidence-based decisions related to:
    
    - Staff scheduling
    - Operational planning
    - Store-level performance
    - Peak and off-peak demand
    - Inventory planning
    - Customer experience
    """
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data():

    # --------------------------------------------------------
    # YOUR DATASET PATH
    # --------------------------------------------------------
    DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "Coffee Shop Sales New.xlsx"
)
    DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "Coffee Shop Sales New.xlsx"
)

    # Check whether file exists
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"""
            Dataset not found.

            Expected location:
            {DATA_PATH}

            Please make sure that:
            1. The file exists.
            2. The file name is exactly:
               Coffee Shop Sales New.xlsx
            3. The file is inside the data folder.
            """
        )

    # Read Excel file
    df = pd.read_excel(DATA_PATH)

    # --------------------------------------------------------
    # REQUIRED COLUMNS
    # --------------------------------------------------------

    required_columns = [
        "transaction_id",
        "transaction_date",
        "transaction_time",
        "transaction_qty",
        "unit_price",
        "store_id",
        "store_location",
        "product_id",
        "product_category",
        "product_type",
        "product_detail"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # --------------------------------------------------------
    # DATA TYPE CONVERSION
    # --------------------------------------------------------

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

    # Convert transaction time
    df["transaction_time"] = pd.to_datetime(
        df["transaction_time"].astype(str),
        format="%H:%M:%S",
        errors="coerce"
    )

    # --------------------------------------------------------
    # FEATURE ENGINEERING
    # --------------------------------------------------------

    # Revenue per transaction
    df["revenue"] = (
        df["transaction_qty"] *
        df["unit_price"]
    )

    # Hour of day
    df["hour"] = df["transaction_time"].dt.hour

    # Day of week
    df["day_of_week"] = (
        df["transaction_date"]
        .dt.day_name()
    )

    # Day number
    df["day_of_week_num"] = (
        df["transaction_date"]
        .dt.dayofweek
    )

    # Week starting date
    df["week_start"] = (
        df["transaction_date"]
        - pd.to_timedelta(
            df["transaction_date"].dt.dayofweek,
            unit="D"
        )
    )

    # Month
    df["month"] = (
        df["transaction_date"]
        .dt.to_period("M")
        .astype(str)
    )

    # Weekend indicator
    df["is_weekend"] = (
        df["day_of_week_num"] >= 5
    )

    # --------------------------------------------------------
    # TIME BUCKET
    # --------------------------------------------------------

    def get_time_bucket(hour):

        if 6 <= hour <= 11:
            return "Morning"

        elif 12 <= hour <= 16:
            return "Afternoon"

        elif 17 <= hour <= 21:
            return "Evening"

        else:
            return "Late Hours"

    df["time_bucket"] = (
        df["hour"]
        .apply(get_time_bucket)
    )

    return df


# ============================================================
# LOAD DATA
# ============================================================

try:

    df = load_data()

except Exception as e:

    st.error(
        "❌ Unable to load the dataset."
    )

    st.exception(e)

    st.stop()


# ============================================================
# DATASET INFORMATION
# ============================================================

st.sidebar.success(
    "✅ Dataset loaded successfully"
)

st.sidebar.write(
    f"**Records:** {len(df):,}"
)

st.sidebar.write(
    f"**Date Range:** "
    f"{df['transaction_date'].min().date()} "
    f"to "
    f"{df['transaction_date'].max().date()}"
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Dashboard Filters")


# ------------------------------------------------------------
# DATE FILTER
# ------------------------------------------------------------

min_date = df["transaction_date"].min().date()
max_date = df["transaction_date"].max().date()

date_range = st.sidebar.date_input(
    "Transaction Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


if isinstance(date_range, tuple) and len(date_range) == 2:

    start_date = date_range[0]
    end_date = date_range[1]

else:

    start_date = date_range
    end_date = date_range


# ------------------------------------------------------------
# STORE FILTER
# ------------------------------------------------------------

stores = [
    "All"
] + sorted(
    df["store_location"]
    .dropna()
    .unique()
    .tolist()
)

selected_store = st.sidebar.selectbox(
    "Store Location",
    stores
)


# ------------------------------------------------------------
# DAY OF WEEK FILTER
# ------------------------------------------------------------

day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

days = ["All"] + day_order

selected_day = st.sidebar.selectbox(
    "Day of Week",
    days
)


# ------------------------------------------------------------
# HOUR FILTER
# ------------------------------------------------------------

hour_range = st.sidebar.slider(
    "Hour Range",
    min_value=0,
    max_value=23,
    value=(0, 23)
)


# ------------------------------------------------------------
# REVENUE / QUANTITY TOGGLE
# ------------------------------------------------------------

metric = st.sidebar.radio(
    "Select Analysis Metric",
    [
        "Revenue",
        "Quantity"
    ]
)


# ============================================================
# FILTER DATA
# ============================================================

filtered = df[
    (df["transaction_date"].dt.date >= start_date)
    &
    (df["transaction_date"].dt.date <= end_date)
    &
    (df["hour"] >= hour_range[0])
    &
    (df["hour"] <= hour_range[1])
].copy()


# Store filter

if selected_store != "All":

    filtered = filtered[
        filtered["store_location"]
        == selected_store
    ]


# Day filter

if selected_day != "All":

    filtered = filtered[
        filtered["day_of_week"]
        == selected_day
    ]


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if filtered.empty:

    st.warning(
        "⚠️ No transactions match the selected filters."
    )

    st.stop()


# ============================================================
# METRIC SELECTION
# ============================================================

if metric == "Revenue":

    value_col = "revenue"

    value_label = "Revenue (£)"

else:

    value_col = "transaction_qty"

    value_label = "Quantity Sold (Items)"


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_revenue = (
    filtered["revenue"].sum()
)

total_transactions = (
    filtered["transaction_id"]
    .nunique()
)

total_quantity = (
    filtered["transaction_qty"]
    .sum()
)

average_order_value = (

    total_revenue
    / total_transactions

    if total_transactions > 0
    else 0
)


# Peak hour

hourly_transactions = (

    filtered
    .groupby("hour")
    ["transaction_id"]
    .nunique()
)


peak_hour = int(
    hourly_transactions.idxmax()
)


# Best day

daily_revenue = (

    filtered
    .groupby("transaction_date")
    ["revenue"]
    .sum()
)

best_day_date = (
    daily_revenue.idxmax()
)

best_day_revenue = (
    daily_revenue.max()
)


# Best day of week

dow_revenue = (

    filtered
    .groupby(
        [
            "day_of_week_num",
            "day_of_week"
        ]
    )
    ["revenue"]
    .sum()
)

best_dow = (
    dow_revenue
    .idxmax()[1]
)


# ============================================================
# KPI DISPLAY
# ============================================================

st.markdown("---")

st.header("📊 Key Performance Indicators")


k1, k2, k3, k4, k5 = st.columns(5)


with k1:

    st.metric(
        "Total Revenue",
        f"£{total_revenue:,.2f}"
    )


with k2:

    st.metric(
        "Transactions",
        f"{total_transactions:,}"
    )


with k3:

    st.metric(
        "Quantity Sold",
        f"{total_quantity:,}"
    )


with k4:

    st.metric(
        "Peak Transaction Hour",
        f"{peak_hour:02d}:00"
    )


with k5:

    st.metric(
        "Best Day of Week",
        best_dow
    )


# ============================================================
# MODULE 1
# OVERALL SALES TREND
# ============================================================

st.markdown("---")

st.header(
    "1️⃣ Overall Sales Trend Analysis"
)


# ------------------------------------------------------------
# DAILY TREND
# ------------------------------------------------------------

daily = (

    filtered
    .groupby("transaction_date")
    .agg(
        revenue=(
            "revenue",
            "sum"
        ),

        quantity=(
            "transaction_qty",
            "sum"
        ),

        transactions=(
            "transaction_id",
            "nunique"
        )
    )

    .reset_index()
)


fig_daily = px.line(

    daily,

    x="transaction_date",

    y=value_col,

    markers=True,

    title=(
        f"Daily {value_label} Trend"
    )
)


fig_daily.update_layout(

    xaxis_title="Transaction Date",

    yaxis_title=value_label
)


st.plotly_chart(

    fig_daily,

    use_container_width=True
)


# ------------------------------------------------------------
# WEEKLY TREND
# ------------------------------------------------------------

weekly = (

    filtered
    .groupby("week_start")
    .agg(

        revenue=(
            "revenue",
            "sum"
        ),

        quantity=(
            "transaction_qty",
            "sum"
        ),

        transactions=(
            "transaction_id",
            "nunique"
        )
    )

    .reset_index()
)


fig_weekly = px.bar(

    weekly,

    x="week_start",

    y=value_col,

    title=(
        f"Weekly {value_label} Aggregation"
    )
)


fig_weekly.update_layout(

    xaxis_title="Week Starting",

    yaxis_title=value_label
)


st.plotly_chart(

    fig_weekly,

    use_container_width=True
)


# ------------------------------------------------------------
# TREND INTERPRETATION
# ------------------------------------------------------------

if len(daily) >= 2:

    x = np.arange(
        len(daily)
    )

    y = daily[
        value_col
    ].values

    slope = np.polyfit(
        x,
        y,
        1
    )[0]


    if slope > 0:

        st.success(
            "📈 Overall trend: "
            "The selected metric shows an upward direction "
            "over the selected period."
        )


    elif slope < 0:

        st.warning(
            "📉 Overall trend: "
            "The selected metric shows a downward direction "
            "over the selected period."
        )


    else:

        st.info(
            "➡️ Overall trend: "
            "The selected metric is broadly stable "
            "over the selected period."
        )


# ============================================================
# MODULE 2
# DAY OF WEEK PERFORMANCE
# ============================================================

st.markdown("---")

st.header(
    "2️⃣ Day-of-Week Performance Analysis"
)


dow = (

    filtered
    .groupby(
        [
            "day_of_week_num",
            "day_of_week"
        ]
    )
    .agg(

        revenue=(
            "revenue",
            "sum"
        ),

        transactions=(
            "transaction_id",
            "nunique"
        ),

        quantity=(
            "transaction_qty",
            "sum"
        )
    )

    .reset_index()

    .sort_values(
        "day_of_week_num"
    )
)


# ------------------------------------------------------------
# REVENUE / QUANTITY BY DAY
# ------------------------------------------------------------

fig_dow = px.bar(

    dow,

    x="day_of_week",

    y=value_col,

    category_orders={
        "day_of_week":
        day_order
    },

    text_auto=".2s",

    title=(
        f"{value_label} by Day of Week"
    )
)


fig_dow.update_layout(

    xaxis_title="Day of Week",

    yaxis_title=value_label
)


st.plotly_chart(

    fig_dow,

    use_container_width=True
)


# ------------------------------------------------------------
# TRANSACTION COUNT BY DAY
# ------------------------------------------------------------

fig_dow_transactions = px.bar(

    dow,

    x="day_of_week",

    y="transactions",

    category_orders={
        "day_of_week":
        day_order
    },

    text_auto=".2s",

    title=(
        "Transaction Count by Day of Week"
    )
)


fig_dow_transactions.update_layout(

    xaxis_title="Day of Week",

    yaxis_title="Number of Transactions"
)


st.plotly_chart(

    fig_dow_transactions,

    use_container_width=True
)


# ------------------------------------------------------------
# AVERAGE DAILY PERFORMANCE
# ------------------------------------------------------------

weekday_stats = (

    filtered

    .groupby(
        [
            "day_of_week_num",
            "day_of_week"
        ]
    )

    .agg(

        total_revenue=(
            "revenue",
            "sum"
        ),

        total_transactions=(
            "transaction_id",
            "nunique"
        ),

        days_observed=(
            "transaction_date",
            "nunique"
        )
    )

    .reset_index()
)


weekday_stats[
    "avg_revenue_per_day"
] = (

    weekday_stats[
        "total_revenue"
    ]

    /

    weekday_stats[
        "days_observed"
    ]
)


weekday_stats[
    "avg_transactions_per_day"
] = (

    weekday_stats[
        "total_transactions"
    ]

    /

    weekday_stats[
        "days_observed"
    ]
)


weekday_stats = (

    weekday_stats

    .sort_values(
        "day_of_week_num"
    )
)


c1, c2 = st.columns(2)


with c1:

    fig_avg_rev = px.bar(

        weekday_stats,

        x="day_of_week",

        y="avg_revenue_per_day",

        category_orders={
            "day_of_week":
            day_order
        },

        title=(
            "Average Revenue per Calendar Day"
        )
    )

    fig_avg_rev.update_layout(

        xaxis_title="Day",

        yaxis_title="Average Revenue (£)"
    )

    st.plotly_chart(

        fig_avg_rev,

        use_container_width=True
    )


with c2:

    fig_avg_txn = px.bar(

        weekday_stats,

        x="day_of_week",

        y="avg_transactions_per_day",

        category_orders={
            "day_of_week":
            day_order
        },

        title=(
            "Average Transactions per Calendar Day"
        )
    )

    fig_avg_txn.update_layout(

        xaxis_title="Day",

        yaxis_title="Average Transactions"
    )

    st.plotly_chart(

        fig_avg_txn,

        use_container_width=True
    )


# ------------------------------------------------------------
# WEEKDAY VS WEEKEND
# ------------------------------------------------------------

filtered["period_type"] = np.where(

    filtered[
        "is_weekend"
    ],

    "Weekend",

    "Weekday"
)


weekday_weekend = (

    filtered

    .groupby(
        "period_type"
    )

    .agg(

        revenue=(
            "revenue",
            "sum"
        ),

        transactions=(
            "transaction_id",
            "nunique"
        ),

        quantity=(
            "transaction_qty",
            "sum"
        )
    )

    .reset_index()
)


fig_weekend = px.bar(

    weekday_weekend,

    x="period_type",

    y=value_col,

    text_auto=".2s",

    title=(
        f"Weekday vs Weekend "
        f"{value_label}"
    )
)


st.plotly_chart(

    fig_weekend,

    use_container_width=True
)


# ============================================================
# MODULE 3
# TIME OF DAY ANALYSIS
# ============================================================

st.markdown("---")

st.header(
    "3️⃣ Time-of-Day Demand Analysis"
)


# ------------------------------------------------------------
# HOURLY DATA
# ------------------------------------------------------------

hourly = (

    filtered

    .groupby("hour")

    .agg(

        revenue=(
            "revenue",
            "sum"
        ),

        quantity=(
            "transaction_qty",
            "sum"
        ),

        transactions=(
            "transaction_id",
            "nunique"
        )
    )

    .reset_index()
)


# ------------------------------------------------------------
# HOURLY TRANSACTION VOLUME
# ------------------------------------------------------------

fig_hour_transactions = px.line(

    hourly,

    x="hour",

    y="transactions",

    markers=True,

    title=(
        "Hourly Transaction Volume Curve"
    )
)


fig_hour_transactions.update_layout(

    xaxis_title="Hour of Day (0–23)",

    yaxis_title="Number of Transactions"
)


st.plotly_chart(

    fig_hour_transactions,

    use_container_width=True
)


# ------------------------------------------------------------
# HOURLY REVENUE / QUANTITY
# ------------------------------------------------------------

fig_hour_value = px.bar(

    hourly,

    x="hour",

    y=value_col,

    text_auto=".2s",

    title=(
        f"Hourly {value_label} Distribution"
    )
)


fig_hour_value.update_layout(

    xaxis_title="Hour of Day (0–23)",

    yaxis_title=value_label
)


st.plotly_chart(

    fig_hour_value,

    use_container_width=True
)


# ------------------------------------------------------------
# TIME BUCKET
# ------------------------------------------------------------

bucket_order = [

    "Morning",

    "Afternoon",

    "Evening",

    "Late Hours"
]


bucket = (

    filtered

    .groupby(
        "time_bucket"
    )

    .agg(

        revenue=(
            "revenue",
            "sum"
        ),

        quantity=(
            "transaction_qty",
            "sum"
        ),

        transactions=(
            "transaction_id",
            "nunique"
        )
    )

    .reindex(
        bucket_order
    )

    .reset_index()
)


fig_bucket = px.bar(

    bucket,

    x="time_bucket",

    y=value_col,

    category_orders={

        "time_bucket":

        bucket_order

    },

    text_auto=".2s",

    title=(

        f"{value_label} "

        "by Time Bucket"

    )
)


fig_bucket.update_layout(

    xaxis_title="Time Bucket",

    yaxis_title=value_label
)


st.plotly_chart(

    fig_bucket,

    use_container_width=True
)


# ------------------------------------------------------------
# PEAK / LOW HOURS
# ------------------------------------------------------------

peak_hour_row = (

    hourly.loc[

        hourly[
            "transactions"
        ].idxmax()

    ]
)


slow_hour_row = (

    hourly.loc[

        hourly[
            "transactions"
        ].idxmin()

    ]
)


st.info(

    f"""
    🔥 **Peak transaction hour:**
    {int(peak_hour_row['hour']):02d}:00

    Transactions:
    {int(peak_hour_row['transactions']):,}

    💤 **Lowest observed transaction hour:**
    {int(slow_hour_row['hour']):02d}:00

    Transactions:
    {int(slow_hour_row['transactions']):,}
    """
)


# ============================================================
# MODULE 4
# CROSS LOCATION TEMPORAL COMPARISON
# ============================================================

st.markdown("---")

st.header(
    "4️⃣ Cross-Location Temporal Comparison"
)


# ------------------------------------------------------------
# STORE-WISE HOURLY ANALYSIS
# ------------------------------------------------------------

store_hour = (

    filtered

    .groupby(
        [
            "store_location",
            "hour"
        ]
    )

    .agg(

        revenue=(
            "revenue",
            "sum"
        ),

        quantity=(
            "transaction_qty",
            "sum"
        ),

        transactions=(
            "transaction_id",
            "nunique"
        )
    )

    .reset_index()
)


fig_store_hour = px.line(

    store_hour,

    x="hour",

    y=value_col,

    color="store_location",

    markers=True,

    title=(

        f"Store-wise Hourly "

        f"{value_label}"

    )
)


fig_store_hour.update_layout(

    xaxis_title="Hour of Day",

    yaxis_title=value_label
)


st.plotly_chart(

    fig_store_hour,

    use_container_width=True
)


# ============================================================
# TRANSACTION COUNT HEATMAP
# ============================================================

st.subheader(
    "📍 Store × Hour Transaction Count Heatmap"
)


heatmap_transactions = (

    filtered

    .pivot_table(

        index="store_location",

        columns="hour",

        values="transaction_id",

        aggfunc="nunique",

        fill_value=0

    )
)


fig_transaction_heatmap = px.imshow(

    heatmap_transactions,

    aspect="auto",

    text_auto=".0f",

    title=(

        "Hourly Transaction Count "

        "Heatmap by Store"

    ),

    labels={

        "x":
        "Hour of Day",

        "y":
        "Store Location",

        "color":
        "Transactions"

    }
)


fig_transaction_heatmap.update_layout(

    xaxis_title=
    "Hour of Day (0–23)",

    yaxis_title=
    "Store Location"
)


st.plotly_chart(

    fig_transaction_heatmap,

    use_container_width=True
)


# ============================================================
# REVENUE HEATMAP
# ============================================================

st.subheader(
    "💰 Store × Hour Revenue Heatmap"
)


heatmap_revenue = (

    filtered

    .pivot_table(

        index="store_location",

        columns="hour",

        values="revenue",

        aggfunc="sum",

        fill_value=0

    )
)


fig_revenue_heatmap = px.imshow(

    heatmap_revenue,

    aspect="auto",

    text_auto=".2s",

    title=(

        "Hourly Revenue "

        "Heatmap by Store"

    ),

    labels={

        "x":
        "Hour of Day",

        "y":
        "Store Location",

        "color":
        "Revenue (£)"

    }
)


fig_revenue_heatmap.update_layout(

    xaxis_title=
    "Hour of Day (0–23)",

    yaxis_title=
    "Store Location"
)


st.plotly_chart(

    fig_revenue_heatmap,

    use_container_width=True
)


# ============================================================
# STORE SPECIFIC PEAK HOURS
# ============================================================

st.subheader(
    "📌 Location-Specific Peak Hours"
)


store_peak_rows = (

    store_hour.loc[

        store_hour

        .groupby(
            "store_location"
        )

        [
            "transactions"
        ]

        .idxmax()

    ]

    .sort_values(
        "store_location"
    )
)


store_peak_display = (

    store_peak_rows

    .rename(

        columns={

            "store_location":
            "Store Location",

            "hour":
            "Peak Hour",

            "transactions":
            "Peak-Hour Transactions"

        }

    )

)


st.dataframe(

    store_peak_display,

    use_container_width=True,

    hide_index=True
)


# ============================================================
# STORE DAILY TREND
# ============================================================

st.subheader(
    "📈 Store-Level Daily Revenue Trends"
)


store_daily = (

    filtered

    .groupby(

        [
            "transaction_date",

            "store_location"

        ]

    )

    .agg(

        revenue=(
            "revenue",
            "sum"
        ),

        transactions=(
            "transaction_id",
            "nunique"
        )
    )

    .reset_index()
)


fig_store_daily = px.line(

    store_daily,

    x="transaction_date",

    y="revenue",

    color="store_location",

    title=(
        "Daily Revenue Trend "
        "by Store"
    )
)


fig_store_daily.update_layout(

    xaxis_title="Date",

    yaxis_title="Revenue (£)"
)


st.plotly_chart(

    fig_store_daily,

    use_container_width=True
)


# ============================================================
# MODULE 5
# PRODUCT CATEGORY CONTEXT
# ============================================================

st.markdown("---")

st.header(
    "5️⃣ Product Category Performance"
)


category = (

    filtered

    .groupby(
        "product_category"
    )

    .agg(

        revenue=(
            "revenue",
            "sum"
        ),

        quantity=(
            "transaction_qty",
            "sum"
        ),

        transactions=(
            "transaction_id",
            "nunique"
        )
    )

    .reset_index()

    .sort_values(

        value_col,

        ascending=False

    )
)


fig_category = px.bar(

    category,

    x="product_category",

    y=value_col,

    text_auto=".2s",

    title=(

        f"{value_label} "

        "by Product Category"

    )
)


fig_category.update_layout(

    xaxis_title=
    "Product Category",

    yaxis_title=
    value_label
)


st.plotly_chart(

    fig_category,

    use_container_width=True
)


# ============================================================
# MODULE 6
# EVIDENCE BASED BUSINESS INSIGHTS
# ============================================================

st.markdown("---")

st.header(
    "6️⃣ Evidence-Based Business Insights"
)


# Top store

top_store = (

    filtered

    .groupby(
        "store_location"
    )

    ["revenue"]

    .sum()

    .idxmax()
)


# Top category

top_category = (

    filtered

    .groupby(
        "product_category"
    )

    ["revenue"]

    .sum()

    .idxmax()
)


# Peak bucket

peak_bucket = (

    bucket.loc[

        bucket[
            "transactions"
        ].idxmax(),

        "time_bucket"

    ]
)


# Best weekday

best_weekday = (

    weekday_stats.loc[

        weekday_stats[
            "avg_revenue_per_day"
        ].idxmax(),

        "day_of_week"

    ]
)


# Lowest weekday

lowest_weekday = (

    weekday_stats.loc[

        weekday_stats[
            "avg_revenue_per_day"
        ].idxmin(),

        "day_of_week"

    ]
)


st.success(

    f"""
    ### Key Findings

    • **Highest-revenue store:** {top_store}

    • **Peak transaction hour:** {peak_hour:02d}:00

    • **Highest-demand time bucket:** {peak_bucket}

    • **Best average-revenue day:** {best_weekday}

    • **Lowest average-revenue day:** {lowest_weekday}

    • **Highest-revenue product category:** {top_category}

    • **Best recorded date:** {best_day_date.date()}

    • **Revenue on best recorded date:** £{best_day_revenue:,.2f}

    ### Operational Recommendations

    • Staff levels should be increased during store-specific peak hours.

    • Staffing should be reduced or optimized during consistently low-demand periods.

    • High-volume products should be stocked before identified peak periods.

    • Promotions can be targeted toward lower-demand periods.

    • Store-level peak-hour differences should be considered when creating employee schedules.

    • Inventory planning should be aligned with hourly and day-of-week demand patterns.

    • Management can use the dashboard to monitor demand and make evidence-based operational decisions.
    """

)


# ============================================================
# MODULE 7
# DATA VALIDATION
# ============================================================

st.markdown("---")

st.header(
    "7️⃣ Data Validation Summary"
)


with st.expander(
    "View Data Quality Checks"
):

    validation = pd.DataFrame(

        {

            "Validation Check": [

                "Total Rows",

                "Total Columns",

                "Missing Values",

                "Duplicate Rows",

                "Duplicate Transaction IDs",

                "Invalid Dates",

                "Invalid Times",

                "Non-positive Quantity",

                "Non-positive Unit Price"

            ],

            "Result": [

                len(df),

                len(df.columns),

                int(
                    df.isna()
                    .sum()
                    .sum()
                ),

                int(
                    df.duplicated()
                    .sum()
                ),

                int(
                    df[
                        "transaction_id"
                    ]
                    .duplicated()
                    .sum()
                ),

                int(
                    df[
                        "transaction_date"
                    ]
                    .isna()
                    .sum()
                ),

                int(
                    df[
                        "transaction_time"
                    ]
                    .isna()
                    .sum()
                ),

                int(
                    (
                        df[
                            "transaction_qty"
                        ]
                        <= 0
                    )
                    .sum()
                ),

                int(
                    (
                        df[
                            "unit_price"
                        ]
                        <= 0
                    )
                    .sum()
                )

            ]

        }

    )


    st.dataframe(

        validation,

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# DATASET INFORMATION
# ============================================================

st.markdown("---")

st.header(
    "8️⃣ Dataset Information"
)


info1, info2, info3 = st.columns(3)


with info1:

    st.metric(
        "Dataset Start Date",
        str(
            df[
                "transaction_date"
            ]
            .min()
            .date()
        )
    )


with info2:

    st.metric(
        "Dataset End Date",
        str(
            df[
                "transaction_date"
            ]
            .max()
            .date()
        )
    )


with info3:

    st.metric(
        "Number of Stores",
        df[
            "store_location"
        ]
        .nunique()
    )


st.info(

    """
    **Dataset Scope Note:**
    
    The date-enabled dataset currently loaded in this dashboard
    contains transactions from **1 January 2023 to 30 June 2023**.
    
    """
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(

    "Afficionado Coffee Roasters | "
    "Sales Trend and Time-Based Performance Analysis | "
    "Machine Learning Internship"

)


# ============================================================
# MODULE 7
# DATA VALIDATION
# ============================================================

st.markdown("---")

st.header(
    "7️⃣ Data Validation Summary"
)


with st.expander(
    "View Data Quality Checks"
):

    validation = pd.DataFrame(

        {

            "Validation Check": [

                "Total Rows",

                "Total Columns",

                "Missing Values",

                "Duplicate Rows",

                "Duplicate Transaction IDs",

                "Invalid Dates",

                "Invalid Times",

                "Non-positive Quantity",

                "Non-positive Unit Price"

            ],

            "Result": [

                len(df),

                len(df.columns),

                int(
                    df.isna()
                    .sum()
                    .sum()
                ),

                int(
                    df.duplicated()
                    .sum()
                ),

                int(
                    df[
                        "transaction_id"
                    ]
                    .duplicated()
                    .sum()
                ),

                int(
                    df[
                        "transaction_date"
                    ]
                    .isna()
                    .sum()
                ),

                int(
                    df[
                        "transaction_time"
                    ]
                    .isna()
                    .sum()
                ),

                int(
                    (
                        df[
                            "transaction_qty"
                        ]
                        <= 0
                    )
                    .sum()
                ),

                int(
                    (
                        df[
                            "unit_price"
                        ]
                        <= 0
                    )
                    .sum()
                )

            ]

        }

    )


    st.dataframe(

        validation,

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# DATASET INFORMATION
# ============================================================

st.markdown("---")

st.header(
    "8️⃣ Dataset Information"
)


info1, info2, info3 = st.columns(3)


with info1:

    st.metric(
        "Dataset Start Date",
        str(
            df[
                "transaction_date"
            ]
            .min()
            .date()
        )
    )


with info2:

    st.metric(
        "Dataset End Date",
        str(
            df[
                "transaction_date"
            ]
            .max()
            .date()
        )
    )


with info3:

    st.metric(
        "Number of Stores",
        df[
            "store_location"
        ]
        .nunique()
    )


st.info(

    """
    **Dataset Scope Note:**
    
    The date-enabled dataset currently loaded in this dashboard
    contains transactions from **1 January 2023 to 30 June 2023**.
    
    """
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(

    "Afficionado Coffee Roasters | "
    "Sales Trend and Time-Based Performance Analysis | "
    "Machine Learning Internship"
)
