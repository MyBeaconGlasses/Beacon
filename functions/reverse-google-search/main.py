import requests
from google.cloud import storage
from dotenv import load_dotenv
import datetime
import os
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
import uuid
import base64

load_dotenv()


def upload_blob(bucket_name, base64_data, destination_blob_name):
    """Uploads base64 encoded data to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Decode the base64 string to bytes
    image_data = base64.b64decode(base64_data)

    # Use upload_from_string to upload the data
    blob.upload_from_string(image_data)

    print(f"Data uploaded to {destination_blob_name}.")


def generate_signed_url(bucket_name, blob_name):
    """Generates a signed URL for a blob."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # This URL is valid for 15 minutes
    url = blob.generate_signed_url(
        expiration=datetime.timedelta(minutes=15), version="v4"
    )

    return url


def reverse_image_search_api(image_url):
    print(image_url)
    api_key = os.getenv("SERPAPI_API_KEY")

    search_url = f"https://serpapi.com/search?engine=google_reverse_image&api_key={api_key}&image_url={image_url}"

    response = requests.get(search_url)
    data = response.json()

    return data


@tool("reverse-image-search")
def reverse_image_search(base64_image: str) -> dict:
    """Reverse Google image search."""
    file_id = str(uuid.uuid4())
    bucket_name = "beacon-reverse-image-api"
    upload_blob(bucket_name, base64_image, file_id)

    image_url = f"https://storage.googleapis.com/{bucket_name}/{file_id}"
    search_results = reverse_image_search_api(image_url)

    return search_results


# image_path = "./car.png"
# with open(image_path, "rb") as image_file:
#     image_data = image_file.read()
# image_base64 = base64.b64encode(image_data)
# image_base64_str = image_base64.decode("utf-8")

# print(reverse_image_search(image_base64_str))
