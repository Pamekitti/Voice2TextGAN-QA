import os
import time
import json
from openai import OpenAI


# configure OpenAI API key
os.environ["OPENAI_API_KEY"] = ""  # TODO: change the API key to your own
client = OpenAI()

# Upload a file with an "assistants" purpose
running_lean_path = ""  # TODO: change the path to your file
file = client.files.create(
    file=open(running_lean_path, "rb"),
    purpose='assistants'
)

# Create an assistant
assistant = client.beta.assistants.create(
    name="Demo Bot",
    instructions="You are a sale engineer chatbot for `AltoTech` company. Use your knowledge base to answer the user queries. You also have access to IoT data through provided functions. Answer as much concise as possible.",
    model="gpt-4-1106-preview",
    file_ids=[file.id],
    tools=[
        {"type": "retrieval"},
        {
            "type": "function",
            "function": {
            "name": "get_current_weather",
            "description": "Get the weather in location",
            "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The city and state e.g. San Francisco, CA"},
                        "unit": {"type": "string", "enum": ["c", "f"], "description": "temperature unit"}
                    },
                    "required": ["location"]
                }
            }
        }
    ]
)
