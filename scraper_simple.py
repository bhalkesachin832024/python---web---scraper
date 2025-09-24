# scraper_simple.py
"""
Super simple web scraper using only Python stdlib.
- Fetches Hacker News front page JSON feed
- Saves to SQLite
- Exports to CSV
Runs immediately when executed.
"""

import sqlite3
import urllib.request
import json
import datetime
import csv

DB_FILE = "scraper.db"
TARGET_FEED = "https://hnrss.org/frontpage.jsonfeed"
CSV_FILE = "export.csv"

# --- Database setup ---
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS scraped_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    title TEXT,
    url TEXT,
    fetched_at TEXT
)
""")
conn.commit()

# --- Scraper ---
print(f"[{datetime.datetime.utcnow().isoformat()}] Fetching {TARGET_FEED}")
req = urllib.request.Request(TARGET_FEED, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.load(resp)

items = []
for item in data.get("items", [])[:5]:  # limit to 5 items
    title = item.get("title")
    link = item.get("url")
    fetched_at = datetime.datetime.utcnow().isoformat()
    items.append((TARGET_FEED, title, link, fetched_at))

# --- Save to DB ---
cur.executemany(
    "INSERT INTO scraped_items (source, title, url, fetched_at) VALUES (?, ?, ?, ?)",
    items
)
conn.commit()
print(f"Inserted {len(items)} rows into {DB_FILE}")

# --- Export to CSV ---
cur.execute("SELECT * FROM scraped_items")
rows = cur.fetchall()
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "source", "title", "url", "fetched_at"])
    writer.writerows(rows)

print(f"Exported {len(rows)} rows to {CSV_FILE}")
conn.close()