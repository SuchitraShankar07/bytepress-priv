import pymongo
from datetime import datetime
from src.utils.config import MONGODB_URI, DATABASE_NAME, USERS_COLLECTION
import json
import os
import ssl

class Database:
    _instance = None
    _client = None
    _db = None
    _connected = False
    _fallback_mode = False
    _fallback_file = "users_fallback.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.connect()
    
    def connect(self):
        """Establish connection to MongoDB with fallback to JSON"""
        try:
            print(f"Attempting to connect to MongoDB...")
            
            # Set up SSL context to handle TLS version issues
            import ssl
            
            # Try different connection approaches with the most compatible settings
            connection_attempts = [
                # Attempt 1: Simplest working configuration
                {
                    'serverSelectionTimeoutMS': 20000,
                    'connectTimeoutMS': 20000,
                    'socketTimeoutMS': 20000,
                    'retryWrites': True
                },
                # Attempt 2: With TLS certificate verification disabled
                {
                    'serverSelectionTimeoutMS': 25000,
                    'connectTimeoutMS': 25000,
                    'socketTimeoutMS': 25000,
                    'retryWrites': True,
                    'tls': True,
                    'tlsAllowInvalidCertificates': True
                },
                # Attempt 3: Longer timeout for slow networks
                {
                    'serverSelectionTimeoutMS': 45000,
                    'connectTimeoutMS': 45000,
                    'socketTimeoutMS': 45000,
                    'retryWrites': True
                }
            ]
            
            for i, options in enumerate(connection_attempts, 1):
                try:
                    print(f"🔄 Connection attempt {i}/3...")
                    self._client = pymongo.MongoClient(MONGODB_URI, **options)
                    
                    # Test the connection
                    self._client.admin.command('ping')
                    self._db = self._client[DATABASE_NAME]
                    self._connected = True
                    self._fallback_mode = False
                    print(f"✅ Connected to MongoDB database: {DATABASE_NAME} (attempt {i})")
                    
                    # Initialize collections and indexes
                    self._initialize_database()
                    return
                    
                except Exception as e:
                    print(f"❌ Attempt {i} failed: {str(e)[:100]}...")
                    if self._client:
                        self._client.close()
                        self._client = None
                    continue
            
            # If all attempts failed, use fallback
            raise Exception("All MongoDB connection attempts failed")
            
        except Exception as e:
            print(f"⚠️  MongoDB connection failed: {str(e)[:100]}...")
            print(f"🔄 Switching to fallback JSON mode...")
            self._connected = False
            self._fallback_mode = True
            self._initialize_fallback()
    
    def _initialize_database(self):
        """Initialize database collections and indexes"""
        try:
            # Create users collection if it doesn't exist
            if USERS_COLLECTION not in self._db.list_collection_names():
                self._db.create_collection(USERS_COLLECTION)
                print(f"✅ Created collection: {USERS_COLLECTION}")
            
            # Create unique index on email
            self._db[USERS_COLLECTION].create_index(
                [("email", 1)], 
                unique=True, 
                background=True
            )
            
            # Create index on created_at for performance
            self._db[USERS_COLLECTION].create_index(
                [("created_at", 1)], 
                background=True
            )
            
            print("✅ Database indexes initialized")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize indexes: {e}")
    
    def _initialize_fallback(self):
        """Initialize JSON fallback file"""
        if not os.path.exists(self._fallback_file):
            with open(self._fallback_file, 'w') as f:
                json.dump({}, f)
        print(f"✅ Fallback JSON database initialized: {self._fallback_file}")
    
    def _load_fallback(self):
        """Load data from fallback JSON file"""
        try:
            with open(self._fallback_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_fallback(self, data):
        """Save data to fallback JSON file"""
        with open(self._fallback_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    @property
    def users(self):
        if self._fallback_mode:
            return None  # Will be handled by fallback methods
        if not self._connected:
            raise Exception("Database not connected")
        return self._db[USERS_COLLECTION]
    
    def is_connected(self):
        return self._connected or self._fallback_mode
    
    def is_fallback_mode(self):
        return self._fallback_mode
    
    def close(self):
        if self._client:
            self._client.close()
            self._connected = False

# Initialize database instance
try:
    db = Database()
except Exception as e:
    print(f"⚠️  Database initialization failed: {e}")
    db = None

def add_user(email: str, password_hash: str, name: str = None) -> dict:
    """Add a new user to the database
    Returns: {"success": bool, "error": str, "error_type": str}
    """
    if db is None or not db.is_connected():
        return {
            "success": False,
            "error": "Database not connected",
            "error_type": "database_error"
        }
    
    try:
        if db.is_fallback_mode():
            # Fallback JSON mode
            data = db._load_fallback()
            
            # Check if user already exists
            if email in data:
                return {
                    "success": False,
                    "error": "Email already registered",
                    "error_type": "user_exists"
                }
            
            # Add new user
            user_data = {
                "email": email,
                "password": password_hash,
                "name": name,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "preferences": {
                    "topics": [],
                    "frequency": "daily",
                    "delivery_time": "08:00"
                }
            }
            
            data[email] = user_data
            db._save_fallback(data)
            
            print(f"✅ User added to fallback database: {email}")
            return {"success": True, "error": None, "error_type": None}
            
        else:
            # MongoDB mode
            # Check if user already exists
            existing_user = db.users.find_one({"email": email})
            if existing_user:
                return {
                    "success": False, 
                    "error": "Email already registered", 
                    "error_type": "user_exists"
                }
            
            user_data = {
                "email": email,
                "password": password_hash,
                "name": name,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "preferences": {
                    "topics": [],
                    "frequency": "daily",
                    "delivery_time": "08:00"
                }
            }
            
            result = db.users.insert_one(user_data)
            if result.inserted_id:
                return {"success": True, "error": None, "error_type": None}
            else:
                return {
                    "success": False, 
                    "error": "Failed to create user", 
                    "error_type": "database_error"
                }
                
    except pymongo.errors.DuplicateKeyError:
        return {
            "success": False,
            "error": "Email already registered",
            "error_type": "user_exists"
        }
    except pymongo.errors.ServerSelectionTimeoutError:
        return {
            "success": False,
            "error": "Database connection timeout",
            "error_type": "database_error"
        }
    except Exception as e:
        print(f"Error adding user: {e}")
        return {
            "success": False, 
            "error": f"Database error: {str(e)}", 
            "error_type": "database_error"
        }

def get_user(email: str) -> dict:
    """Get user by email"""
    if db is None or not db.is_connected():
        print("Database not connected")
        return None
        
    try:
        if db.is_fallback_mode():
            # Fallback JSON mode
            data = db._load_fallback()
            return data.get(email)
        else:
            # MongoDB mode
            return db.users.find_one({"email": email})
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def update_user(email: str, updates: dict) -> bool:
    """Update user information"""
    try:
        updates["updated_at"] = datetime.utcnow()
        result = db.users.update_one(
            {"email": email},
            {"$set": updates}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating user: {e}")
        return False

def delete_user(email: str) -> bool:
    """Delete user by email"""
    try:
        result = db.users.delete_one({"email": email})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

def get_all_users() -> list:
    """Get all users (for admin purposes)"""
    try:
        return list(db.users.find({}, {"password": 0}))  # Exclude password field
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []
