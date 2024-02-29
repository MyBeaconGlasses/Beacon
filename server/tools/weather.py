import os
import requests
from langchain.tools import tool
from urllib.parse import quote
from agents import Agent

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_HOST = "http://api.weatherapi.com/v1/"
WEATHER_SEARCH_PATH = "current.json"


def get_info(city: str) -> str:
    """Queries the Weather API for the current weather condition based on the input city from the user.

    Args:
        city (str): The city of the user.

    Returns: A string of the current weather condition in the city the user is in.
    """
    weather_url_params = {
        "q": city,
        "key": WEATHER_API_KEY,
    }
    weather_url_params = weather_url_params or {}
    url = "{0}{1}".format(WEATHER_API_HOST, quote(WEATHER_SEARCH_PATH.encode("utf8")))
    headers = {
        "Authorization": "Bearer %s" % WEATHER_API_KEY,
    }
    # print(u'Querying {0} ...'.format(url))

    response = requests.request("GET", url, headers=headers, params=weather_url_params)
    return response.json()


@tool
def find_weather_condition(city: str) -> str:
    """Queries the Weather API for the current weather condition based on the input city from the user.

    Args:
        city (str): The city of the user.

    Returns: A string of the current weather condition in the city the user is in.
    """
    return get_info(city)["current"]["condition"]["text"]


@tool
def find_temp(city: str) -> str:
    """Queries the Weather API for the current temperature in Fahrenheit based on the input city from the user.

    Args:
        city (str): The city of the user.

    Returns: A string of the current temperature in Fahrenheit of the city the user is in.
    """
    return get_info(city)["current"]["temp_f"]


@tool
def find_humidity(city: str) -> str:
    """Queries the Weather API for the current humidity as a percentage based on the input city from the user.

    Args:
        city (str): The city of the user.

    Returns: A string of the current humidity as a percentage in the city the user is in.
    """
    return get_info(city)["current"]["humidity"]


@tool
def find_precip(city: str) -> str:
    """Queries the Weather API for the current precipitation in inches based on the input city from the user.

    Args:
        city (str): The city of the user.

    Returns: A string of the precipitation in inches of the city the user is in.
    """
    return get_info(city)["current"]["precip_in"]


@tool
def find_wind_speed(city: str) -> str:
    """Queries the Weather API for the wind speed in miles per hour based on the input city from the user.

    Args:
        city (str): The city of the user.

    Returns: A string of the current wind speed in miles per hour of the city the user is in.
    """
    return get_info(city)["current"]["wind_mph"]


@tool
def process_weather_agent(input: str) -> str:
    """Asks the weather agent to process the input and return the output.
    The agent is able to find the current weather condition, temperature, humidity, precipitation, and wind speed of the city the user is in.

    Arg:
        input (str): The city of the user.

    Returns: A string of the current weather condition, temperature, humidity, precipitation, and wind speed of the city the user is in.
    """
    # Define a list of tools
    tools = [
        find_weather_condition,
        find_temp,
        find_humidity,
        find_precip,
        find_wind_speed,
    ]
    agent = Agent(tools)
    output = agent.invoke(input)
    return output
