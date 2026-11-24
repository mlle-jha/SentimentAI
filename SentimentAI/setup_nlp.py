"""One-time setup for SentimentAI text processing dependencies."""
import nltk

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("punkt_tab")
print("NLTK resources downloaded.")
print("Next, run: python -m spacy download en_core_web_sm")
