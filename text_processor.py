"""
SentimentAI - Text Processing Module
Responsibilities:
- Extract text from PDF files using PyMuPDF
- Clean and preprocess text
- Calculate word, character, and sentence counts
- Identify frequent words and important keywords
- Prepare cleaned text for a separate sentiment classifier

This module does NOT perform sentiment classification.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import nltk
import spacy
from nltk.corpus import stopwords

# Run setup_nlp.py once before using this module.
try:
    NLP = spacy.load("en_core_web_sm")
except OSError as exc:
    raise RuntimeError(
        "spaCy English model is missing. Run: python -m spacy download en_core_web_sm"
    ) from exc

try:
    STOP_WORDS = set(stopwords.words("english"))
except LookupError as exc:
    raise RuntimeError(
        "NLTK stopwords are missing. Run: python setup_nlp.py"
    ) from exc

# Keep meaningful negation words because they can change sentiment:
# "not good" should not become "good".
STOP_WORDS.difference_update({"no", "nor", "not", "never", "n't"})

WORD_PATTERN = re.compile(r"\b[\w]+(?:['’][\w]+)?\b", re.UNICODE)


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract selectable text from every page of a PDF."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    pages: list[str] = []
    with fitz.open(path) as document:
        if document.is_encrypted:
            raise ValueError("The PDF is password-protected.")

        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text("text")
            if page_text.strip():
                pages.append(page_text)

    extracted = "\n".join(pages).strip()
    if not extracted:
        raise ValueError(
            "No selectable text was found. The PDF may contain scanned images; "
            "OCR would be needed to read it."
        )
    return extracted


def clean_text(text: str) -> str:
    """
    Normalize text for NLP.
    Removes URLs, HTML-like tags, and most punctuation while preserving
    apostrophes and negation words. The original text is not modified.
    """
    if not isinstance(text, str):
        raise TypeError("Text input must be a string.")

    cleaned = text.lower()
    cleaned = re.sub(r"https?://\S+|www\.\S+", " ", cleaned)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"[^\w\s'’]", " ", cleaned, flags=re.UNICODE)
    cleaned = re.sub(r"[_\d]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def preprocess_text(text: str) -> dict[str, Any]:
    """
    Process text and return metrics plus data for a sentiment classifier.

    Counts are calculated from the original text where appropriate:
    - total_characters: all characters, including spaces and punctuation
    - total_words: words in the original text
    - total_sentences: spaCy sentence count
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please provide non-empty text.")

    doc = NLP(text)

    original_words = WORD_PATTERN.findall(text)
    sentence_list = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    normalized = clean_text(text)
    normalized_doc = NLP(normalized)

    # Lemmatized tokens are useful for frequency analysis and classification.
    processed_tokens: list[str] = []
    for token in normalized_doc:
        lemma = token.lemma_.lower().strip()
        if (
            token.is_alpha
            and len(lemma) > 1
            and lemma not in STOP_WORDS
            and lemma not in NLP.Defaults.stop_words
        ):
            processed_tokens.append(lemma)

    frequencies = Counter(processed_tokens)
    frequent_words = [
        {"word": word, "count": count}
        for word, count in frequencies.most_common(10)
    ]

    # Extract noun phrases and named entities as candidate keywords.
    # Filter stopwords and very short candidates; preserve readable phrases.
    candidates: Counter[str] = Counter()

    for chunk in doc.noun_chunks:
        phrase_words = [
            token.lemma_.lower()
            for token in chunk
            if token.is_alpha and token.lemma_.lower() not in STOP_WORDS
        ]
        phrase = " ".join(phrase_words).strip()
        if phrase and len(phrase) > 2:
            candidates[phrase] += 1

    for entity in doc.ents:
        entity_text = entity.text.strip()
        if entity_text and entity.label_ not in {"CARDINAL", "ORDINAL", "QUANTITY"}:
            candidates[entity_text.lower()] += 1

    # If noun chunks/entities are sparse, use frequent content words as fallback.
    if not candidates:
        for word, count in frequencies.most_common(10):
            candidates[word] = count

    keywords = [
        {"keyword": phrase, "count": count}
        for phrase, count in candidates.most_common(10)
    ]

    # Use cleaned, stopword-filtered text for the downstream sentiment model.
    classification_text = " ".join(processed_tokens)

    return {
        "total_words": len(original_words),
        "total_sentences": len(sentence_list),
        "total_characters": len(text),
        "frequent_words": frequent_words,
        "keywords": keywords,
        "cleaned_text": normalized,
        "processed_tokens": processed_tokens,
        "classification_text": classification_text,
        "sentences": sentence_list,
    }


def analyze_text(text: str) -> dict[str, Any]:
    """Public entry point for text input."""
    return preprocess_text(text)


def analyze_pdf(pdf_path: str | Path) -> dict[str, Any]:
    """Public entry point for PDF input."""
    extracted_text = extract_text_from_pdf(pdf_path)
    result = preprocess_text(extracted_text)
    result["source"] = "pdf"
    result["extracted_text"] = extracted_text
    return result
