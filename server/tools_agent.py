from dotenv import load_dotenv

load_dotenv()
from tools import process_google_agent, process_weather_agent, process_yelp_agent
from agents import Controller
from audio_utils import generate_stream_input, stream_output
import asyncio


async def process_agent(input: str) -> str:
    """A helper function to process the input with the agent"""
    controller = Controller(
        [process_google_agent, process_weather_agent, process_yelp_agent]
    )
    generator = controller.invoke(input)
    first_text_chunk = await generator.__anext__()
    return generate_stream_input(first_text_chunk, generator)


# async def main():
#     await stream_output(
#         await process_agent(
#             "Find me a taco place in LA within 5 miles of Union Station, then give me a brief description of its history."
#         )
#     )


# asyncio.run(main())
