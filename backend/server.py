import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient
from typing import List, Dict, Any
import re

load_dotenv()

app = Flask(__name__)
CORS(app)

# OpenAI Configuration
current_model_index = 0
ai_models = ["openai/gpt-4.1", "openai/gpt-4.1-mini", "openai/gpt-4.1-nano", "openai/gpt-4o", "openai/gpt-4o-mini", "openai/o4-mini"]
token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model = ai_models[current_model_index]

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

# Store customer sessions
customer_sessions = {}

# Tool Functions
def search_shoes(brand=None, category=None, price_min=None, price_max=None, color=None,
                gender=None, size=None, in_stock_only=True, min_rating=None):
    """Search for shoes in the database based on various criteria"""
    try:
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

        results = list(db.shoes.find(query_filter).limit(10))

        # Convert ObjectId to string
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
        pipeline = [
            {"$match": {"in_stock": True, "rating": {"$gte": 4.0}}},
            {"$sort": {"rating": -1, "price": 1}},
            {"$limit": 8}
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

def save_customer_info(first_name, last_name=None, age=None, phone=None,
                      interested_products=None, conversation_history=None):
    """Save customer information to the database"""
    try:
        customer_data = {
            "first_name": first_name,
            "last_name": last_name,
            "age": int(age) if age else None,
            "phone": phone,
            "interested_products": interested_products or [],
            "conversation_history": conversation_history or [],
            "created_at": datetime.now()
        }

        customer_data = {k: v for k, v in customer_data.items() if v is not None}

        result = db.customers.insert_one(customer_data)

        return json.dumps({
            "success": True,
            "customer_id": str(result.inserted_id),
            "message": "Customer information saved successfully!"
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to save customer info: {str(e)}"
        })

# Tool definitions
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_shoes",
            "description": "Search for shoes based on customer preferences",
            "parameters": {
                "type": "object",
                "properties": {
                    "brand": {"type": "string", "description": "Shoe brand"},
                    "category": {"type": "string", "description": "Shoe category"},
                    "price_min": {"type": "number", "description": "Minimum price in DH"},
                    "price_max": {"type": "number", "description": "Maximum price in DH"},
                    "color": {"type": "string", "description": "Shoe color"},
                    "gender": {"type": "string", "description": "Target gender"},
                    "size": {"type": "number", "description": "Shoe size (EU)"},
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
            "description": "Get general shoe recommendations",
            "parameters": {
                "type": "object",
                "properties": {
                    "preferences": {"type": "string", "description": "Customer preferences"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_brands_and_categories",
            "description": "Get available brands, categories, and colors",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_shoe_availability",
            "description": "Check shoe availability in specific size",
            "parameters": {
                "type": "object",
                "properties": {
                    "shoe_name": {"type": "string", "description": "Name of the shoe"},
                    "size": {"type": "number", "description": "Shoe size (EU)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_customer_info",
            "description": "Save customer information",
            "parameters": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string", "description": "Customer's first name"},
                    "last_name": {"type": "string", "description": "Customer's last name"},
                    "age": {"type": "number", "description": "Customer's age"},
                    "phone": {"type": "string", "description": "Customer's phone number"},
                    "interested_products": {"type": "array", "items": {"type": "string"}},
                    "conversation_history": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["first_name"]
            }
        }
    }
]

available_functions = {
    "search_shoes": search_shoes,
    "get_shoe_recommendations": get_shoe_recommendations,
    "get_brands_and_categories": get_brands_and_categories,
    "check_shoe_availability": check_shoe_availability,
    "save_customer_info": save_customer_info
}

def get_system_message():
    return {
        "role": "system",
        "content": """You are Amine, a helpful AI shopping assistant for Techno Shoe in Casablanca Sidi Maarouf, Morocco.

STORE INFO:
- Name: Techno Shoe
- Location: Casablanca Sidi Maarouf, Morocco
- Currency: Moroccan Dirham (DH)
- Sizes: European sizes (36-47)

PERSONALITY: Be friendly, enthusiastic, and knowledgeable.

CRITICAL INSTRUCTIONS FOR FRONTEND INTEGRATION:
1. Your responses are sent to a frontend application that handles data display separately
2. NEVER include raw shoe data (JSON objects, detailed product specs) in your conversational responses
3. When you use tools to fetch shoe data, the frontend automatically receives and displays this data
4. Your role is to provide conversational context and guidance, NOT to display product details
5. Instead of showing product details, refer to them conversationally like:
   - "I found some great options for you!"
   - "Here are [X] shoes that match your criteria"
   - "The products are now displayed for you to browse"
   - "Take a look at these recommendations"

EXAMPLE GOOD RESPONSES:
- "I found 5 Nike sneakers in your size! Take a look at the options displayed."
- "Here are our top-rated shoes currently available. What do you think?"
- "Perfect! I found some great running shoes within your budget."

EXAMPLE BAD RESPONSES (DON'T DO THIS):
- Including shoe names, prices, or detailed specs in your text
- Listing product information like "Nike Air Max - 850 DH - Rating: 4.5"
- Showing JSON data or structured product information

Remember: Be conversational and helpful, but let the frontend handle all product data display!"""
    }

def clean_ai_response(ai_reply, shoes_data):
    """
    Clean the AI response to ensure no shoe data leaks into the conversational text
    """
    if not shoes_data:
        return ai_reply
    
    # Remove any potential product data patterns from the response
    # This is a safety net in case the LLM still includes product info
    
    # Pattern to match common product data formats
    patterns_to_remove = [
        r'\{[^}]*"name"[^}]*\}',  # JSON-like objects with "name" field
        r'\{[^}]*"price"[^}]*\}',  # JSON-like objects with "price" field
        r'\{[^}]*"brand"[^}]*\}',  # JSON-like objects with "brand" field
        r'SHOES_DATA:.*?(?=\n\n|\n[A-Z]|$)',  # SHOES_DATA sections
        r'\[.*?"_id".*?\]',  # Arrays with _id fields
    ]
    
    cleaned_response = ai_reply
    for pattern in patterns_to_remove:
        cleaned_response = re.sub(pattern, '', cleaned_response, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up any extra whitespace or newlines left behind
    cleaned_response = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_response)
    cleaned_response = cleaned_response.strip()
    
    return cleaned_response

@app.route('/api/chat', methods=['POST'])
def chat():
    global model, current_model_index
    print("-------------- AI model: ", model, " --------------")
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')

        # print("-----", model, "-----", user_message, "-----")

        # Initialize or get session
        if session_id not in customer_sessions:
            customer_sessions[session_id] = {
                "conversation_history": [get_system_message()],
                "customer_state": {
                    "interested_products": [],
                    "conversation_turns": 0,
                    "serious_interest_indicators": 0,
                    "contact_info": {}
                }
            }

        session = customer_sessions[session_id]
        conversation_history = session["conversation_history"]

        # Add user message to history
        conversation_history.append({"role": "user", "content": user_message})

        # Get AI response
        response = client.chat.completions.create(
            model=model,
            messages=conversation_history,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
            top_p=0.9,
        )

        response_message = response.choices[0].message
        shoes_data = None

        # Handle tool calls
        if response_message.tool_calls:
            conversation_history.append(response_message)

            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                if function_name in available_functions:
                    function_response = available_functions[function_name](**function_args)

                    # Parse shoes data for frontend
                    if function_name in ["search_shoes", "get_shoe_recommendations", "check_shoe_availability"]:
                        try:
                            parsed_response = json.loads(function_response)
                            if "shoes" in parsed_response:
                                shoes_data = parsed_response["shoes"]
                            elif "recommendations" in parsed_response:
                                shoes_data = parsed_response["recommendations"]
                        except:
                            pass
                else:
                    function_response = f"Error: Function {function_name} not found"

                conversation_history.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response
                })

            # Get final response
            final_response = client.chat.completions.create(
                model=model,
                messages=conversation_history,
                temperature=0.7,
                top_p=0.9,
            )

            ai_reply = final_response.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": ai_reply})
        else:
            ai_reply = response_message.content
            conversation_history.append({"role": "assistant", "content": ai_reply})

        # Clean the AI response to ensure no product data leaks through
        clean_reply = clean_ai_response(ai_reply, shoes_data)

        # print("-----", clean_reply, "-----")
        # print("------------------")
        # print("-----", shoes_data, "-----")
        return jsonify({
            "message": clean_reply,
            "shoes_data": shoes_data,
            "session_id": session_id
        })

    except Exception as e:
        # global current_model_index
        if current_model_index ==  len(ai_models) - 1:
            current_model_index = 0
        else:
            # Rotate to the next model in case of an error
            current_model_index += 1
            print(f"Error with model {model}: {e}. Switching to next model.")
            model = ai_models[current_model_index]
            # client.model = model
            # Increment the model index and wrap around if necessary

        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Techno Shoe API is running!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)