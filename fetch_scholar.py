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

    # Extract data from author object
    data = {
        "name": author.get("name"),
        "affiliation": author.get("affiliation"),
        "profile_url": author.get("scholar_url"),
        "citations_all": author.get("citedby"),
        "citations": author.get("citedby"),
        "h_index": author.get("hindex"),
        "i10_index": author.get("i10index"),
        "raw_indices": author.get("indices", {}),
        "last_updated": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    }

    # Save to data.json
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Data saved to data.json")
    print(f"Author: {data['name']}")
    print(f"Citations: {data['citations_all'] or data['citations']}")
    print(f"H-index: {data['h_index']}")
    print(f"I10-index: {data['i10_index']}")

if __name__ == "__main__":
    main()
