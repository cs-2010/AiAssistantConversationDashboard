"""
Database connection and operations for the AI Assistant Conversation Dashboard.
"""

import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Constants
DEFAULT_MONGO_TIMEOUT = 30000
_mongo_client = None

def get_mongodb_uri() -> str:
    """Retrieve MongoDB URI from environment variables."""
    # Load environment variables from .env file
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    # Get the MongoDB URI from the environment variables
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise ValueError("MONGO_URI environment variable is not set. Please check your .env file.")
    return str(uri).strip()

def initialize_mongodb():
    """Initialize MongoDB connection."""
    global _mongo_client
    
    # If a client already exists, return it
    if _mongo_client is not None:
        return _mongo_client
        
    try:
        # Get the MongoDB URI
        MONGO_URI = get_mongodb_uri()
        # Create a new MongoDB client
        _mongo_client = MongoClient(
            MONGO_URI,
            connectTimeoutMS=DEFAULT_MONGO_TIMEOUT,
            socketTimeoutMS=DEFAULT_MONGO_TIMEOUT,
            serverSelectionTimeoutMS=DEFAULT_MONGO_TIMEOUT,
            waitQueueTimeoutMS=DEFAULT_MONGO_TIMEOUT,
            retryWrites=True,
            tls=True,
        )
        # Test the connection
        _mongo_client.admin.command('ping')
        return _mongo_client
    except Exception as e:
        raise Exception(f"Error creating MongoDB client: {str(e)}")

def get_database(database_name: str):
    """Get a MongoDB database instance."""
    global _mongo_client
    # If a client doesn't exist, initialize it
    if _mongo_client is None:
        _mongo_client = initialize_mongodb()
    # Return the database instance
    return _mongo_client[database_name]

def fetch_conversation_data(conversation_id: str) -> tuple:
    """Fetch conversation data from MongoDB."""
    try:
        # Validate conversation ID
        if not isinstance(conversation_id, str):
            raise ValueError(f"Invalid conversation ID: {conversation_id}. Please provide a single conversation ID as a string.")
        
        # Get database instances
        app_db = get_database("muse-application")
        feedback_db = get_database("muse-assistant-feedback")
        
        # Get conversation details
        conversation_details = app_db.conversations.find_one({
            "$or": [{"id": conversation_id}, {"conversation_id": conversation_id}]
        })
        
        if not conversation_details:
            return None, None, None, None
        
        # Get analytics data
        analytics_data = feedback_db.analytics.find_one({"conversation_id": conversation_id})
        if not analytics_data:
            return None, None, None, None
        
        # Get context entries
        context_entries = []
        messages = analytics_data.get("message_history", [])
        context_ids = {msg.get("context_id") for msg in messages if msg.get("context_id")}
        
        if context_ids:
            # Convert set to list for MongoDB query
            context_ids_list = list(context_ids)
            context_entries = list(app_db.context.find(
                {"id": {"$in": context_ids_list}},
                projection={"_id": 0, "id": 1, "data": 1, "timestamp": 1}
            ))
        
        return conversation_details, analytics_data, context_entries, messages
        
    except Exception as e:
        return None, None, None, None

def search_conversations(search_pattern: str, min_messages: int = 0, max_messages: int = 0, limit: int = 1000, skip: int = 0, start_date = None, end_date = None):
    """
    Search for conversations where the title matches the given pattern,
    and optionally filter by the number of messages.
    Returns a list of conversations with their basic information.
    """
    try:
        # Initialize MongoDB client
        client = initialize_mongodb()
        # Get the database instance
        db = client.get_database("muse-application")
        # Get the conversations collection
        collection = db["conversations"]
        
        # Create a query to find conversations with matching titles
        query = {}
        if search_pattern:
            pattern = {"$regex": f".*{search_pattern}.*", "$options": "i"}
            query["title"] = pattern
        
        if min_messages > 0 or max_messages > 0:
            query["$where"] = ""
            if min_messages > 0 and max_messages > 0:
                query["$where"] = f"this.history && this.history.length >= {min_messages} && this.history.length <= {max_messages}"
            elif min_messages > 0:
                query["$where"] = f"this.history && this.history.length >= {min_messages}"
            elif max_messages > 0 :
                query["$where"] = f"this.history && this.history.length <= {max_messages}"
        
        if start_date and end_date:
            start_of_day = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            end_of_day = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
            query["history.0.timestamp"] = {"$gte": int(start_of_day.timestamp() * 1000), "$lte": int(end_of_day.timestamp() * 1000)}
        elif start_date:
            start_of_day = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
            query["history.0.timestamp"] = {"$gte": int(start_of_day.timestamp() * 1000)}
        elif end_date:
            end_of_day = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
            query["history.0.timestamp"] = {"$lte": int(end_of_day.timestamp() * 1000)}
        
        # Execute the query
        cursor = collection.find(query).skip(skip).limit(limit)
        
        results = []
        # Iterate through the results
        for conv in cursor:
            try:
                # Safely get history with fallback to empty list
                history = conv.get("history", []) or []
                
                # Safely get first and last messages
                first_msg = history[0] if history else {}
                last_msg = history[-1] if history else {}
                
                # Safely get message content with fallback to empty string
                first_msg_content = first_msg.get("content", "") if isinstance(first_msg, dict) else ""
                last_msg_content = last_msg.get("content", "") if isinstance(last_msg, dict) else ""
                
                # Get available function names with error handling
                function_catalog = conv.get("function_catalog", []) or []
                functions = [f.get("name", "") for f in function_catalog if isinstance(f, dict)]
                
                # Create a result dictionary
                result = {
                    "id": conv.get("id", str(conv["_id"])),
                    "name": conv.get("title", "Unnamed"),
                    "message_count": len(history),
                    "is_favorite": conv.get("is_favorite", False),
                    "tags": conv.get("tags", []) or [],
                    "owners": conv.get("owners", []) or [],
                    "first_message": first_msg_content[:100] + "..." if first_msg_content else "No content",
                    "last_message": last_msg_content[:100] + "..." if last_msg_content else "No content",
                    "created_at": first_msg.get("timestamp") if isinstance(first_msg, dict) else None,
                    "updated_at": last_msg.get("timestamp") if isinstance(last_msg, dict) else None,
                    "available_functions": ", ".join(functions) if functions else "None"
                }
                
                results.append(result)
            except Exception as e:
                continue
        
        return results
    except Exception as e:
        return []
