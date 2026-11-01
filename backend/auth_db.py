"""
CropGuardian — MongoDB & Fallback User Authentication Manager
Handles user registration, login, password hashing with bcrypt,
and persistence in MongoDB (with automatic persistent JSON fallback if MongoDB is offline).
"""

import os
import json
import logging
from datetime import datetime
import bcrypt

logger = logging.getLogger("CropGuardianAuth")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "cropguardian_db"
COLLECTION_NAME = "users"
FALLBACK_USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "users_db.json")

mongo_client = None
mongo_db = None
users_col = None
is_mongo_connected = False

def init_db():
    global mongo_client, mongo_db, users_col, is_mongo_connected
    try:
        import pymongo
        mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
        mongo_client.server_info() # verify connection
        mongo_db = mongo_client[DB_NAME]
        users_col = mongo_db[COLLECTION_NAME]
        users_col.create_index("email", unique=True)
        is_mongo_connected = True
        logger.info(f"Connected to MongoDB at {MONGO_URI} (Database: {DB_NAME})")
    except Exception as e:
        is_mongo_connected = False
        logger.warning(f"MongoDB not reachable ({e}). Using persistent JSON storage: {FALLBACK_USERS_FILE}")
        if not os.path.exists(FALLBACK_USERS_FILE):
            with open(FALLBACK_USERS_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

init_db()

def _load_fallback_users():
    if not os.path.exists(FALLBACK_USERS_FILE):
        return {}
    try:
        with open(FALLBACK_USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_fallback_users(data):
    with open(FALLBACK_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def register_user(name, email, password, role="Agronomist / Farmer"):
    """Register a new user account."""
    email = email.strip().lower()
    name = name.strip()
    
    if not email or not password or not name:
        return {"success": False, "error": "All fields are required."}
    
    # Hash password
    salt = bcrypt.gensalt(rounds=12)
    pwd_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    
    user_doc = {
        "name": name,
        "email": email,
        "password_hash": pwd_hash,
        "role": role,
        "created_at": datetime.now().isoformat(),
        "storage": "mongodb" if is_mongo_connected else "local_json"
    }

    if is_mongo_connected and users_col is not None:
        try:
            if users_col.find_one({"email": email}):
                return {"success": False, "error": "Email is already registered. Please sign in."}
            users_col.insert_one(user_doc)
            return {"success": True, "message": "Account created successfully via MongoDB!", "user": {"name": name, "email": email, "role": role}}
        except Exception as e:
            logger.error(f"MongoDB insert failed: {e}")

    # Fallback to persistent JSON storage
    fallback_users = _load_fallback_users()
    if email in fallback_users:
        return {"success": False, "error": "Email is already registered. Please sign in."}
    fallback_users[email] = user_doc
    _save_fallback_users(fallback_users)
    return {"success": True, "message": "Account created successfully!", "user": {"name": name, "email": email, "role": role}}

def authenticate_user(email, password):
    """Authenticate existing user credentials."""
    email = email.strip().lower()
    
    if is_mongo_connected and users_col is not None:
        try:
            user = users_col.find_one({"email": email})
            if user:
                if bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
                    return {
                        "success": True,
                        "message": "Authentication successful (MongoDB)",
                        "user": {"name": user["name"], "email": user["email"], "role": user.get("role", "Agronomist / Farmer")}
                    }
                else:
                    return {"success": False, "error": "Invalid email or password."}
        except Exception as e:
            logger.error(f"MongoDB query failed: {e}")

    # Fallback to persistent JSON
    fallback_users = _load_fallback_users()
    if email in fallback_users:
        user = fallback_users[email]
        if bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            return {
                "success": True,
                "message": "Authentication successful!",
                "user": {"name": user["name"], "email": user["email"], "role": user.get("role", "Agronomist / Farmer")}
            }
        else:
            return {"success": False, "error": "Invalid email or password."}
            
    return {"success": False, "error": "No account found with this email. Please register."}
