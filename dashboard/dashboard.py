import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Afficionado Coffee Analytics Dashboard",
    page_icon="☕",
    layout="wide"
)

st.title("☕ Afficionado Coffee Roasters Analytics Dashboard")
st.markdown("---")

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():

    BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    file_path = os.path.join(
        BASE_DIR,
        "data",
        "Afficionado Coffee Roasters.xlsx"
    )

    df = pd.read_excel(file_path)

    # Revenue
    df["revenue"] = (
        df["transaction_qty"]
        * df["unit_price"]
    )

    # Convert transaction time
    df["transaction_time"] = pd.to_datetime(
        df["transaction_time"],
        format="%H:%M:%S"
    )

    # Extract hour
    df["hour"] = df["transaction_time"].dt.hour

    # Time Buckets
    def get_bucket(hour):

        if 6 <= hour <= 11:
            return "Morning"

        elif 12 <= hour <= 16:
            return "Afternoon"

        elif 17 <= hour <= 21:
            return "Evening"

        else:
            return "Late Hours"

    df["time_bucket"] = df["hour"].apply(get_bucket)

    return df


df = load_data()

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Filters")

store_options = (
    ["All"]
    + sorted(
        list(
            df["store_location"].unique()
        )
    )
)

selected_store = st.sidebar.selectbox(
    "Store Location",
    store_options
)

hour_range = st.sidebar.slider(
    "Hour Range",
    0,
    23,
    (0, 23)
)

metric = st.sidebar.radio(
    "Metric",
    ["Revenue", "Quantity"]
)

# =====================================================
# FILTER DATA
# =====================================================

filtered_df = df.copy()

if selected_store != "All":
    filtered_df = filtered_df[
        filtered_df["store_location"]
        == selected_store
    ]

filtered_df = filtered_df[
    (filtered_df["hour"] >= hour_range[0]) &
    (filtered_df["hour"] <= hour_range[1])
]

# =====================================================
# METRIC TOGGLE
# =====================================================

if metric == "Revenue":
    value_col = "revenue"
    value_label = "Revenue ($)"
else:
    value_col = "transaction_qty"
    value_label = "Quantity Sold (Items)"

# =====================================================
# KPI CARDS
# =====================================================

total_revenue = filtered_df["revenue"].sum()
total_transactions = len(filtered_df)
avg_order = filtered_df["revenue"].mean()

peak_hour = (
    filtered_df.groupby("hour")
    ["transaction_id"]
    .count()
    .idxmax()
)

top_store = (
    df.groupby("store_location")
    ["revenue"]
    .sum()
    .idxmax()
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Revenue",
    f"${total_revenue:,.2f}"
)

c2.metric(
    "Transactions",
    f"{total_transactions:,}"
)

c3.metric(
    "Average Order Value",
    f"${avg_order:,.2f}"
)

c4.metric(
    "Peak Hour",
    f"{peak_hour}:00"
)

c5.metric(
    "Top Store",
    top_store
)

st.markdown("---")

# =====================================================
# CHART 1
# =====================================================

st.subheader(f"{value_label} by Store")

store_data = (
    filtered_df.groupby("store_location")
    [value_col]
    .sum()
    .reset_index()
)

fig1 = px.bar(
    store_data,
    x="store_location",
    y=value_col,
    color="store_location",
    text_auto=".0f"
)

fig1.update_yaxes(title=value_label)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# =====================================================
# CHART 2
# =====================================================

st.subheader(f"{value_label} by Hour")

hour_data = (
    filtered_df.groupby("hour")
    [value_col]
    .sum()
    .reset_index()
)

fig2 = px.line(
    hour_data,
    x="hour",
    y=value_col,
    markers=True
)

fig2.update_yaxes(title=value_label)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =====================================================
# CHART 3
# =====================================================

st.subheader(f"{value_label} by Time Bucket")

bucket_data = (
    filtered_df.groupby("time_bucket")
    [value_col]
    .sum()
    .reset_index()
)

fig3 = px.bar(
    bucket_data,
    x="time_bucket",
    y=value_col,
    color="time_bucket",
    text_auto=".0f"
)

fig3.update_yaxes(title=value_label)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =====================================================
# CHART 4
# =====================================================

st.subheader(f"{value_label} by Product Category")

category_data = (
    filtered_df.groupby("product_category")
    [value_col]
    .sum()
    .reset_index()
)

fig4 = px.bar(
    category_data,
    x="product_category",
    y=value_col,
    color="product_category",
    text_auto=".0f"
)

fig4.update_yaxes(title=value_label)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# =====================================================
# CHART 5
# =====================================================

st.subheader(f"Top 10 Products by {value_label}")

product_data = (
    filtered_df.groupby("product_type")
    [value_col]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig5 = px.bar(
    product_data,
    x="product_type",
    y=value_col,
    color="product_type",
    text_auto=".0f"
)

fig5.update_yaxes(title=value_label)

st.plotly_chart(
    fig5,
    use_container_width=True
)

# =====================================================
# HEATMAP
# =====================================================

st.subheader(f"Store vs Hour {value_label} Heatmap")

heatmap = pd.pivot_table(
    filtered_df,
    values=value_col,
    index="store_location",
    columns="hour",
    aggfunc="sum"
)

fig6 = px.imshow(
    heatmap,
    aspect="auto",
    text_auto=True
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

# =====================================================
# DATA PREVIEW
# =====================================================

st.subheader("Dataset Preview")

st.dataframe(
    filtered_df.head(20),
    use_container_width=True
)

# =====================================================
# BUSINESS INSIGHTS
# =====================================================

st.markdown("---")

st.subheader("Business Insights")

st.success(
    f"""
✅ Peak demand occurs around **{peak_hour}:00 hrs**

✅ **{top_store}** is the highest revenue-generating store.

✅ Increase staffing during peak hours.

✅ Run promotions during low-demand periods.

✅ Maintain inventory for top-selling products.
"""
)
