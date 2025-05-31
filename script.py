import os
import json
from openai import OpenAI
from pydantic import BaseModel

# === CONFIG ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4.1"  # Replace with "gpt-4-0613" if needed

# === INITIALIZE CLIENT ===
client = OpenAI(api_key=OPENAI_API_KEY)

# === TOOL DEFINITION ===
tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_stoic_scripts",
            "description": "Generate short video scripts",
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

class Script(BaseModel):
    title: str
    hook: str
    body: str
    close: str

    @property
    def text(self):
        return self.hook + self.body + self.close

# === MAIN LOGIC ===
def generate_scripts():
    print("🚀 Generating Scripts...")

    # Create the chat completion request
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    "Generate ten unique Stoicism-themed YouTube Shorts scripts. "
                    "Each script should include: title, hook, body, and close. "
                    "Format them using the generate_stoic_scripts function. "
                    "Make them engaging and educative. Aim for viral potential. "
                    "In the close always call to action."
                )
            }
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "generate_stoic_scripts"}}
    )

    # Extract the function call arguments
    try:
        tool_response = response.choices[0].message.tool_calls[0].function
        scripts = json.loads(tool_response.arguments)["scripts"]
    except Exception as e:
        print("❌ Failed to parse scripts:")
        print(json.dumps(response.model_dump(), indent=2))
        raise e

    # Save the scripts to a file
    output_path = "stoic_shorts_bulk.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scripts, f, indent=2, ensure_ascii=False)

    print(f"✅ All scripts saved to '{output_path}'")

    return scripts

# === ENTRY POINT ===
if __name__ == "__main__":
    scripts = generate_scripts()
