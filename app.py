import os
import pandas as pd
import psycopg
import streamlit as st
import altair as alt
from dotenv import load_dotenv

load_dotenv() 

#DB helpers
def get_conn():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

@st.cache_data(ttl=60)
def run_query(sql, params=None):
    with get_conn() as conn:
        df = pd.read_sql(sql, conn, params=params)
    return df

#Page
st.set_page_config(page_title="Personal Finance Analyser", layout="wide")
st.title("Personal Finance Analyser")

#Load months for filter from your view
months_df = run_query("SELECT month FROM v_monthly_totals ORDER BY month;")
if months_df.empty:
    st.info("No data yet. Import a CSV first.")
    st.stop()

#Ensure datetime so we can use .dt
months_df["month"] = pd.to_datetime(months_df["month"])
months = months_df["month"].dt.date.tolist()
min_m, max_m = months[0], months[-1]

st.sidebar.header("Filters")
start_m, end_m = st.sidebar.select_slider(
    "Month range", options=months, value=(min_m, max_m),
)

#Back to timestamps for SQL params
start_ts = pd.Timestamp(start_m)
end_ts   = pd.Timestamp(end_m)

#Inclusive month range: [start_of_start_month, start_of_end_month + 1 month)
kpis = run_query(
    """
    SELECT
      COALESCE(SUM(CASE WHEN amount > 0 THEN amount END), 0) AS income,
      COALESCE(SUM(CASE WHEN amount < 0 THEN amount END), 0) AS spend,
      COALESCE(SUM(amount), 0) AS net
    FROM transactions
    WHERE txn_date >= date_trunc('month', %s)
      AND txn_date <  (date_trunc('month', %s) + INTERVAL '1 month');
    """,
    params=[start_ts, end_ts],
)

col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"£{kpis['income'].iloc[0]:,.2f}")
col2.metric("Total Spend",  f"£{kpis['spend'].iloc[0]:,.2f}")
col3.metric("Net",          f"£{kpis['net'].iloc[0]:,.2f}")

st.divider()

#Monthly totals chart (line)
mt = run_query(
    """
    SELECT month, income, spend, net
    FROM v_monthly_totals
    WHERE month BETWEEN date_trunc('month', %s)::date AND date_trunc('month', %s)::date
    ORDER BY month;
    """,
    params=[start_ts, end_ts],
)
st.subheader("Monthly totals")
st.line_chart(mt.set_index("month")[["income", "spend", "net"]])

#Spend by category per month (stacked bar with totals, one bar per month)
st.subheader("Spend by category per month")
sbcm = run_query(
    """
    SELECT month, category, total
    FROM v_spend_by_category_month
    WHERE month BETWEEN date_trunc('month', %s)::date AND date_trunc('month', %s)::date
      AND total < 0  -- expenses only
    ORDER BY month, category;
    """,
    params=[start_ts, end_ts],
)

if sbcm.empty:
    st.write("No category data in the selected range.")
else:
    plot = sbcm.copy()
    plot["month"] = pd.to_datetime(plot["month"])
    plot["month_label"] = plot["month"].dt.strftime("%b %Y")   
    plot["amount_pos"] = (-plot["total"]).astype(float)        # flip negatives to positive bar heights

    
    totals = (
        plot.groupby("month_label", as_index=False)["amount_pos"]
            .sum()
            .rename(columns={"amount_pos": "total"})
    )
    totals["total_label"] = totals["total"].apply(lambda v: f"£{v:,.0f}")

    bars = (
        alt.Chart(plot)
        .mark_bar()
        .encode(
            x=alt.X("month_label:N", title="Month"),
            y=alt.Y("amount_pos:Q", title="Total spend (£)", stack="zero"),
            color=alt.Color("category:N", title="Category"),
            tooltip=[
                alt.Tooltip("month_label:N", title="Month"),
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("amount_pos:Q", title="Spend (£)", format=",.2f"),
            ],
        )
        .properties(height=500)
    )

    labels = (
        alt.Chart(totals)
        .mark_text(dy=-8, fontWeight="bold")
        .encode(
            x=alt.X("month_label:N"),
            y=alt.Y("total:Q"),
            text="total_label:N",
        )
    )

    st.altair_chart(bars + labels, use_container_width=True)

#Recurring candidates
st.subheader("Recurring candidates (merchant-based)")
rec = run_query(
    "SELECT merchant, kind, months_seen, avg_amount FROM v_recurring_candidates ORDER BY months_seen DESC, kind, merchant;"
)
if rec.empty:
    st.write("No recurring candidates yet.")
else:
    st.dataframe(rec)

st.caption("Built with Streamlit + PostgreSQL.")
