
from pathlib import Path
from urllib.parse import unquote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


WIKI_API = "https://cs.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "Recognify"}


session = requests.Session()

retry = Retry(total = 5, backoff_factor = 2, status_forcelist = [429, 500, 502, 503, 504], allowed_methods = ["GET"])
adapter = HTTPAdapter(max_retries = retry)

session.mount("https://", adapter)
session.mount("http://", adapter)

session.headers.update(HEADERS)


def search(query: str) -> str | None:
    r = session.get(WIKI_API, params = {"action": "query", "list": "search", "srsearch": query, "utf8": 1, "format": "json"})
    r.raise_for_status()
    results = r.json()["query"]["search"]

    if not results: return None

    print([r["title"] for r in results])

    return results[0]["title"]


def get_main_image(page_title: str) -> str | None:
    r = session.get(WIKI_API, params = {"action": "query", "prop": "pageimages", "titles": page_title, "piprop": "original", "format": "json"})
    r.raise_for_status()
    pages = r.json()["query"]["pages"]
    if not pages: return None

    page = next(iter(pages.values()))
    print(f"- Stránka: {page['title']}")
    if "original" in page:
        return page["original"]["source"]

    return None


def download_image(url: str, output_dir: Path) -> Path:
    output_dir.mkdir(exist_ok = True)
    filename = unquote(url.split("/")[-1])
    path = output_dir / filename

    if path.exists(): return path

    r = session.get(url, stream = True, timeout = 60)
    r.raise_for_status()

    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    return path


def download_species_image(species: str, output_dir: Path) -> Path | None:
    page = search(species)
    if not page: return None

    image_url = get_main_image(page)
    if not image_url: return None

    path = download_image(image_url, output_dir)
    return path
