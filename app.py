import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Veridi Dashboard", layout="wide")

st.markdown("""
<style>
header {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    padding-top: 0.25rem;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    padding-bottom: 0rem;
}

h2 {
    text-align: center;
    font-size: 18px !important;
    margin-top: 0px !important;
    margin-bottom: 6px !important;
}

h3 {
    font-size: 11px !important;
    margin-top: 4px !important;
    margin-bottom: 2px !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
}
</style>
""", unsafe_allow_html=True)

def read_file(file):
    try:
        return pd.read_csv(file)
    except:
        st.error(f"{file} is empty or missing. Please upload/fix this file.")
        st.stop()

delivered = read_file("delivered.csv")
state = read_file("state_performance.csv")
category = read_file("category_performance.csv")
monthly = read_file("monthly_performance.csv")
delay = read_file("delay_review.csv")

st.markdown("<h2>Veridi Logistics Last-Mile Audit Dashboard</h2>", unsafe_allow_html=True)

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
        height=165,
        margin=dict(l=5, r=5, t=5, b=5),
        font=dict(size=7)
    )

    fig.update_xaxes(
        title_font=dict(size=9, family="Arial Black"),
        tickfont=dict(size=8, family="Arial Black")
    )

    fig.update_yaxes(
        title_font=dict(size=9, family="Arial Black"),
        tickfont=dict(size=8, family="Arial Black")
    )

    return fig

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Delivery Performance Distribution")
    fig = px.pie(
        delivered,
        names="Delivery_Status",
        hole=0.45,
        labels={"Delivery_Status": "Delivery Status"}
    )
    st.plotly_chart(small(fig), use_container_width=True)

with col2:
    st.subheader("Late Delivery Percentage by State")
    state = state.sort_values("Late_Percentage", ascending=False)
    fig = px.bar(
        state,
        x="customer_state",
        y="Late_Percentage",
        labels={
            "customer_state": "State",
            "Late_Percentage": "Late Delivery (%)"
        }
    )
    st.plotly_chart(small(fig), use_container_width=True)

with col3:
    st.subheader("Average Review Score by Delivery Status")
    review = delivered.groupby("Delivery_Status", as_index=False)["review_score"].mean()
    fig = px.bar(
        review,
        x="Delivery_Status",
        y="review_score",
        labels={
            "Delivery_Status": "Delivery Status",
            "review_score": "Average Review Score"
        }
    )
    st.plotly_chart(small(fig), use_container_width=True)

col4, col5, col6 = st.columns(3)

with col4:
    st.subheader("Delivery Delay vs Average Review Score")
    fig = px.scatter(
        delay,
        x="Delivery_Delay_Days",
        y="review_score",
        labels={
            "Delivery_Delay_Days": "Delivery Delay (Days)",
            "review_score": "Average Review Score"
        }
    )
    st.plotly_chart(small(fig), use_container_width=True)

with col5:
    st.subheader("Late Delivery % by Product Category")
    top_cat = category.sort_values("Late_Percentage", ascending=False).head(5)
    fig = px.bar(
        top_cat,
        x="Late_Percentage",
        y="product_category_name_english",
        orientation="h",
        labels={
            "Late_Percentage": "Late Delivery (%)",
            "product_category_name_english": "Product Category"
        }
    )
    st.plotly_chart(small(fig), use_container_width=True)

with col6:
    st.subheader("Monthly Late Delivery Trend")
    fig = px.line(
        monthly,
        x="Month",
        y="Late_Percentage",
        markers=True,
        labels={
            "Month": "Month",
            "Late_Percentage": "Late Delivery (%)"
        }
    )
    st.plotly_chart(small(fig), use_container_width=True)
