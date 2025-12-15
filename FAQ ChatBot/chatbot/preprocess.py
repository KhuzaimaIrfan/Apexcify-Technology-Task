# chatbot/preprocess.py
import re

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer

    _NLTK_OK = True
except Exception:
    _NLTK_OK = False

facts = {
    "website_name": "RAS Innovatech",
    "domain": "www.rasinnovatech.com",
    "contact_email": "support@rasinnovatech.com"
}

def _ensure_nltk():
    if not _NLTK_OK:
        return
    for pkg, path in [
        ("punkt", "tokenizers/punkt"),
        ("stopwords", "corpora/stopwords"),
        ("wordnet", "corpora/wordnet"),
    ]:
        try:
            nltk.data.find(path)
        except Exception:
            nltk.download(pkg, quiet=True)


_ensure_nltk()

if _NLTK_OK:
    _STOPWORDS = set(stopwords.words("english"))
    _LEMM = WordNetLemmatizer()


def preprocess_text(text: str) -> str:
    """
    Preprocessing for TF-IDF retrieval:
    - lowercase
    - remove punctuation/special characters
    - normalize whitespace
    - optional NLTK: tokenization, stopwords removal, lemmatization
    """
    if not text:
        return ""

    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if not _NLTK_OK:
        return text

    tokens = nltk.word_tokenize(text)
    tokens = [t for t in tokens if t not in _STOPWORDS and len(t) > 1]
    tokens = [_LEMM.lemmatize(t) for t in tokens]
    return " ".join(tokens)
