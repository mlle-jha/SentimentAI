
"""
SentimentAI - Sentiment Analysis Module

Model: DistilBERT fine-tuned for 3-class sentiment analysis.
Classes: POSITIVE, NEGATIVE, NEUTRAL
"""

from transformers import pipeline
from collections import Counter


# PRETRAINED MODEL
MODEL_NAME = "iam-tsr/distilbert-finetuned-sentiment-analysis"

# Load the model once and reuse it.
classifier = None


def load_model():
    """Load the pretrained sentiment analysis model."""
    global classifier

    if classifier is None:
        print("Loading sentiment analysis model...")

        classifier = pipeline(
            "text-classification",
            model=MODEL_NAME,
            tokenizer=MODEL_NAME,
            device=-1
        )

        print("Sentiment model loaded successfully!")

    return classifier


def analyze_sentiment(text):
    """Classify text and calculate sentiment distribution."""

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please provide non-empty text.")

    model = load_model()

    # Split text into individual sentences.
    sentences = [
        sentence.strip()
        for sentence in text.replace("\n", " ").split(".")
        if sentence.strip()
    ]

    # Run sentiment classification.
    predictions = model(
        sentences,
        truncation=True,
        max_length=512,
        top_k=None
    )

    results = []
    sentiment_counts = Counter()

    score_totals = {
        "POSITIVE": 0.0,
        "NEGATIVE": 0.0,
        "NEUTRAL": 0.0
    }

    for sentence, scores in zip(sentences, predictions):

        # Get the highest scoring sentiment.
        best_prediction = max(scores, key=lambda item: item["score"])

        sentiment = best_prediction["label"].upper()
        confidence = best_prediction["score"]

        sentiment_counts[sentiment] += 1

        for item in scores:
            label = item["label"].upper()

            if label in score_totals:
                score_totals[label] += item["score"]

        results.append({
            "text": sentence,
            "sentiment": sentiment,
            "confidence": round(confidence * 100, 2),
            "scores": {
                item["label"].upper(): round(item["score"] * 100, 2)
                for item in scores
            }
        })

    total = len(sentences)

    # Calculate sentiment percentages.
    percentages = {
        sentiment: round(
            sentiment_counts[sentiment] / total * 100, 2
        )
        for sentiment in score_totals
    }

    # Calculate average model scores.
    average_scores = {
        sentiment: round(score_totals[sentiment] / total * 100, 2)
        for sentiment in score_totals
    }

    # Determine overall sentiment.
    highest_count = max(sentiment_counts.values())

    dominant_sentiments = [
        sentiment
        for sentiment, count in sentiment_counts.items()
        if count == highest_count
    ]

    if len(dominant_sentiments) > 1:
        overall_sentiment = "MIXED"
        interpretation = (
            "The text contains a balanced mixture of different sentiments."
        )
    else:
        overall_sentiment = dominant_sentiments[0]
        dominant_percentage = percentages[overall_sentiment]

        interpretation = (
            f"The overall sentiment is {overall_sentiment.lower()}, "
            f"with {dominant_percentage}% of sentences expressing "
            f"this sentiment."
        )

    return {
        "overall_sentiment": overall_sentiment,
        "interpretation": interpretation,
        "total_sentences": total,
        "sentiment_counts": dict(sentiment_counts),
        "sentiment_percentages": percentages,
        "average_scores": average_scores,
        "sentence_results": results
    }
