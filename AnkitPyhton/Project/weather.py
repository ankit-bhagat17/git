import requests
import datetime

API_KEY = "88a64324cf5421e8f91232ed276fd873"  # Replace with your OpenWeather API key
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city, state=None, country="IN"):
    location_query = f"{city},{country}" if not state else f"{city},{state},{country}"
    url = f"{BASE_URL}?q={location_query}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return {
            "city": data.get("name", city),
            "state": state or "N/A",
            "temperature": data["main"].get("temp"),
            "humidity": data["main"].get("humidity"),
            "wind_speed": data["wind"].get("speed"),
            "weather": data["weather"][0].get("main"),
            "lat": data["coord"].get("lat"),
            "lon": data["coord"].get("lon"),
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except requests.RequestException:
        return None