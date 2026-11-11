"""Fetch job listings for Qatar from the Jooble API and save them to jobs.json.
Uses only the Python standard library. The API key comes from the JOOBLE_API_KEY
environment variable (a GitHub secret) and is never printed or saved."""
import datetime
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

KEY = os.environ.get("JOOBLE_API_KEY", "").strip()
LOCATION = os.environ.get("JOB_LOCATION", "Qatar").strip()
KEYWORDS = [k.strip() for k in os.environ.get("JOB_KEYWORDS", "").split(",")]
PAGES = int(os.environ.get("JOB_PAGES", "2") or 2)
JOBS_FILE = "jobs.json"
MAX_JOBS = 300
MAX_AGE_DAYS = 30

if not KEY:
    sys.exit("JOOBLE_API_KEY is missing. Add it under Settings > Secrets and variables > Actions.")


def clean(text):
    text = html.unescape(str(text or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fetch(keywords, page):
    body = json.dumps({"keywords": keywords, "location": LOCATION, "page": str(page)}).encode("utf-8")
    req = urllib.request.Request(
        "https://jooble.org/api/" + KEY, data=body, method="POST",
        headers={"Content-Type": "application/json"},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("Jooble says we are over the request limit (429). Keeping the existing jobs.")
                sys.exit(0)
            if e.code in (500, 502, 503) and attempt < 2:
                time.sleep(15 * (attempt + 1))
                continue
            sys.exit(f"Jooble API error {e.code}")
        except (TimeoutError, urllib.error.URLError):
            if attempt < 2:
                time.sleep(15)
                continue
            sys.exit("Could not reach Jooble.")


try:
    with open(JOBS_FILE, encoding="utf-8") as f:
        old = json.load(f).get("jobs", [])
except (FileNotFoundError, json.JSONDecodeError):
    old = []

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
            jid = str(j.get("id") or link)
            updated = str(j.get("updated", ""))[:10]
            found[jid] = {
                "id": jid,
                "title": clean(j.get("title")),
                "company": clean(j.get("company")),
                "location": clean(j.get("location")),
                "snippet": clean(j.get("snippet"))[:300],
                "salary": clean(j.get("salary")),
                "type": clean(j.get("type")),
                "posted": updated,
                "link": link,
            }

merged = {j["id"]: j for j in old}
merged.update(found)

cutoff = (datetime.date.today() - datetime.timedelta(days=MAX_AGE_DAYS)).isoformat()
jobs = [j for j in merged.values() if j.get("title") and (not j.get("posted") or j["posted"] >= cutoff)]
jobs.sort(key=lambda j: j.get("posted", ""), reverse=True)
jobs = jobs[:MAX_JOBS]

if json.dumps(jobs, sort_keys=True) == json.dumps(old, sort_keys=True):
    print("No changes.")
    sys.exit(0)

with open(JOBS_FILE, "w", encoding="utf-8") as f:
    json.dump({"updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "jobs": jobs},
              f, ensure_ascii=False, indent=1)

print(f"Saved {len(jobs)} jobs ({len(found)} fetched this run).")
