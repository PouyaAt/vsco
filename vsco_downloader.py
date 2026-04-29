import requests
import os
import sys
from bs4 import BeautifulSoup

BASE_URL = "https://vsco.co"

def get_profile_images(username):
    url = f"{BASE_URL}/{username}/images"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    images = set()

    # VSCO images typically have data-src or src
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

        print("Downloading:", filename)

        r = requests.get(url, stream=True)
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)


if __name__ == "__main__":
    username = sys.argv[1]

    folder = f"downloads/{username}"
    urls = get_profile_images(username)

    print("Found", len(urls), "images")
    download_images(urls, folder)
