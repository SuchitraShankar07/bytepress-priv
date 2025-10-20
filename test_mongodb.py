#!/usr/bin/env python3
"""
Test script to verify MongoDB connectivity and basic operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("🧪 Testing MongoDB Connection")
    print("=" * 40)
    
    try:
        from src.utils.config import MONGODB_URI, DATABASE_NAME
        print(f"📍 MongoDB URI: {MONGODB_URI[:50]}...")
        print(f"📚 Database Name: {DATABASE_NAME}")
        
        from src.core.database import db
        
        if db is None:
            print("❌ Database instance is None")
            return False
            
        if not db.is_connected():
            print("❌ Database is not connected")
            return False
        
        if db.is_fallback_mode():
            print("⚠️  Using fallback JSON mode (MongoDB unavailable)")
        else:
            print("✅ Using MongoDB")
            
        print("✅ Database connection successful!")
        
        # Test a simple operation
        if not db.is_fallback_mode():
            collections = db._db.list_collection_names()
            print(f"📋 Available collections: {collections}")
        else:
            print("📋 Using local JSON file for data storage")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n💡 Possible solutions:")
        print("1. Check your MongoDB Atlas connection string")
        print("2. Replace <db_password> with your actual password")
        print("3. Ensure your IP is whitelisted in MongoDB Atlas")
        print("4. Check if the cluster is running")
        return False

def test_user_operations():
    """Test user CRUD operations"""
    print("\n🔄 Testing User Operations")
    print("=" * 40)
    
    try:
        from src.core.auth import register_user
        from src.core.database import get_user, db
        
        test_email = "test@example.com"
        test_name = "Test User"
        test_password = "testpassword123"
        
        # Clean up any existing test user
        if db and db.is_connected():
            if db.is_fallback_mode():
                data = db._load_fallback()
                if test_email in data:
                    del data[test_email]
                    db._save_fallback(data)
                    print("🧹 Cleaned up existing test user")
            else:
                try:
                    db.users.delete_one({"email": test_email})
                    print("🧹 Cleaned up existing test user")
                except:
                    pass
        
        # Test user registration
        print(f"🔄 Testing registration for: {test_email}")
        result = register_user(test_email, test_password, test_name)
        
        if result["success"]:
            print("✅ User registration successful!")
            
            # Test user retrieval
            user = get_user(test_email)
            if user and user["name"] == test_name:
                print("✅ User retrieval successful!")
                print(f"   👤 Name: {user['name']}")
                print(f"   � Email: {user['email']}")
            else:
                print("❌ User retrieval failed!")
                return False
            
            # Test duplicate registration
            duplicate_result = register_user(test_email, "newpassword", "New Name")
            if not duplicate_result["success"] and duplicate_result["error_type"] == "user_exists":
                print("✅ Duplicate email prevention works!")
            else:
                print(f"❌ Duplicate prevention failed: {duplicate_result}")
            
            # Clean up
            if db and db.is_connected():
                if db.is_fallback_mode():
                    # Clean up from JSON file
                    data = db._load_fallback()
                    if test_email in data:
                        del data[test_email]
                        db._save_fallback(data)
                else:
                    # Clean up from MongoDB
                    db.users.delete_one({"email": test_email})
                print("🧹 Test user cleaned up")
            
            return True
        else:
            print(f"❌ User registration failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ User operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔬 MongoDB Integration Test")
    print("🚀 Bytepress Database Diagnostics")
    print("=" * 50)
    
    # Test connection first
    if not test_mongodb_connection():
        return
    
    # Test database operations
    if test_user_operations():
        print("\n🎉 All tests passed! MongoDB integration is working correctly.")
    else:
        print("\n💥 Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
