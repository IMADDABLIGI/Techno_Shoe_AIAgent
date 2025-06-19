import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential

load_dotenv()

# Initialize client
endpoint = "https://models.github.ai/inference"
model = "deepseek/DeepSeek-V3-0324"
token = os.environ["GITHUB_TOKEN"]

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

# Store conversation history
conversation_history = [
    SystemMessage("You are a helpful AI assistant."),
]

def chat_with_llm():
    print("Chat with AI (type 'quit' to exit):")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "quit":
            break

        # Add user message to history
        conversation_history.append(UserMessage(user_input))

        # Get LLM response
        response = client.complete(
            messages=conversation_history,
            temperature=0.8,
            top_p=0.1,
            max_tokens=2048,
            model=model
        )

        ai_response = response.choices[0].message.content
        print(f"\nAI: {ai_response}")

        # Add AI response to history
        conversation_history.append(AssistantMessage(ai_response))

        print("History Messages: ",conversation_history)

if __name__ == "__main__":
    try:
        chat_with_llm()
    except Exception as err:
        print("Error: ", err)