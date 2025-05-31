import os
from openai import OpenAI
import json

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the function schema
tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_stoic_scripts",
            "description": "Generate Stoicism-themed short video scripts",
            "parameters": {
                "type": "object",
                "properties": {
                    "scripts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "hook": {"type": "string"},
                                "body": {"type": "string"},
                                "close": {"type": "string"}
                            },
                            "required": ["title", "hook", "body", "close"]
                        }
                    }
                },
                "required": ["scripts"]
            }
        }
    }
]

# Create the chat completion request
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {
            "role": "user",
            "content": "Generate ten unique Stoicism-themed YouTube Shorts scripts. Each script should include: title, hook, body, and close. Format them using the generate_stoic_scripts function. Make them engaging and educative. Aim for viral potential. In the close always call to action."
        }
    ],
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "generate_stoic_scripts"}}
)

# Extract the function arguments
tool_response = response.choices[0].message.tool_calls[0].function
scripts = json.loads(tool_response.arguments)["scripts"]

# Save the scripts to a JSON file
with open("stoic_shorts_bulk.json", "w", encoding="utf-8") as f:
    json.dump(scripts, f, indent=2, ensure_ascii=False)

print("✅ All scripts saved to 'stoic_shorts_bulk.json'")
