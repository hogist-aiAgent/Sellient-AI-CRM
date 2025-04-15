from nltk.sentiment import SentimentIntensityAnalyzer
#import nltk

#nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()

def analyze_sentiment(response_text):
    """Determine customer sentiment"""
    sentiment_score = sia.polarity_scores(response_text)["compound"]
    if sentiment_score >= 0.05:
        return "positive"
    elif sentiment_score <= -0.05:
        return "negative"
    else:
        return "neutral"
