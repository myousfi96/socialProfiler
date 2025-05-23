from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class AnalyzeRequest(BaseModel):
    """Request model for profile analysis."""
    username: str
    tweet_count: int = Field(10, ge=1, le=50, description="Number of tweets to analyze (1-50)")

class AnalysisResponse(BaseModel):
    """Response model for profile analysis results."""
    username: str
    user_bio: Optional[str] = None
    user_display_name: Optional[str] = None
    user_profile_image_url: Optional[str] = None
    recent_tweets: Optional[List[str]] = None
    category_scores: Optional[Dict[str, Dict[str, Any]]] = None
    mbti_result: Optional[Dict[str, str]] = None
    top_keywords: Optional[List[str]] = None
    sentiment_scaled_score: Optional[float] = None
    error: Optional[str] = None 