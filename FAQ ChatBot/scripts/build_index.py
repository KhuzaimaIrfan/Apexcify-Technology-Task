import sys
import os

# Ensure we can import from local modules
sys.path.append(os.getcwd())

from chatbot.retriever import WebsiteTfidfRetriever

def main():
    print("Building index using WebsiteTfidfRetriever...")
    retriever = WebsiteTfidfRetriever(
        model_dir="models",
        chunks_path="data/site_chunks.jsonl"
    )
    retriever.build_index()
    print("Index built successfully in models/")

if __name__ == "__main__":
    main()
