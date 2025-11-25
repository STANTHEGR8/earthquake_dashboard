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
```
2. **Create a virtual environment (optional but recommended)**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. **Install dependencies**
```bash
pip install -r requirements.txt
```
4. **Running the Dashboard**
```bash
streamlit run earthquake_dashboard.py
```
Open the link in your browser (usually http://localhost:8501).

Configuration
Sidebar Controls:
Minimum magnitude filter
Show only significant quakes (>=4.0)
Auto-refresh toggle + interval (seconds)
Number of hours/days for trend analysis

Data Source:
_USGS Earthquake GeoJSON Feeds_
