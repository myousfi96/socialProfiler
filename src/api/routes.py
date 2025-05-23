from fastapi import APIRouter, Depends

from .models import AnalyzeRequest, AnalysisResponse
from .services import analyze_profile_service

router = APIRouter(tags=["analysis"])

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_profile(request: AnalyzeRequest):
    """
    Analyzes an X profile by fetching bio and recent tweets, then processing them through a LangGraph pipeline.
    
    Returns a JSON object with persona insights, category scores, MBTI classification, keywords, 
    and sentiment analysis.
    """
    # Call the service function to perform the analysis
    final_state = await analyze_profile_service(
        username=request.username,
        tweet_count=request.tweet_count
    )
    
    # Construct the response from the final state
    response_data = AnalysisResponse(
        username=final_state.get("username", request.username),
        user_bio=final_state.get("user_bio"),
        user_display_name=final_state.get("user_display_name"),
        user_profile_image_url=final_state.get("user_profile_image_url"),
        recent_tweets=final_state.get("recent_tweets"),
        category_scores=final_state.get("category_scores"),
        mbti_result=final_state.get("mbti_result"),
        top_keywords=final_state.get("top_keywords"),
        sentiment_scaled_score=final_state.get("sentiment_scaled_score"),
        error=final_state.get("error")
    )
    
    return response_data 