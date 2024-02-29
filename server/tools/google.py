from agents import Agent

from langchain.agents import Tool
from langchain.tools import tool

from langchain_community.tools.google_finance import GoogleFinanceQueryRun
from langchain_community.utilities.google_finance import GoogleFinanceAPIWrapper

from langchain_community.tools.google_jobs import GoogleJobsQueryRun
from langchain_community.utilities.google_jobs import GoogleJobsAPIWrapper

from langchain_community.tools.google_scholar import GoogleScholarQueryRun
from langchain_community.utilities.google_scholar import GoogleScholarAPIWrapper

from langchain_community.tools.google_trends import GoogleTrendsQueryRun
from langchain_community.utilities.google_trends import GoogleTrendsAPIWrapper

from langchain_community.utilities import GoogleSerperAPIWrapper

google_finance = GoogleFinanceQueryRun(api_wrapper=GoogleFinanceAPIWrapper())
google_finance.description = (
    "Queries the Google Finance API for the stock price of the input company ticker."
)
google_jobs = GoogleJobsQueryRun(api_wrapper=GoogleJobsAPIWrapper())
google_scholar = GoogleScholarQueryRun(api_wrapper=GoogleScholarAPIWrapper())

search = GoogleSerperAPIWrapper()
google_search = Tool(
    name="google_search",
    func=search.run,
    description="Searches Google for the input query",
)

google_trends = GoogleTrendsQueryRun(api_wrapper=GoogleTrendsAPIWrapper())

# Define a list of tools
tools = [google_finance, google_jobs, google_scholar, google_search, google_trends]


@tool
def process_google_agent(input: str) -> str:
    """Asks the google agent to process the input and return the output.
    The agent is able to answer questions about:
    - Finance
    - Jobs
    - Scholar (Academic Response)
    - Search
    - Trends

    Arg:
        input (str): The query of the user.

    Returns: A string of the response of the query.
    """
    agent = Agent(tools)
    output = agent.invoke(input)
    return output


# print(process_google_agent("What is the price of Trader Joe's hand cream?"))
