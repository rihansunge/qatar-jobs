import os
import json
import urllib.request
import urllib.error

# 1. Retrieve the secret key safely from GitHub Actions environment
api_key = os.environ.get("JOOBLE_API_KEY")
if not api_key:
    print("Error: JOOBLE_API_KEY is missing from repository secrets.")
    exit(1)

# 2. Setup the official Jooble API endpoint
url = f"https://jooble.org/api/{api_key}"

# 3. Flexible payload to pull genuine listings matching Qatar
payload = json.dumps({
    "keywords": "jobs",
    "location": "Qatar",
    "page": 1
}).encode("utf-8")

req = urllib.request.Request(
    url,
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    # 4. Fetch the data from trusted sources via Jooble API
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        jobs = result.get("jobs", [])
        
        # 5. Save the active jobs directly into jobs.json for your website
        with open("jobs.json", "w", encoding="utf-8") as f:
            json.dump(jobs, f, ensure_ascii=False, indent=4)
            
        print(f"Successfully saved {len(jobs)} trusted jobs to jobs.json")

except Exception as e:
    print(f"Failed to fetch jobs: {e}")
    # Fallback to an empty list so your website UI doesn't break
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump([], f)
