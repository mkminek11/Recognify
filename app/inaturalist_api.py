
import os, re, time, requests
from typing import Iterator

OUT = "img"
PER_PAGE = 100

os.makedirs(OUT, exist_ok=True)

session = requests.Session()

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

def download_photos(query: str, max_img: int) -> None:
    downloaded = 0
    page_i = 0
    
    while downloaded < max_img:
        page = get_page(query, page_i)
        if not page: break

        for observation in page:
            if downloaded >= max_img: break
            obs_id: int = observation.get("id", 0)
            
            for photo in observation.get("photos", []):
                if downloaded >= max_img: break
                success = download_photo(photo, obs_id, downloaded)
                if success: downloaded += 1
                
def download_photo(photo: dict, obs_id: int, downloaded: int) -> bool:
    original_size_url: str = photo.get("url", "") or photo.get("large_url", "") or photo.get("original_url", "")
    if not original_size_url: return False
    
    for candidate_url in img_candidates(original_size_url):
        success = download_candidate(candidate_url, obs_id, downloaded)
        if success: break
    else:
        return False
    return True

def download_candidate(candidate_url: str, obs_id: int, downloaded: int) -> bool:
    try:
        response = session.get(candidate_url, stream=True, timeout=20)
        if response.status_code != 200: return False
        if not response.headers.get("content-type", "").startswith("image"): return False

        extension = (response.headers.get("content-type", "")).split("/")[-1].split(";")[0]
        if extension == "jpeg": extension = "jpg"

        filename = f"inat_{obs_id}_{downloaded:03d}.{extension}"
        path = os.path.join(OUT, filename)
        write_file(response.iter_content(1024*16), path)
        return True
    except Exception:
        return False

def write_file(content_iter: Iterator[bytes], path: str) -> None:
    with open(path, "wb") as f:
        for chunk in content_iter:
            if chunk:
                f.write(chunk)

__all__ = ["download_photos"]
