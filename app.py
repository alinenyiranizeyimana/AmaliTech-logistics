
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Veridi Logistics Last-Mile Audit Dashboard", layout="wide")

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
st.write("Delivery performance audit connecting logistics delays, customer sentiment, states, product categories, and monthly trends.")

total_delivered = delivered["order_id"].nunique()
late_orders = delivered.loc[delivered["Delivery_Status"] != "On Time", "order_id"].nunique()
super_late_orders = delivered.loc[delivered["Delivery_Status"] == "Super Late", "order_id"].nunique()
late_pct = (late_orders / total_delivered) * 100
avg_review = delivered["review_score"].mean()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Delivered Orders", f"{total_delivered:,}")
col2.metric("Late Orders", f"{late_orders:,}")
col3.metric("Late Delivery %", f"{late_pct:.2f}%")
col4.metric("Super Late Orders", f"{super_late_orders:,}")
col5.metric("Average Review Score", f"{avg_review:.2f}")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Delivery Status Distribution")
    status_counts = delivered["Delivery_Status"].value_counts().reset_index()
    status_counts.columns = ["Delivery_Status", "Orders"]
    fig = px.pie(status_counts, names="Delivery_Status", values="Orders", hole=0.35)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Average Review Score by Delivery Status")
    sentiment_summary = delivered.groupby("Delivery_Status", as_index=False)["review_score"].mean()
    fig = px.bar(sentiment_summary, x="Delivery_Status", y="review_score", text=sentiment_summary["review_score"].round(2))
    fig.update_layout(xaxis_title="Delivery Status", yaxis_title="Average Review Score (1-5)")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("States with the Highest Late Delivery Rates")
state_plot = state_performance.sort_values("Late_Percentage", ascending=False)
fig = px.bar(
    state_plot,
    x="Late_Percentage",
    y="customer_state",
    orientation="h",
    hover_data=["Total_Orders", "Late_Orders", "Late_Percentage"]
)
fig.update_layout(xaxis_title="Late Delivery Percentage (%)", yaxis_title="State", yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, use_container_width=True)

st.info(
    "Insight: AL had the highest late delivery rate at 23.93%, followed by MA at 19.67%. "
    "Most high-delay states are in the North and Northeast, suggesting that less central regions are more affected by late deliveries. "
    "However, RJ also appears among high-delay states, showing the problem is not only remote-area related."
)

st.divider()

st.subheader("Delivery Delay vs Average Review Score")
fig = px.scatter(delay_review, x="Days_Difference", y="review_score", hover_data=["Days_Difference", "review_score"])
fig.update_layout(xaxis_title="Delivery Delay (Days)", yaxis_title="Average Review Score (1-5)")
st.plotly_chart(fig, use_container_width=True)

st.write("Negative Days_Difference means the order arrived late. This chart shows whether review scores decline as delivery performance worsens.")

st.divider()

st.subheader("Late Delivery Percentage by Product Category")
top_categories = category_performance.sort_values("Late_Percentage", ascending=False).head(15)
fig = px.bar(
    top_categories,
    x="Late_Percentage",
    y="product_category_name_english",
    orientation="h",
    hover_data=["Total_Orders", "Late_Orders", "Avg_Review"]
)
fig.update_layout(xaxis_title="Late Delivery Percentage (%)", yaxis_title="Product Category", yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, use_container_width=True)

st.write(
    "Product categories were translated from Portuguese to English using the category translation file. "
    "This helps compare delivery reliability across categories such as electronics, furniture, food, and audio."
)

st.divider()

st.subheader("Candidate’s Choice: Monthly Late Delivery Trend")
if "Month_Num" in monthly_performance.columns:
    monthly_performance = monthly_performance.sort_values("Month_Num")

fig = px.line(
    monthly_performance,
    x="Month",
    y="Late_Percentage",
    markers=True,
    hover_data=["Total_Orders", "Late_Orders", "Late_Percentage"]
)
fig.update_layout(xaxis_title="Month", yaxis_title="Late Delivery Percentage (%)")
st.plotly_chart(fig, use_container_width=True)

st.success(
    "Candidate’s Choice: I added monthly late delivery analysis because it helps the business see whether delays are seasonal. "
    "This matters because Veridi Logistics can prepare extra delivery capacity before high-risk months instead of reacting after customer complaints increase."
)

st.divider()

st.subheader("Executive Summary")
st.write(
    "Most deliveries were completed on time, but a meaningful share of orders missed their estimated delivery dates. "
    "Late delivery rates are concentrated in specific states, especially parts of the North and Northeast. "
    "Customer review scores are lower for delayed orders, supporting the concern that logistics performance is linked to negative customer sentiment. "
    "Product category and monthly trend analysis provide extra business value by identifying categories and periods that require closer operational planning."
)
