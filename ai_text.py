import os
from openai import OpenAI

os.environ["OPENAI_API_KEY"] = "sk-proj-sGXNiyTNh5Eday3cR5hLT3BlbkFJnZ6DShB7M1NcHZO4r0n9"

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "너에 대해서 설명해줘",
        }
    ],
    model="gpt-4o",
)

print(chat_completion.choices[0].message.content)
