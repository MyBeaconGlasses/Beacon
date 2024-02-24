from dotenv import load_dotenv
from typing import List, Callable

load_dotenv()
from tools import (
    process_google_agent,
    process_weather_agent,
    process_yelp_agent,
    BucketHandler,
)
from langchain.tools import tool

from agents import Controller
from audio_utils import generate_stream_input, stream_output
import asyncio
from segment_demo import segment_point, segment_text
from openai import OpenAI


def extract_object(query):
    client = OpenAI()
    system_prompt = """
    You will be given a user question. Extract the object from the user question.
    
    Example:
    What is the the model of this car?
    
    Object: car
    """

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        max_tokens=100,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"{query}",
            },
        ],
    )

    return completion.choices[0].message.content


async def process_visual_agent(
    input: str,
    client_id: str,
    base_64_image: str,
    mode: str,
    segment_data: List,
    callback: Callable,
) -> str:
    """A helper function to process the input with the agent"""
    if "base64" in base_64_image:
        base_64_image = base_64_image.split(",")[1]
    cropped_image = ""
    if mode == "text":
        object_extracted = extract_object(input)
        mask, _, cropped_image = segment_text(base_64_image, object_extracted)
    else:
        print(segment_data)
        mask, _, cropped_image = segment_point(base_64_image, segment_data)

    await callback({"mask": mask})

    handler = BucketHandler(client_id, base_64_image, cropped_image)

    await callback({"update:": "Image uploaded"})

    @tool
    def google_lens() -> str:
        """
        Performs a google lens search on the current image for object detection. 
        Use when a specific product or object is in the image.

        Returns: The result of the google lens search.
        """
        return handler.google_lens_search()

    @tool
    def vision_analysis(prompt: str) -> str:
        """
        Uses the OPENAI Vision API to answer a question based on the user's image.
        Use when the user asks a more broad question about the image.

        Input:
        - text: a question about the image.

        Returns: The answer to the question based on the image.
        """
        return handler.vision_llm(prompt)

    controller = Controller(
        [
            process_google_agent,
            process_weather_agent,
            process_yelp_agent,
            google_lens,
            vision_analysis,
        ]
    )
    generator = controller.invoke(input)
    await callback({"update:": "Agent invoked"})
    first_text_chunk = await generator.__anext__()
    return generate_stream_input(first_text_chunk, generator)


# async def main():
#     await stream_output(
#         await process_agent(
#             "Find me a taco place in LA within 5 miles of Union Station, then give me a brief description of its history."
#         )
#     )


# asyncio.run(main())
