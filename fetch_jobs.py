import os
import json
import time
import urllib.request
import urllib.error

# Get API key from GitHub repository secrets
api_key = os.environ.get("JOOBLE_API_KEY")
if not api_key:
    print("Error: JOOBLE_API_KEY is missing.")
    exit(1)

url = f"https://jooble.org/api/{api_key}"

# Locations to fetch all active job postings in the country
search_locations = ["Qatar", "Doha"]

all_jobs = []
seen_links = set()

# Loop through pages for each location to gather maximum vacancies
for location in search_locations:
    for page in range(1, 4):  # Fetches pages 1, 2, and 3
        payload = json.dumps({
            "location": location,
            "page": page
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
                
                if not jobs:
                    break  # Stop if no more jobs on this page
                
                for job in jobs:
                    link = job.get("link")
                    if link and link not in seen_links:
                        seen_links.add(link)
                        all_jobs.append(job)
                        
            # Small delay to prevent Jooble API rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching page {page} for {location}: {e}")
            break

# Save collected jobs to jobs.json
if all_jobs:
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=4)
    print(f"Successfully saved {len(all_jobs)} jobs to jobs.json")
else:
    print("No jobs fetched; preserving existing jobs.json to avoid breaking site.")
