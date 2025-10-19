# fetch_scholar.py

from scholarly import scholarly
import json
import datetime
import sys
import time
import signal
from contextlib import contextmanager

# Use your Google Scholar author ID
# This is from your profile URL: user=sSPq-ZEAAAAJ
AUTHOR_ID = "sSPq-ZEAAAAJ"

# (We don't need AUTHOR_QUERY now — direct ID is more robust)
AUTHOR_QUERY = None

# Configuration
MAX_RETRIES = 3
TIMEOUT_SECONDS = 60
RETRY_DELAY = 5

@contextmanager
def timeout(duration):
    """Context manager for timing out operations"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {duration} seconds")
    
    # Set the signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(duration)
    
    try:
        yield
    finally:
        # Restore the old signal handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def fetch_by_id(author_id, retry_count=0):
    try:
        print(f"Fetching author by ID: {author_id} (attempt {retry_count + 1}/{MAX_RETRIES})")
        
        with timeout(TIMEOUT_SECONDS):
            print("  - Searching for author...")
            author = scholarly.search_author_id(author_id)
            
            print("  - Filling author details...")
            author = scholarly.fill(author, sections=["indices"])
            
        print("  - Successfully fetched author data")
        return author
        
    except TimeoutError as e:
        print(f"  - Timeout error: {e}", file=sys.stderr)
        if retry_count < MAX_RETRIES - 1:
            print(f"  - Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
            return fetch_by_id(author_id, retry_count + 1)
        else:
            print("  - Max retries reached", file=sys.stderr)
            return None
    except Exception as e:
        print(f"  - Error fetching by ID: {e}", file=sys.stderr)
        if retry_count < MAX_RETRIES - 1:
            print(f"  - Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
            return fetch_by_id(author_id, retry_count + 1)
        else:
            print("  - Max retries reached", file=sys.stderr)
            return None

def fetch_by_search(query, retry_count=0):
    try:
        print(f"Fetching author by search: {query} (attempt {retry_count + 1}/{MAX_RETRIES})")
        
        with timeout(TIMEOUT_SECONDS):
            print("  - Searching for author...")
            search = scholarly.search_author(query)
            author = next(search, None)
            
            if author is None:
                print("  - No author found in search results")
                return None
                
            print("  - Filling author details...")
            author = scholarly.fill(author, sections=["indices"])
            
        print("  - Successfully fetched author data")
        return author
        
    except TimeoutError as e:
        print(f"  - Timeout error: {e}", file=sys.stderr)
        if retry_count < MAX_RETRIES - 1:
            print(f"  - Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
            return fetch_by_search(query, retry_count + 1)
        else:
            print("  - Max retries reached", file=sys.stderr)
            return None
    except Exception as e:
        print(f"  - Error fetching by search: {e}", file=sys.stderr)
        if retry_count < MAX_RETRIES - 1:
            print(f"  - Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
            return fetch_by_search(query, retry_count + 1)
        else:
            print("  - Max retries reached", file=sys.stderr)
            return None

def main():
    print("Starting Google Scholar data fetch...")
    print(f"Configuration: MAX_RETRIES={MAX_RETRIES}, TIMEOUT={TIMEOUT_SECONDS}s")
    
    author = None
    if AUTHOR_ID:
        print(f"Attempting to fetch author by ID: {AUTHOR_ID}")
        author = fetch_by_id(AUTHOR_ID)
    
    if author is None and AUTHOR_QUERY:
        print(f"Attempting to fetch author by search: {AUTHOR_QUERY}")
        author = fetch_by_search(AUTHOR_QUERY)

    if not author:
        print("Failed to find author profile after all attempts.", file=sys.stderr)
        print("This could be due to:", file=sys.stderr)
        print("  - Network connectivity issues", file=sys.stderr)
        print("  - Google Scholar rate limiting", file=sys.stderr)
        print("  - Changes in Google Scholar's structure", file=sys.stderr)
        print("  - Invalid author ID or search query", file=sys.stderr)
        sys.exit(2)

    print("Successfully retrieved author data, processing...")
    
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
    print("Saving data to data.json...")
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Data successfully saved to data.json")
    print(f"📊 Author: {data['name']}")
    print(f"📈 Citations: {data['citations_all'] or data['citations']}")
    print(f"📊 H-index: {data['h_index']}")
    print(f"📊 I10-index: {data['i10_index']}")
    print(f"🕒 Last updated: {data['last_updated']}")

if __name__ == "__main__":
    main()
