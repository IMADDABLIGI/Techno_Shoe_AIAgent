import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient
from typing import List, Dict, Any

load_dotenv()

# OpenAI Configuration
token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4o"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

# MongoDB Configuration
def get_db_connection():
    mongo_client = MongoClient(os.getenv("CONNECTION_STRING"))
    try:
        mongo_client.admin.command('ping')
        print("✅ Connected to MongoDB successfully!")
    except Exception as e:
        raise Exception(f"❌ Could not connect to MongoDB: {e}")
    
    db_name = os.getenv("DB_NAME")
    return mongo_client[db_name]

# Database instance
db = get_db_connection()

# Tool Functions
def search_shoes(brand=None, category=None, price_min=None, price_max=None, color=None, 
                gender=None, size=None, in_stock_only=True, min_rating=None):
    """Search for shoes in the database based on various criteria"""
    try:
        # Build query filter
        query_filter = {}
        
        if brand:
            query_filter["brand"] = {"$regex": brand, "$options": "i"}
        
        if category:
            query_filter["category"] = {"$regex": category, "$options": "i"}
        
        if price_min is not None or price_max is not None:
            price_filter = {}
            if price_min is not None:
                price_filter["$gte"] = float(price_min)
            if price_max is not None:
                price_filter["$lte"] = float(price_max)
            query_filter["price"] = price_filter
        
        if color:
            query_filter["color"] = {"$regex": color, "$options": "i"}
        
        if gender:
            query_filter["gender"] = {"$regex": gender, "$options": "i"}
        
        if size:
            query_filter["sizes"] = int(size)
        
        if in_stock_only:
            query_filter["in_stock"] = True
        
        if min_rating is not None:
            query_filter["rating"] = {"$gte": float(min_rating)}
        
        # Execute query
        results = list(db.shoes.find(query_filter).limit(10))
        
        # Convert ObjectId to string for JSON serialization
        for result in results:
            result["_id"] = str(result["_id"])
        
        if not results:
            return json.dumps({
                "message": "No shoes found matching your criteria.",
                "suggestions": "Try adjusting your requirements or check our full catalog."
            })
        
        return json.dumps({
            "found_shoes": len(results),
            "shoes": results,
            "message": f"Found {len(results)} shoes matching your criteria!"
        })
        
    except Exception as e:
        return json.dumps({"error": f"Database search error: {str(e)}"})

def get_shoe_recommendations(preferences=None):
    """Get general shoe recommendations based on customer preferences"""
    try:
        # Get top-rated, in-stock shoes
        pipeline = [
            {"$match": {"in_stock": True, "rating": {"$gte": 4.0}}},
            {"$sort": {"rating": -1, "price": 1}},
            {"$limit": 5}
        ]
        
        results = list(db.shoes.aggregate(pipeline))
        
        # Convert ObjectId to string
        for result in results:
            result["_id"] = str(result["_id"])
        
        return json.dumps({
            "recommendations": results,
            "message": "Here are our top-rated shoes currently in stock!"
        })
        
    except Exception as e:
        return json.dumps({"error": f"Recommendation error: {str(e)}"})

def get_brands_and_categories():
    """Get available brands and categories from the database"""
    try:
        brands = db.shoes.distinct("brand")
        categories = db.shoes.distinct("category")
        colors = db.shoes.distinct("color")
        
        return json.dumps({
            "available_brands": brands,
            "available_categories": categories,
            "available_colors": colors,
            "message": "Here's what we have available in our store!"
        })
        
    except Exception as e:
        return json.dumps({"error": f"Catalog error: {str(e)}"})

def check_shoe_availability(shoe_name=None, size=None):
    """Check if a specific shoe is available in a specific size"""
    try:
        query_filter = {}
        
        if shoe_name:
            query_filter["name"] = {"$regex": shoe_name, "$options": "i"}
        
        if size:
            query_filter["sizes"] = int(size)
        
        query_filter["in_stock"] = True
        
        results = list(db.shoes.find(query_filter))
        
        # Convert ObjectId to string
        for result in results:
            result["_id"] = str(result["_id"])
        
        return json.dumps({
            "available": len(results) > 0,
            "shoes": results,
            "message": f"{'Available!' if results else 'Sorry, not available in that size.'}"
        })
        
    except Exception as e:
        return json.dumps({"error": f"Availability check error: {str(e)}"})

# Tool definitions for OpenAI function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_shoes",
            "description": "Search for shoes based on customer preferences like brand, category, price range, color, gender, size, and rating",
            "parameters": {
                "type": "object",
                "properties": {
                    "brand": {"type": "string", "description": "Shoe brand (Nike, Adidas, Puma, etc.)"},
                    "category": {"type": "string", "description": "Shoe category (Running, Basketball, Casual, Training)"},
                    "price_min": {"type": "number", "description": "Minimum price"},
                    "price_max": {"type": "number", "description": "Maximum price"},
                    "color": {"type": "string", "description": "Shoe color"},
                    "gender": {"type": "string", "description": "Target gender (Men, Women, Unisex)"},
                    "size": {"type": "number", "description": "Shoe size"},
                    "in_stock_only": {"type": "boolean", "description": "Only show in-stock items", "default": True},
                    "min_rating": {"type": "number", "description": "Minimum rating (1-5)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_shoe_recommendations",
            "description": "Get general shoe recommendations for customers who are browsing",
            "parameters": {
                "type": "object",
                "properties": {
                    "preferences": {"type": "string", "description": "Customer preferences or notes"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_brands_and_categories",
            "description": "Get all available brands, categories, and colors in the store",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_shoe_availability",
            "description": "Check if a specific shoe is available in a particular size",
            "parameters": {
                "type": "object",
                "properties": {
                    "shoe_name": {"type": "string", "description": "Name of the shoe to check"},
                    "size": {"type": "number", "description": "Shoe size to check"}
                }
            }
        }
    }
]

# Map function names to actual functions
available_functions = {
    "search_shoes": search_shoes,
    "get_shoe_recommendations": get_shoe_recommendations,
    "get_brands_and_categories": get_brands_and_categories,
    "check_shoe_availability": check_shoe_availability
}

# Initialize conversation history with e-commerce context
conversation_history = [
    {"role": "system", "content": """You are a helpful AI shopping assistant for a shoe store. Your goal is to help customers find the perfect shoes based on their needs and preferences.

PERSONALITY:
- Be friendly, enthusiastic, and knowledgeable about shoes
- Ask clarifying questions to understand customer needs
- Provide personalized recommendations
- Always mention key details like price, rating, and availability

CONVERSATION FLOW:
1. Greet the customer warmly
2. Ask about their shoe needs (occasion, style, size, budget, etc.)
3. Use the search tools to find matching shoes
4. Present options with pros/cons
5. Help them make a decision
6. Offer alternatives if nothing matches perfectly

WHEN PRESENTING SHOES:
- Always mention: name, brand, price, rating, availability
- Highlight what makes each shoe special
- Group similar options together
- Suggest alternatives if budget/preferences don't match

SEARCH STRATEGY:
- Start broad, then narrow down based on customer feedback
- Always check availability and stock
- Consider price range and value
- Factor in ratings and reviews

Remember: You're here to help customers find shoes they'll love, not just make a sale!"""},
]

def format_shoe_presentation(shoes_data):
    """Helper function to format shoe data for customer presentation"""
    if isinstance(shoes_data, str):
        data = json.loads(shoes_data)
    else:
        data = shoes_data
    
    if "shoes" in data:
        formatted_shoes = []
        for shoe in data["shoes"]:
            shoe_info = f"""
🔥 **{shoe['name']}**
   • Brand: {shoe['brand']} | Category: {shoe['category']}
   • Price: ${shoe['price']} | Rating: {shoe['rating']}/5 ⭐
   • Color: {shoe['color']} | Gender: {shoe['gender']}
   • Available Sizes: {', '.join(map(str, shoe['sizes']))}
   • Status: {'✅ In Stock' if shoe['in_stock'] else '❌ Out of Stock'}
"""
            formatted_shoes.append(shoe_info)
        return "\n".join(formatted_shoes)
    return str(data)

def chat_shoe_assistant():
    print("👟 Welcome to our AI Shoe Shopping Assistant! 👟")
    print("Ask me about shoes and I'll help you find the perfect pair!")
    print("Type 'quit' to exit")
    print("-" * 60)
    
    # Start with a greeting
    print("\nAI Assistant: Hello! Welcome to our shoe store! 👋")
    print("I'm here to help you find the perfect shoes. What kind of shoes are you looking for today?")
    print("You can tell me about:")
    print("• The occasion (running, work, casual, sports)")
    print("• Your preferred brand or style")
    print("• Your budget range")
    print("• Your size and color preferences")
    print("• Or just ask for recommendations!")
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("\nAI Assistant: Thanks for shopping with us! Come back anytime! 👟✨")
            break

        # Add user message to history
        conversation_history.append({"role": "user", "content": user_input})

        try:
            # Get AI response with tools
            response = client.chat.completions.create(
                model=model,
                messages=conversation_history,
                tools=tools,
                tool_choice="auto",
                temperature=0.7,
                top_p=0.9,
            )

            response_message = response.choices[0].message
            
            # Check if the model wants to call a function
            if response_message.tool_calls:
                print("\n🔍 Searching our shoe inventory...")
                
                # Add the assistant's response to conversation history
                conversation_history.append(response_message)
                
                # Process each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"   📋 Looking for: {function_args}")
                    
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
                print(f"\nAI Assistant: {ai_reply}")
                
                # Add final response to history
                conversation_history.append({"role": "assistant", "content": ai_reply})
                
            else:
                # No tool calls needed, just regular response
                ai_reply = response_message.content
                print(f"\nAI Assistant: {ai_reply}")
                
                # Add AI reply to history
                conversation_history.append({"role": "assistant", "content": ai_reply})
                
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or rephrase your request.")

if __name__ == "__main__":
    try:
        chat_shoe_assistant()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for visiting our shoe store! Have a great day!")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please check your database connection and try again.")