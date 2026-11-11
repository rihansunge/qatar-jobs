import os
import json
import urllib.request
import urllib.error

# Get your API key from GitHub repository secrets
api_key = os.environ.get("JOOBLE_API_KEY")
if not api_key:
    print("Error: JOOBLE_API_KEY is missing.")
    exit(1)

url = f"https://jooble.org/api/{api_key}"

# Comprehensive list of search keywords covering all job types and industries in Qatar
categories = [
    # Administration & Front Office
    "receptionist", "cashier", "administrator", "secretary", "data entry", "office boy",
    
    # Skilled Trades, Automotive & Operations
    "auto painter", "denter", "mechanic", "technician", "electrician", "plumber", "welder", "carpenter",
    
    # Logistics, Transport & General Labor
    "driver", "delivery", "storekeeper", "warehouse worker", "laborer", "cleaner", "security guard",
    
    # Finance, Sales & Retail
    "accountant", "sales associate", "sales executive", "merchandiser", "cashier", "marketing",
    
    # Engineering, Construction & IT
    "engineer", "civil engineer", "safety officer", "draftsman", "IT technician", "software developer",
    
    # Hospitality, Food & Services
    "waiter", "waitress", "barista", "cook", "chef", "housekeeping", "hotel staff",
    
    # Healthcare & Customer Service
    "nurse", "pharmacist", "customer service", "call center",
    
    # Management & General Search
    "manager", "supervisor", "coordinator", "jobs"
]

all_jobs = []
seen_links = set()

# Loop through each keyword to pull all available listings in Qatar
for keyword in categories:
    payload = json.dumps({
        "keywords": keyword,
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
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            jobs = result.get("jobs", [])
            
            # Prevent duplicate job posts if a listing hits multiple keyword queries
            for job in jobs:
                link = job.get("link")
                if link and link not in seen_links:
                    seen_links.add(link)
                    all_jobs.append(job)
                    
    except Exception as e:
        print(f"Skipped keyword '{keyword}' due to error: {e}")

# Save all gathered jobs to jobs.json
try:
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=4)
    print(f"Successfully saved a total of {len(all_jobs)} jobs across all categories to jobs.json")
except Exception as e:
    print(f"Failed to save jobs.json: {e}")
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump([], f)
