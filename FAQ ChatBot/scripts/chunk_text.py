import os
import json
import re
from glob import glob

RAW_DIR = "data/raw"
OUT_PATH = "data/site_chunks.jsonl"

CHUNK_SIZE = 400    # Smaller chunks = more precise retrieval
OVERLAP = 50

def chunk_text(text: str):
    # Normalize excessive whitespace but KEEP newlines
    # text = " ".join(text.split())  <-- This was the bug
    text = re.sub(r'[ \t]+', ' ', text) # normalize spaces only
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    
    chunks = []
    step = CHUNK_SIZE - OVERLAP
    for i in range(0, len(text), step):
        chunk = text[i : i + CHUNK_SIZE].strip()
        if chunk:
            chunks.append(chunk)
    return chunks

def main():
    files = glob(os.path.join(RAW_DIR, "*.json"))
    total = 0
    with open(OUT_PATH, "w", encoding="utf-8") as out:
        for fp in files:
            with open(fp, "r", encoding="utf-8") as f:
                rec = json.load(f)
            url = rec.get("url","")
            title = rec.get("title","")
            text = rec.get("text","")
            if not text:
                continue

            for idx, ch in enumerate(chunk_text(text)):
                out.write(json.dumps({
                    "chunk_id": idx,
                    "source": url,
                    "title": title,
                    "text": ch
                }, ensure_ascii=False) + "\n")
                total += 1
    print(f"Wrote {total} chunks to {OUT_PATH}")

if __name__ == "__main__":
    main()
