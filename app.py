import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Veridi Logistics Dashboard", layout="wide")

delivered = pd.read_csv("delivered.csv")
state = pd.read_csv("state_performance.csv")
category = pd.read_csv("category_performance.csv")
monthly = pd.read_csv("monthly_performance.csv")
delay = pd.read_csv("delay_review.csv")

st.title("Veridi Logistics Last-Mile Audit Dashboard")

total = delivered["order_id"].nunique()
late = delivered[delivered["Delivery_Status"] != "On Time"]["order_id"].nunique()
late_percent = late / total * 100
avg_review = delivered["review_score"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Delivered Orders", f"{total/1000:.0f}K")
c2.metric("Late Orders", f"{late/1000:.0f}K")
c3.metric("Late Delivery %", f"{late_percent:.2f}%")
c4.metric("Average Review Score", f"{avg_review:.2f}")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Delivery Performance Distribution")
    fig = px.pie(delivered, names="Delivery_Status")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Late Delivery Percentage by State")
    state = state.sort_values("Late_Percentage", ascending=False)
    fig = px.bar(state, x="customer_state", y="Late_Percentage")
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.subheader("Average Review Score by Delivery Status")
    review = delivered.groupby("Delivery_Status", as_index=False)["review_score"].mean()
    fig = px.bar(review, x="Delivery_Status", y="review_score")
    st.plotly_chart(fig, use_container_width=True)

col4, col5, col6 = st.columns(3)

with col4:
    st.subheader("Delivery Delay vs Review Score")
    fig = px.scatter(delay, x="Days_Difference", y="review_score")
    st.plotly_chart(fig, use_container_width=True)

with col5:
    st.subheader("Late Delivery % by Product Category")
    top_cat = category.sort_values("Late_Percentage", ascending=False).head(6)
    fig = px.bar(top_cat, x="Late_Percentage", y="product_category_name_english", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.subheader("Monthly Late Delivery Trend")
    fig = px.line(monthly, x="Month", y="Late_Percentage", markers=True)
    st.plotly_chart(fig, use_container_width=True)
