import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential

load_dotenv()

client = ChatCompletionsClient(
    endpoint="https://models.github.ai/inference",
    credential=AzureKeyCredential(os.environ["GITHUB_TOKEN"]),
)

messages = []

print("Type 'exit' to quit.")
while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "exit":
        break

    messages.append(UserMessage(user_input))

    response = client.complete(
        messages=messages,
        model="microsoft/Phi-3-mini-4k-instruct",
        temperature=0.8,
        max_tokens=2048,
        top_p=0.1
    )

    assistant_reply = response.choices[0].message.content
    print("\nAssistant:", assistant_reply)
    messages.append(AssistantMessage(assistant_reply))