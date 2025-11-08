import requests
import random
import time
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api/v1"

file_types = ["video", "image", "document", "database", "logs", "backup"]
owners = ["team-alpha", "team-beta", "data-science", "engineering", "marketing"]
locations = ["on-premise", "aws", "azure", "gcp"]
tiers = ["hot", "warm", "cold"]

def generate_data_objects(count=50):
    print(f"📦 Generating {count} data objects...")
    for i in range(count):
        size_gb = random.choice([0.5, 1, 5, 10, 50, 100, 500, 1000])
        data = {
            "name": f"dataset-{random.randint(1000, 9999)}-{file_types[i % len(file_types)]}.dat",
            "size_bytes": int(size_gb * 1024 * 1024 * 1024),
            "current_tier": random.choice(tiers),
            "current_location": random.choice(locations),
            "metadata": {
                "file_type": random.choice(file_types),
                "owner": random.choice(owners),
                "tags": random.sample(["production", "staging", "test", "archived", "critical"], k=2),
                "description": f"Sample dataset for {file_types[i % len(file_types)]}"
            },
            "checksum": f"sha256:{random.randbytes(32).hex()}"
        }
        try:
            response = requests.post(f"{API_BASE}/data/upload", json=data)
            if response.status_code == 200:
                print(f"✅ Created: {data['name']}")
            else:
                print(f"❌ Failed to create {data['name']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(0.1)

def generate_access_logs(count=200):
    print(f"\n📊 Generating {count} access logs...")
    try:
        response = requests.get(f"{API_BASE}/data/")
        if response.status_code != 200:
            print("❌ Could not fetch data objects")
            return
        objects = response.json()
        if not objects:
            print("❌ No data objects found")
            return
        for i in range(count):
            obj = random.choice(objects)
            access_data = {
                "data_object_id": obj["_id"],
                "access_type": random.choice(["read", "write", "delete"]),
                "latency_ms": random.uniform(10, 500),
                "location": random.choice(locations)
            }
            try:
                response = requests.post(f"{API_BASE}/data/{obj['_id']}/access", params=access_data)
                if response.status_code == 200:
                    print(f"✅ Logged access for: {obj['name'][:30]}...")
            except Exception as e:
                print(f"❌ Error: {e}")
            time.sleep(0.05)
    except Exception as e:
        print(f"❌ Error: {e}")

def generate_migrations(count=10):
    print(f"\n🚀 Generating {count} migration jobs...")
    try:
        response = requests.get(f"{API_BASE}/data/")
        if response.status_code != 200:
            print("❌ Could not fetch data objects")
            return
        objects = response.json()
        if not objects:
            print("❌ No data objects found")
            return
        for i in range(count):
            obj = random.choice(objects)
            target_location = random.choice([loc for loc in locations if loc != obj["current_location"]])
            target_tier = random.choice(tiers)
            migration_data = {
                "data_object_id": obj["_id"],
                "target_location": target_location,
                "target_tier": target_tier,
                "priority": random.randint(1, 10)
            }
            try:
                response = requests.post(f"{API_BASE}/migration/initiate", json=migration_data)
                if response.status_code == 200:
                    print(f"✅ Migration initiated: {obj['name'][:30]}... -> {target_location}/{target_tier}")
                else:
                    print(f"❌ Failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Error: {e}")
            time.sleep(0.2)
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🌟 CloudFlow Sample Data Generator")
    print("=" * 50)
    print("\nWaiting for API to be ready...")
    time.sleep(5)
    
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code != 200:
            print("❌ API not ready. Please ensure the backend is running.")
            return
        print("✅ API is ready!\n")
    except Exception as e:
        print(f"❌ Could not connect to API: {e}")
        return
    
    generate_data_objects(50)
    generate_access_logs(200)
    generate_migrations(10)
    
    print("\n✅ Sample data generation complete!")
    print(f"\n📊 View the dashboard at: http://localhost:3000")
    print(f"📚 View API docs at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
