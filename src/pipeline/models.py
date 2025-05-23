from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.pydantic_v1 import BaseModel, Field

# --- State Definition ---
class ProfileAnalysisState(TypedDict):
    username: str
    user_bio: str | None
    user_display_name: str | None
    user_profile_image_url: str | None
    recent_tweets: List[str] | None
    tweet_count_requested: int
    category_scores: Dict[str, Dict[str, Any]] | None
    mbti_result: Dict[str, str] | None 
    top_keywords: List[str] | None
    sentiment_scaled_score: float | None
    error: str | None

# --- Category Scorer Models ---
class CategoryScoreWithEvidence(BaseModel):
    category: str = Field(description="The relevant category that was identified and scored.")
    score: float = Field(description="The relevance score for this category, from 0 to 100.")
    evidence: List[str] = Field(description="A list of specific text segments from the input (bio or tweets) that support the score for this category.")

class CategoryScores(BaseModel):
    scores: List[CategoryScoreWithEvidence] = Field(description="A list of scores and evidence for ONLY the relevant categories identified in the text.")

# --- Keywords Extractor Model ---
class TopKeywords(BaseModel):
    keywords: List[str] = Field(description="A list of the top 3-5 keywords or hashtags that summarize the provided text.")

# --- MBTI Classifier Model ---
class MBTIResult(BaseModel):
    mbti_code: str = Field(description="The 4-letter MBTI code from the allowed list.")
    mbti_name: str = Field(description="The corresponding MBTI name from the allowed list (e.g., Logistician, Defender).")
    rationale: str = Field(description="A detailed rationale explaining why this MBTI type was chosen, based on the provided text.")

# --- Sentiment Analyzer Model ---
class SentimentDirectScaledScore(BaseModel):
    scaled_sentiment_score: float = Field(description="A single sentiment score from 0 (most negative) to 100 (most positive), with 50 representing neutral.") 