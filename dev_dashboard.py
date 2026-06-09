# dev_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
from datetime import datetime, timedelta

# -----------------------------
# 1. PAGE CONFIG & THEME
# -----------------------------
st.set_page_config(
    page_title="Integrated Development Dashboard",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>
    .big-title {
        font-size: 32px;
        font-weight: 700;
        color: #1f77b4;
    }
    .sub-title {
        font-size: 18px;
        color: #555555;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<p class="big-title">📊 Integrated Development Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Synthetic data • Interactive filters • Colorful visuals</p>', unsafe_allow_html=True)

st.write("---")

# -----------------------------
# 2. SYNTHETIC DATA GENERATION
# -----------------------------
@st.cache_data
def generate_synthetic_data(n_days: int = 60, n_projects: int = 4):
    np.random.seed(42)

    # Create date range
    dates = [datetime.today() - timedelta(days=i) for i in range(n_days)]
    dates = sorted(dates)

    projects = [f"Project {chr(65 + i)}" for i in range(n_projects)]
    environments = ["Dev", "Test", "Prod"]

    rows = []
    for d in dates:
        for p in projects:
            for env in environments:
                commits = np.random.poisson(lam=3 if env == "Dev" else 1.5)
                tests_run = np.random.randint(20, 200)
                tests_pass = int(tests_run * np.random.uniform(0.7, 0.99))
                cpu = np.random.uniform(10, 95)
                latency = np.random.uniform(50, 500)

                rows.append(
                    {
                        "date": d.date(),
                        "project": p,
                        "environment": env,
                        "commits": commits,
                        "tests_run": tests_run,
                        "tests_pass": tests_pass,
                        "cpu_usage": cpu,
                        "latency_ms": latency,
                    }
                )

    df = pd.DataFrame(rows)
    df["pass_rate"] = df["tests_pass"] / df["tests_run"]
    return df

data = generate_synthetic_data()

# -----------------------------
# 3. SIDEBAR CONTROLS
# -----------------------------
st.sidebar.header("🔧 Controls")

project_filter = st.sidebar.multiselect(
    "Select project(s)",
    options=sorted(data["project"].unique()),
    default=sorted(data["project"].unique())
)

env_filter = st.sidebar.multiselect(
    "Select environment(s)",
    options=sorted(data["environment"].unique()),
    default=sorted(data["environment"].unique())
)

date_min = data["date"].min()
date_max = data["date"].max()

date_range = st.sidebar.slider(
    "Date range",
    min_value=date_min,
    max_value=date_max,
    value=(date_min, date_max)
)

st.sidebar.write("---")
st.sidebar.write("💡 Tip: Use filters to explore trends by project and environment.")

# -----------------------------
# 4. FILTERED DATA
# -----------------------------
mask = (
    data["project"].isin(project_filter)
    & data["environment"].isin(env_filter)
    & (data["date"] >= date_range[0])
    & (data["date"] <= date_range[1])
)

df_filtered = data[mask]

# -----------------------------
# 5. TOP METRICS (KPIs)
# -----------------------------
st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_commits = int(df_filtered["commits"].sum())
    st.metric("Total Commits", f"{total_commits}")

with col2:
    avg_pass_rate = df_filtered["pass_rate"].mean()
    st.metric("Avg Test Pass Rate", f"{avg_pass_rate:.2%}")

with col3:
    avg_cpu = df_filtered["cpu_usage"].mean()
    st.metric("Avg CPU Usage", f"{avg_cpu:.1f}%")

with col4:
    avg_latency = df_filtered["latency_ms"].mean()
    st.metric("Avg Latency", f"{avg_latency:.0f} ms")

st.write("---")

# -----------------------------
# 6. TIME SERIES VISUALS
# -----------------------------
st.subheader("📈 Activity Over Time")

# Commits over time
fig_commits = px.line(
    df_filtered.groupby(["date", "project"], as_index=False)["commits"].sum(),
    x="date",
    y="commits",
    color="project",
    title="Commits per Day by Project",
    markers=True,
    color_discrete_sequence=px.colors.qualitative.Bold,
)
fig_commits.update_layout(template="plotly_white")

# Pass rate over time
fig_pass = px.line(
    df_filtered.groupby(["date", "environment"], as_index=False)["pass_rate"].mean(),
    x="date",
    y="pass_rate",
    color="environment",
    title="Average Test Pass Rate by Environment",
    markers=True,
    color_discrete_sequence=px.colors.qualitative.Set2,
)
fig_pass.update_yaxes(tickformat=".0%")
fig_pass.update_layout(template="plotly_white")

col_a, col_b = st.columns(2)
with col_a:
    st.plotly_chart(fig_commits, use_container_width=True)
with col_b:
    st.plotly_chart(fig_pass, use_container_width=True)

# -----------------------------
# 7. RESOURCE USAGE VISUALS
# -----------------------------
st.subheader("🖥️ Resource Usage")

fig_cpu = px.box(
    df_filtered,
    x="environment",
    y="cpu_usage",
    color="environment",
    title="CPU Usage Distribution by Environment",
    color_discrete_sequence=px.colors.qualitative.Pastel,
)
fig_cpu.update_layout(template="plotly_white")

fig_latency = px.violin(
    df_filtered,
    x="environment",
    y="latency_ms",
    color="environment",
    box=True,
    points="all",
    title="Latency Distribution by Environment",
    color_discrete_sequence=px.colors.qualitative.Vivid,
)
fig_latency.update_layout(template="plotly_white")

col_c, col_d = st.columns(2)
with col_c:
    st.plotly_chart(fig_cpu, use_container_width=True)
with col_d:
    st.plotly_chart(fig_latency, use_container_width=True)

# -----------------------------
# 8. INTERACTIVE TABLE
# -----------------------------
st.subheader("📋 Detailed View (Filtered Data)")

st.dataframe(
    df_filtered.sort_values(["date", "project", "environment"]),
    use_container_width=True,
    height=300,
)

# -----------------------------
# 9. SIMPLE "LIVE" SIMULATION
# -----------------------------
st.subheader("⏱️ Live Simulation (Synthetic)")

placeholder = st.empty()

if st.button("Run 5-second synthetic load simulation"):
    for i in range(5):
        load = np.random.uniform(30, 95)
        latency = np.random.uniform(80, 400)
        with placeholder.container():
            colx, coly = st.columns(2)
            with colx:
                st.metric("Simulated CPU Load", f"{load:.1f}%")
            with coly:
                st.metric("Simulated Latency", f"{latency:.0f} ms")
        time.sleep(1)

st.write("---")
st.caption("Built with Streamlit + Plotly • Synthetic data • Example integrated development dashboard")
