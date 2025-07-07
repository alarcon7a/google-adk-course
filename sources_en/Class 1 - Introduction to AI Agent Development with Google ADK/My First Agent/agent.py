import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import requests

def get_weather(city: str) -> dict:
    """Returns a weather report using the public wttr.in API (no key required)."""
    response = requests.get(f"https://wttr.in/{city}?format=j1")
    if not response.ok:
        return {"status": "error", "error_message": "Could not get weather information."}
    data = response.json()
    c = data["current_condition"][0]
    report = (
        f"The weather in {city} is {c['weatherDesc'][0]['value'].lower()} "
        f"with temperature {c['temp_C']}°C, humidity {c['humidity']}% "
        f"and feels like {c['FeelsLikeC']}°C."
    )
    return {"status": "success", "report": report}


def get_current_time(city: str) -> dict:
    """Returns local time for multiple cities using their time zones."""
    # Extended dictionary of cities and their time zones
    tz_map = {
        "bogota": "America/Bogota",
        "new york": "America/New_York",
        "london": "Europe/London",
        "paris": "Europe/Paris",
        "madrid": "Europe/Madrid",
        "tokyo": "Asia/Tokyo",
        "sydney": "Australia/Sydney",
        "mexico city": "America/Mexico_City",
        "buenos aires": "America/Argentina/Buenos_Aires",
        "hong kong": "Asia/Hong_Kong",
        "dubai": "Asia/Dubai",
        "moscow": "Europe/Moscow",
        "singapore": "Asia/Singapore",
        "rio de janeiro": "America/Sao_Paulo",
        "chicago": "America/Chicago",
        "los angeles": "America/Los_Angeles",
        "toronto": "America/Toronto",
        "berlin": "Europe/Berlin",
        "amsterdam": "Europe/Amsterdam",
        "rome": "Europe/Rome"
    }
    # Normalize input
    city_lower = city.lower()

    if city_lower not in tz_map:
        return {"status": "error", "error_message": f"I don't have timezone information for {city}."}

    try:
        now = datetime.datetime.now(ZoneInfo(tz_map[city_lower]))
        report = now.strftime("%H:%M:%S on %d-%m-%Y")
        return {"status": "success", "report": f"The time in {city} is {report}."}
    except Exception as e:
        return {"status": "error", "error_message": f"Error getting time: {str(e)}"}


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.5-flash",
    description=(
        "You are an agent that answers questions about weather and time"
    ),
    instruction=(
        "You are an assistant that can answer weather and time questions according to the city, use the available tools for this purpose. "
        "Send the city in lowercase and without accents or symbols, always respond in English."
    ),
    tools=[get_weather, get_current_time],
)