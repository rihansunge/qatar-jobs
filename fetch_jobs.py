import os
import json
import urllib.request
import urllib.parse
import html
import re
from datetime import datetime, timezone

API_KEY = os.environ.get("JOOBLE_API_KEY", "").strip()
LOCATION = os.environ.get("JOB_LOCATION", "Qatar").strip()
KEYWORDS = [k.strip() for k in os.environ.get("JOB_KEYWORDS", "manager, engineer, sales, accountant, driver, receptionist, cashier, auto painter, technician, administrator").split(",") if k.strip()]
PAGES = int(os.environ.get("JOB_PAGES", "2") or 2)
JOBS_FILE = "jobs.json"
MAX_JOBS = 300

if not API_KEY:
    raise SystemExit("JOOBLE_API_KEY is missing.")

def clean(text):
    text = html.unescape(str(text or ""))
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()

def fetch(keywords, page):
    body = json.dumps({"keywords": keywords, "location": LOCATION, "page": str(page)}).encode("utf-8")
    req = urllib.request.Request(
        f"https://jooble.org/api/{API_KEY}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except Exception as e:
        print(f"Error fetching '{keywords}' page {page}: {e}")
        return {}

found = {}
for kw in KEYWORDS:
    for page in range(1, PAGES + 1):
        data = fetch(kw, page)
        items = data.get("jobs", []) if isinstance(data, dict) else []
        if not items:
            break
        for j in items:
            link = str(j.get("link", "")).strip()
            if not link.startswith("https://"):
                continue
            job_id = str(j.get("id") or link)
            updated = str(j.get("updated", ""))[:10]
            found[job_id] = {
                "id": job_id,
                "title": clean(j.get("title")),
                "company": clean(j.get("company")),
                "location": clean(j.get("location")),
                "snippet": clean(j.get("snippet"))[:600],
                "salary": clean(j.get("salary")),
                "type": clean(j.get("type")),
                "posted": updated,
                "link": link,
            }

jobs_list = list(found.values())[:MAX_JOBS]

output = {
    "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "jobs": jobs_list
}

with open(JOBS_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Successfully saved {len(jobs_list)} jobs to {JOBS_FILE}")
