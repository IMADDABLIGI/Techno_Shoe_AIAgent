import os
from pymongo import MongoClient
from dotenv import load_dotenv
from typing import List, Dict
import random
from datetime import datetime

# Load environment variables
load_dotenv()

def get_db_connection():
    """Establish connection to MongoDB and return database object"""
    client = MongoClient(os.getenv("CONNECTION_STRING"))
    
    # Check if cluster is reachable
    try:
        client.admin.command('ping')
        print("✅ Pinged your cluster. Connection successful!")
    except Exception as e:
        raise Exception(f"❌ Could not connect to cluster: {e}")

    db_name = os.getenv("DB_NAME")
    return client[db_name]

def generate_simple_shoes_data() -> List[Dict]:
    """Generate a simple, clean dataset of shoes."""
    brands = ["Nike", "Adidas", "Puma", "Reebok", "New Balance"]
    categories = ["Running", "Basketball", "Casual", "Training"]
    colors = ["Black", "White", "Red", "Blue", "Gray"]
    genders = ["Men", "Women", "Unisex"]
    sizes = [7, 8, 9, 10, 11]
    
    shoes_data = []
    
    # Generate 50 shoes (much smaller dataset)
    for i in range(50):
        brand = random.choice(brands)
        category = random.choice(categories)
        
        shoe = {
            "name": f"{brand} {category} {i+1}",
            "brand": brand,
            "category": category,
            "price": round(random.uniform(60, 150), 2),
            "color": random.choice(colors),
            "sizes": random.sample(sizes, random.randint(3, 5)),
            "gender": random.choice(genders),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "in_stock": random.choice([True, False])
        }
        
        shoes_data.append(shoe)
    
    return shoes_data

def initialize_shoes_collection(db) -> None:
    """Initialize the shoes collection with sample data if it doesn't exist"""
    if "shoes" not in db.list_collection_names():
        print("🔄 Creating and populating 'shoes' collection...")
        shoes_data = generate_simple_shoes_data()
        
        try:
            db.create_collection("shoes")
            db.shoes.insert_many(shoes_data)
            print(f"✅ Created 'shoes' collection with {len(shoes_data)} documents.")
            
            # Show sample document
            sample = db.shoes.find_one()
            print("\n📄 Sample document structure:")
            for key, value in sample.items():
                print(f"  {key}: {value}")
            
            # Basic statistics
            print(f"\n📊 Total shoes: {db.shoes.count_documents({})}")
            print(f"In stock: {db.shoes.count_documents({'in_stock': True})}")
            print(f"Out of stock: {db.shoes.count_documents({'in_stock': False})}")
            
        except Exception as e:
            print(f"❌ Error creating shoes collection: {e}")
    else:
        print("ℹ️ 'shoes' collection already exists - skipping initialization")

def initialize_customers_collection(db) -> None:
    """Initialize the customers collection with schema validation if it doesn't exist"""
    if "customers" not in db.list_collection_names():
        try:
            db.create_collection("customers", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["first_name", "phone", "interested_products"],
                    "properties": {
                        "first_name": {"bsonType": "string"},
                        "last_name": {"bsonType": "string"},
                        "age": {"bsonType": "int"},
                        "phone": {"bsonType": "string"},
                        "interested_products": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"}
                        },
                        "conversation_history": {
                            "bsonType": "array",
                            "items": {"bsonType": "object"}
                        },
                        "created_at": {"bsonType": "date"}
                    }
                }
            })
            print("✅ Created 'customers' collection with schema validation")
        except Exception as e:
            print(f"❌ Error creating customers collection: {e}")
    else:
        print("ℹ️ 'customers' collection already exists - skipping initialization")

def initialize_database():
    """Main initialization function - only creates collections if they don't exist"""
    try:
        db = get_db_connection()
        
        initialize_shoes_collection(db)
        initialize_customers_collection(db)
        
        print("\n🎉 Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    initialize_database()