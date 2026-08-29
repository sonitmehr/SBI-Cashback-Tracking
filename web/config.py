import os
from datetime import datetime
from pymongo import MongoClient

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    # Look for .env in current directory and parent directories
    load_dotenv()
    parent_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(parent_env):
        load_dotenv(parent_env)
except ImportError:
    pass

# MongoDB Configuration
MONGODB_URI = (os.environ.get("MONGODB_URI") or "").strip()
DATABASE_NAME = (os.environ.get("DATABASE_NAME") or "sbi_cashback_tracking").strip()
MERCHANTS_COLLECTION = (os.environ.get("MERCHANTS_COLLECTION") or "merchants").strip()
ADMIN_COLLECTION = (os.environ.get("ADMIN_COLLECTION") or "admin_approvals").strip()

# Admin Configuration
DEFAULT_ADMIN_PASSWORD = (os.environ.get("ADMIN_PASSWORD") or "Sonit").strip()

# MongoDB Client with connection settings
client = None
db = None
merchants_collection = None
admin_collection = None

if MONGODB_URI:
    try:
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            maxPoolSize=10,
            retryWrites=True
        )
        db = client[DATABASE_NAME]
        merchants_collection = db[MERCHANTS_COLLECTION]
        admin_collection = db[ADMIN_COLLECTION]
    except Exception as e:
        print(f"Failed to initialize MongoDB client: {str(e)}")
        client = None

def get_merchants_from_db():
    """
    Fetch merchants from MongoDB.
    Returns a dictionary mapping merchant names to modes.
    Falls back to CSV if MongoDB is unavailable.
    """
    merchants_map = {}
    if not client or merchants_collection is None:
        print("MongoDB URI not provided or client not initialized. Using CSV fallback...")
        return load_merchants_from_csv_fallback()

    try:
        # Test connection first
        client.admin.command('ping')
        merchants = merchants_collection.find({"status": "approved"})
        for merchant in merchants:
            merchants_map[merchant["name"]] = merchant["mode"]
        print(f"Successfully loaded {len(merchants_map)} merchants from MongoDB")
    except Exception as e:
        print(f"MongoDB connection failed: {str(e)}")
        print("Falling back to CSV file...")
        # Fallback to CSV
        merchants_map = load_merchants_from_csv_fallback()
    return merchants_map

def load_merchants_from_csv_fallback():
    """
    Fallback function to load merchants from CSV when MongoDB is unavailable.
    """
    import csv
    import os
    
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
    if not client or admin_collection is None:
        print("MongoDB unavailable - merchant changes will not be saved for approval")
        return False

    try:
        # Test connection first
        client.admin.command('ping')
        
        approval_doc = {
            "merchant_name": merchant_name,
            "mode": mode,
            "action_type": action_type,  # "new", "update"
            "status": "pending",
            "submitted_by": user_ip,
            "submitted_at": datetime.utcnow(),
            "approved_by": None,
            "approved_at": None
        }
        admin_collection.insert_one(approval_doc)
        return True
    except Exception as e:
        print(f"MongoDB unavailable for saving merchant approval: {str(e)}")
        print("Merchant changes will not be saved for admin approval")
        return False

def get_pending_approvals():
    """
    Get all pending merchant approvals.
    """
    if not client or admin_collection is None:
        return []

    try:
        return list(admin_collection.find({"status": "pending"}))
    except Exception as e:
        print(f"Error fetching pending approvals: {str(e)}")
        return []

def approve_merchant(approval_id, admin_user="admin"):
    """
    Approve a merchant change and update the merchants collection.
    """
    if not client or merchants_collection is None or admin_collection is None:
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
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
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
                "updated_at": datetime.utcnow()
            }
            merchants_collection.update_one(
                {"name": approval["merchant_name"]},
                {
                    "$set": {
                        "mode": approval["mode"],
                        "updated_at": datetime.utcnow()
                    },
                    "$push": {"history": history_entry}
                }
            )
        else:
            # Insert new merchant
            merchants_collection.insert_one(merchant_doc)
        
        # Update approval status
        admin_collection.update_one(
            {"_id": approval_id},
            {
                "$set": {
                    "status": "approved",
                    "approved_by": admin_user,
                    "approved_at": datetime.utcnow()
                }
            }
        )
        
        return True
    except Exception as e:
        print(f"Error approving merchant: {str(e)}")
        return False

def reject_merchant(approval_id, admin_user="admin"):
    """
    Reject a merchant change.
    """
    if not client or admin_collection is None:
        return False

    try:
        admin_collection.update_one(
            {"_id": approval_id},
            {
                "$set": {
                    "status": "rejected",
                    "approved_by": admin_user,
                    "approved_at": datetime.utcnow()
                }
            }
        )
        return True
    except Exception as e:
        print(f"Error rejecting merchant: {str(e)}")
        return False

def initialize_merchants_from_csv(csv_path):
    """
    Initialize MongoDB merchants collection from CSV file (one-time setup).
    Skips initialization if MongoDB is unavailable.
    """
    import csv
    import os
    
    if not client or merchants_collection is None:
        print("MongoDB unavailable - skipping initialization")
        return False

    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return False
    
    try:
        # Test MongoDB connection first
        client.admin.command('ping')
        
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
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "history": []
                }
                merchants_to_insert.append(merchant_doc)
            
            if merchants_to_insert:
                merchants_collection.insert_many(merchants_to_insert)
                print(f"Initialized {len(merchants_to_insert)} merchants from CSV")
        
        return True
    except Exception as e:
        print(f"MongoDB unavailable for initialization: {str(e)}")
        print("Skipping MongoDB initialization - will use CSV fallback")
        return False
