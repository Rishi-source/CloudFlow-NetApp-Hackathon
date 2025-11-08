import requests
import random
import time
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api/v1"

def simulate_access_patterns(days=30):
    print(f"🔄 Simulating {days} days of access patterns...")
    try:
        response = requests.get(f"{API_BASE}/data/")
        if response.status_code != 200:
            print("❌ Could not fetch data objects")
            return
        objects = response.json()
        if not objects:
            print("❌ No data objects found. Run generate_sample_data.py first")
            return
        patterns = {
            'regular': lambda: random.randint(5, 15),
            'bursty': lambda: random.randint(0, 100) if random.random() > 0.9 else 0,
            'declining': lambda d: max(0, 20 - d),
            'increasing': lambda d: min(100, d * 2),
            'sporadic': lambda: random.randint(0, 5) if random.random() > 0.7 else 0
        }
        total_logs = 0
        for obj in objects:
            pattern_type = random.choice(list(patterns.keys()))
            pattern_func = patterns[pattern_type]
            print(f"\n📊 Simulating {pattern_type} pattern for: {obj['name'][:30]}...")
            for day in range(days):
                if pattern_type in ['declining', 'increasing']:
                    access_count = pattern_func(day)
                else:
                    access_count = pattern_func()
                for _ in range(int(access_count)):
                    access_data = {
                        "data_object_id": obj["_id"],
                        "access_type": random.choice(["read", "write", "metadata"]),
                        "latency_ms": random.uniform(10, 500),
                        "location": random.choice(["on-premise", "aws", "azure", "gcp"])
                    }
                    try:
                        response = requests.post(f"{API_BASE}/data/{obj['_id']}/access", params=access_data)
                        if response.status_code == 200:
                            total_logs += 1
                    except Exception:
                        pass
            time.sleep(0.1)
        print(f"\n✅ Generated {total_logs} access logs")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print("🌟 CloudFlow Access Pattern Simulator")
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
    simulate_access_patterns(30)
    print("\n✅ Access pattern simulation complete!")
    print(f"\n📊 View analytics at: http://localhost:3000")

if __name__ == "__main__":
    main()
