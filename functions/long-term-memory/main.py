from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def get_embedding(text, model="text-embedding-3-small"):
  text = text.replace("\n", " ")
  return client.embed(text, model=model).data[0].embedding

