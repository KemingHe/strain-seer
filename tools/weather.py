import json
from typing import Optional

from httpx import get, Response
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from config.envs import WEATHERAPI_API_KEY


def normalize_forcast_days(forcast_days: int, max_days: int = 3) -> int:
    if forcast_days > 0:
        if forcast_days <= max_days:
            return forcast_days
        else:
            return max_days
    return 0


def get_weather_data(location: str, forcast_days: int = 0) -> str:
    normalized_forcast_days: int = normalize_forcast_days(forcast_days)

    current_endpoint: str = (
        f"https://api.weatherapi.com/v1/current.json?key={WEATHERAPI_API_KEY}"
    )
    forcast_endpoint: str = (
        f"https://api.weatherapi.com/v1/forecast.json?key={WEATHERAPI_API_KEY}"
    )

    location_param: str = f"&q={location}"
    forcast_days_param: str = f"&days={normalized_forcast_days}"
    air_quality_param: str = "&aqi=yes"
    alerts_param: str = "&alerts=yes"

    response: Response | None = None
    if normalized_forcast_days > 0:
        response = get(
            forcast_endpoint
            + location_param
            + forcast_days_param
            + air_quality_param
            + alerts_param
        )
    else:
        response = get(current_endpoint + location_param + air_quality_param)

    if response and response.status_code == 200:
        return json.dumps(response.json(), indent=2)

    return "Failed to fetch weather data from WeatherAPI."


class WeatherInput(BaseModel):
    location: str = Field(
        description="The city name, zip/postal code, or coordinates (lat,lon) to get weather data for"
    )
    forcast_days: Optional[int] = Field(
        default=0,
        description="Number of forecast days (0-3). Use 0 for current weather only, 1-3 for forecast",
        ge=0,
        le=3,
    )


class WeatherTool(BaseTool):
    name: str = "Weather Tool"
    description: str = """This tool fetches current weather data and forecasts from WeatherAPI.
    It can provide current conditions or forecasts up to 3 days including today.
    The data includes temperature, conditions, air quality, and weather alerts if available."""
    args_schema: type[BaseModel] = WeatherInput

    def _run(self, location: str, forcast_days: int = 0) -> str:
        return get_weather_data(location, forcast_days)
