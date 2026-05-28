import os
import re
import streamlit as st
import google.generativeai as genai
from streamlit_extras.add_vertical_space import add_vertical_space
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
import requests
from PyPDF2 import PdfReader
from warnings import filterwarnings

# 🔥 NEW (Lottie)
from streamlit_lottie import st_lottie
import requests as rq

# 🔥 RAG + Evaluation imports
from rag import build_index, retrieve
from evaluation import evaluate

from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content,
)

from pdfminer.high_level import extract_text
from parse import parse_with_ollama


# ========= LOTTIE LOADER =========
def load_lottie(url):
    r = rq.get(url)
    return r.json() if r.status_code == 200 else None


lottie_ai = load_lottie("https://assets2.lottiefiles.com/packages/lf20_kyu7xb1v.json")


# ========== Setup ==========
filterwarnings("ignore")
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(page_title='Multi Scrapper AI', layout="wide")

# ========= HEADER =========
col1, col2 = st.columns([1, 2])

with col1:
    if lottie_ai:
        st_lottie(lottie_ai, height=150)

with col2:
    st.markdown("<h1 style='color:#38bdf8;'>🚀 Multiscraper AI</h1>", unsafe_allow_html=True)
    st.markdown("AI-powered Multimodal Content Extraction & Summarization")

add_vertical_space(1)

tool_choice = st.sidebar.radio(
    "Choose a Tool",
    ["YouTube Video Summarizer", "PDF/Website Parser"]
)

# ===========================
# 🎥 YOUTUBE FUNCTIONS
# ===========================

def extract_languages(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        available_transcripts = [t.language_code for t in transcript_list]
        return list(set(available_transcripts)), {lang: lang for lang in available_transcripts}
    except Exception as e:
        st.error(f"Error fetching languages: {e}")
        return [], {}


def extract_transcript(video_id, language):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id, languages=[language])
        return " ".join([t.text for t in transcript])
    except Exception as e:
        st.error(f"Transcript error: {e}")
        return ""


def generate_summary(transcript_text):
    transcript_text = transcript_text[:8000]

    try:
        model = genai.GenerativeModel(model_name='gemini-2.0-flash')
        response = model.generate_content("Summarize:\n" + transcript_text)
        return response.text

    except Exception:
        try:
            from langchain_ollama import OllamaLLM
            model = OllamaLLM(model="llama3")
            return model.invoke(transcript_text)
        except Exception as e:
            st.error(f"Summary error: {e}")
            return ""


# ===========================
# 🎥 YOUTUBE UI
# ===========================

if tool_choice == "YouTube Video Summarizer":

    st.subheader("🎥 YouTube Video Summarizer")
    video_link = st.text_input("Enter YouTube Video URL")

    if video_link:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", video_link)
        video_id = match.group(1) if match else None

        if video_id:
            langs, lang_map = extract_languages(video_id)

            if langs:
                selected = st.selectbox("Select Language", langs)

                if st.button("Summarize Video"):
                    
                    st.image(f'https://img.youtube.com/vi/{video_id}/0.jpg', use_container_width=True)

                    progress = st.progress(0)

                    for i in range(100):
                        progress.progress(i + 1)

                    transcript = extract_transcript(video_id, selected)

                    if transcript:
                        summary = generate_summary(transcript)

                        # 🔥 Chat style
                        st.chat_message("assistant").write(summary)

            else:
                st.warning("No transcripts available.")


# ===========================
# 📄 PDF / WEBSITE UI
# ===========================

elif tool_choice == "PDF/Website Parser":

    st.subheader("📄 PDF / Website Scraper + AI Parser")

    parser_mode = st.radio("Choose Input Type", ["PDF File", "Website URL"])

    if parser_mode == "Website URL":
        url = st.text_input("Enter Website URL")

        if st.button("Scrape Website"):

            progress = st.progress(0)

            html = scrape_website(url)
            progress.progress(30)

            body = extract_body_content(html)
            cleaned = clean_body_content(body)
            progress.progress(60)

            st.session_state.dom_content = cleaned

            chunks = split_dom_content(cleaned)
            build_index(chunks)

            progress.progress(100)
            st.success("Website scraped & indexed")

    elif parser_mode == "PDF File":
        uploaded = st.file_uploader("Upload PDF", type="pdf")

        if uploaded:

            progress = st.progress(0)

            text = extract_text(uploaded)
            progress.progress(50)

            st.session_state.dom_content = text

            chunks = split_dom_content(text)
            build_index(chunks)

            progress.progress(100)
            st.success("PDF processed & indexed")

    # 🔥 Chat-style Query
    if "dom_content" in st.session_state:

        query = st.chat_input("Ask something about the content...")

        if query:

            st.chat_message("user").write(query)

            retrieved = retrieve(query)
            context = " ".join(retrieved)

            result = parse_with_ollama([context], query)

            st.chat_message("assistant").write(result)

            try:
                reference = context[:200]
                score = evaluate(reference, result)

                st.markdown("### 📊 ROUGE Score")
                st.write(score)

            except Exception as e:
                st.warning(f"Evaluation error: {e}")