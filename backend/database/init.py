import os
from pymongo import MongoClient
from dotenv import load_dotenv
from typing import List, Dict
import random

# Load environment variables
load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv("CONNECTION_STRING"))
    
    # Check if cluster is reachable
    try:
        client.admin.command('ping')
        print("✅ Pinged your cluster. Connection successful!")
    except Exception as e:
        raise Exception(f"❌ Could not connect to cluster: {e}")

    db_name = os.getenv("DB_NAME")
    return client[db_name]  # Database will auto-create on first insert

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

def create_shoes_collection(db) -> None:
    """Create and populate the 'shoes' collection with simple data."""
    
    print("🔄 Generating simple shoes dataset...")
    shoes_data = generate_simple_shoes_data()
    
    try:
        # Drop existing collection to remove all previous data
        db.shoes.drop()
        print("🗑️  Deleted all previous data from 'shoes' collection")
        
        # Insert new simple documents
        db.shoes.insert_many(shoes_data)
        print(f"✅ Created 'shoes' collection with {len(shoes_data)} simple documents.")
        
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
        print(f"❌ Error creating collection: {e}")

def clean_all_collections(db) -> None:
    """Remove all previous collections to start fresh."""
    collections = db.list_collection_names()
    for collection in collections:
        db[collection].drop()
        print(f"🗑️  Dropped collection: {collection}")

if __name__ == "__main__":
    db = get_db_connection()
    clean_all_collections(db)  # Remove all previous data
    create_shoes_collection(db)
    print("\n🎉 Simple database setup complete!")