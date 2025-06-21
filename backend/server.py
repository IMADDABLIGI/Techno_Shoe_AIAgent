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

# Store customer sessions
customer_sessions = {}

def get_shoe_image_url(shoe_name, brand):
    """Generate a placeholder image URL for shoes"""
    # In a real app, you'd have actual product images
    shoe_type = "sneaker" if any(word in shoe_name.lower() for word in ["air", "running", "sport"]) else "shoe"
    return f"https://via.placeholder.com/300x200/4F46E5/FFFFFF?text={brand}+{shoe_type.title()}"

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
        
        # Add image URLs and convert ObjectId to string
        for result in results:
            result["_id"] = str(result["_id"])
            result["image_url"] = get_shoe_image_url(result["name"], result["brand"])
        
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
        
        # Add image URLs and convert ObjectId to string
        for result in results:
            result["_id"] = str(result["_id"])
            result["image_url"] = get_shoe_image_url(result["name"], result["brand"])
        
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
        
        # Add image URLs and convert ObjectId to string
        for result in results:
            result["_id"] = str(result["_id"])
            result["image_url"] = get_shoe_image_url(result["name"], result["brand"])
        
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
        "content": """You are Amine, a helpful AI shopping assistant for Techno Shoes in Casablanca Sidi Maarouf, Morocco. 

STORE INFO:
- Name: Techno Shoes
- Location: Casablanca Sidi Maarouf, Morocco
- Currency: Moroccan Dirham (DH)
- Sizes: European sizes (36-47)

PERSONALITY: Be friendly, enthusiastic, and knowledgeable. Always mention price (DH), rating, and availability.

IMPORTANT: When presenting shoes, format your response to clearly indicate when you're showing product data by using the phrase "SHOES_DATA:" followed by the shoe information. This helps the frontend display products properly.

Example format:
"Here are some great options for you!

SHOES_DATA:
[The shoe data will be processed by the system]

Would you like to know more about any of these shoes?"
"""
    }

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
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
        
        return jsonify({
            "message": ai_reply,
            "shoes_data": shoes_data,
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Techno Shoes API is running!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)