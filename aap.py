import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Weather Analytics Dashboard",
    page_icon="🌦️",
    layout="wide"
)

st.title("🌦️ Real-Time Weather Analytics Dashboard")
st.write("Check current weather and forecast for any city.")

city = st.text_input("Enter City Name", "Nagpur")

if st.button("Get Weather"):
    if not city.strip():
        st.warning("Please enter a city name.")
        st.stop()

    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_response = requests.get(
            geo_url,
            params={"name": city, "count": 1, "language": "en"},
            timeout=15
        )
        geo_response.raise_for_status()
        locations = geo_response.json().get("results", [])

        if not locations:
            st.error("City not found. Please try another city.")
            st.stop()

        location = locations[0]
        latitude = location["latitude"]
        longitude = location["longitude"]

        weather_url = "https://api.open-meteo.com/v1/forecast"

        response = requests.get(
            weather_url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,relative_humidity_2m,"
                    "apparent_temperature,wind_speed_10m"
                ),
                "daily": (
                    "temperature_2m_max,temperature_2m_min,"
                    "precipitation_probability_max"
                ),
                "timezone": "auto",
                "forecast_days": 7
            },
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        daily = data["daily"]

        st.subheader(
            f"📍 {location['name']}, "
            f"{location.get('country', '')}"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Temperature",
            f"{current['temperature_2m']} °C"
        )

        col2.metric(
            "Feels Like",
            f"{current['apparent_temperature']} °C"
        )

        col3.metric(
            "Humidity",
            f"{current['relative_humidity_2m']}%"
        )

        col4.metric(
            "Wind Speed",
            f"{current['wind_speed_10m']} km/h"
        )

        st.caption(
            f"Last observation time: {current['time']} "
            f"({data.get('timezone', 'local time')})"
        )

        st.subheader("📊 Seven-Day Weather Forecast")

        forecast = pd.DataFrame({
            "Date": daily["time"],
            "Maximum Temperature (°C)": daily["temperature_2m_max"],
            "Minimum Temperature (°C)": daily["temperature_2m_min"],
            "Rain Probability (%)": daily["precipitation_probability_max"]
        })

        st.line_chart(
            forecast.set_index("Date")[
                [
                    "Maximum Temperature (°C)",
                    "Minimum Temperature (°C)"
                ]
            ]
        )

        st.bar_chart(
            forecast.set_index("Date")[["Rain Probability (%)"]]
        )

        st.dataframe(forecast, use_container_width=True)

        st.download_button(
            "Download Weather Report (CSV)",
            forecast.to_csv(index=False),
            file_name="weather_report.csv",
            mime="text/csv"
        )

    except requests.RequestException:
        st.error("Weather service unavailable. Please try again.")

    except (KeyError, ValueError, TypeError):
        st.error("Unable to process weather data. Please try again.")
