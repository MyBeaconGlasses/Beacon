import weaviate
import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

client = weaviate.Client(
    url="http://localhost:8080",  # Replace with your endpoint
    additional_headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_APIKEY")},
)

schema = {
    "classes": [
        {
            "class": "Memory",
            "description": "A class to store AI memories",
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "The content of the memory",
                },
                {
                    "name": "createdAt",
                    "dataType": ["date"],
                    "description": "When the memory was created",
                },
                {
                    "name": "location",
                    "dataType": ["geoCoordinates"],
                    "description": "Geographical location of the memory",
                },
            ],
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {},
                "generative-openai": {},
            },
        }
    ]
}


def create_schema(schema):
    client.schema.create(schema)


def insert_sample_memory():
    memory_object = {
        "content": "This is a test memory stored in the LTM system.",
        "createdAt": "2023-01-01T12:00:00Z",
        "location": {"latitude": 40.7128, "longitude": -74.0060},
    }

    result = client.data_object.create(data_object=memory_object, class_name="Memory")
    object_id = result[
        "id"
    ]  # Assuming result is the successful response containing the ID
    try:
        retrieved_object = client.data_object.get(uuid=object_id, class_name="Memory")
        print("Retrieved object:", retrieved_object)
    except weaviate.ObjectNotFoundException:
        print("Object not found.")
