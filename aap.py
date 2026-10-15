python
```
import streamlit as st
import json
import urllib.request
import urllib.parse

st.set_page_config(
    page_title="Weather Analytics Dashboard",
    page_icon="🌦️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #101418;
    color: #e8edf2;
}
[data-testid="stSidebar"] {
    background: #171d23;
}
h1, h2, h3, p, label {
    color: #e8edf2;
}
.hero {
    padding: 1.5rem;
    border: 1px solid #34434e;
    border-radius: 16px;
    background: linear-gradient(120deg, #182630, #172027);
    margin-bottom: 1.5rem;
}
.metric-card {
    padding: 1.2rem;
    background: #192229;
    border: 1px solid #34434e;
    border-radius: 12px;
    text-align: center;
}
.weather-value {
    font-size: 2rem;
    font-weight: bold;
    color: #38bdf8;
}
.weather-box {
    padding: 1rem;
    background: #0b0e11;
    border: 1px solid #35434d;
    border-radius: 12px;
    margin-bottom: 0.5rem;
}
div.stButton > button {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

def get_weather(city):
    geo_url = (
        "https://geocoding-api.open-meteo.com/v1/search?"
        + urllib.parse.urlencode({
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        })
    )

    request = urllib.request.Request(
        geo_url,
        headers={"User-Agent": "WeatherDashboard/1.0"}
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        geo = json.loads(response.read().decode("utf-8"))

    if not geo.get("results"):
        raise ValueError("City not found. Please enter a valid city name.")

    place = geo["results"][0]

    forecast_url = (
        "https://api.open-meteo.com/v1/forecast?"
        + urllib.parse.urlencode({
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "hourly": "temperature_2m,relative_humidity_2m",
            "forecast_days": 1,
            "timezone": "auto"
        })
    )

    request = urllib.request.Request(
        forecast_url,
        headers={"User-Agent": "WeatherDashboard/1.0"}
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))

    hourly = data["hourly"]
    times = hourly["time"]
    temperatures = hourly["temperature_2m"]
    humidity = hourly["relative_humidity_2m"]

    valid_temps = [t for t in temperatures if t is not None]
    valid_humidity = [h for h in humidity if h is not None]

    if not valid_temps or not valid_humidity:
        raise ValueError("Weather data is unavailable for this city.")

    # Find the forecast closest to the current local time.
    current_time = data.get("current", {}).get("time")

    if current_time in times:
        current_index = times.index(current_time)
    else:
        current_index = 0

    hourly_data = []

    for i in range(0, min(len(times), 24), 3):
        if temperatures[i] is not None:
            hourly_data.append({
                "time": times[i],
                "temperature": temperatures[i],
                "humidity": humidity[i]
            })

    return {
        "city": place["name"],
        "country": place.get("country", ""),
        "temperature": temperatures[current_index],
        "humidity": humidity[current_index],
        "average_temperature": round(
            sum(valid_temps) / len(valid_temps), 1
        ),
        "maximum_temperature": max(valid_temps),
        "minimum_temperature": min(valid_temps),
        "average_humidity": round(
            sum(valid_humidity) / len(valid_humidity), 1
        ),
        "hourly": hourly_data
    }

# Header
st.markdown("""
<div class="hero">
    <small>PYTHON EXPERIENTIAL LEARNING PROJECT</small>
    <h1>🌦️ Weather Analytics Dashboard</h1>
    <p>Explore temperature, humidity, and hourly weather forecasts
    using Python and the Open-Meteo API.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🧭 Navigation")
    page = st.radio(
        "Choose Section",
        [
            "Weather Dashboard",
            "Hourly Forecast",
            "About Project"
        ]
    )

    st.divider()
    st.caption("Weather data powered by Open-Meteo.")
    st.caption("Enter a city to retrieve its forecast.")

# City search
st.subheader("🔍 Search City")

with st.form("weather_search"):
    city = st.text_input(
        "Enter city name",
        placeholder="e.g. Nagpur, Mumbai, London"
    )
    submitted = st.form_submit_button(
        "🌤️ Get Weather",
        use_container_width=True
    )

if "weather" not in st.session_state:
    st.session_state.weather = None

if submitted:
    if not city.strip():
        st.error("Please enter a city name.")
    else:
        try:
            with st.spinner("Fetching weather data..."):
                st.session_state.weather = get_weather(city.strip())
        except ValueError as e:
            st.session_state.weather = None
            st.error(str(e))
        except Exception:
            st.session_state.weather = None
            st.error(
                "Unable to retrieve weather data. "
                "Check your internet connection and try again."
            )

weather = st.session_state.weather

if weather:
    st.markdown(
        f"### 📍 {weather['city']}, {weather['country']}"
    )

    if page == "Weather Dashboard":
        st.subheader("📊 Weather Statistics")

        a, b, c = st.columns(3)

        with a:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>🌡️ Temperature</h3>
                    <div class="weather-value">
                        {weather['temperature']}°C
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with b:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>💧 Humidity</h3>
                    <div class="weather-value">
                        {weather['humidity']}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>📅 Average Temperature</h3>
                    <div class="weather-value">
                        {weather['average_temperature']}°C
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")

        d, e, f = st.columns(3)

        d.metric(
            "Maximum Temperature",
            f"{weather['maximum_temperature']}°C"
        )
        e.metric(
            "Minimum Temperature",
            f"{weather['minimum_temperature']}°C"
        )
        f.metric(
            "Average Humidity",
            f"{weather['average_humidity']}%"
        )

        st.divider()

        st.subheader("📈 Temperature Analysis")

        chart_data = {
            "Time": [
                item["time"].split("T")[-1]
                for item in weather["hourly"]
            ],
            "Temperature (°C)": [
                item["temperature"]
                for item in weather["hourly"]
            ]
        }

        st.line_chart(
            chart_data,
            x="Time",
            y="Temperature (°C)"
        )

        st.subheader("💧 Humidity Analysis")

        humidity_data = {
            "Time": [
                item["time"].split("T")[-1]
                for item in weather["hourly"]
            ],
            "Humidity (%)": [
                item["humidity"]
                for item in weather["hourly"]
            ]
        }

        st.line_chart(
            humidity_data,
            x="Time",
            y="Humidity (%)"
        )

    elif page == "Hourly Forecast":
        st.subheader("🕒 Hourly Weather Forecast")
        st.caption("Forecast values are shown at three-hour intervals.")

        for item in weather["hourly"]:
            col1, col2, col3 = st.columns(3)

            col1.write(f"🕒 **{item['time']}**")
            col2.write(f"🌡️ {item['temperature']} °C")

            if item["humidity"] is not None:
                col3.write(f"💧 {item['humidity']}%")
            else:
                col3.write("💧 Unavailable")

            st.divider()

        st.download_button(
            "⬇️ Download Weather Report",
            data=json.dumps(weather, indent=4),
            file_name="weather_report.json",
            mime="application/json",
            use_container_width=True
        )

    elif page == "About Project":
        st.subheader("📘 About This Project")

        st.markdown("""
        <div class="weather-box">
            <h3>Project Overview</h3>
            This application retrieves weather forecasts for a selected
            city and presents useful statistics in an interactive dashboard.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🛠️ Technologies Used")

        st.markdown("""
        - **Python** — application logic and calculations
        - **Streamlit** — interactive website interface
        - **Open-Meteo API** — geocoding and weather forecast data
        - **JSON** — API responses and report downloads
        - **Pandas-style charts** — visual weather analysis
        """)

        st.markdown("### ✨ Features")

        st.markdown("""
        - City-based weather search
        - Temperature and humidity statistics
        - Maximum and minimum temperature calculations
        - Hourly forecast display
        - Interactive charts
        - JSON weather report download
        """)

else:
    st.info(
        "👆 Enter a city name above and click **Get Weather** "
        "to view its forecast."
    )

    st.markdown("### 🌍 What You Can Explore")

    a, b, c = st.columns(3)

    a.markdown("""
    <div class="metric-card">
        <h3>🌡️ Temperature</h3>
        <p>View average, maximum, and minimum temperatures.</p>
    </div>
    """, unsafe_allow_html=True)

    b.markdown("""
    <div class="metric-card">
        <h3>💧 Humidity</h3>
        <p>Explore humidity readings and daily averages.</p>
    </div>
    """, unsafe_allow_html=True)

    c.markdown("""
    <div class="metric-card">
        <h3>📈 Analytics</h3>
        <p>Visualize weather trends with interactive charts.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.caption(
    "Python • Streamlit • REST API • Weather Analytics • Data Visualization"
)
```
