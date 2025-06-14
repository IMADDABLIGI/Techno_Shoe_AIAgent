import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

# Enhanced weather function
def get_weather(location: str):
    """Simulate weather API call with richer data"""
    return {
        "location": location,
        "temperature": "22°C",
        "forecast": "Sunny",
        "humidity": "65%",
        "wind_speed": "15 km/h"
    }

# Better location extraction
def extract_location(text: str):
    """Extract location using simple regex (improve with NLP if needed)"""
    match = re.search(r"(weather|forecast) in (\w+)", text, re.IGNORECASE)
    return match.group(2) if match else "Paris"  # default

def handle_weather_query(user_input: str):
    """Handle weather queries and format response for LLM"""
    location = extract_location(user_input)
    weather_data = get_weather(location)
    
    # Format that forces LLM to use the data
    return {
        "role": "user",
        "content": (
            f"User asked: '{user_input}'. "
            f"Here's weather data for {location}: {json.dumps(weather_data)}. "
            "Use this data to answer precisely."
        )
    }

conversation_history = [
    {"role": "system", "content": (
        "You're a helpful assistant. When given data, use it to answer. "
        "Never make up information when data is provided."
    )},
]
def chat_ai_agent():
    print("Chat with AI (type 'quit' to exit):")
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["quit", "exit"]:
            break

        # Check for weather queries
        if "weather" in user_input.lower() or "forecast" in user_input.lower():
            weather_context = handle_weather_query(user_input)
            conversation_history.append(weather_context)
        else:
            conversation_history.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=model,
            messages=conversation_history,
            temperature=0.7,
            top_p=0.9
        )

        ai_reply = response.choices[0].message.content
        print(f"\nAI: {ai_reply}")
        conversation_history.append({"role": "assistant", "content": ai_reply})

if __name__ == "__main__":
    try:
        chat_ai_agent()
    except:
        print("\nBye...")