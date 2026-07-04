import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Veridi Dashboard", layout="wide")

st.markdown("""
<style>
header {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    padding-top: 0rem;
    padding-bottom: 0rem;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
}

h1 {
    font-size: 20px !important;
    text-align: center;
    margin: -35px 0 5px 0 !important;
    padding: 0 !important;
}

h3 {
    font-size: 12px !important;
    margin: 0px !important;
    padding: 0px !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.2rem !important;
}

[data-testid="stMetric"] {
    padding: 4px 8px;
}

[data-testid="stMetricLabel"] {
    font-size: 10px !important;
}

[data-testid="stMetricValue"] {
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

delivered = pd.read_csv("delivered.csv")
state = pd.read_csv("state_performance.csv")
category = pd.read_csv("category_performance.csv")
monthly = pd.read_csv("monthly_performance.csv")
delay = pd.read_csv("delay_review.csv")

st.title("Veridi Logistics Last-Mile Audit Dashboard")

total = delivered["order_id"].nunique()
late = delivered[delivered["Delivery_Status"] != "On Time"]["order_id"].nunique()
super_late = delivered[delivered["Delivery_Status"] == "Super Late"]["order_id"].nunique()
late_percent = late / total * 100
avg_review = delivered["review_score"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Delivered Orders", f"{total/1000:.0f}K")
c2.metric("Late Orders", f"{late/1000:.0f}K")
c3.metric("Late Delivery %", f"{late_percent:.2f}%")
c4.metric("Super Late Orders", f"{super_late:,}")
c5.metric("Average Review Score", f"{avg_review:.2f}")

def small(fig):
    fig.update_layout(
        height=160,
        margin=dict(l=5, r=5, t=20, b=5),
        font=dict(size=9),
        title_font=dict(size=11)
    )
    fig.update_xaxes(title_font=dict(size=9), tickfont=dict(size=8))
    fig.update_yaxes(title_font=dict(size=9), tickfont=dict(size=8))
    return fig

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Delivery Performance Distribution")
    fig = px.pie(delivered, names="Delivery_Status", hole=0.45)
    st.plotly_chart(small(fig), use_container_width=True)

with col2:
    st.subheader("Late Delivery Percentage by State")
    state = state.sort_values("Late_Percentage", ascending=False)
    fig = px.bar(state, x="customer_state", y="Late_Percentage")
    st.plotly_chart(small(fig), use_container_width=True)

with col3:
    st.subheader("Average Review Score by Delivery Status")
    review = delivered.groupby("Delivery_Status", as_index=False)["review_score"].mean()
    fig = px.bar(review, x="Delivery_Status", y="review_score")
    st.plotly_chart(small(fig), use_container_width=True)

col4, col5, col6 = st.columns(3)

with col4:
    st.subheader("Delivery Delay vs Review Score")
    fig = px.scatter(delay, x="Days_Difference", y="review_score")
    st.plotly_chart(small(fig), use_container_width=True)

with col5:
    st.subheader("Late Delivery % by Product Category")
    top_cat = category.sort_values("Late_Percentage", ascending=False).head(5)
    fig = px.bar(top_cat, x="Late_Percentage", y="product_category_name_english", orientation="h")
    st.plotly_chart(small(fig), use_container_width=True)

with col6:
    st.subheader("Monthly Late Delivery Trend")
    fig = px.line(monthly, x="Month", y="Late_Percentage", markers=True)
    st.plotly_chart(small(fig), use_container_width=True)
