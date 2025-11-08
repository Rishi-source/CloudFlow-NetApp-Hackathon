import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

@pytest.fixture
def mock_db():
    return {
        "data_objects": MockCollection(),
        "migration_jobs": MockCollection(),
        "access_logs": MockCollection(),
        "policies": MockCollection(),
        "alerts": MockCollection(),
        "users": MockCollection()
    }

class MockCollection:
    def __init__(self):
        self.data = []
    def insert_one(self, doc):
        self.data.append(doc)
        return type('obj', (object,), {'inserted_id': 'mock_id'})
    def find_one(self, query):
        for doc in self.data:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None
    def find(self, query=None):
        if query is None:
            return self.data
        return [doc for doc in self.data if all(doc.get(k) == v for k, v in query.items())]
    def update_one(self, query, update):
        for doc in self.data:
            if all(doc.get(k) == v for k, v in query.items()):
                doc.update(update.get('$set', {}))
                return type('obj', (object,), {'modified_count': 1})
        return type('obj', (object,), {'modified_count': 0})
    def delete_one(self, query):
        for i, doc in enumerate(self.data):
            if all(doc.get(k) == v for k, v in query.items()):
                self.data.pop(i)
                return type('obj', (object,), {'deleted_count': 1})
        return type('obj', (object,), {'deleted_count': 0})
    def count_documents(self, query):
        return len(self.find(query))
    def aggregate(self, pipeline):
        return []
    def sort(self, key, direction):
        return self
    def limit(self, n):
        return self.data[:n]
