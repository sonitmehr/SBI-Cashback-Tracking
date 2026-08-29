import os
import csv
from pymongo import MongoClient

# Local MongoDB Configuration (fallback)
LOCAL_MONGODB_URI = os.environ.get("LOCAL_MONGODB_URI", "mongodb://localhost:27017/")
CLOUD_MONGODB_URI = os.environ.get("MONGODB_URI", "")

DATABASE_NAME = os.environ.get("DATABASE_NAME", "sbi_cashback_tracking")
MERCHANTS_COLLECTION = os.environ.get("MERCHANTS_COLLECTION", "merchants")
ADMIN_COLLECTION = os.environ.get("ADMIN_COLLECTION", "admin_approvals")

# Admin Configuration
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Sonit")

def get_mongodb_client():
    """Get MongoDB client with fallback to local instance"""
    
    # Try cloud MongoDB first
    try:
        print("Attempting to connect to MongoDB Atlas...")
        client = MongoClient(
            CLOUD_MONGODB_URI,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=3000
        )
        client.admin.command('ping')
        print("SUCCESS: Connected to MongoDB Atlas")
        return client
    except Exception as e:
        print(f"MongoDB Atlas connection failed: {str(e)}")
        
    # Fallback to local MongoDB
    try:
        print("Attempting to connect to local MongoDB...")
        client = MongoClient(
            LOCAL_MONGODB_URI,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=3000
        )
        client.admin.command('ping')
        print("SUCCESS: Connected to local MongoDB")
        return client
    except Exception as e:
        print(f"Local MongoDB connection failed: {str(e)}")
        print("Please install MongoDB locally or fix Atlas connection")
        return None

# Initialize client
client = get_mongodb_client()

if client:
    db = client[DATABASE_NAME]
    merchants_collection = db[MERCHANTS_COLLECTION]
    admin_collection = db[ADMIN_COLLECTION]
else:
    db = None
    merchants_collection = None
    admin_collection = None

def get_merchants_from_db():
    """
    Fetch merchants from MongoDB.
    Returns a dictionary mapping merchant names to modes.
    Falls back to CSV if MongoDB is unavailable.
    """
    merchants_map = {}
    
    if not client or not merchants_collection:
        print("MongoDB unavailable, using CSV fallback")
        return load_merchants_from_csv_fallback()
    
    try:
        merchants = merchants_collection.find({"status": "approved"})
        for merchant in merchants:
            merchants_map[merchant["name"]] = merchant["mode"]
        print(f"Successfully loaded {len(merchants_map)} merchants from MongoDB")
    except Exception as e:
        print(f"MongoDB query failed: {str(e)}")
        print("Falling back to CSV file...")
        merchants_map = load_merchants_from_csv_fallback()
    
    return merchants_map

def load_merchants_from_csv_fallback():
    """
    Fallback function to load merchants from CSV when MongoDB is unavailable.
    """
    merchants_map = {}
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'merchants.csv')
    
    try:
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                merchant_name = row.get("Merchant Name", "").strip()
                mode = row.get("Mode", "").strip().upper()
                if merchant_name and mode:
                    merchants_map[merchant_name] = mode
        print(f"Loaded {len(merchants_map)} merchants from CSV fallback")
    except Exception as e:
        print(f"Error loading CSV fallback: {str(e)}")
    
    return merchants_map

def save_merchant_for_approval(merchant_name, mode, action_type="new", user_ip="unknown"):
    """
    Save merchant change for admin approval.
    Returns False if MongoDB is unavailable (graceful degradation).
    """
    if not client or not admin_collection:
        print("MongoDB unavailable - merchant changes will not be saved for approval")
        return False
    
    try:
        approval_doc = {
            "merchant_name": merchant_name,
            "mode": mode,
            "action_type": action_type,
            "status": "pending",
            "submitted_by": user_ip,
            "submitted_at": {"$date": {"$numberLong": str(int(__import__('time').time() * 1000))}},
            "approved_by": None,
            "approved_at": None
        }
        admin_collection.insert_one(approval_doc)
        return True
    except Exception as e:
        print(f"MongoDB unavailable for saving merchant approval: {str(e)}")
        return False

def get_pending_approvals():
    """Get all pending merchant approvals."""
    if not client or not admin_collection:
        return []
    
    try:
        return list(admin_collection.find({"status": "pending"}))
    except Exception as e:
        print(f"Error fetching pending approvals: {str(e)}")
        return []

def approve_merchant(approval_id, admin_user="admin"):
    """Approve a merchant change and update the merchants collection."""
    if not client or not merchants_collection or not admin_collection:
        return False
    
    try:
        # Get the approval document
        approval = admin_collection.find_one({"_id": approval_id})
        if not approval:
            return False
        
        # Update or insert merchant
        merchant_doc = {
            "name": approval["merchant_name"],
            "mode": approval["mode"],
            "status": "approved",
            "created_at": {"$date": {"$numberLong": str(int(__import__('time').time() * 1000))}},
            "updated_at": {"$date": {"$numberLong": str(int(__import__('time').time() * 1000))}},
            "history": []
        }
        
        # Check if merchant exists
        existing_merchant = merchants_collection.find_one({"name": approval["merchant_name"]})
        if existing_merchant:
            # Add to history
            history_entry = {
                "old_mode": existing_merchant.get("mode"),
                "new_mode": approval["mode"],
                "updated_by": admin_user,
                "updated_at": {"$date": {"$numberLong": str(int(__import__('time').time() * 1000))}}
            }
            merchants_collection.update_one(
                {"name": approval["merchant_name"]},
                {
                    "$set": {
                        "mode": approval["mode"],
                        "updated_at": {"$date": {"$numberLong": str(int(__import__('time').time() * 1000))}}
                    },
                    "$push": {"history": history_entry}
                }
            )
        else:
            merchants_collection.insert_one(merchant_doc)
        
        # Update approval status
        admin_collection.update_one(
            {"_id": approval_id},
            {
                "$set": {
                    "status": "approved",
                    "approved_by": admin_user,
                    "approved_at": {"$date": {"$numberLong": str(int(__import__('time').time() * 1000))}}
                }
            }
        )
        
        return True
    except Exception as e:
        print(f"Error approving merchant: {str(e)}")
        return False

def reject_merchant(approval_id, admin_user="admin"):
    """Reject a merchant change."""
    if not client or not admin_collection:
        return False
    
    try:
        admin_collection.update_one(
            {"_id": approval_id},
            {
                "$set": {
                    "status": "rejected",
                    "approved_by": admin_user,
                    "approved_at": {"$date": {"$numberLong": str(int(__import__('time').time() * 1000))}}
                }
            }
        )
        return True
    except Exception as e:
        print(f"Error rejecting merchant: {str(e)}")
        return False

def initialize_merchants_from_csv(csv_path):
    """Initialize MongoDB merchants collection from CSV file (one-time setup)."""
    if not client or not merchants_collection:
        print("MongoDB unavailable - skipping initialization")
        return False
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return False
    
    try:
        # Check if collection already has data
        if merchants_collection.count_documents({}) > 0:
            print("Merchants collection already initialized")
            return True
        
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            merchants_to_insert = []
            
            for row in reader:
                merchant_doc = {
                    "name": row["Merchant Name"].strip(),
                    "mode": row["Mode"].strip().upper(),
                    "status": "approved",
                    "created_at": {"$date": {"$numberLong": str(int(__import__('time').time() * 1000))}},
                    "updated_at": {"$date": {"$numberLong": str(int(__import__('time').time() * 1000))}},
                    "history": []
                }
                merchants_to_insert.append(merchant_doc)
            
            if merchants_to_insert:
                merchants_collection.insert_many(merchants_to_insert)
                print(f"Initialized {len(merchants_to_insert)} merchants from CSV")
        
        return True
    except Exception as e:
        print(f"Error initializing merchants from CSV: {str(e)}")
        return False
