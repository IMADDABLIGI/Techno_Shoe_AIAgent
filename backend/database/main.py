import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Replace with your actual connection string from Atlas
CONNECTION_STRING = os.environ["CONNECTION_STRING"]

def create_users_demo():
    """Simple demo: Create users in MongoDB"""
    
    # Connect to MongoDB
    print("🔗 Connecting to MongoDB Atlas...")
    client = MongoClient(CONNECTION_STRING)
    
    # Test connection
    try:
        client.admin.command('ping')
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Select database and collection
    db = client['demo_app']        # Database name
    users = db['users']            # Collection name (like a table)
    
    print(f"\n📊 Database: {db.name}")
    print(f"📋 Collection: {users.name}")
    
    # Create some sample users
    print("\n👥 Creating users...")
    
    # User 1
    user1 = {
        "name": "Alice Johnson",
        "email": "alice@example.com", 
        "age": 28,
        "city": "New York",
        "created_at": datetime.now()
    }
    
    result1 = users.insert_one(user1)
    print(f"✅ Created user: {user1['name']} (ID: {result1.inserted_id})")
    
    # User 2
    user2 = {
        "name": "Bob Smith",
        "email": "bob@example.com",
        "age": 32, 
        "city": "Los Angeles",
        "created_at": datetime.now()
    }
    
    result2 = users.insert_one(user2)
    print(f"✅ Created user: {user2['name']} (ID: {result2.inserted_id})")
    
    # User 3
    user3 = {
        "name": "Carol Davis", 
        "email": "carol@example.com",
        "age": 25,
        "city": "Chicago",
        "created_at": datetime.now()
    }
    
    result3 = users.insert_one(user3)
    print(f"✅ Created user: {user3['name']} (ID: {result3.inserted_id})")
    
    # Count total users
    total_users = users.count_documents({})
    print(f"\n📈 Total users in database: {total_users}")
    
    # Show all users
    print(f"\n👥 All users:")
    for user in users.find():
        print(f"   • {user['name']} - {user['email']} - {user['city']}")
    
    # Close connection
    client.close()
    print("\n🔒 Connection closed.")

if __name__ == "__main__":
    print("🚀 MongoDB User Creation Demo")
    print("=" * 35)
    create_users_demo()
    print("\n✨ Demo completed!")