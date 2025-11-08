from pymongo import MongoClient
from config.settings import settings

_client = None
_db = None

def get_database():
    global _client, _db
    if _db is None:
        _client = MongoClient(settings.mongodb_url)
        _db = _client[settings.mongodb_database]
    return _db

def close_database():
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
