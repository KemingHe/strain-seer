import json

import pytest

from tools.weather import get_weather_data


@pytest.fixture
def weather_response():
    return {
        "location": {
            "name": "London",
            "region": "City of London, Greater London",
            "country": "United Kingdom",
        },
        "current": {"temp_c": 5.2, "condition": {"text": "Sunny"}},
    }


@pytest.fixture
def forecast_response(weather_response):
    return {
        **weather_response,
        "forecast": {
            "forecastday": [
                {"date": "2025-02-18", "day": {"maxtemp_c": 6.8}},
                {"date": "2025-02-19", "day": {"maxtemp_c": 9.0}},
            ]
        },
    }


def test_get_forecast_weather_success(mocker, forecast_response):
    mock_response = mocker.Mock(status_code=200)
    mock_response.json.return_value = forecast_response
    mock_get = mocker.patch("tools.weather.get", return_value=mock_response)

    result = get_weather_data("London", 2)
    expected = json.dumps(forecast_response, indent=2)

    assert result == expected
    assert "forecast.json" in mock_get.call_args[0][0]
    assert "days=2" in mock_get.call_args[0][0]


def test_get_weather_invalid_location(mocker):
    mock_response = mocker.Mock(status_code=404)
    mocker.patch("tools.weather.get", return_value=mock_response)

    result = get_weather_data("InvalidLocation")
    assert result == "Failed to fetch weather data from WeatherAPI."


def test_get_weather_api_error(mocker):
    mocker.patch("tools.weather.get", return_value=None)

    result = get_weather_data("London")
    assert result == "Failed to fetch weather data from WeatherAPI."


def test_normalize_forecast_days_limits(mocker):
    # Test with various forecast day values
    test_cases = [
        (0, 0),  # No forecast
        (1, 1),  # Valid 1-day forecast
        (3, 3),  # Maximum allowed days
        (4, 3),  # Exceeds maximum, should return 3
        (-1, 0),  # Invalid negative days
    ]

    mock_get = mocker.patch("tools.weather.get")
    for input_days, expected_days in test_cases:
        get_weather_data("London", input_days)
        if expected_days > 0:
            assert "days=" + str(expected_days) in mock_get.call_args[0][0]
