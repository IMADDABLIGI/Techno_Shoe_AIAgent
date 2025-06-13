import os
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

# Initialize conversation history
conversation_history = [
    {"role": "system", "content": "You are a helpful AI assistant."},
]

print("Chat with AI (type 'quit' to exit):")
while True:
    # Get user input
    user_input = input("\nYou: ")
    if user_input.lower() in ["quit", "exit"]:
        break

    # Add user message to history
    conversation_history.append({"role": "user", "content": user_input})

    # Get AI response
    response = client.chat.completions.create(
        model=model,
        messages=conversation_history,
        temperature=0.7,  # Less random than 1 for coherent conversations
        top_p=0.9,
    )

    # Get and print AI reply
    ai_reply = response.choices[0].message.content
    print(f"\nAI: {ai_reply}")

    # Add AI reply to history
    conversation_history.append({"role": "assistant", "content": ai_reply})