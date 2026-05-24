#!/usr/bin/env python3
"""
MongoDB Initialization Script
Creates collections and initializes data from CSV
"""

import csv
import os
import sys
from datetime import datetime
from pymongo import MongoClient

# MongoDB Configuration
MONGODB_URI = "mongodb+srv://sonitmehrotra_db_user:aqT94F6Ws00G5m8g@my-life-cluster.uk6jc6c.mongodb.net/sbi_cashback_tracking?retryWrites=true&w=majority"
DATABASE_NAME = "sbi_cashback_tracking"
MERCHANTS_COLLECTION = "merchants"
ADMIN_COLLECTION = "admin_approvals"

def init_mongodb():
    """Initialize MongoDB collections and data"""
    
    print("Initializing MongoDB...")
    
    try:
        # Connect to MongoDB with shorter timeout
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        # Test connection
        print("Testing MongoDB connection...")
        client.admin.command('ping')
        print("MongoDB connection successful!")
        
        # Get database and collections
        db = client[DATABASE_NAME]
        merchants_collection = db[MERCHANTS_COLLECTION]
        admin_collection = db[ADMIN_COLLECTION]
        
        # Create collections if they don't exist
        print("Creating collections...")
        
        # Check if merchants collection exists and has data
        merchant_count = merchants_collection.count_documents({})
        print(f"Current merchants in DB: {merchant_count}")
        
        if merchant_count == 0:
            print("Loading merchants from CSV...")
            
            # Load from CSV
            csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'merchants.csv')
            
            if not os.path.exists(csv_path):
                print(f"ERROR: CSV file not found: {csv_path}")
                return False
            
            merchants_to_insert = []
            current_time = datetime.utcnow()
            
            with open(csv_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    merchant_name = row.get("Merchant Name", "").strip()
                    mode = row.get("Mode", "").strip().upper()
                    
                    if merchant_name and mode:
                        merchant_doc = {
                            "name": merchant_name,
                            "mode": mode,
                            "status": "approved",
                            "created_at": current_time,
                            "updated_at": current_time,
                            "history": []
                        }
                        merchants_to_insert.append(merchant_doc)
            
            if merchants_to_insert:
                result = merchants_collection.insert_many(merchants_to_insert)
                print(f"SUCCESS: Inserted {len(result.inserted_ids)} merchants into MongoDB")
            else:
                print("WARNING: No valid merchants found in CSV")
        else:
            print("INFO: Merchants collection already has data, skipping CSV import")
        
        # Create indexes for better performance
        print("Creating indexes...")
        merchants_collection.create_index("name")
        merchants_collection.create_index("status")
        admin_collection.create_index("status")
        admin_collection.create_index("submitted_at")
        print("SUCCESS: Indexes created")
        
        # Show final stats
        merchant_count = merchants_collection.count_documents({})
        admin_count = admin_collection.count_documents({})
        
        print("\nMongoDB Initialization Complete!")
        print(f"   • Merchants: {merchant_count}")
        print(f"   • Admin approvals: {admin_count}")
        print(f"   • Database: {DATABASE_NAME}")
        
        # Show sample merchants
        print("\nSample merchants:")
        sample_merchants = merchants_collection.find().limit(5)
        for merchant in sample_merchants:
            print(f"   • {merchant['name']} → {merchant['mode']}")
        
        return True
        
    except Exception as e:
        print(f"ERROR initializing MongoDB: {str(e)}")
        return False

def test_connection():
    """Test MongoDB connection and show collections"""
    
    try:
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # Test connection
        client.admin.command('ping')
        
        db = client[DATABASE_NAME]
        
        print("SUCCESS: MongoDB Connection Test Successful!")
        print(f"Database: {DATABASE_NAME}")
        print("Collections:")
        
        collections = db.list_collection_names()
        for collection in collections:
            count = db[collection].count_documents({})
            print(f"   • {collection}: {count} documents")
        
        return True
        
    except Exception as e:
        print(f"ERROR: MongoDB Connection Failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("MongoDB Initialization Script")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_connection()
    else:
        init_mongodb()
