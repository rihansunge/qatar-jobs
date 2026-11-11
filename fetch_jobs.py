import os
import json
import urllib.request
import urllib.error

# Get API key
api_key = os.environ.get("JOOBLE_API_KEY")
if not api_key:
    print("Error: JOOBLE_API_KEY is missing.")
    exit(1)

# FIXED: Added the 'f' at the beginning so python reads your secret key
url = f"https://jooble.org/api/{api_key}"

# Search payload for Qatar jobs
payload = json.dumps({
    "keywords": "accountant, engineer, sales, manager, driver",
    "location": "Qatar",
    "page": "1"
}).encode("utf-8")

req = urllib.request.Request(
    url,
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        jobs = result.get("jobs", [])
        
        # Save jobs directly as a list to jobs.json
        with open("jobs.json", "w", encoding="utf-8") as f:
            json.dump(jobs, f, ensure_ascii=False, indent=4)
            
        print(f"Successfully saved {len(jobs)} jobs to jobs.json")

except Exception as e:
    print(f"Failed to fetch jobs: {e}")
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump([], f)
