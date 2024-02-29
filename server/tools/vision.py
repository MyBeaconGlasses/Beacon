from google.cloud import storage
import os
import uuid
from serpapi import GoogleSearch
from openai import OpenAI
import base64


def identify_object(lst):
    client = OpenAI()
    system_prompt = "Your task is to identify the most common and specific subject in a given list of image titles, sorted in non-decreasing order of priority. Return the result in the format {title: <title>, object: <object>}, where <title> is the most specific name of the subject directly from the list, and <object> is the general category or type of the item. Prioritize earlier items in the list for determining the most common subject. Ensure specificity in identification, applicable to various subjects like technology, food, or other categories. For example, if the most common subject is 'Nikon D850', the response should be {title: 'Nikon D850', object: 'camera'}."
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"List: {lst}",
            },
        ],
    )

    return completion.choices[0].message.content


def convert_to_base64(image_path: str):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    image_base64 = base64.b64encode(image_data)
    image_base64_str = image_base64.decode("utf-8")
    return image_base64_str


class BucketHandler:
    def __init__(self, client_id, full_image, cropped_image):
        self.bucket_name = "beacon_demo"
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self.bucket_name)
        self.client_id = client_id
        self.bucket_name = "beacon_demo"
        self.upload_blob(full_image, cropped_image)

    def upload_blob(self, full_image, cropped_image):
        """Uploads base64 encoded data to the bucket."""
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)

        # For full image
        blob = bucket.blob(self.client_id)
        image_data = base64.b64decode(full_image)
        blob.cache_control = 'no-cache'
        blob.upload_from_string(image_data, content_type="image/jpeg")

        # For cropped image
        blob = bucket.blob(f"{self.client_id}_cropped")
        cropped_image_data = base64.b64decode(cropped_image)
        blob.cache_control = 'no-cache'
        blob.upload_from_string(cropped_image_data, content_type="image/jpeg")

        print(f"Data uploaded to {self.client_id}.")

    def google_lens_search(self):
        """Reverse Google image search."""
        file_id = self.client_id
        bucket_name = self.bucket_name
        image_url = f"https://storage.googleapis.com/{bucket_name}/{file_id}"

        params = {
            "engine": "google_lens",
            "url": image_url,
            "api_key": os.getenv("SERPAPI_API_KEY"),
        } 

        search = GoogleSearch(params)
        results = search.get_dict()
        if "visual_matches" not in results:
            return "No visual matches found."
        visual_matches = results["visual_matches"]
        titles = [match["title"] for match in visual_matches if "title" in match]
        res = identify_object(titles)
        return res

    def vision_llm(self, query):
        file_id = self.client_id
        bucket_name = self.bucket_name
        image_url = f"https://storage.googleapis.com/{bucket_name}/{file_id}"
        cropped_image_url = (
            f"https://storage.googleapis.com/{bucket_name}/{file_id}_cropped"
        )

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"You are given two images, one is the original image and the other is the cropped image that the user has selected. User query: {query}",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": cropped_image_url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=1000,
        )

        return response.choices[0].message.content
