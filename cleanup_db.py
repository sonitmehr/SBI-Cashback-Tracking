#!/usr/bin/env python3
"""
Monthly Database Cleanup Script
Cleans up rejected merchant approval submissions from MongoDB to optimize storage
and keep the database clean and performant.
Runs locally and via GitHub Actions on the 1st of every month.
"""

import os
import sys
from datetime import datetime, timezone

# Force UTF-8 output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Load environment variables if running locally
try:
    from dotenv import load_dotenv
    load_dotenv()
    parent_env = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(parent_env):
        load_dotenv(parent_env)
except ImportError:
    pass

from pymongo import MongoClient

MONGODB_URI = os.environ.get("MONGODB_URI")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "sbi_cashback_tracking")
ADMIN_COLLECTION = os.environ.get("ADMIN_COLLECTION", "admin_approvals")


def cleanup_rejected_approvals():
    """
    Finds and deletes all approval records with status 'rejected'.
    """
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI environment variable is missing!")

    print(f"🔌 [{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}] Connecting to MongoDB Atlas...")
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )
    client.admin.command('ping')
    print("✅ Connected to MongoDB Atlas successfully!")

    db = client[DATABASE_NAME]
    admin_col = db[ADMIN_COLLECTION]

    # Count before deletion
    total_before = admin_col.count_documents({})
    rejected_count = admin_col.count_documents({"status": "rejected"})
    pending_count = admin_col.count_documents({"status": "pending"})
    approved_count = admin_col.count_documents({"status": "approved"})

    print("\n" + "=" * 55)
    print("📊 CURRENT DB STATS BEFORE CLEANUP:")
    print(f"  • Total Approval Records: {total_before}")
    print(f"  • Pending Approvals:      {pending_count}")
    print(f"  • Approved Approvals:     {approved_count}")
    print(f"  • Rejected Approvals:     {rejected_count}")
    print("=" * 55)

    if rejected_count == 0:
        print("\n✨ No rejected records found. Database is already clean!")
        return 0

    print(f"\n🗑️ Deleting {rejected_count} rejected record(s)...")
    delete_result = admin_col.delete_many({"status": "rejected"})
    deleted_count = delete_result.deleted_count

    print(f"✅ Successfully deleted {deleted_count} rejected record(s).")
    
    total_after = admin_col.count_documents({})
    print(f"📦 Total remaining approval records: {total_after}")
    return deleted_count


def main():
    try:
        cleanup_rejected_approvals()
        print("\n🎉 Monthly cleanup completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during cleanup: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
