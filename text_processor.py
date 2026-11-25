
"""
SentimentAI - Text Processing Module

Responsibilities:
- Extract text from PDF files using PyMuPDF
- Clean and preprocess text
- Calculate word, stop word, meaningful word, character, and sentence counts
- Generate a short text summary
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
        "spaCy English model is missing. "
        "Run: python -m spacy download en_core_web_sm"
    ) from exc

try:
    STOP_WORDS = set(stopwords.words("english"))
except LookupError as exc:
    raise RuntimeError(
        "NLTK stopwords are missing. Run: python setup_nlp.py"
    ) from exc


# Keep meaningful negation words because they can change sentiment.
# Example: "not good" should not become "good".
STOP_WORDS.difference_update({"no", "nor", "not", "never", "n't"})

WORD_PATTERN = re.compile(
    r"\b[\w]+(?:['’][\w]+)?\b",
    re.UNICODE
)


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract selectable text from every page of a PDF."""

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    pages: list[str] = []

    with fitz.open(path) as document:

        if document.is_encrypted:
            raise ValueError("The PDF is password-protected.")

        for page in document:
            page_text = page.get_text("text")

            if page_text.strip():
                pages.append(page_text)

    extracted = "\n".join(pages).strip()

    if not extracted:
        raise ValueError(
            "No selectable text was found. The PDF may contain scanned "
            "images; OCR would be needed to read it."
        )

    return extracted


def clean_text(text: str) -> str:
    """
    Normalize text for NLP.
    Removes URLs, HTML-like tags, punctuation, and digits.
    The original text is not modified.
    """

    if not isinstance(text, str):
        raise TypeError("Text input must be a string.")

    cleaned = text.lower()

    cleaned = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        cleaned
    )

    cleaned = re.sub(r"<[^>]+>", " ", cleaned)

    cleaned = re.sub(
        r"[^\w\s'’]",
        " ",
        cleaned,
        flags=re.UNICODE
    )

    cleaned = re.sub(r"[_\d]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def generate_summary(
    sentences: list[str],
    processed_tokens: list[str],
    max_sentences: int = 3
) -> str:
    """
    Generate an extractive summary by selecting sentences
    containing the most frequent meaningful words.

    The original sentences are preserved.
    """

    if not sentences:
        return ""

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    frequencies = Counter(processed_tokens)

    if not frequencies:
        return " ".join(sentences[:max_sentences])

    sentence_scores = []

    for index, sentence in enumerate(sentences):

        sentence_tokens = NLP(sentence)

        words = [
            token.lemma_.lower()
            for token in sentence_tokens
            if (
                token.is_alpha
                and len(token.lemma_) > 1
                and token.lemma_.lower() not in STOP_WORDS
            )
        ]

        if words:
            score = sum(
                frequencies.get(word, 0)
                for word in words
            ) / len(words)
        else:
            score = 0

        sentence_scores.append((index, score, sentence))

    # Select the highest-scoring sentences.
    selected = sorted(
        sentence_scores,
        key=lambda item: item[1],
        reverse=True
    )[:max_sentences]

    # Restore the original sentence order.
    selected.sort(key=lambda item: item[0])

    return " ".join(
        sentence for _, _, sentence in selected
    )


def preprocess_text(text: str) -> dict[str, Any]:
    """
    Process text and return metrics plus data for a sentiment classifier.

    Counts:
    - total_words: words in the original text
    - total_stop_words: words matching the English stop word list
    - total_meaningful_words: words excluding stop words
    - total_sentences: spaCy sentence count
    - total_characters: all characters, including spaces and punctuation
    """

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please provide non-empty text.")

    doc = NLP(text)

    # Count words from the original text.
    original_words = WORD_PATTERN.findall(text)

    # Calculate stop words and meaningful words.
    stop_word_count = sum(
        1
        for word in original_words
        if word.lower() in STOP_WORDS
    )

    meaningful_word_count = (
        len(original_words) - stop_word_count
    )

    # Extract sentences.
    sentence_list = [
        sentence.text.strip()
        for sentence in doc.sents
        if sentence.text.strip()
    ]

    # Normalize text.
    normalized = clean_text(text)
    normalized_doc = NLP(normalized)

    # Lemmatized tokens for frequency analysis and classification.
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

    # Frequent words.
    frequencies = Counter(processed_tokens)

    frequent_words = [
        {"word": word, "count": count}
        for word, count in frequencies.most_common(10)
    ]

    # Extract noun phrases and named entities as candidate keywords.
    candidates: Counter[str] = Counter()

    for chunk in doc.noun_chunks:

        phrase_words = [
            token.lemma_.lower()
            for token in chunk
            if (
                token.is_alpha
                and token.lemma_.lower() not in STOP_WORDS
            )
        ]

        phrase = " ".join(phrase_words).strip()

        if phrase and len(phrase) > 2:
            candidates[phrase] += 1

    for entity in doc.ents:

        entity_text = entity.text.strip()

        if (
            entity_text
            and entity.label_ not in {
                "CARDINAL",
                "ORDINAL",
                "QUANTITY"
            }
        ):
            candidates[entity_text.lower()] += 1

    # Use frequent content words as fallback keywords.
    if not candidates:

        for word, count in frequencies.most_common(10):
            candidates[word] = count

    keywords = [
        {"keyword": phrase, "count": count}
        for phrase, count in candidates.most_common(10)
    ]

    # Generate the text summary.
    summary = generate_summary(
        sentence_list,
        processed_tokens
    )

    # Prepare text for the downstream sentiment classifier.
    classification_text = " ".join(processed_tokens)

    return {
        "total_words": len(original_words),
        "total_stop_words": stop_word_count,
        "total_meaningful_words": meaningful_word_count,
        "total_sentences": len(sentence_list),
        "total_characters": len(text),
        "summary": summary,
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
