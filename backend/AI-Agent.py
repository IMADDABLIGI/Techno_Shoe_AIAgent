import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient
from typing import List, Dict, Any
import re

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

# Customer state tracking
customer_state = {
    "interested_products": [],
    "conversation_turns": 0,
    "serious_interest_indicators": 0,
    "contact_info_requested": False,
    "contact_info": {},
    "gathering_contact": False,
    "contact_step": None  # "first_name", "last_name", "age", "phone"
}

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
        
        # Remove None values
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

def detect_serious_interest(user_message):
    """Detect if customer shows serious interest in purchasing"""
    interest_keywords = [
        "buy", "purchase", "order", "get this", "take it", "want this",
        "interested in", "looks good", "perfect", "exactly what", 
        "how much", "price", "cost", "afford", "budget", "payment",
        "when can i", "available", "in stock", "reserve", "hold",
        "size", "fit", "try on", "store location", "pickup", "delivery"
    ]
    
    message_lower = user_message.lower()
    interest_count = sum(1 for keyword in interest_keywords if keyword in message_lower)
    
    return interest_count >= 2 or any(phrase in message_lower for phrase in [
        "i want", "i'll take", "can i buy", "how do i order", 
        "where can i", "i need these", "perfect for me"
    ])

def extract_contact_info(user_message):
    """Extract contact information from user message"""
    contact_info = {}
    
    # Extract phone number (various formats)
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890 or 123.456.7890 or 1234567890
        r'\(\d{3}\)\s?\d{3}[-.]?\d{4}',    # (123) 456-7890
        r'\+1\s?\d{3}[-.]?\d{3}[-.]?\d{4}' # +1 123-456-7890
    ]
    
    for pattern in phone_patterns:
        phone_match = re.search(pattern, user_message)
        if phone_match:
            contact_info['phone'] = phone_match.group()
            break
    
    # Extract age (simple number between 16-99)
    age_match = re.search(r'\b(1[6-9]|[2-9]\d)\b', user_message)
    if age_match:
        potential_age = int(age_match.group())
        if 16 <= potential_age <= 99:
            contact_info['age'] = potential_age
    
    return contact_info

# Tool definitions for OpenAI function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_shoes",
            "description": "Search for shoes based on customer preferences like brand, category, price range (in DH), color, gender, size (EU), and rating",
            "parameters": {
                "type": "object",
                "properties": {
                    "brand": {"type": "string", "description": "Shoe brand (Nike, Adidas, Puma, etc.)"},
                    "category": {"type": "string", "description": "Shoe category (Running, Basketball, Casual, Training)"},
                    "price_min": {"type": "number", "description": "Minimum price in DH"},
                    "price_max": {"type": "number", "description": "Maximum price in DH"},
                    "color": {"type": "string", "description": "Shoe color"},
                    "gender": {"type": "string", "description": "Target gender (Men, Women, Unisex)"},
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
            "description": "Check if a specific shoe is available in a particular EU size",
            "parameters": {
                "type": "object",
                "properties": {
                    "shoe_name": {"type": "string", "description": "Name of the shoe to check"},
                    "size": {"type": "number", "description": "Shoe size (EU) to check"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_customer_info",
            "description": "Save customer contact information and interests to database when they show serious buying intent",
            "parameters": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string", "description": "Customer's first name"},
                    "last_name": {"type": "string", "description": "Customer's last name"},
                    "age": {"type": "number", "description": "Customer's age"},
                    "phone": {"type": "string", "description": "Customer's phone number"},
                    "interested_products": {"type": "array", "items": {"type": "string"}, "description": "List of products customer is interested in"},
                    "conversation_history": {"type": "array", "items": {"type": "object"}, "description": "Chat conversation history"}
                },
                "required": ["first_name"]
            }
        }
    }
]

# Map function names to actual functions
available_functions = {
    "search_shoes": search_shoes,
    "get_shoe_recommendations": get_shoe_recommendations,
    "get_brands_and_categories": get_brands_and_categories,
    "check_shoe_availability": check_shoe_availability,
    "save_customer_info": save_customer_info
}

# Initialize conversation history with enhanced e-commerce context
conversation_history = [
    {"role": "system", "content": """You are Amine, a helpful AI shopping assistant for Techno Shoes in Casablanca Sidi Maarouf, Morocco. Your goal is to help customers find the perfect shoes and gather their contact information when they show serious buying intent.

STORE INFORMATION:
- Name: Techno Shoes
- Location: Casablanca Sidi Maarouf, Morocco
- Currency: Moroccan Dirham (DH)
- Sizes: European sizes (36-47)

PERSONALITY:
- Be friendly, enthusiastic, and knowledgeable about shoes
- Ask clarifying questions to understand customer needs
- Provide personalized recommendations
- Always mention key details like price (in DH), rating, and availability

CONVERSATION FLOW:
1. Greet the customer warmly
2. Ask about their shoe needs (occasion, style, size (EU), budget in DH, etc.)
3. Use the search tools to find matching shoes
4. Present options with pros/cons
5. **DETECT SERIOUS INTEREST** - Watch for buying signals
6. **GATHER CONTACT INFO** when customer shows serious interest
7. Help them make a decision
8. Offer alternatives if nothing matches perfectly

WHEN PRESENTING SHOES:
- Always mention: name, brand, price (in DH), rating, availability
- Highlight what makes each shoe special
- Group similar options together
- Suggest alternatives if budget/preferences don't match

SERIOUS INTEREST INDICATORS:
- Customer asks about pricing, availability, or sizes
- Uses words like "buy", "purchase", "want this", "interested"
- Asks about store location, pickup, or delivery
- Asks "how much" or discusses budget
- Says shoes are "perfect" or "exactly what I need"
- Asks about trying on or fit

CONTACT INFORMATION GATHERING:
When you detect serious interest (2+ indicators), politely ask for contact information:
1. Start with: "I'd love to help you with this purchase! Could I get your name so I can assist you better?"
2. Collect: First name (required), Last name, Age, Phone number
3. Be natural and conversational, not like a form
4. Explain benefits: "This way I can follow up with you about availability and any special offers"
5. Save information using the save_customer_info function

CONTACT GATHERING SCRIPT:
- "To help you with this purchase, could I get your first name?"
- "And your last name?" 
- "What's the best phone number to reach you at?"
- "Just for our records, may I ask your age?" (optional)

Remember: Only gather contact info when customer shows SERIOUS buying intent, not just browsing!"""},
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
   • Price: {shoe['price']} DH | Rating: {shoe['rating']}/5 ⭐
   • Color: {shoe['color']} | Gender: {shoe['gender']}
   • Available Sizes (EU): {', '.join(map(str, shoe['sizes']))}
   • Status: {'✅ In Stock' if shoe['in_stock'] else '❌ Out of Stock'}
"""
            formatted_shoes.append(shoe_info)
            
            # Track interested products
            if shoe['in_stock']:
                customer_state["interested_products"].append(shoe['name'])
        
        return "\n".join(formatted_shoes)
    return str(data)

def process_user_message(user_input):
    """Process user message and update customer state"""
    customer_state["conversation_turns"] += 1
    
    # Check for serious interest indicators
    if detect_serious_interest(user_input):
        customer_state["serious_interest_indicators"] += 1
    
    # Extract any contact info from the message
    extracted_contact = extract_contact_info(user_input)
    customer_state["contact_info"].update(extracted_contact)
    
    # Handle contact info gathering flow
    if customer_state["gathering_contact"]:
        handle_contact_gathering(user_input)

def handle_contact_gathering(user_input):
    """Handle the contact information gathering process"""
    current_step = customer_state["contact_step"]
    
    if current_step == "first_name":
        # Extract first name (assume single word or first word)
        name_words = user_input.strip().split()
        if name_words:
            customer_state["contact_info"]["first_name"] = name_words[0].title()
            customer_state["contact_step"] = "last_name"
    
    elif current_step == "last_name":
        name_words = user_input.strip().split()
        if name_words:
            customer_state["contact_info"]["last_name"] = name_words[-1].title()
            customer_state["contact_step"] = "phone"
    
    elif current_step == "phone":
        # Phone should be extracted by extract_contact_info function
        if "phone" in customer_state["contact_info"]:
            customer_state["contact_step"] = "age"
    
    elif current_step == "age":
        # Age should be extracted by extract_contact_info function
        customer_state["gathering_contact"] = False
        customer_state["contact_step"] = None

def should_request_contact_info():
    """Determine if we should request contact information"""
    return (
        customer_state["serious_interest_indicators"] >= 2 and
        not customer_state["contact_info_requested"] and
        customer_state["conversation_turns"] >= 3 and
        len(customer_state["interested_products"]) > 0
    )

def chat_shoe_assistant():
    print("👟 Welcome to Techno Shoes AI Assistant! 👟")
    print("Ask me about shoes and I'll help you find the perfect pair!")
    print("Type 'quit' to exit")
    print("-" * 60)
    
    # Start with a greeting
    print("\nAmine: Hello! Welcome to Techno Shoes in Casablanca Sidi Maarouf! 👋")
    print("I'm Amine, your shoe shopping assistant. How can I help you find the perfect shoes today?")
    print("You can tell me about:")
    print("• The occasion (running, work, casual, sports)")
    print("• Your preferred brand or style")
    print("• Your budget range in DH")
    print("• Your size (EU sizes from 36-47) and color preferences")
    print("• Or just ask for recommendations!")
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            # Save conversation history if we have contact info
            if customer_state["contact_info"].get("first_name"):
                try:
                    save_result = save_customer_info(
                        first_name=customer_state["contact_info"].get("first_name"),
                        last_name=customer_state["contact_info"].get("last_name"),
                        age=customer_state["contact_info"].get("age"),
                        phone=customer_state["contact_info"].get("phone"),
                        interested_products=list(set(customer_state["interested_products"])),
                        conversation_history=[msg for msg in conversation_history if msg["role"] != "system"]
                    )
                    print("\n💾 Your information has been saved for follow-up!")
                except Exception as e:
                    print(f"\n⚠️ Note: Could not save conversation history: {e}")
            
            print("\nAmine: Thanks for shopping with us at Techno Shoes! Come back anytime! 👟✨")
            break

        # Process the user message
        process_user_message(user_input)
        
        # Add user message to history
        conversation_history.append({"role": "user", "content": user_input})

        try:
            # Check if we should request contact info
            if should_request_contact_info():
                customer_state["contact_info_requested"] = True
                customer_state["gathering_contact"] = True
                customer_state["contact_step"] = "first_name"
                
                print("\nAmine: I can see you're really interested in some of our shoes! 😊")
                print("To help you with your purchase and keep you updated about availability and special offers,")
                print("could I get your first name?")
                continue

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
                print(f"\nAmine: {ai_reply}")
                
                # Add final response to history
                conversation_history.append({"role": "assistant", "content": ai_reply})
                
            else:
                # No tool calls needed, just regular response
                ai_reply = response_message.content
                print(f"\nAmine: {ai_reply}")
                
                # Add AI reply to history
                conversation_history.append({"role": "assistant", "content": ai_reply})
                
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or rephrase your request.")

if __name__ == "__main__":
    try:
        chat_shoe_assistant()
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for visiting Techno Shoes! Have a great day!")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please check your database connection and try again.")