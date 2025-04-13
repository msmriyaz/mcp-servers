import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the same directory as this file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

WEATHER_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
WEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city using OpenWeather API.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if not WEATHER_API_KEY:
        return {
            "status": "error",
            "error_message": "OpenWeather API key not configured. Please set OPENWEATHERMAP_API_KEY in .env file."
        }

    try:
        response = requests.get(
            f"{WEATHER_API_BASE}/weather",
            params={
                "q": city,
                "appid": WEATHER_API_KEY,
                "units": "metric"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            
            return {
                "status": "success",
                "report": (
                    f"The weather in {city} is {weather} with a temperature of {temp}°C. "
                    f"Humidity: {humidity}%, Wind Speed: {wind_speed} m/s"
                )
            }
        else:
            return {
                "status": "error",
                "error_message": f"Failed to get weather data for {city}. Error: {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error retrieving weather data: {str(e)}"
        }

def get_forecast(city: str, days: int = 3) -> dict:
    """Retrieves weather forecast for a specified city using OpenWeather API.

    Args:
        city (str): The name of the city for which to retrieve the forecast.
        days (int): Number of days to forecast (1-5, default 3).

    Returns:
        dict: status and result or error msg.
    """
    if not WEATHER_API_KEY:
        return {
            "status": "error",
            "error_message": "OpenWeather API key not configured. Please set OPENWEATHERMAP_API_KEY in .env file."
        }

    try:
        # First get coordinates
        geo_response = requests.get(
            f"{WEATHER_API_BASE}/weather",
            params={
                "q": city,
                "appid": WEATHER_API_KEY
            }
        )
        
        if geo_response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"Failed to get location data for {city}. Error: {geo_response.status_code}"
            }

        geo_data = geo_response.json()
        lat = geo_data["coord"]["lat"]
        lon = geo_data["coord"]["lon"]

        # Get forecast data
        forecast_response = requests.get(
            f"{WEATHER_API_BASE}/forecast",
            params={
                "lat": lat,
                "lon": lon,
                "appid": WEATHER_API_KEY,
                "units": "metric",
                "cnt": days * 8  # 8 forecasts per day
            }
        )

        if forecast_response.status_code == 200:
            data = forecast_response.json()
            forecast_by_day = {}
            
            for item in data["list"]:
                dt = datetime.fromtimestamp(item["dt"])
                date = dt.strftime('%Y-%m-%d')
                time = dt.strftime('%H:%M')
                temp = item["main"]["temp"]
                weather = item["weather"][0]["description"]
                rain_prob = item.get("pop", 0) * 100  # Probability of precipitation
                
                if date not in forecast_by_day:
                    forecast_by_day[date] = []
                
                forecast_by_day[date].append(
                    f"  • {time}: {weather.capitalize()}, {temp:.1f}°C"
                    f"{f', {rain_prob:.0f}% chance of rain' if rain_prob > 20 else ''}"
                )
            
            # Format the output
            output_parts = [f"Weather Forecast for {city}:"]
            for date, forecasts in forecast_by_day.items():
                day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
                output_parts.append(f"\n{day_name} ({date}):")
                output_parts.extend(forecasts)
            
            return {
                "status": "success",
                "report": "\n".join(output_parts)
            }
        else:
            return {
                "status": "error",
                "error_message": f"Failed to get forecast data for {city}. Error: {forecast_response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error retrieving forecast data: {str(e)}"
        }

def get_alerts(city: str) -> dict:
    """Retrieves weather alerts for a specified city using OpenWeather API.

    Args:
        city (str): The name of the city for which to retrieve alerts.

    Returns:
        dict: status and result or error msg.
    """
    if not WEATHER_API_KEY:
        return {
            "status": "error",
            "error_message": "OpenWeather API key not configured. Please set OPENWEATHERMAP_API_KEY in .env file."
        }

    try:
        # First get coordinates
        geo_response = requests.get(
            f"{WEATHER_API_BASE}/weather",
            params={
                "q": city,
                "appid": WEATHER_API_KEY
            }
        )
        
        if geo_response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"Failed to get location data for {city}. Error: {geo_response.status_code}"
            }

        geo_data = geo_response.json()
        lat = geo_data["coord"]["lat"]
        lon = geo_data["coord"]["lon"]

        # Get alerts data
        alerts_response = requests.get(
            f"{WEATHER_API_BASE}/onecall",
            params={
                "lat": lat,
                "lon": lon,
                "appid": WEATHER_API_KEY,
                "exclude": "current,minutely,hourly,daily"
            }
        )

        if alerts_response.status_code == 200:
            data = alerts_response.json()
            if "alerts" in data and data["alerts"]:
                alerts_list = []
                for alert in data["alerts"]:
                    start = datetime.fromtimestamp(alert["start"]).strftime('%Y-%m-%d %H:%M')
                    end = datetime.fromtimestamp(alert["end"]).strftime('%Y-%m-%d %H:%M')
                    alerts_list.append(
                        f"Alert: {alert['event']}\n"
                        f"From: {start} to {end}\n"
                        f"Description: {alert['description']}\n"
                    )
                
                return {
                    "status": "success",
                    "report": f"Weather alerts for {city}:\n" + "\n".join(alerts_list)
                }
            else:
                return {
                    "status": "success",
                    "report": f"No active weather alerts for {city}."
                }
        else:
            return {
                "status": "error",
                "error_message": f"Failed to get alerts data for {city}. Error: {alerts_response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error retrieving alerts data: {str(e)}"
        }

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city using OpenWeather API for timezone lookup.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """
    if not WEATHER_API_KEY:
        return {
            "status": "error",
            "error_message": "OpenWeather API key not configured. Please set OPENWEATHERMAP_API_KEY in .env file."
        }

    try:
        # First get the city's coordinates and timezone
        response = requests.get(
            f"{WEATHER_API_BASE}/weather",
            params={
                "q": city,
                "appid": WEATHER_API_KEY
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            timezone = data["timezone"]
            tz = ZoneInfo(timezone)
            now = datetime.now(tz)
            
            return {
                "status": "success",
                "report": f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
            }
        else:
            return {
                "status": "error",
                "error_message": f"Failed to get timezone data for {city}. Error: {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error retrieving time data: {str(e)}"
        }

root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash-exp",
    description=(
        "Agent to answer questions about the time, weather, forecasts, and alerts in any city worldwide using OpenWeather API."
    ),
    instruction=(
        "I can answer your questions about the time, current weather, forecasts, and alerts in any city worldwide. "
        "I use the OpenWeather API to provide accurate and up-to-date information."
    ),
    tools=[get_weather, get_forecast, get_alerts, get_current_time],
)