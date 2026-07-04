import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Veridi Logistics Last-Mile Audit Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Compact dashboard styling: keeps the report close to one page
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 0.6rem;
        padding-bottom: 0.2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    h1 {
        text-align: center;
        font-size: 30px !important;
        margin-bottom: 0.4rem !important;
    }
    h3 {
        font-size: 15px !important;
        margin-bottom: 0.2rem !important;
    }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        border-radius: 8px;
        padding: 0.45rem 0.6rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricValue"] {
        font-size: 25px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0.35rem;
    }
    hr {
        margin: 0.25rem 0rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data():
    delivered = pd.read_csv("delivered.csv")
    state_performance = pd.read_csv("state_performance.csv")
    category_performance = pd.read_csv("category_performance.csv")
    monthly_performance = pd.read_csv("monthly_performance.csv")
    delay_review = pd.read_csv("delay_review.csv")
    return delivered, state_performance, category_performance, monthly_performance, delay_review


delivered, state_performance, category_performance, monthly_performance, delay_review = load_data()

st.title("Veridi Logistics Last-Mile Audit Dashboard")

# KPI calculations
total_delivered = delivered["order_id"].nunique()
late_orders = delivered.loc[delivered["Delivery_Status"] != "On Time", "order_id"].nunique()
super_late_orders = delivered.loc[delivered["Delivery_Status"] == "Super Late", "order_id"].nunique()
late_pct = (late_orders / total_delivered) * 100
avg_review = delivered["review_score"].mean()

# KPI cards
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Delivered Orders", f"{total_delivered/1000:.0f}K")
col2.metric("Late Orders", f"{late_orders/1000:.0f}K")
col3.metric("Late Delivery %", f"{late_pct:.2f}%")
col4.metric("Super Late Orders", f"{super_late_orders:,}")
col5.metric("Average Review Score", f"{avg_review:.2f}")

CHART_HEIGHT = 245
CHART_CONFIG = {"displayModeBar": False, "responsive": True}

# First chart row
left, middle, right = st.columns([1.05, 1.55, 1.05])

with left:
    st.subheader("Delivery Performance Distribution")
    status_counts = delivered["Delivery_Status"].value_counts().reset_index()
    status_counts.columns = ["Delivery_Status", "Orders"]
    fig = px.pie(
        status_counts,
        names="Delivery_Status",
        values="Orders",
        hole=0.35,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        height=CHART_HEIGHT,
        margin=dict(l=5, r=5, t=5, b=5),
        legend=dict(orientation="v", y=0.5, x=0.95),
        font=dict(size=10)
    )
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

with middle:
    st.subheader("Late Delivery Percentage by State")
    state_plot = state_performance.sort_values("Late_Percentage", ascending=False)
    fig = px.bar(
        state_plot,
        x="customer_state",
        y="Late_Percentage",
        hover_data=["Total_Orders", "Late_Orders", "Late_Percentage"]
    )
    fig.update_layout(
        height=CHART_HEIGHT,
        margin=dict(l=10, r=5, t=5, b=20),
        xaxis_title="State",
        yaxis_title="Late Delivery (%)",
        font=dict(size=10)
    )
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

with right:
    st.subheader("Average Review Score by Delivery Status")
    sentiment_summary = delivered.groupby("Delivery_Status", as_index=False)["review_score"].mean()
    fig = px.bar(
        sentiment_summary,
        x="Delivery_Status",
        y="review_score",
        text=sentiment_summary["review_score"].round(2)
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=CHART_HEIGHT,
        margin=dict(l=10, r=5, t=5, b=20),
        xaxis_title="Delivery Status",
        yaxis_title="Average Review Score",
        font=dict(size=10)
    )
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

# Second chart row
left, middle, right = st.columns([1.15, 1.2, 1.15])

with left:
    st.subheader("Delivery Delay vs Average Review Score")
    fig = px.scatter(
        delay_review,
        x="Days_Difference",
        y="review_score",
        hover_data=["Days_Difference", "review_score"]
    )
    fig.update_layout(
        height=CHART_HEIGHT,
        margin=dict(l=10, r=5, t=5, b=20),
        xaxis_title="Delivery Delay (Days)",
        yaxis_title="Average Review Score",
        font=dict(size=10)
    )
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

with middle:
    st.subheader("Late Delivery % by Product Category")
    top_categories = category_performance.sort_values("Late_Percentage", ascending=False).head(8)
    fig = px.bar(
        top_categories,
        x="Late_Percentage",
        y="product_category_name_english",
        orientation="h",
        hover_data=["Total_Orders", "Late_Orders", "Avg_Review"]
    )
    fig.update_layout(
        height=CHART_HEIGHT,
        margin=dict(l=5, r=5, t=5, b=20),
        xaxis_title="Late Delivery (%)",
        yaxis_title="Product Category",
        yaxis={"categoryorder": "total ascending"},
        font=dict(size=10)
    )
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

with right:
    st.subheader("Monthly Late Delivery Trend")
    if "Month_Num" in monthly_performance.columns:
        monthly_performance = monthly_performance.sort_values("Month_Num")

    fig = px.line(
        monthly_performance,
        x="Month",
        y="Late_Percentage",
        markers=True,
        hover_data=["Total_Orders", "Late_Orders", "Late_Percentage"]
    )
    fig.update_layout(
        height=CHART_HEIGHT,
        margin=dict(l=10, r=5, t=5, b=20),
        xaxis_title="Month",
        yaxis_title="Late Delivery (%)",
        font=dict(size=10)
    )
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
