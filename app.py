# app.py
import streamlit as st
from chatbot.retriever import WebsiteTfidfRetriever
import re

st.set_page_config(
    page_title="Website ChatBot",
    page_icon="💬",
    layout="centered"
)

st.title("💬 Website ChatBot")
st.caption(
    "Ask questions and get answers strictly from the crawled website content."
)

# Load retriever once
@st.cache_resource
def get_retriever():
    return WebsiteTfidfRetriever(model_dir="models").load()

retriever = get_retriever()

import re
from chatbot.preprocess import facts  # User-defined constants

# ... existing retrieval logic ...

def get_fact(query: str) -> str:
    """Check if query matches a hardcoded fact."""
    q = query.lower()
    if "name" in q and ("website" in q or "company" in q):
        return f"The website name is {facts.get('website_name', 'RAS Innovatech')}."
    if "email" in q or "contact" in q:
        return f"You can contact us at {facts.get('contact_email', 'support@rasinnovatech.com')}."
    if "domain" in q or "url" in q:
        return f"The domain is {facts.get('domain', 'www.rasinnovatech.com')}."
    return ""

def format_response(query: str, text: str, title: str) -> str:
    """
    Formats the answer based on question intent and text structure.
    """
    # 0. Check Hardcoded Facts first
    fact = get_fact(query)
    if fact:
        return fact

    q_lower = query.lower()
    
    # 1. Intent: Identity via Title (fallback if fact missing)
    if any(k in q_lower for k in ["name", "who are you", "what is this", "company"]):
        if title and len(title) < 100:
            return f"The company is **{title}**.\n\n{text[:200]}..."
    
    # 2. Intent: Lists / Procedures (Services, Steps, How to)
    if any(k in q_lower for k in ["service", "product", "technolog", "feature", "offer", "stack", "how to", "step", "procedure"]):
        lines = text.split('\n')
        # Filter for list-like items or headers
        formatted = [line.strip() for line in lines if len(line.strip()) > 3]
        
        is_procedure = any(k in q_lower for k in ["how to", "step", "procedure"])
        
        if formatted:
            if is_procedure:
                 # Bullets for steps are better
                 items = [f"- {item}" for item in formatted[:5]]
                 return "\n".join(items)
            else:
                 # Comma-separated for services (concise sentence style)
                 # Take top 6 items
                 items = [item.rstrip(':') for item in formatted[:6] if not item.endswith(':')]
                 if items:
                     return f"We provide: {', '.join(items)}."

    # 3. Default: Summarize (1-2 sentences)
    # Split into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    # Filter stopwords for scoring
    common_words = {"what", "is", "are", "the", "a", "an", "how", "do", "you", "does", "provide", "offer", "can", "i"}
    query_words = set(re.findall(r'\w+', q_lower)) - common_words
    
    scored_sentences = []
    for s in sentences:
        s_words = set(re.findall(r'\w+', s.lower()))
        # Score = number of unique keywords found in this sentence
        score = len(query_words & s_words)
        if score > 0: # Must have at least one keyword
            scored_sentences.append((score, s))
    
    # Sort by score descending
    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    
    # Return top 1-2 sentences
    if scored_sentences:
        best_sentence = scored_sentences[0][1]
        
        # If we have a second good sentence and total length is short, add it
        if len(scored_sentences) > 1:
            second_best = scored_sentences[1][1]
            if len(best_sentence) + len(second_best) < 300:
                return f"{best_sentence} {second_best}"
        
        return best_sentence
        
    # Fallback: return short chunk or first sentence
    if len(text) < 150:
        return text
    
    return sentences[0] if sentences else text

# Session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear chat button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🗑 Clear"):
        st.session_state.messages = []
        st.rerun()

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input (fixed at bottom)
user_input = st.chat_input("Type your question here...")

if user_input:
    # User message (RIGHT side)
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    with st.chat_message("user"):
        st.markdown(user_input)

    # Bot response (LEFT side)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            results = retriever.query(
                user_input,
                threshold=0.08,  # Slightly higher for precision
                top_k=3
            )

            if not results:
                reply = (
                    "I couldn't find specific information on the website about that. "
                    "You might want to check the 'Contact' page or ask differently."
                )
            else:
                # Get best match
                raw_text = results[0].text
                doc_title = results[0].title
                
                # Apply smart formatting
                reply = format_response(user_input, raw_text, doc_title)

            st.markdown(reply)

    # Save bot reply
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })
