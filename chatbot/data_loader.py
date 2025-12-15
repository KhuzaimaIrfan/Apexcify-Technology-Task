# chatbot/data_loader.py
import json
import os
from typing import Dict, List


def load_site_chunks_jsonl(path: str = "data/site_chunks.jsonl") -> List[Dict]:
    """
    Loads crawled + chunked website content.

    Expected JSONL format per line (minimum):
      {
        "source": "<url>",
        "chunk_id": <int>,
        "text": "<chunk text>"
      }

    Returns documents:
      {
        "doc_type": "site",
        "source": "<url>",
        "chunk_id": <int>,
        "text": "<chunk text>"
      }
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing {path}. Run your scripts first to generate site chunks."
        )

    docs: List[Dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)

            # Handle common alternate field names safely
            text = obj.get("text") or obj.get("content") or ""
            source = obj.get("source") or obj.get("url") or ""
            chunk_id = obj.get("chunk_id", 0)

            title = obj.get("title") or ""

            text = str(text).strip()
            source = str(source).strip()
            title = str(title).strip()

            # skip empty chunks
            if len(text) < 50:
                continue

            docs.append(
                {
                    "doc_type": "site",
                    "source": source,
                    "title": title,
                    "chunk_id": int(chunk_id) if str(chunk_id).isdigit() else 0,
                    "text": text,
                }
            )

    if not docs:
        raise RuntimeError(f"No valid chunks found in {path}. Check your chunking script output.")

    return docs
