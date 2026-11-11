import os
import json
import urllib.request
import html
import re
import time
from datetime import datetime, timezone

API_KEY = os.environ.get("JOOBLE_API_KEY", "").strip()
JOBS_FILE = "jobs.json"
MAX_JOBS = 300

if not API_KEY:
    print("Error: JOOBLE_API_KEY is missing from repository secrets.")
    exit(1)

def clean(text):
    text = html.unescape(str(text or ""))
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()

def query_jooble(keywords, location="Qatar", page="1"):
    url = f"https://jooble.org/api/{API_KEY}"
    payload = {
        "keywords": keywords,
        "location": location,
        "page": str(page)
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_data = json.load(resp)
            return res_data.get("jobs", []) if isinstance(res_data, dict) else []
    except Exception as e:
        print(f"API Request error for '{keywords}' in {location}: {e}")
        return []

found = {}

# Primary Search Terms
search_terms = [
    "jobs",
    "driver",
    "accountant",
    "engineer",
    "receptionist",
    "cashier",
    "auto painter",
    "technician",
    "sales",
    "administrator",
    "waiter",
    "cleaner",
    "security guard"
]

for term in search_terms:
    items = query_jooble(keywords=term, location="Qatar", page="1")
    for j in items:
        link = str(j.get("link", "")).strip()
        if not link.startswith("https://"):
            continue
        job_id = str(j.get("id") or link)
        found[job_id] = {
            "id": job_id,
            "title": clean(j.get("title")),
            "company": clean(j.get("company")),
            "location": clean(j.get("location")) or "Qatar",
            "snippet": clean(j.get("snippet"))[:600],
            "salary": clean(j.get("salary")),
            "type": clean(j.get("type")),
            "posted": str(j.get("updated", ""))[:10],
            "link": link,
        }
    time.sleep(0.5)

jobs_list = list(found.values())[:MAX_JOBS]

# Write out the updated structure matching index.html
if jobs_list:
    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "jobs": jobs_list
    }
    with open(JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved {len(jobs_list)} jobs to {JOBS_FILE}")
else:
    print("Warning: API returned 0 jobs. Preserving file to avoid wiping site.")
