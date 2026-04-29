import requests
import os
import sys

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}


def get_site_id(username):
    url = f"https://vsco.co/api/2.0/sites?subdomain={username}"

    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()

    data = r.json()

    return data["sites"][0]["id"]


def get_media(site_id):
    url = f"https://vsco.co/api/2.0/medias?site_id={site_id}&size=100"

    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()

    data = r.json()

    media_urls = []

    for item in data["media"]:
        url = item["responsive_url"]
        media_urls.append(url)

    return media_urls


def download(urls, folder):
    os.makedirs(folder, exist_ok=True)

    for url in urls:
        filename = url.split("/")[-1].split("?")[0]
        path = os.path.join(folder, filename)

        print("Downloading:", url)

        r = requests.get(url, stream=True)

        if r.status_code == 200:
            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)


if __name__ == "__main__":
    username = sys.argv[1]

    print("Getting site id...")
    site_id = get_site_id(username)

    print("Site id:", site_id)

    print("Getting media...")
    media = get_media(site_id)

    print("Found", len(media), "posts")

    download(media, f"downloads/{username}")
