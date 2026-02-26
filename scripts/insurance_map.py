import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, Fullscreen, MarkerCluster
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sqlalchemy import create_engine

print("Connecting to Snowflake...")

# =========================
# SQLALCHEMY CONNECTION (FIXED)
# =========================
engine = create_engine(
    "snowflake://Zaya:74qaN4Gez8AybuU@vxrkkol-fe49345/INSURANCE_DB/PUBLIC?warehouse=INSURANCE_WH"
)

# =========================
# DATA QUERY
# =========================
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
    ST_X(m.suggested_branch_location) AS branch_lon
FROM map_ready m
JOIN master_clients mc
ON m.client_id = mc.client_id
WHERE m.client_location IS NOT NULL
"""

df = pd.read_sql(query, engine)
df.columns = df.columns.str.lower()

print("Rows loaded:", len(df))

# =========================
# FEATURE SCALING
# =========================
scaler = MinMaxScaler()

df["income_score"] = scaler.fit_transform(df[["avg_monthly_income"]])
df["density_score"] = scaler.fit_transform(df[["population_density_per_km2"]])
df["growth_score"] = scaler.fit_transform(df[["annual_growth_rate_pct"]])
df["unemployment_score"] = 1 - scaler.fit_transform(df[["unemployment_rate_pct"]])

# =========================
# OPPORTUNITY SCORE
# =========================
df["opportunity_score"] = (
    df["income_score"]*0.35 +
    df["density_score"]*0.30 +
    df["growth_score"]*0.20 +
    df["unemployment_score"]*0.15
)

# =========================
# AI PROPENSITY MODEL
# =========================
X = df[[
    "income_score",
    "density_score",
    "growth_score",
    "unemployment_score"
]]

# synthetic label for demo (replace later with real conversion flag)
y = (df["opportunity_score"] > df["opportunity_score"].median()).astype(int)

model = LogisticRegression(max_iter=500)
model.fit(X,y)

df["propensity"] = model.predict_proba(X)[:,1]

# =========================
# CHURN MODEL
# =========================
df["churn_risk"] = (
    (1-df["income_score"])*0.4 +
    (df["unemployment_rate_pct"]/100)*0.4 +
    (df["median_age"]/100)*0.2
)

# =========================
# MAP BASE
# =========================
center_lat = df.lat.mean()
center_lon = df.lon.mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=7,
    tiles="cartodbpositron"
)

Fullscreen().add_to(m)

# =========================
# HEATMAP LAYER
# =========================
heat_layer = folium.FeatureGroup(name="Opportunity Heatmap")

HeatMap(
    df[["lat","lon","opportunity_score"]].values,
    radius=20,
    blur=18
).add_to(heat_layer)

heat_layer.add_to(m)

# =========================
# CLIENT CLUSTER LAYER
# =========================
cluster_layer = folium.FeatureGroup(name="Clients")
cluster = MarkerCluster().add_to(cluster_layer)

for _, r in df.iterrows():

    if r["propensity"] > 0.7:
        color = "green"
    elif r["propensity"] > 0.4:
        color = "orange"
    else:
        color = "red"

    popup = f"""
    <b>Client:</b> {r.client_id}<br>
    Cluster: {r.cluster_id}<br>
    Opportunity: {round(r.opportunity_score,2)}<br>
    Propensity: {round(r.propensity,2)}<br>
    Churn Risk: {round(r.churn_risk,2)}
    """

    folium.CircleMarker(
        location=[r.lat,r.lon],
        radius=6,
        color=color,
        fill=True,
        fill_opacity=0.85,
        popup=popup
    ).add_to(cluster)

cluster_layer.add_to(m)

# =========================
# BRANCH OPTIMIZER LAYER
# =========================
branch_layer = folium.FeatureGroup(name="Suggested Branches")

branches = df.groupby(["branch_lat","branch_lon"]).agg({
    "clients_in_cluster":"max",
    "opportunity_score":"mean"
}).reset_index()

for _, b in branches.iterrows():

    if b.opportunity_score > 0.7:
        c="darkgreen"
    elif b.opportunity_score > 0.4:
        c="blue"
    else:
        c="gray"

    folium.Marker(
        location=[b.branch_lat,b.branch_lon],
        icon=folium.Icon(color=c, icon="briefcase"),
        popup=f"""
        <b>Branch Recommendation</b><br>
        Clients: {b.clients_in_cluster}<br>
        Score: {round(b.opportunity_score,2)}
        """
    ).add_to(branch_layer)

branch_layer.add_to(m)

# =========================
# REAL-TIME SCORING SIMULATION
# =========================
df["live_score"] = df["opportunity_score"] * np.random.uniform(0.9,1.1,len(df))

live_layer = folium.FeatureGroup(name="Live Scores")

for _, r in df.sample(min(200,len(df))).iterrows():
    folium.CircleMarker(
        [r.lat,r.lon],
        radius=3,
        color="purple",
        fill=True,
        popup=f"Live Score: {round(r.live_score,2)}"
    ).add_to(live_layer)

live_layer.add_to(m)

# =========================
# LEGEND
# =========================
legend_html = """
<div style="
position: fixed;
bottom: 50px;
left: 50px;
width: 260px;
background-color: white;
border:2px solid grey;
z-index:9999;
padding:10px;
font-size:14px;
">
<b>Insurance Intelligence Legend</b><br><br>

<b>Client Color</b><br>
Green = High Propensity<br>
Orange = Medium<br>
Red = Low<br><br>

<b>Branch Marker</b><br>
Dark Green = Strong Location<br>
Blue = Moderate<br>
Gray = Weak<br><br>

Purple dots = Live AI Score
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# =========================
# EXECUTIVE SUMMARY TABLE
# =========================
summary = df.describe().round(2).to_html()

table_popup = folium.Popup(summary, max_width=700)

folium.Marker(
    [center_lat, center_lon],
    icon=folium.Icon(color="black", icon="info-sign"),
    popup=table_popup
).add_to(m)

# =========================
# LAYER CONTROL
# =========================
folium.LayerControl(collapsed=False).add_to(m)

# =========================
# SAVE
# =========================
output_file = "insurance_ai_map.html"
m.save(output_file)

print("SUCCESS — MAP CREATED:", output_file)
