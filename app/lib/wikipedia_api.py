
import requests
from urllib.parse import quote, unquote, urlparse
import re
import time

THUMBNAIL_WIDTH = 900
USER_AGENT = "Recognify/1.0 (contact: mkminek11@seznam.cz)"
TIMEOUT = 8
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")  # skips svg icons/flags/maps
MIN_IMAGE_SIZE = 200
WIKI_LANGS = {"cs": "Czech Wikipedia", "en": "English Wikipedia"}

_session = requests.Session()
_session.headers["User-Agent"] = USER_AGENT


def get_links(species_list: list[str], lang: str) -> list[dict[str, str | list[str]]]:
    links: list[dict] = []
    for species in species_list:
        urls = get_links_for(species, lang)
        links.append({"species": species, "urls": urls})
    return links

def get_links_for(species: str, lang: str) -> list[str]:
    species = species.strip()
    attempts: list[str] = []
    attempts.extend(_by_title(species, lang))
    # attempts.extend(_by_search(species, lang))
    # attempts.extend(_from_commons(species, lang))

    return attempts

def _by_title(species: str, lang: str) -> list[str]:
    for page in _wiki_pages(species, lang):
        result = _get_article_data(page, lang)
        if not result: continue
        thumb_url = result.get("image_url")
        if not thumb_url: continue
        urls = [thumb_url]
        for url in _page_images(result["title"], lang):
            if not any(_same_file(url, u) for u in urls):
                urls.append(url)
        return urls
    return []

def _file_name(url: str) -> str:
    name = unquote(urlparse(url).path.rsplit("/", 1)[-1])
    return re.sub(r"^\d+px-", "", name)

def _same_file(a: str, b: str) -> bool:
    return _file_name(a) == _file_name(b)

def _page_images(title: str, lang: str) -> list[str]:
    host = f"{lang}.wikipedia.org"
    pages = _api(host, titles=title, redirects=1, prop="images", imlimit="max")
    file_titles = [
        img["title"]
        for page in pages
        for img in page.get("images", [])
        if img["title"].lower().endswith(IMAGE_EXTENSIONS)
    ]
    urls: list[str] = []
    for i in range(0, len(file_titles), 50):
        batch = file_titles[i:i + 50]
        infos = _api(
            host,
            titles="|".join(batch),
            prop="imageinfo",
            iiprop="url|size",
            iiurlwidth=THUMBNAIL_WIDTH,
        )
        for info in infos:
            ii = (info.get("imageinfo") or [None])[0]
            if not ii or ii.get("width", 0) < MIN_IMAGE_SIZE or ii.get("height", 0) < MIN_IMAGE_SIZE:
                continue
            urls.append(ii.get("thumburl") or ii["url"])
    return urls

def _wiki_pages(species: str, lang: str) -> list[dict]:
    return _api(
        f"{lang}.wikipedia.org",
        titles=species,
        redirects=1,
        prop="pageimages|pageprops|extracts",
        piprop="thumbnail",
        pithumbsize=THUMBNAIL_WIDTH,
        ppprop="disambiguation",
        exintro=1,
        explaintext=1,
        exsentences=2,
        exlimit="max",
    )

def _api(host, **params):
    params = {"action": "query", "format": "json", "formatversion": "2", **params}
    for attempt in range(5):
        r = _session.get(f"https://{host}/w/api.php", params=params, timeout=15)
        if r.status_code == 429:
            time.sleep(min(float(r.headers.get("Retry-After", 2 ** attempt)), 60))
            continue
        r.raise_for_status()
        return r.json().get("query", {}).get("pages", [])
    raise RuntimeError("Wikipedia kept returning 429; try again in a few minutes")

def _get_article_data(page: dict, lang: str) -> dict[str, str] | None:
    thumb: dict[str, str] = page.get("thumbnail", {})
    print(f"{thumb=}")
    if not thumb or page.get("missing"):
        return None
    if "disambiguation" in page.get("pageprops", {}):
        return None
    title: str = page.get("title", "")

    return {
        "title": title,
        "image_url": thumb.get("source", ""),
        "page_url": f"https://{lang}.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}",
    }
