import streamlit as st
import pandas as pd
import requests
import datetime as dt
import pydeck as pdk
import matplotlib.pyplot as plt

# ---------------- Config ----------------
USGS_FEED = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
CACHE_TTL_SECONDS = 30  # how often to refresh feed
# ----------------------------------------

st.set_page_config(page_title="Live Earthquake Dashboard", layout="wide")
st.title("🌍 Live Earthquake Dashboard")

st.markdown(
    """
This dashboard visualizes recent earthquakes using USGS GeoJSON feeds.  
Interactive map, recent events, top 10 vulnerable quakes, and pie chart of magnitude.
"""
)

# ---------------- Sidebar Controls ----------------
with st.sidebar:
    st.header("Controls")
    min_mag = st.slider("Minimum magnitude", min_value=0.0, max_value=8.0, value=0.0, step=0.1)
    show_only_significant = st.checkbox("Show only magnitude >= 4.0", value=False)
    
    # NEW: refresh controls
    st.markdown("---")
    auto_refresh = st.checkbox("Enable auto-refresh", value=True)
    refresh_interval = st.number_input("Refresh interval (seconds)", min_value=5, max_value=3600, value=30, step=5)
    refresh_now = st.button("Refresh Now")
    
    st.markdown("---")
    st.markdown("Data source: USGS Earthquake Feeds (GeoJSON)")

# ---------------- Fetch USGS Data ----------------
@st.cache_data(ttl=CACHE_TTL_SECONDS)
def fetch_usgs():
    resp = requests.get(USGS_FEED)
    resp.raise_for_status()
    return resp.json()

geojson = fetch_usgs()

# ---------------- Parse into DataFrame ----------------
features = geojson.get("features", [])
rows = []
for f in features:
    props = f.get("properties", {})
    geom = f.get("geometry", {})
    coords = geom.get("coordinates", [None, None, None])
    lon, lat, depth = coords[0], coords[1], coords[2] if len(coords) >= 3 else None
    time_ms = props.get("time")
    time_dt = dt.datetime.utcfromtimestamp(time_ms / 1000.0) if time_ms else None
    rows.append({
        "time": time_dt,
        "place": props.get("place"),
        "magnitude": props.get("mag"),
        "depth_km": depth,
        "lon": lon,
        "lat": lat,
    })

df = pd.DataFrame(rows)
df = df.dropna(subset=["lat", "lon"])  # require location
df["magnitude"] = pd.to_numeric(df["magnitude"], errors="coerce")
df["depth_km"] = pd.to_numeric(df["depth_km"], errors="coerce")
df = df.sort_values("time", ascending=False)

# Filter
if show_only_significant:
    min_mag = max(min_mag, 4.0)
df = df[df["magnitude"].fillna(0) >= min_mag]

# ---------------- Layout: Map + Table ----------------
map_col, table_col = st.columns([2, 1])

with map_col:
    st.subheader("Earthquake Map")
    if df.empty:
        st.info("No earthquakes matching the filters.")
    else:
        # radius scale
        def mag_to_radius(m):
            base = 10000
            return base * (1.8 ** (m if m else 0))

        df["radius_m"] = df["magnitude"].apply(mag_to_radius)

        # color by depth
        def depth_to_color(depth):
            if pd.isna(depth):
                return [200, 200, 200]
            d = max(0, min(700, float(depth)))
            r = int(max(0, 255 - (d / 700) * 200))
            g = int(max(60, 160 - (d / 700) * 60))
            b = int(min(255, int((d / 700) * 255)))
            return [r, g, b]

        df["color"] = df["depth_km"].apply(depth_to_color)

        deck_df = df[["lat", "lon", "magnitude", "place", "time", "depth_km", "radius_m", "color"]]
        deck_df["time_str"] = deck_df["time"].dt.strftime("%Y-%m-%d %H:%M:%S UTC")

        initial_view = pdk.ViewState(
            latitude=float(deck_df["lat"].median()),
            longitude=float(deck_df["lon"].median()),
            zoom=1.5,
            pitch=0
        )

        scatter = pdk.Layer(
            "ScatterplotLayer",
            data=deck_df,
            get_position=["lon", "lat"],
            get_radius="radius_m",
            get_fill_color="color",
            pickable=True,
            auto_highlight=True
        )

        tooltip = {
            "html": "<b>{place}</b><br/>Mag: {magnitude} &nbsp;&nbsp; Depth: {depth_km} km<br/>{time_str}<br/><a href='{url}' target='_blank'>Details</a>",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }

        r = pdk.Deck(layers=[scatter], initial_view_state=initial_view, tooltip=tooltip)
        st.pydeck_chart(r, use_container_width=True)

with table_col:
    st.subheader("Recent Events")
    st.markdown(f"**Events:** {len(df)}")
    recent = df[["time", "place", "magnitude", "depth_km"]].head(30)
    st.dataframe(recent.rename(columns={"depth_km": "depth (km)"}), use_container_width=True)

# ---------------- Top 10 Vulnerable ----------------
st.subheader("🔥 Top 10 Most Vulnerable Earthquakes (by magnitude)")
top10 = df.sort_values("magnitude", ascending=False).head(10)

if not top10.empty:
    st.table(top10[["time", "place", "magnitude", "depth_km"]].rename(
        columns={"depth_km": "depth (km)"}))

    # Pie chart using matplotlib
    fig, ax = plt.subplots(figsize=(6,6))
    labels = top10["place"].tolist()
    sizes = top10["magnitude"].tolist()
    explode = [0.1 if i == 0 else 0 for i in range(len(sizes))]
    ax.pie(sizes, labels=labels, autopct='%1.1f', startangle=140, explode=explode, shadow=False)
    ax.set_title("Magnitude (Richter Scale) Distribution")
    st.pyplot(fig)
else:
    st.info("No earthquake events to display for top 10 vulnerable list.")

# ---------------- Trend Analysis ----------------
st.subheader("📈 Magnitude Trend Analysis")

# Use last N hours (instead of days) for USGS all_day feed
num_hours = st.sidebar.slider("Number of past hours for trend", 1, 24, 12)

if not df.empty:
    now = dt.datetime.utcnow()
    start_time = now - dt.timedelta(hours=num_hours)
    trend_df = df[df["time"] >= start_time]

    if not trend_df.empty:
        # Round time to the nearest hour for grouping
        trend_df["hour"] = trend_df["time"].dt.floor("H")
        trend = trend_df.groupby("hour")["magnitude"].mean().reset_index()

        fig, ax = plt.subplots(figsize=(8,4))
        ax.plot(trend["hour"], trend["magnitude"], marker='o', linestyle='-', color='orange')
        ax.set_title(f"Average Magnitude Over Last {num_hours} Hours")
        ax.set_xlabel("Time (UTC)")
        ax.set_ylabel("Average Magnitude")
        ax.grid(True)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.info(f"No earthquake data in the last {num_hours} hours.")
else:
    st.info("No earthquake data available for trend analysis.")

# ---------------- Depth vs Magnitude Scatter ----------------
st.subheader("⚡ Depth vs Magnitude Scatter Plot")

if not df.empty:
    fig, ax = plt.subplots(figsize=(8,5))
    sc = ax.scatter(df["magnitude"], df["depth_km"], c=df["depth_km"], cmap="viridis", s=50, alpha=0.7)
    ax.set_xlabel("Magnitude (Richter)")
    ax.set_ylabel("Depth (km)")
    ax.set_title("Depth vs Magnitude of Earthquakes")
    plt.colorbar(sc, label="Depth (km)")
    ax.grid(True)
    st.pyplot(fig)
else:
    st.info("No earthquake data available for scatter plot.")

st.markdown("---")
st.caption(f"Data source: USGS GeoJSON feed. Cached for {CACHE_TTL_SECONDS} seconds.")