import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, MarkerCluster
from sqlalchemy import create_engine
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from streamlit.components.v1 import html

st.set_page_config(layout="wide")
st.title("Insurance Geo Intelligence Platform")

# =========================
# CONNECT TO SNOWFLAKE
# =========================
@st.cache_data
def load_data():
    engine = create_engine(
        "snowflake://Zaya:74qaN4Gez8AybuU@vxrkkol-fe49345/INSURANCE_DB/PUBLIC?warehouse=INSURANCE_WH"
    )

    query = """
    SELECT 
        m.client_id,
        m.cluster_id,
        ST_Y(m.client_location) AS lat,
        ST_X(m.client_location) AS lon,
        m.clients_in_cluster,
        mc.avg_monthly_income,
        mc.population_density_per_km2,
        mc.annual_growth_rate_pct,
        mc.unemployment_rate_pct,
        mc.median_age,
        ST_Y(m.suggested_branch_location) AS branch_lat,
        ST_X(m.suggested_branch_location) AS branch_lon,
        mc.province
    FROM map_ready m
    JOIN master_clients mc
    ON m.client_id = mc.client_id
    WHERE m.client_location IS NOT NULL
    """

    df = pd.read_sql(query, engine)
    df.columns = df.columns.str.lower()
    return df

df = load_data()

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("Filters")

province = st.sidebar.multiselect(
    "Province",
    df.province.unique(),
    default=list(df.province.unique())
)

cluster = st.sidebar.multiselect(
    "Cluster",
    df.cluster_id.unique(),
    default=list(df.cluster_id.unique())
)

df = df[df.province.isin(province)]
df = df[df.cluster_id.isin(cluster)]

# =========================
# HANDLE EMPTY DATA
# =========================
if df.empty:
    st.warning("No data available for the selected filters. Please adjust your Province or Cluster selections.")
    st.stop()  # stop further execution gracefully

# =========================
# AI SCORING
# =========================
scaler = MinMaxScaler()

df["income_score"] = scaler.fit_transform(df[["avg_monthly_income"]])
df["density_score"] = scaler.fit_transform(df[["population_density_per_km2"]])
df["growth_score"] = scaler.fit_transform(df[["annual_growth_rate_pct"]])
df["unemployment_score"] = 1 - scaler.fit_transform(df[["unemployment_rate_pct"]])

df["opportunity_score"] = (
    df["income_score"]*0.35 +
    df["density_score"]*0.30 +
    df["growth_score"]*0.20 +
    df["unemployment_score"]*0.15
)

# =========================
# PROPENSITY MODEL
# =========================
X = df[["income_score","density_score","growth_score","unemployment_score"]]
y = (df["opportunity_score"] > df["opportunity_score"].median()).astype(int)

model = LogisticRegression(max_iter=500)
model.fit(X, y)

df["propensity"] = model.predict_proba(X)[:,1]

# =========================
# KPIs
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Clients", len(df))
col2.metric("Avg Opportunity", round(df.opportunity_score.mean(),2))
col3.metric("High Propensity %", round((df.propensity>0.7).mean()*100,1))
col4.metric("Clusters", df.cluster_id.nunique())

# =========================
# MAP
# =========================
center_lat = df.lat.mean()
center_lon = df.lon.mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=6,
    tiles="cartodbpositron"
)

# Heatmap
HeatMap(df[["lat","lon","opportunity_score"]].values).add_to(m)

# Clients
cluster_group = MarkerCluster().add_to(m)

for _, r in df.iterrows():
    if r.propensity > .7:
        color="green"
    elif r.propensity > .4:
        color="orange"
    else:
        color="red"

    folium.CircleMarker(
        [r.lat,r.lon],
        radius=5,
        color=color,
        fill=True,
        fill_opacity=0.8,
        popup=f"""
        Client {r.client_id}<br>
        Opportunity {round(r.opportunity_score,2)}<br>
        Propensity {round(r.propensity,2)}
        """
    ).add_to(cluster_group)

# Branches
branches = df.groupby(["branch_lat","branch_lon"]).agg({
    "clients_in_cluster":"max",
    "opportunity_score":"mean"
}).reset_index()

for _, b in branches.iterrows():
    folium.Marker(
        [b.branch_lat, b.branch_lon],
        icon=folium.Icon(color="blue",icon="briefcase"),
        popup=f"Clients {b.clients_in_cluster}<br>Score {round(b.opportunity_score,2)}"
    ).add_to(m)

# Render map
st.subheader("Interactive Map")
html(m._repr_html_(), height=600)

# =========================
# DATA TABLE
# =========================
st.subheader("Client Intelligence Table")
st.dataframe(df.sort_values("opportunity_score", ascending=False))
