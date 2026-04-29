import re
import requests
from bs4 import BeautifulSoup

SITES = [
    "https://www.expertstool.com",
    "https://www.toolesh.com",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.8",
}

TIMEOUT = 15


def extract_candidate_urls(html, base):
    """Find URLs that look like APIs or tools inside a page."""
    soup = BeautifulSoup(html, "html.parser")
    text = html

    found = set()

    # Any href or src attributes
    for tag in soup.find_all(["a", "script", "form", "link"]):
        for attr in ["href", "src", "action"]:
            val = tag.get(attr)
            if val and isinstance(val, str):
                found.add(val)

    # Raw text patterns
    candidates = re.findall(
        r"https?://[^\s\"']+(?:download|api|php|aspx|vsco)[^\s\"']*",
        text,
        re.I,
    )
    found.update(candidates)

    # Normalize relative paths
    clean = []
    for f in found:
        if f.startswith("http"):
            clean.append(f)
        elif f.startswith("/") and not f.startswith("//"):
            clean.append(base.rstrip("/") + f)
    return list(set(clean))


def try_fetch_json(url):
    """Try calling a detected endpoint to see if it returns JSON."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        ct = r.headers.get("Content-Type", "")
        if "json" in ct.lower():
            return True
        # look for JSON-like text even if ct is text/html
        if r.text.strip().startswith("{") or r.text.strip().startswith("["):
            return True
        return False
    except Exception:
        return False


def main():
    print("=== Public Downloader API Detector ===\n")

    for site in SITES:
        print(f"🔍 Checking {site} ...")
        try:
            resp = requests.get(site, headers=HEADERS, timeout=TIMEOUT)
            html = resp.text
            candidates = extract_candidate_urls(html, site)

            print(f"  Found {len(candidates)} possible endpoints:")
            for c in candidates:
                if try_fetch_json(c):
                    print(f"     ✅ JSON endpoint: {c}")
                else:
                    print(f"     📄 Non‑JSON endpoint or inaccessible: {c}")

        except requests.exceptions.RequestException as e:
            print(f"  ❌ Failed: {e}")
        print("-" * 60)


if __name__ == "__main__":
    main()
