
from sentiment_analyzer import analyze_sentiment

# Sample text for testing
sample_text = """
I absolutely love this application. 
The features are amazing and very helpful.
However, some parts are confusing.
The overall experience is good.
"""

# Analyze the text
result = analyze_sentiment(sample_text)

# Display results
print("\n========== SENTIMENT ANALYSIS ==========")

print("\nOverall Sentiment:")
print(result["overall_sentiment"])

print("\nInterpretation:")
print(result["interpretation"])

print("\nSentiment Distribution:")
for sentiment, count in result["sentiment_counts"].items():
    print(f"{sentiment}: {count}")

print("\nSentiment Percentages:")
for sentiment, percentage in result["sentiment_percentages"].items():
    print(f"{sentiment}: {percentage}%")

print("\nIndividual Sentence Results:")
for item in result["sentence_results"]:
    print(f"\nText: {item['text']}")
    print(f"Sentiment: {item['sentiment']}")
    print(f"Confidence: {item['confidence']}%")
    print(f"Scores: {item['scores']}")

print("\n========================================")
