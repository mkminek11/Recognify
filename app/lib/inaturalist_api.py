
import os, re, time, requests
from typing import Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

PER_PAGE = 100
RATE_LIMIT_DELAY = 0.2  # Delay between API requests in seconds
rate_limit_lock = threading.Lock()
last_request_time = 0

# Create session with proxy bypass to avoid proxy connection issues
session = requests.Session()
session.proxies = {}  # Bypass system proxy
session.headers.update({'User-Agent': 'Recognify'})

def clean(name: str) -> str:
    return re.sub(r'[^0-9A-Za-zčřžýáíéúůťďň _.-]', '_', name)[:160]

def img_candidates(url: str) -> list[str]:
    u = url.split('?')[0]
    replacements = [("/square", "/original"), ("/small", "/original"), 
                   ("/medium", "/original"), ("/large", "/original"),
                   ("/square", "/large"), ("/small", "/large"),
                   ("/square", "/medium"), ("/small", "/medium")]
    
    candidates: list[str] = []
    for old, new in replacements:
        if old in u:
            candidates.append(u.replace(old, new))
    
    candidates.extend([u, url])
    return list(dict.fromkeys(filter(None, candidates)))

def get_page(query: str, page_i: int) -> list[dict]:
    params = {"q": query, "quality_grade": "research", "photos": "true", "per_page": PER_PAGE, "page": page_i+1}
    r = session.get("https://api.inaturalist.org/v1/observations", params = params, timeout = 20)
    r.raise_for_status()

    res: list[dict] = r.json().get("results", [])
    return res

def get_image_links(species: str, max_images: int) -> list[str]:
    image_links: list[str] = []
    saved = 0
    page_i = 0
    
    while saved < max_images:
        page = get_page(species, page_i)
        if not page: break

        for observation in page:
            if saved >= max_images: break
            for photo in observation.get("photos", []):
                if saved >= max_images: break
                base_url: str = photo.get("url", "")
                if base_url:
                    # Use img_candidates to get best quality URL (converts square→original/large)
                    candidates = img_candidates(base_url)
                    if candidates:
                        image_links.append(candidates[0])
                        saved += 1
        page_i += 1
    
    return image_links

def download_photos(query: str, max_img: int, output: str) -> None:
    links = get_image_links(query, max_img)
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = [executor.submit(download_candidate, link, output, 0, i) for i, link in enumerate(links)]
        for future in tasks:
            future.result()
                
def download_photo(photo: dict, obs_id: int, downloaded: int, output: str) -> bool:
    original_size_url: str = photo.get("url", "") or photo.get("large_url", "") or photo.get("original_url", "")
    if not original_size_url: return False
    
    for candidate_url in img_candidates(original_size_url):
        success = download_candidate(candidate_url, output, obs_id, downloaded)
        if success: break
    else:
        return False
    return True

def download_candidate(candidate_url: str, output: str, obs_id: int, downloaded: int) -> bool:
    try:
        response = session.get(candidate_url, stream=True, timeout=20, proxies={})
        if response.status_code != 200: return False
        if not response.headers.get("content-type", "").startswith("image"): return False

        extension = (response.headers.get("content-type", "")).split("/")[-1].split(";")[0]
        if extension == "jpeg": extension = "jpg"

        filename = f"inat_{obs_id}_{downloaded:03d}.{extension}"
        path = os.path.join(output, filename)
        write_file(response.iter_content(1024*16), path)
        return True
    except Exception:
        return False

def write_file(content_iter: Iterator[bytes], path: str) -> None:
    with open(path, "wb") as f:
        for chunk in content_iter:
            if chunk:
                f.write(chunk)

def get_inaturalist_image_links(species_list: list[str], max_images_per_species: int = 10) -> list[dict[str, str | list[str]]]:
    image_sets: list[dict] = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(get_image_links, species, max_images_per_species): species for species in species_list}
        for future in futures:
            species = futures[future]
            image_sets.append({"species": species, "urls": future.result()})
    return image_sets

__all__ = ["download_photos", "get_inaturalist_image_links"]
