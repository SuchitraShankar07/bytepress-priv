#!/usr/bin/env python3
"""
Test script to verify MongoDB connectivity and basic operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import db, add_user, get_user
from src.core.auth import register_user
import pymongo

def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        # Test connection
        db._client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_user_operations():
    """Test user CRUD operations"""
    test_email = "test@example.com"
    test_name = "Test User"
    test_password = "testpassword123"
    
    try:
        # Clean up any existing test user
        existing = get_user(test_email)
        if existing:
            db.users.delete_one({"email": test_email})
            print("🧹 Cleaned up existing test user")
        
        # Test user registration
        success = register_user(test_email, test_password, test_name)
        if success:
            print("✅ User registration successful!")
        else:
            print("❌ User registration failed!")
            return False
        
        # Test user retrieval
        user = get_user(test_email)
        if user and user["name"] == test_name:
            print("✅ User retrieval successful!")
            print(f"   📧 Email: {user['email']}")
            print(f"   👤 Name: {user['name']}")
            print(f"   📅 Created: {user['created_at']}")
        else:
            print("❌ User retrieval failed!")
            return False
        
        # Test duplicate registration
        duplicate = register_user(test_email, "newpassword", "New Name")
        if not duplicate:
            print("✅ Duplicate email prevention works!")
        else:
            print("❌ Duplicate email prevention failed!")
        
        # Clean up
        db.users.delete_one({"email": test_email})
        print("🧹 Test user cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ User operations test failed: {e}")
        return False

def main():
    print("🧪 Testing MongoDB Integration")
    print("=" * 40)
    
    # Test connection
    if not test_mongodb_connection():
        print("\n💡 Make sure MongoDB is running:")
        print("   - Install MongoDB: https://docs.mongodb.com/manual/installation/")
        print("   - Start MongoDB: sudo systemctl start mongod")
        print("   - Or use Docker: docker run -d -p 27017:27017 mongo")
        return
    
    # Test database operations
    print("\n🔄 Testing user operations...")
    if test_user_operations():
        print("\n🎉 All tests passed! MongoDB integration is working correctly.")
    else:
        print("\n💥 Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
