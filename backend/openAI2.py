import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4o"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

# Define available tools/functions
def get_weather(city):
    """Get current weather for a city"""
    # This is a mock function - replace with actual weather API
    weather_data = {
        "city": city,
        "temperature": "22°C",
        "condition": "Sunny",
        "humidity": "65%"
    }
    return json.dumps(weather_data)

def get_current_time():
    """Get current date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate_math(expression):
    """Safely calculate mathematical expressions"""
    try:
        # Only allow basic math operations for safety
        allowed_chars = "0123456789+-*/.() "
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return str(result)
        else:
            return "Error: Invalid characters in expression"
    except:
        return "Error: Cannot calculate expression"

def search_web(query):
    """Mock web search function"""
    # Replace this with actual web search API
    return f"Search results for '{query}': [Mock results - integrate with real search API]"

# Tool definitions for OpenAI function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather information for a specific city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name to get weather for"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_math",
            "description": "Calculate mathematical expressions",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to calculate"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Map function names to actual functions
available_functions = {
    "get_weather": get_weather,
    "get_current_time": get_current_time,
    "calculate_math": calculate_math,
    "search_web": search_web
}

# Initialize conversation history
conversation_history = [
    {"role": "system", "content": """You are a helpful AI assistant with access to various tools. 
    You can get weather information, current time, perform calculations, and search the web.
    When a user asks for information that requires using a tool, use the appropriate function."""},
]

def chat_ai_agent():
    print("Chat with AI Agent (type 'quit' to exit)")
    print("Available functions: weather, time, math calculations, web search")
    print("-" * 50)
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        # Add user message to history
        conversation_history.append({"role": "user", "content": user_input})

        try:
            # Get AI response with tools
            response = client.chat.completions.create(
                model=model,
                messages=conversation_history,
                tools=tools,
                tool_choice="auto",  # Let the model decide when to use tools
                temperature=0.7,
                top_p=0.9,
            )

            response_message = response.choices[0].message
            
            # Check if the model wants to call a function
            if response_message.tool_calls:
                print("\n🔧 Using tools...")
                
                # Add the assistant's response to conversation history
                conversation_history.append(response_message)
                
                # Process each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"   Calling {function_name} with args: {function_args}")
                    
                    # Call the function
                    if function_name in available_functions:
                        function_response = available_functions[function_name](**function_args)
                    else:
                        function_response = f"Error: Function {function_name} not found"
                    
                    # Add function response to conversation
                    conversation_history.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response
                    })
                
                # Get the final response from the model
                final_response = client.chat.completions.create(
                    model=model,
                    messages=conversation_history,
                    temperature=0.7,
                    top_p=0.9,
                )
                
                ai_reply = final_response.choices[0].message.content
                print(f"\nAI: {ai_reply}")
                
                # Add final response to history
                conversation_history.append({"role": "assistant", "content": ai_reply})
                
            else:
                # No tool calls needed, just regular response
                ai_reply = response_message.content
                print(f"\nAI: {ai_reply}")
                
                # Add AI reply to history
                conversation_history.append({"role": "assistant", "content": ai_reply})
                
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")

if __name__ == "__main__":
    try:
        chat_ai_agent()
    except KeyboardInterrupt:
        print("\n\nBye...")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")