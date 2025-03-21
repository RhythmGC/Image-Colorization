import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from bson import ObjectId
import json
from typing import List, Optional
from pydantic import BaseModel, Field
import traceback

# Load environment variables
load_dotenv()

# Get MongoDB Atlas credentials from environment variables
ATLAS_PASSWORD = os.getenv("ATLAS_PASSWORD")
ATLAS_USERNAME = os.getenv("ATLAS_USERNAME", "admin")
ATLAS_CLUSTER = os.getenv("ATLAS_CLUSTER", "cluster0.mongodb.net")
ATLAS_DB_NAME = os.getenv("ATLAS_DB_NAME", "image_colorization_db")

print(f"Using Atlas password: {'*' * len(ATLAS_PASSWORD) if ATLAS_PASSWORD else 'None'}")

# Initialize client variable
client = None

# Try to connect to MongoDB Atlas
try:
    # Using standard connection string (no SRV lookup)
    # Format: mongodb://username:password@host:port/database
    host = ATLAS_CLUSTER.replace(".mongodb.net", "")  # Get the base host name
    CONNECTION_STRING = f"mongodb+srv://{ATLAS_USERNAME}:{ATLAS_PASSWORD}@{ATLAS_CLUSTER}/?retryWrites=true&w=majority&appName={ATLAS_DB_NAME}"
    
    print(f"Connecting to MongoDB Atlas (password masked): {CONNECTION_STRING.replace(ATLAS_PASSWORD, '*****') if ATLAS_PASSWORD else CONNECTION_STRING}")
    
    # Connect with increased timeouts
    client = MongoClient(
        CONNECTION_STRING,
        serverSelectionTimeoutMS=5000,  # 5 seconds for server selection
        connectTimeoutMS=5000,          # 5 seconds to establish connection
        socketTimeoutMS=5000,           # 5 seconds for socket operations
    )
    
    # Test connection
    client.admin.command('ping')
    print("MongoDB Atlas connection successful")
except Exception as e:
    print(f"Error connecting to MongoDB Atlas: {str(e)}")
    print("Falling back to local MongoDB server...")
    
    try:
        # Try connecting to local MongoDB server
        LOCAL_CONNECTION_STRING = "mongodb://localhost:27017/"
        print(f"Connecting to local MongoDB: {LOCAL_CONNECTION_STRING}")
        
        client = MongoClient(LOCAL_CONNECTION_STRING, serverSelectionTimeoutMS=3000)
        
        # Test local connection
        client.admin.command('ping')
        print("Connected to local MongoDB server")
    except Exception as e_local:
        print(f"Error connecting to local MongoDB: {str(e_local)}")
        print("""
================================================================================
MONGODB CONNECTION FAILED
--------------------------------------------------------------------------------
Please ensure either:
1. Your internet connection is working for MongoDB Atlas, or
2. You have a local MongoDB server running

If you need to install MongoDB locally:
- Windows: https://www.mongodb.com/try/download/community
- Connect using the URI: mongodb://localhost:27017
================================================================================
""")
        raise Exception("Failed to connect to any MongoDB server (Atlas or local)") from e

# Database and collection
if client:
    db = client.image_colorization_db
    collection = db.images
    print(f"Using database: {db.name}, collection: {collection.name}")

# Helper for JSON serialization of ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

# Pydantic models for data validation
class ImageBase(BaseModel):
    title: str
    description: Optional[str] = None
    cloudinary_url: str
    colorized: bool = False
    colorized_cloudinary_url: Optional[str] = None
    
class ImageCreate(ImageBase):
    pass

class ImageResponse(ImageBase):
    id: str = Field(..., alias="_id")
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

# Database operations
def get_all_images():
    try:
        images = list(collection.find())
        print(f"Retrieved {len(images)} images from database")
        return json.loads(json.dumps(images, cls=JSONEncoder))
    except Exception as e:
        print(f"Error in get_all_images: {str(e)}")
        traceback.print_exc()
        return []

def get_image_by_id(image_id: str):
    try:
        image = collection.find_one({"_id": ObjectId(image_id)})
        if image:
            print(f"Retrieved image with ID {image_id}")
            return json.loads(json.dumps(image, cls=JSONEncoder))
        print(f"Image with ID {image_id} not found")
        return None
    except Exception as e:
        print(f"Error in get_image_by_id: {str(e)}")
        traceback.print_exc()
        return None

def create_image(image_data: dict):
    try:
        print(f"Inserting image data: {image_data}")
        result = collection.insert_one(image_data)
        print(f"Insert result: {result.inserted_id}")
        image_data["_id"] = result.inserted_id
        return json.loads(json.dumps(image_data, cls=JSONEncoder))
    except Exception as e:
        print(f"Error in create_image: {str(e)}")
        traceback.print_exc()
        return None

def update_image(image_id: str, image_data: dict):
    try:
        print(f"Updating image with ID {image_id}, data: {image_data}")
        collection.update_one({"_id": ObjectId(image_id)}, {"$set": image_data})
        updated_image = collection.find_one({"_id": ObjectId(image_id)})
        return json.loads(json.dumps(updated_image, cls=JSONEncoder))
    except Exception as e:
        print(f"Error in update_image: {str(e)}")
        traceback.print_exc()
        return None

def delete_image(image_id: str):
    try:
        print(f"Deleting image with ID {image_id}")
        result = collection.delete_one({"_id": ObjectId(image_id)})
        print(f"Delete result: {result.deleted_count} document(s) deleted")
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error in delete_image: {str(e)}")
        traceback.print_exc()
        return False
