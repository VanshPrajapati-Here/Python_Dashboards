import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
import os

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Clash of Clans Dashboard", layout="wide")

# -------------------------------------------------
# CUSTOM CSS (COC DARK STONE THEME)
# -------------------------------------------------
st.markdown("""
<style>
/* Main App Background */
.stApp {
    background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                url('https://www.transparenttextures.com/patterns/dark-matter.png');
    background-color: #1B120B; 
    color: #FFFFFF;
}

/* Headings - Gold Gradient Style */
h1, h2, h3 {
    color: #F1C40F !important;
    text-shadow: 2px 2px 4px #000000;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #0E0804 !important;
    border-right: 1px solid #3E2723;
}
[data-testid="stSidebar"] * {
    color: #F1C40F !important;
}

/* KPI Cards - Wood Plank Look */
[data-testid="metric-container"] {
    background-color: #2D1E17 !important;
    border: 2px solid #5D4037 !important;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.5);
}

/* Fix for Metric Label and Value Visibility */
[data-testid="stMetricLabel"] {
    color: #BDC3C7 !important;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-weight: bold;
}

/* Dataframe Styling */
[data-testid="stTable"], [data-testid="stDataFrame"] {
    background-color: #FFFFFF;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HELPER: PLOTLY DARK TEMPLATE
# -------------------------------------------------
def apply_coc_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="#FFFFFF",
        margin=dict(t=30, b=10, l=10, r=10),
        legend=dict(font=dict(color="#FFFFFF"))
    )
    fig.update_xaxes(gridcolor='#3E2723', zerolinecolor='#3E2723')
    fig.update_yaxes(gridcolor='#3E2723', zerolinecolor='#3E2723')
    return fig

# -------------------------------------------------
# TITLE
# -------------------------------------------------
st.title("⚔️ Clash of Clans Player Churn Analytics")

# -------------------------------------------------
# SIDEBAR IMAGE & FILTERS
# -------------------------------------------------
# Adjust path to your local image
img_path = r"F:\Vs Code\Clash Of Clans Churn Analysis\ClashOfClans.jpg"
if os.path.exists(img_path):
    st.sidebar.image(img_path, use_container_width=True)

st.sidebar.header("Command Center")

# LOAD DATA
df = pd.read_csv(r"F:\\Vs Code\\Clash Of Clans Churn Analysis\\clash_of_clans_churn_dataset_v2.csv")
df["Update_Event"] = df["Update_Event"].fillna("None")

# FILTERS
year = st.sidebar.selectbox("Year", ["All"] + sorted(df["Year"].unique().tolist()))
region = st.sidebar.multiselect("Region", df["Region"].unique(), default=df["Region"].unique())
platform = st.sidebar.multiselect("Platform", df["Platform"].unique(), default=df["Platform"].unique())

filtered = df.copy()
if year != "All":
    filtered = filtered[filtered["Year"] == year]

filtered = filtered[
    (filtered["Region"].isin(region)) & 
    (filtered["Platform"].isin(platform))
]

# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------
st.subheader("Village Vitals")
total_players = filtered["Player_Name"].nunique()
churned = filtered["Churned"].sum()
churn_rate = (churned / len(filtered)) * 100 if len(filtered) > 0 else 0
avg_sat = filtered["Satisfaction_Score"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Players", f"{total_players:,}")
c2.metric("Lost Warriors", f"{churned:,}")
c3.metric("Churn Rate", f"{churn_rate:.1f}%")
c4.metric("Avg Morale", f"{avg_sat:.2f}/10")

st.divider()

# -------------------------------------------------
# CHARTS
# -------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Platform Territory")
    platform_data = filtered.groupby("Platform")["Player_Name"].count().reset_index()
    fig_donut = px.pie(
        platform_data, values="Player_Name", names="Platform",
        hole=0.6, color_discrete_sequence=["#A6BD4C", "#F1D412"]
    )
    st.plotly_chart(apply_coc_theme(fig_donut), use_container_width=True)

with col2:
    st.subheader("Global Churn Map")

    # Map regions to representative country ISO codes
    region_iso = {
        "Asia": "IND",
        "Europe": "FRA",
        "North America": "USA",
        "South America": "BRA"
    }

    map_data = filtered.groupby("Region")["Churned"].mean().reset_index()
    map_data["iso"] = map_data["Region"].map(region_iso)

    fig_map = px.choropleth(
        map_data,
        locations="iso",
        color="Churned",
        hover_name="Region",
        color_continuous_scale="Reds",
        projection="natural earth"
    )

    fig_map.update_geos(
        showcoastlines=True,
        coastlinecolor="white",
        showland=True,
        landcolor="#2D1E17",
        bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(apply_coc_theme(fig_map), use_container_width=True)


st.divider()

# SECOND ROW
col3, col4 = st.columns(2)

with col3:
    st.subheader("Update Impact")
    update_trend = filtered.groupby(["Year", "Update_Event"])["Monthly_Active_Index"].mean().reset_index()
    fig_line = px.line(
        update_trend, x="Year", y="Monthly_Active_Index", color="Update_Event",
        color_discrete_sequence=["#C340D6", "#F1D412", "#A6BD4C"]
    )
    st.plotly_chart(apply_coc_theme(fig_line), use_container_width=True)

with col4:
    st.subheader("Playtime vs Churn")
    churn_trend = filtered.groupby(["Year", "Churned"])["Monthly_Active_Index"].mean().reset_index()
    churn_trend["Churned"] = churn_trend["Churned"].map({0: "Active", 1: "Churned"})
    fig_churn = px.line(
        churn_trend, x="Year", y="Monthly_Active_Index", color="Churned",
        markers=True, color_discrete_sequence=["#A6BD4C", "#F34230"]
    )
    st.plotly_chart(apply_coc_theme(fig_churn), use_container_width=True)

# -------------------------------------------------
# DATA PREVIEW
# -------------------------------------------------
st.subheader("📜 Clan Records")
st.dataframe(filtered.head(50), use_container_width=True)