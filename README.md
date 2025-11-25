# 🌍 Live Earthquake Dashboard

This is a **real-time earthquake dashboard** built with **Python**, **Streamlit**, and **Matplotlib/Pydeck**. It visualizes earthquakes from the **USGS GeoJSON feed** and provides interactive features.

## Features

- 🌐 **Interactive Map**: Plot earthquake locations, magnitude, and depth.  
- 📋 **Recent Events Table**: Shows latest earthquakes with details.  
- 🔥 **Top 10 Vulnerable Earthquakes**: Table + Matplotlib pie chart of magnitude distribution.  
- 📈 **Magnitude Trend Analysis**: Moving average magnitude over the past N hours/days.  
- ⚡ **Depth vs Magnitude Scatter Plot**: Visualize patterns between quake depth and magnitude.  
- ⏱ **Manual & Auto Refresh**: Update live data with user-defined intervals.  

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/<your-username>/earthquake-dashboard.git
cd earthquake-dashboard
Create a virtual environment (optional but recommended)

bash
Copy code
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
Install dependencies

bash
Copy code
pip install -r requirements.txt
Running the Dashboard
bash
Copy code
streamlit run earthquake_dashboard.py
Open the link in your browser (usually http://localhost:8501).

Configuration
Sidebar Controls:

Minimum magnitude filter

Show only significant quakes (>=4.0)

Auto-refresh toggle + interval (seconds)

Number of hours/days for trend analysis

Data Source
USGS Earthquake GeoJSON Feeds
