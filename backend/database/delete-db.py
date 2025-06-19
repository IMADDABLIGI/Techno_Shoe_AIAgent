import os
from pymongo import MongoClient
from dotenv import load_dotenv

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

def delete_all_data(db):
    """Delete all documents from all collections in the database"""
    try:
        collection_names = db.list_collection_names()
        
        if not collection_names:
            print("ℹ️ No collections found in the database.")
            return True
        
        print(f"📋 Found {len(collection_names)} collections: {collection_names}")
        
        # Get confirmation before proceeding
        confirm = input(f"\n⚠️ WARNING: This will delete ALL data from {len(collection_names)} collections.\n"
                       f"Collections: {', '.join(collection_names)}\n"
                       f"Type 'YES' to confirm deletion: ")
        
        if confirm != 'YES':
            print("❌ Operation cancelled.")
            return False
        
        total_deleted = 0
        
        # Delete all documents from each collection
        for collection_name in collection_names:
            collection = db[collection_name]
            
            # Count documents before deletion
            doc_count = collection.count_documents({})
            
            if doc_count > 0:
                # Delete all documents
                delete_result = collection.delete_many({})
                deleted_count = delete_result.deleted_count
                total_deleted += deleted_count
                
                print(f"🗑️ Deleted {deleted_count} documents from '{collection_name}' collection")
            else:
                print(f"ℹ️ Collection '{collection_name}' was already empty")
        
        print(f"\n✅ Successfully deleted {total_deleted} total documents from the database")
        print("📝 Note: Collections and their schemas are preserved")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deleting data: {e}")
        return False

def delete_specific_collection(db, collection_name):
    """Delete all documents from a specific collection"""
    try:
        if collection_name not in db.list_collection_names():
            print(f"❌ Collection '{collection_name}' does not exist")
            return False
        
        collection = db[collection_name]
        doc_count = collection.count_documents({})
        
        if doc_count == 0:
            print(f"ℹ️ Collection '{collection_name}' is already empty")
            return True
        
        confirm = input(f"⚠️ WARNING: This will delete ALL {doc_count} documents from '{collection_name}' collection.\n"
                       f"Type 'YES' to confirm: ")
        
        if confirm != 'YES':
            print("❌ Operation cancelled.")
            return False
        
        delete_result = collection.delete_many({})
        deleted_count = delete_result.deleted_count
        
        print(f"✅ Successfully deleted {deleted_count} documents from '{collection_name}' collection")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting data from '{collection_name}': {e}")
        return False

def show_database_status(db):
    """Show current status of all collections"""
    try:
        collection_names = db.list_collection_names()
        
        if not collection_names:
            print("ℹ️ No collections found in the database.")
            return
        
        print(f"\n📊 Database Status:")
        print(f"Database: {db.name}")
        print(f"Collections: {len(collection_names)}")
        print("-" * 40)
        
        total_documents = 0
        for collection_name in collection_names:
            doc_count = db[collection_name].count_documents({})
            total_documents += doc_count
            print(f"{collection_name}: {doc_count} documents")
        
        print("-" * 40)
        print(f"Total documents: {total_documents}")
        
    except Exception as e:
        print(f"❌ Error checking database status: {e}")

def main():
    """Main function with menu options"""
    try:
        db = get_db_connection()
        
        while True:
            print("\n" + "="*50)
            print("🗑️ MongoDB Database Cleaner")
            print("="*50)
            print("1. Show database status")
            print("2. Delete ALL data from ALL collections")
            print("3. Delete data from specific collection")
            print("4. Exit")
            print("-" * 50)
            
            choice = input("Select an option (1-4): ").strip()
            
            if choice == '1':
                show_database_status(db)
                
            elif choice == '2':
                delete_all_data(db)
                
            elif choice == '3':
                show_database_status(db)
                collection_name = input("\nEnter collection name to clear: ").strip()
                if collection_name:
                    delete_specific_collection(db, collection_name)
                else:
                    print("❌ Invalid collection name")
                    
            elif choice == '4':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-4.")
        
    except Exception as e:
        print(f"❌ Application error: {str(e)}")

if __name__ == "__main__":
    main()