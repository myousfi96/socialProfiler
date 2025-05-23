import os

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
ANALYZE_ENDPOINT = f"{API_BASE_URL}/analyze"

# UI Configuration
PAGE_TITLE = "Social Profiler"
PAGE_LAYOUT = "wide"

# Sentiment Analysis Color Scheme
SENTIMENT_COLORS = [
    (0, 33.33, "#dc3545"),     # Negative - Red
    (33.33, 66.66, "#ffc107"), # Neutral - Yellow
    (66.66, 100, "#28a745")    # Positive - Green
] 