from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

MONGO_DETAILS = "mongodb://localhost:27017"

client = MongoClient(MONGO_DETAILS)
database = client.chat_db

users_collection = database.get_collection("users")
conversations_collection = database.get_collection("conversations")

def add_message(conversation_id: str, ehempid: str, content: str):
    message = {
        "message_id": str(ObjectId()),
        "ehempid": ehempid,
        "content": content,
        "timestamp": datetime.utcnow()
    }
    conversations_collection.update_one(
        {"conv_id": conversation_id},
        {"$push": {"messages": message}}
    )

def retrieve_messages(conversation_id: str):
    conversation = conversations_collection.find_one({"conv_id": conversation_id})
    if conversation:
        return conversation["messages"]
    return []

def create_or_get_conversation(ehempid1: str, ehempid2: str):
    conversation = conversations_collection.find_one({"participants": {"$all": [ehempid1, ehempid2]}})
    if conversation:
        return conversation["conv_id"]
    else:
        conversation_id = str(ObjectId())
        conversation = {
            "conv_id": conversation_id,
            "participants": [ehempid1, ehempid2],
            "messages": []
        }
        conversations_collection.insert_one(conversation)
        
        users_collection.update_one(
            {"ehempid": ehempid1},
            {"$push": {"convoids": {ehempid2: conversation_id}}},
            upsert=True
        )
        
        users_collection.update_one(
            {"ehempid": ehempid2},
            {"$push": {"convoids": {ehempid1: conversation_id}}},
            upsert=True
        )
        
        return conversation_id

def convert_objectid_to_str(document):
    if isinstance(document, list):
        for doc in document:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
    elif isinstance(document, dict):
        if '_id' in document:
            document['_id'] = str(document['_id'])
    return document