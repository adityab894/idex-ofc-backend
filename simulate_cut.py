import httpx
import sys

# Target API endpoint
URL = "http://127.0.0.1:8000/api/alarms/simulate"

def simulate():
    # Fetch segments to get an ID
    res = httpx.get("http://127.0.0.1:8000/api/segments")
    segments = res.json()
    if not segments:
        print("No segments found in the database. Did you run seed.py?")
        sys.exit(1)
        
    # We'll just cut the first one (usually Hindon-Ambala)
    target = segments[0]
    segment_id = target["id"]
    
    payload = {
        "segment_id": segment_id,
        "message": f"Critical Fiber Severed on {target['name']}! Immediate dispatch required.",
    }
    
    print(f"Simulating OFC cut on segment: {target['name']}...")
    resp = httpx.post(URL, json=payload)
    if resp.status_code == 200:
        alarm = resp.json()
        print(f"Success! Alarm generated: {alarm['id']}")
    else:
        print("Error:", resp.text)

if __name__ == "__main__":
    simulate()
