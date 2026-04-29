import requests
import os
import sys
from bs4 import BeautifulSoup

BASE_URL = "https://vsco.co"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}


def get_profile_images(username):
    url = f"{BASE_URL}/{username}/images"

    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    images = set()

    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")

        if src and "vsco" in src:
            if src.startswith("//"):
                src = "https:" + src
            images.add(src)

    return list(images)


def download_images(urls, folder):
    os.makedirs(folder, exist_ok=True)

    for url in urls:
        filename = url.split("/")[-1].split("?")[0]
        path = os.path.join(folder, filename)

        print("Downloading:", url)

        r = requests.get(url, headers=HEADERS, stream=True)

        if r.status_code == 200:
            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
        else:
            print("Failed:", url, r.status_code)


if __name__ == "__main__":
    username = sys.argv[1]

    folder = f"downloads/{username}"

    urls = get_profile_images(username)

    print("Found", len(urls), "images")

    download_images(urls, folder)
