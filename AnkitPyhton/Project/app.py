import requests
import datetime
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json
import plotly.express as px

# ----------- Weather API Configuration -----------
API_KEY = "88a64324cf5421e8f91232ed276fd873"  # Replace with your OpenWeather API key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city, state=None, country="IN"):
    """Fetches current weather data for any given city and state."""
    location_query = f"{city},{country}" if not state else f"{city},{state},{country}"
    url = f"{BASE_URL}?q={location_query}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        weather_info = {
            "city": data.get("name", city),
            "state": state if state else "N/A",
            "country": country,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": data["main"].get("temp", "N/A"),
            "humidity": data["main"].get("humidity", "N/A"),
            "wind_speed": data["wind"].get("speed", "N/A"),
            "pressure": data["main"].get("pressure", "N/A"),
            "weather_condition": data["weather"][0].get("main", "N/A"),
            "latitude": data["coord"].get("lat", "N/A"),
            "longitude": data["coord"].get("lon", "N/A"),
        }
        return weather_info

    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {e}")
        return None

# ----------- Streamlit Dashboard UI -----------

st.set_page_config(page_title="Weather Dashboard", layout="wide")
st.title("🌤️ Real-Time Weather Dashboard")

# Load state-city data
with open("data.json", "r") as f:
    state_city_data = json.load(f)

# UI for state and city selection
state_name = st.selectbox("🏙️ Select State", sorted(state_city_data.keys()))
city_list = state_city_data.get(state_name, [])
city_name = st.selectbox("🌆 Select City", city_list)

# Button to fetch weather
if st.button("🔍 Get Weather"):
    weather_info = get_weather(city_name, state_name)

    if weather_info:
        st.success("✅ Weather data retrieved!")

        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌡 Temperature", f"{weather_info['temperature']} °C")
        col2.metric("💧 Humidity", f"{weather_info['humidity']}%")
        col3.metric("🌬 Wind Speed", f"{weather_info['wind_speed']} m/s")
        col4.metric("📈 Pressure", f"{weather_info['pressure']} hPa")

        st.write(f"📍 Coordinates: {weather_info['latitude']}, {weather_info['longitude']}")
        st.write(f"🕒 Date/Time: {weather_info['date']}")
        st.write(f"🌥 Condition: {weather_info['weather_condition']}")

        # Map
        st.subheader("🗺️ Location Map")
        map_obj = folium.Map(location=[weather_info['latitude'], weather_info['longitude']], zoom_start=10)
        folium.Marker(
            [weather_info['latitude'], weather_info['longitude']],
            popup=f"{city_name}",
            tooltip=weather_info['weather_condition']
        ).add_to(map_obj)
        folium_static(map_obj)

        # Simulated data
        st.subheader("📊 Simulated 10-Day Trends")
        df = pd.DataFrame({
            "Date": pd.date_range(end=pd.Timestamp.today(), periods=10),
            "Temperature": [weather_info["temperature"] + i for i in range(10)],
            "Humidity": [weather_info["humidity"] - i for i in range(10)],
            "Wind Speed": [weather_info["wind_speed"] + i * 0.2 for i in range(10)],
        })
        st.dataframe(df)

        # 📈 Interactive Line Chart
        st.subheader("📈 Weather Trends (Line Chart)")
        fig_line = px.line(df, x="Date", y=["Temperature", "Humidity", "Wind Speed"], markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

        # 📊 Histogram
        st.subheader("📊 Metric Distributions")
        for col in ["Temperature", "Humidity", "Wind Speed"]:
            fig_hist = px.histogram(df, x=col, nbins=10, title=f"{col} Distribution", marginal="box", color_discrete_sequence=["skyblue"])
            st.plotly_chart(fig_hist, use_container_width=True)

        # 📊 Bar Chart
        st.subheader("📊 Bar Charts")
        for col in ["Temperature", "Humidity", "Wind Speed"]:
            fig_bar = px.bar(df, x="Date", y=col, title=f"{col} Over Time", text_auto=True)
            st.plotly_chart(fig_bar, use_container_width=True)

        # 🔵 Scatter Plots
        st.subheader("🔵 Scatter Plots")
        fig_scatter1 = px.scatter(df, x="Temperature", y="Humidity", title="Temperature vs Humidity", size_max=10)
        st.plotly_chart(fig_scatter1, use_container_width=True)

        fig_scatter2 = px.scatter(df, x="Temperature", y="Wind Speed", title="Temperature vs Wind Speed", size_max=10)
        st.plotly_chart(fig_scatter2, use_container_width=True)

        # 🔥 Correlation Heatmap
        st.subheader("🔥 Correlation Heatmap")
        corr = df[["Temperature", "Humidity", "Wind Speed"]].corr()
        fig_heat = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", title="Correlation Matrix")
        st.plotly_chart(fig_heat, use_container_width=True)

        # 🌄 Area Chart
        st.subheader("🌄 Area Chart (Stacked Trends)")
        fig_area = px.area(df, x="Date", y=["Temperature", "Humidity", "Wind Speed"], title="Weather Metrics Over Time")
        st.plotly_chart(fig_area, use_container_width=True)

    else:
        st.error("❌ Failed to retrieve weather data. Check city/state or API key.")
