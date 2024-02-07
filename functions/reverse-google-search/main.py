import requests
from google.cloud import storage
from dotenv import load_dotenv
import datetime
import os

load_dotenv()


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")


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


def reverse_image_search(image_url):
    print(image_url)
    api_key = os.getenv("SERPAPI_API_KEY")

    search_url = f"https://serpapi.com/search?engine=google_reverse_image&api_key={api_key}&image_url={image_url}"

    response = requests.get(search_url)
    data = response.json()

    return data


# TESTING THE FUNCTION
bucket_name = "beacon-reverse-image-api"
source_file_name = "./car.png"
destination_blob_name = "car.png"

# Upload the image
upload_blob(bucket_name, source_file_name, destination_blob_name)

# Generate and print the authenticated URL for the uploaded image
image_url = f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"

# Run the reverse image search
search_results = reverse_image_search(image_url)

print(search_results)
