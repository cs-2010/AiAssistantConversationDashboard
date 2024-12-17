"""
Database connection and operations for the AI Assistant Conversation Dashboard.
"""

import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv
import streamlit as st

# Constants
DEFAULT_MONGO_TIMEOUT = 30000
_mongo_client = None

def get_mongodb_uri() -> str:
    """Retrieve MongoDB URI from environment variables."""
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise ValueError("MONGO_URI environment variable is not set. Please check your .env file.")
    return str(uri).strip()

def initialize_mongodb():
    """Initialize MongoDB connection."""
    global _mongo_client
    
    if _mongo_client is not None:
        return _mongo_client
        
    try:
        MONGO_URI = get_mongodb_uri()
        _mongo_client = MongoClient(
            MONGO_URI,
            connectTimeoutMS=DEFAULT_MONGO_TIMEOUT,
            socketTimeoutMS=DEFAULT_MONGO_TIMEOUT,
            serverSelectionTimeoutMS=DEFAULT_MONGO_TIMEOUT,
            waitQueueTimeoutMS=DEFAULT_MONGO_TIMEOUT,
            retryWrites=True,
            tls=True,
        )
        # Test connection
        _mongo_client.admin.command('ping')
        return _mongo_client
    except Exception as e:
        raise Exception(f"Error creating MongoDB client: {str(e)}")

def get_database(database_name: str):
    """Get a MongoDB database instance."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = initialize_mongodb()
    return _mongo_client[database_name]

def fetch_conversation_data(conversation_id: str) -> tuple:
    """Fetch conversation data from MongoDB."""
    try:
        if not isinstance(conversation_id, str):
            raise ValueError(f"Invalid conversation ID: {conversation_id}. Please provide a single conversation ID as a string.")
        
        app_db = get_database("muse-application")
        feedback_db = get_database("muse-assistant-feedback")
        
        # Get conversation details
        conversation_details = app_db.conversations.find_one({
            "$or": [{"id": conversation_id}, {"conversation_id": conversation_id}]
        })
        
        if not conversation_details:
            st.warning(f"Debug: Could not find conversation with id: {conversation_id}")
            st.warning(f"Available collections: {', '.join(app_db.list_collection_names())}")
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
        st.error(f"Error: {str(e)}")
        return None, None, None, None
