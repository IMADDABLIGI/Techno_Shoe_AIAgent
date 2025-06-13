from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from typing import Optional

# SECRET_KEY=''
# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="LLM API Server")

# Initialize Anthropic client
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

client = Anthropic(api_key=anthropic_api_key)

@app.get("/ask")
async def ask_question(question: str, model: Optional[str] = "claude-3-haiku-20240307"):
    """
    Endpoint to ask questions to Claude LLM
    Example: /ask?question=What is the meaning of life?&model=claude-3-sonnet-20240229
    """
    try:
        # Call Anthropic API
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[
                {"role": "user", "content": question}
            ]
        )
        
        return {
            "question": question,
            "answer": response.content[0].text,
            "model": model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "LLM API Server is running. Use /ask?question=YOUR_QUESTION to interact with Claude."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)