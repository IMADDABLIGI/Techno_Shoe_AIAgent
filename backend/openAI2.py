import os
import json
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

# Define available tools
def get_weather(location: str):
    """Simulate weather API call - replace with real API in production"""
    return {
        "location": location,
        "temperature": "22°C",
        "forecast": "Sunny",
        "unit": "celsius"
    }

def get_stock_price(stock_symbol: str):
    """Simulate stock lookup - replace with real API"""
    return {
        "symbol": stock_symbol,
        "price": 150.42,
        "currency": "USD"
    }

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g. Paris"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get current stock price",
            "parameters": {
                "type": "object",
                "properties": {
                    "stock_symbol": {
                        "type": "string",
                        "description": "Stock symbol, e.g. AAPL"
                    }
                },
                "required": ["stock_symbol"]
            }
        }
    }
]

conversation_history = [
    {"role": "system", "content": "You are a helpful assistant. Use tools when needed."},
]

print("Chat with AI (type 'quit' to exit):")
while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["quit", "exit"]:
        break

    conversation_history.append({"role": "user", "content": user_input})

    # First API call - let LLM decide if tool is needed
    response = client.chat.completions.create(
        model=model,
        messages=conversation_history,
        tools=tools,
        tool_choice="auto",  # Let model decide
        temperature=0.7
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # If tool is called, execute it
    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "get_weather":
                function_response = get_weather(location=function_args["location"])
            elif function_name == "get_stock_price":
                function_response = get_stock_price(stock_symbol=function_args["stock_symbol"])

            # Add tool response to conversation
            conversation_history.append({
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response),
                "tool_call_id": tool_call.id
            })

        # Second API call - let LLM respond with tool data
        response = client.chat.completions.create(
            model=model,
            messages=conversation_history,
            temperature=0.7
        )
        response_message = response.choices[0].message

    # Print final response
    ai_reply = response_message.content
    print(f"\nAI: {ai_reply}")
    conversation_history.append({"role": "assistant", "content": ai_reply})