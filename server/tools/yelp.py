import os
import requests

from langchain.tools import tool
from datetime import datetime
from urllib.parse import quote
from agents import Agent
import time


API_KEY = os.getenv("YELP_API_KEY")
API_HOST = "https://api.yelp.com"
SEARCH_PATH = "/v3/businesses/search"
SEARCH_PATH_DETAILS = "/v3/businesses"


@tool
def get_places(location: str, radius: int, term: str) -> str:
    """Queries the Yelp API for up to five open businesses based the input values from the user, including location, radius from user in miles, and search term of the location the user wants to go to.

    Args:
        location (str): This string indicates the geographic area to be used when searching for businesses.
            Examples: "New York City", "NYC", "350 5th Ave, New York, NY 10118".
        radius(int): The radius from the user in miles.
        term(str): Search term, e.g. "food" or "restaurants".
            The term may also be the business's name, such as "Starbucks".

    Returns: 5 businesses and their information in the form of a dictionary.
        Example:
        {
            "name": {
                "id": "string",
                "name": "string",
                "rating": "float",
                "review_count": "int",
                "price": "string",
                "location": "string"
            }
        }
    """
    url_params = {
        "location": location.replace(" ", "+"),
        "radius": radius * 1600,
        "open_now": True,
        "term": term,
        "limit": 5,
    }
    url_params = url_params or {}
    url = "{0}{1}".format(API_HOST, quote(SEARCH_PATH.encode("utf8")))
    headers = {
        "Authorization": "Bearer %s" % API_KEY,
    }

    response = requests.request("GET", url, headers=headers, params=url_params)
    returnJson = {}

    businesses = response.json().get("businesses")
    for business in businesses:
        returnJson[business["name"]] = {
            "id": business.get("id", ""),
            "name": business.get("name", ""),
            "rating": business.get("rating", ""),
            "review_count": business.get("review_count", ""),
            "price": business.get("price", ""),
            "location": business.get("location", ""),
        }
    return returnJson


@tool
def get_business_details(business_id: str) -> str:
    """Queries the Yelp API for detailed business information based on the business id.

    Args:
        business_id (str): The id of the business to be queried.

    Returns: A dictionary of the business's detailed information.
        Keys: ["name", "is_closed", "phone", "review_count", "rating", "location", "price", "hours"]
    """

    url = "{0}{1}/{2}".format(API_HOST, SEARCH_PATH_DETAILS, business_id)
    headers = {
        "Authorization": "Bearer %s" % API_KEY,
    }

    keys_to_keep = [
        "name",
        "is_closed",
        "phone",
        "review_count",
        "rating",
        "location",
        "price",
        "hours",
    ]

    response = requests.request("GET", url, headers=headers)
    returnJson = {}
    business = response.json()
    for key in keys_to_keep:
        returnJson[key] = business.get(key, "")
    return returnJson


@tool
def get_reviews(id: str) -> str:
    """
    This function takes in the id of a business and returns the reviews of that business.

    Args:
        id (str): The id of the business.

    Returns: The reviews of the business in the form of a list
    """

    allReviews = []
    url_params = {"sort_by": "newest", "business_id_or_alias": id}
    url_params = url_params or {}
    url = "{0}{1}/{2}/reviews".format(API_HOST, SEARCH_PATH_DETAILS, id)
    headers = {
        "Authorization": "Bearer %s" % API_KEY,
    }

    response = requests.request("GET", url, headers=headers, params=url_params)
    reviewsDictionary = response.json()
    for review in reviewsDictionary["reviews"]:
        allReviews.append(review["text"])

    return str(allReviews)[1:-1]


# get_reviews("4yPqqJDJOQX69gC66YUDkA")


@tool
def process_yelp_agent(input: str) -> str:
    """Queries the Yelp agent to process the input and return the output.
    The agent is able to answer questions about:
        - Places
        - Business Details
        - Reviews
    Args:
        input (str): The user's query.

    Returns: A string of up to five businesses that are open in the location within the raidus in miles that the user wants to go to, a string of up to five events near the user, or three reviews from a business requested by the user.
    """
    # Define a list of tools
    tools = [get_places, get_business_details, get_reviews]
    agent = Agent(tools)
    output = agent.invoke(input)
    return output


# print(process_yelp_agent("Find me a taco place in LA within 5 miles of Union Station"))
