import os
from openai import OpenAI  # ← Switch to OpenAI's client
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Get key from https://platform.openai.com/api-keys

# Define tools (same as before)
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
}]

messages = [{"role": "system", "content": "You're a helpful assistant."}]

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    messages.append({"role": "user", "content": user_input})

    # First call: Let LLM decide if it needs a tool
    response = client.chat.completions.create(
        model="gpt-4-turbo",  # or "gpt-3.5-turbo"
        messages=messages,
        tools=tools,  # ← Pass tools here
        tool_choice="auto",  # ← Let model decide
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Execute tools if needed
    if tool_calls:
        for tool_call in tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            if func_name == "get_weather":
                result = get_weather(args["location"])  # Your function
                messages.append({
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id
                })

        # Second call: LLM responds with tool results
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages
        )
        response_message = response.choices[0].message

    print("Assistant:", response_message.content)
    messages.append(response_message)