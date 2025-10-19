# fetch_scholar.py

from scholarly import scholarly
import json
import datetime
import sys

# Use your Google Scholar author ID
# This is from your profile URL: user=sSPq-ZEAAAAJ
AUTHOR_ID = "sSPq-ZEAAAAJ"

# (We don't need AUTHOR_QUERY now — direct ID is more robust)
AUTHOR_QUERY = None

def fetch_by_id(author_id):
    try:
        author = scholarly.search_author_id(author_id)
        author = scholarly.fill(author, sections=["indices"])
        return author
    except Exception as e:
        print("Error fetching by ID:", e, file=sys.stderr)
        return None

def fetch_by_search(query):
    try:
        search = scholarly.search_author(query)
        author = next(search, None)
        if author is None:
            return None
        author = scholarly.fill(author, sections=["indices"])
        return author
    except Exception as e:
        print("Error fetching by search:", e, file=sys.stderr)
        return None

def main():
    author = None
    if AUTHOR_ID:
        author = fetch_by_id(AUTHOR_ID)
    if author is None and AUTHOR_QUERY:
        author = fetch_by_search(AUTHOR_QUERY)

    if not author:
        print("Failed to find author profile.", file=sys.stderr)
        sys.exit(2)

    indices = author.get("indices", {})

    data = {
        "name": author.get("name"),
        "affiliation": author.get("affiliation"),
        "profile_url": author.get("scholar_url"),
        "citations_all": None,
        "citations": None,
        "h_index": None,
        "i10_index": None,
        "raw_indices": indices,
        "last_updated": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    }

    # Scholarly’s internal structure might vary; we handle both common patterns
    # Pattern A: indices["cites"] is a dict with keys "all" & "since201X"
    cites = indices.get("cites")
    if isinstance(cites, dict):
        data["citations_all"] = cites.get("all")
    # Pattern B / fallback
    data["citations"] = author.get("citedby")

    # h
