"""
Test script to verify MongoDB and Google Gemini connections.
"""

import os
from dotenv import load_dotenv
import pymongo
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test the MongoDB connection."""
    print("Testing MongoDB connection...")
    
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("MongoDB URI not found in .env file")
        return False
    
    try:
        client = pymongo.MongoClient(mongodb_uri)
        # The ismaster command is cheap and does not require auth
        client.admin.command('ismaster')
        print("MongoDB connection successful!")
        
        # Check if our database exists
        db_names = client.list_database_names()
        if "fantasy_rpg" in db_names:
            print("'fantasy_rpg' database found")
            
            # Check collections
            db = client["fantasy_rpg"]
            collections = db.list_collection_names()
            print(f"Collections in database: {', '.join(collections)}")
            
            # Count documents in each collection
            for collection in collections:
                count = db[collection].count_documents({})
                print(f"  - {collection}: {count} documents")
        else:
            print("'fantasy_rpg' database not found")
        
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False

def test_gemini_connection():
    """Test the Google Gemini connection."""
    print("\nTesting Google Gemini connection...")
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Gemini API key not found in .env file")
        return False
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=gemini_api_key)
        
        # Create a model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generate a simple response
        response = model.generate_content("Write a one-sentence description of a fantasy village.")
        
        print("Google Gemini connection successful!")
        print(f"Sample response: {response.text}")
        return True
    except Exception as e:
        print(f"Google Gemini connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Connection Tests ===")
    mongodb_success = test_mongodb_connection()
    gemini_success = test_gemini_connection()
    
    print("\n=== Summary ===")
    print(f"MongoDB: {'Connected' if mongodb_success else 'Failed'}")
    print(f"Google Gemini: {'Connected' if gemini_success else 'Failed'}")
    
    if mongodb_success and gemini_success:
        print("\nAll systems ready! You can start the game with 'python main.py'")
    else:
        print("\nPlease fix the connection issues before starting the game.")