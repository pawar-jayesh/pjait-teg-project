import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(city: str, units: str = "metric"):
    if not WEATHER_API_KEY:
        return {"error": "Missing api key"}

    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": units
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return {"error": f"Weather API error {response.status_code}", "details": response.text}

    data = response.json()
    return {
        "location": data.get("name"),
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"]
    }
