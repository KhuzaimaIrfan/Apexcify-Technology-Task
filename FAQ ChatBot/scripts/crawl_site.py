import os
import re
import json
import time
from collections import deque
from urllib.parse import urlparse, urljoin, urldefrag

from tqdm import tqdm
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "https://www.rasinnovatech.com/"
OUT_DIR = "data/raw"
MAX_PAGES = 120
DELAY_SEC = 1.0
NAV_TIMEOUT_MS = 30000
WAIT_AFTER_LOAD_MS = 2000  # Increased for stability

SKIP_EXT = (
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico",
    ".pdf", ".zip", ".rar", ".7z", ".mp4", ".mp3", ".css", ".js"
)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

def clean_url(url: str) -> str:
    url, _ = urldefrag(url)
    return url.rstrip("/")

def safe_filename(url: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", url)[:180] + ".json"

def is_internal(url: str, base_netloc: str) -> bool:
    try:
        return urlparse(url).netloc == base_netloc
    except Exception:
        return False

def should_skip(url: str) -> bool:
    return url.lower().endswith(SKIP_EXT)

def is_valid_page(title: str, text: str) -> bool:
    """Detects soft-404s, platform errors (Vercel/Netlify), and empty pages."""
    t_lower = title.lower()
    if any(x in t_lower for x in ["404", "not found", "page not found", "deployment error"]):
        return False
    
    if len(text) < 200:
        return False
        
    text_lower = text.lower()
    if "this page could not be found" in text_lower:
        return False
        
    return True

def extract_content(html: str):
    """Extracts clean text and links using BeautifulSoup."""
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove non-content tags
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside", "svg"]):
        tag.decompose()
        
    # Preserve structure with newlines
    text = soup.get_text("\n", strip=True)
    
    # Compress multiple newlines to max 2 (paragraphs)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    links = []
    for a in soup.select("a[href]"):
        href = a.get("href", "").strip()
        if href:
            links.append(href)
            
    return text, links

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    base_netloc = urlparse(BASE_URL).netloc
    
    queue = deque([clean_url(BASE_URL)])
    seen = set()
    saved_count = 0
    
    with sync_playwright() as p:
        # Launch with specific args to mimic real browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()
        
        pbar = tqdm(total=MAX_PAGES, desc="Crawling")
        
        while queue and saved_count < MAX_PAGES:
            url = clean_url(queue.popleft())
            
            if url in seen:
                continue
            seen.add(url)
            
            if should_skip(url) or not url.startswith("http") or not is_internal(url, base_netloc):
                continue
                
            try:
                # Optimized Wait Strategy
                # 1. domcontentloaded is faster/safer than networkidle for SPAs
                page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
                
                # 2. Fixed sleep for hydration/rendering (essential for Next.js/React)
                page.wait_for_timeout(WAIT_AFTER_LOAD_MS)
                
                # Extraction
                html = page.content()
                title = page.title() or ""
                text, raw_links = extract_content(html)
                
                # Validation
                if not is_valid_page(title, text):
                    continue
                
                # Save Data
                data = {
                    "url": url,
                    "title": title,
                    "text": text
                }
                
                out_path = os.path.join(OUT_DIR, safe_filename(url))
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                    
                saved_count += 1
                pbar.update(1)
                
                # Add new links
                for link in raw_links:
                    full_url = clean_url(urljoin(url, link))
                    if is_internal(full_url, base_netloc) and full_url not in seen:
                        queue.append(full_url)
                        
                time.sleep(DELAY_SEC)
                
            except Exception as e:
                # Silent continue on errors to keep crawler moving
                continue
                
        pbar.close()
        browser.close()
        print(f"Crawler finished. Saved {saved_count} valid pages.")

if __name__ == "__main__":
    main()
