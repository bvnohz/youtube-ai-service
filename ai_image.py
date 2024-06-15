import os
from openai import OpenAI

os.environ["OPENAI_API_KEY"] = "sk-proj-sGXNiyTNh5Eday3cR5hLT3BlbkFJnZ6DShB7M1NcHZO4r0n9"

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

response = client.images.generate(
  model="dall-e-3",
  prompt="대나무 숲의 판다",
  size="1024x1024",
  quality="standard",
  n=1,
)

image_url = response.data[0].url
print(image_url)