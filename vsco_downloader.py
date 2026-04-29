import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

SITES = [
    "https://www.expertstool.com",
    "https://www.toolesh.com",
    "https://www.instag.com",
    "https://www.faceb.com",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT = 15


def probe_site(url):
    result = {
        "url": url,
        "status": None,
        "reachable": False,
        "has_html": False,
        "has_form": False,
        "bot_block_detected": False,
        "notes": [],
    }

    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        result["status"] = r.status_code
        result["reachable"] = True

        if r.headers.get("Content-Type", "").startswith("text/html"):
            result["has_html"] = True
            soup = BeautifulSoup(r.text, "html.parser")

            if soup.find("form"):
                result["has_form"] = True

            text = r.text.lower()
            if any(k in text for k in ["cloudflare", "captcha", "verify you are human"]):
                result["bot_block_detected"] = True
                result["notes"].append("Possible bot protection detected")

        else:
            result["notes"].append("Non-HTML response")

        if r.status_code in (403, 429):
            result["notes"].append("Access blocked from CI IP")

    except requests.exceptions.RequestException as e:
        result["notes"].append(str(e))

    return result


def main():
    print("VSCO Downloader Site Probe (GitHub Actions compatible)\n")

    for site in SITES:
        res = probe_site(site)

        print(f"Site: {res['url']}")
        print(f"  Status: {res['status']}")
        print(f"  Reachable: {res['reachable']}")
        print(f"  HTML Returned: {res['has_html']}")
        print(f"  Has <form>: {res['has_form']}")
        print(f"  Bot Block Detected: {res['bot_block_detected']}")

        if res["notes"]:
            for note in res["notes"]:
                print(f"  Note: {note}")

        print("-" * 50)


if __name__ == "__main__":
    main()
