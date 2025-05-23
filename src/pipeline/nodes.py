import asyncio
from typing import Dict, Any, List
from .models import ProfileAnalysisState
from .constants import CATEGORIES, MBTI_TYPES
from .prompts import (
    CATEGORY_SCORING_PROMPT_TEMPLATE,
    MBTI_CLASSIFICATION_PROMPT_TEMPLATE, 
    KEYWORD_EXTRACTION_PROMPT_TEMPLATE,
    SENTIMENT_ANALYSIS_PROMPT_TEMPLATE
)
from .llm import (
    get_category_scorer_llm,
    get_mbti_classifier_llm,
    get_keywords_extractor_llm,
    get_sentiment_analyzer_llm
)
from .utils import _prepare_prompt_inputs

# Import data fetchers
from src.data_fetcher.fetcher import fetch_user_details, fetch_recent_tweets

async def data_fetcher_node(state: ProfileAnalysisState) -> ProfileAnalysisState:
    """
    Fetches user bio, display name, profile image URL and recent tweets using functions from fetcher.py.
    This node is asynchronous.
    """
    print("--- Running Data Fetcher Node ---")
    username = state.get("username")
    tweet_count = state.get("tweet_count_requested", 10) # Default to 10 if not provided

    if not username:
        print("Error: Username not provided in state for data_fetcher_node.")
        return {
            **state,
            "user_bio": None,
            "user_display_name": None,
            "user_profile_image_url": None,
            "recent_tweets": [],
            "error": "Username not provided."
        }

    try:
        # Fetch user details (bio, display name, profile image url)
        user_details_result = await fetch_user_details(username)
        # Fetch recent tweets
        tweets_task = fetch_recent_tweets(username, n=tweet_count) # Use tweet_count from state
        
        recent_tweets_result = await tweets_task
        
        bio = None
        display_name = None
        profile_image_url = None

        if user_details_result:
            bio = user_details_result.get("bio")
            display_name = user_details_result.get("display_name")
            profile_image_url = user_details_result.get("profile_image_url")
            print(f"User details fetched: Bio_found={bool(bio)}, Name_found={bool(display_name)}, Image_found={bool(profile_image_url)}")
        else:
            print(f"Failed to fetch user details for {username}.")

        
        return {
            **state,
            "user_bio": bio,
            "user_display_name": display_name,
            "user_profile_image_url": profile_image_url,
            "recent_tweets": recent_tweets_result,
            "error": None
        }
    except Exception as e:
        return {
            **state,
            "user_bio": None,
            "user_display_name": None,
            "user_profile_image_url": None,
            "recent_tweets": [], # Ensure it's an empty list on error
            "error": f"Data fetching failed: {str(e)}"
        }

def category_scorer_node(state: ProfileAnalysisState) -> ProfileAnalysisState:
    """
    Identifies relevant categories, scores them, and extracts evidence using an LLM.
    """
    print("--- Running Category Scorer Node ---")
    user_bio = state.get("user_bio")
    recent_tweets = state.get("recent_tweets")
    
    if not user_bio and not (recent_tweets and len(recent_tweets) > 0):
        print("No text available for category scoring.")
        return {**state, "category_scores": {}, "error": "No text to analyze for categories."}

    prompt_inputs = _prepare_prompt_inputs(user_bio, recent_tweets)
    
    category_list_str = ", ".join(CATEGORIES)
    
    try:
        llm = get_category_scorer_llm()
        prompt = CATEGORY_SCORING_PROMPT_TEMPLATE.format_messages(
            categories=category_list_str,
            bio=prompt_inputs["bio"],
            tweets_text=prompt_inputs["tweets_text"]
        )
        
        response = llm.invoke(prompt) 
        
        scores_dict: Dict[str, Dict[str, Any]] = {}
        if response and response.scores:
            for item in response.scores:
                if item.category in CATEGORIES:
                    scores_dict[item.category] = {
                        "score": round(item.score, 2),
                        "evidence": item.evidence
                    }
                else:
                    print(f"Warning: LLM returned score for an unknown category: {item.category}")
        
        return {**state, "category_scores": scores_dict, "error": None}

    except Exception as e:
        print(f"Error during category scoring: {type(e).__name__} - {e}")
        return {**state, "category_scores": None, "error": f"LLM call failed: {str(e)}"}

def mbti_classifier_node(state: ProfileAnalysisState) -> ProfileAnalysisState:
    """
    Classifies the user's MBTI type based on their bio and tweets using an LLM.
    """
    print("--- Running MBTI Classifier Node ---")
    user_bio = state.get("user_bio")
    recent_tweets = state.get("recent_tweets")

    if not user_bio and not (recent_tweets and len(recent_tweets) > 0):
        print("No text available for MBTI classification.")
        return {**state, "mbti_result": None, "error": "No text to analyze for MBTI."}

    prompt_inputs = _prepare_prompt_inputs(user_bio, recent_tweets)

    try:
        llm = get_mbti_classifier_llm()
        prompt = MBTI_CLASSIFICATION_PROMPT_TEMPLATE.format_messages(
            mbti_types_list_json=str({k: {"name": v["name"], "portrait": v["portrait"]} for k, v in MBTI_TYPES.items()}),
            bio=prompt_inputs["bio"],
            tweets_text=prompt_inputs["tweets_text"]
        )
        response = llm.invoke(prompt) 
        
        if response and response.mbti_code in MBTI_TYPES:
            mbti_details = MBTI_TYPES[response.mbti_code]
            mbti_data = {
                "mbti_code": response.mbti_code,
                "mbti_name": response.mbti_name,
                "mbti_portrait": mbti_details["portrait"], 
                "rationale": response.rationale
            }
            print(f"MBTI Classification successful: {mbti_data['mbti_code']} ({mbti_data['mbti_name']})")
            return {**state, "mbti_result": mbti_data}
        else:
            print(f"MBTI classification failed or returned invalid code: {response}")
            error_msg = "MBTI classification failed or returned an invalid MBTI code."
            if response and response.mbti_code:
                error_msg += f" Received code: {response.mbti_code}"
            return {**state, "mbti_result": None, "error": error_msg}

    except Exception as e:
        print(f"Error during MBTI classification: {type(e).__name__} - {e}")
        return {**state, "mbti_result": None, "error": f"MBTI LLM call failed: {str(e)}"}

def keywords_extractor_node(state: ProfileAnalysisState) -> ProfileAnalysisState:
    """
    Extracts top 3-5 keywords or hashtags from the user's bio and tweets using an LLM.
    """
    print("--- Running Keywords Extractor Node ---")
    user_bio = state.get("user_bio")
    recent_tweets = state.get("recent_tweets")

    if not user_bio and not (recent_tweets and len(recent_tweets) > 0):
        print("No text available for keyword extraction.")
        # Return empty list instead of None to be consistent with expected output type
        return {**state, "top_keywords": [], "error": "No text to analyze for keywords."}

    prompt_inputs = _prepare_prompt_inputs(user_bio, recent_tweets)

    try:
        llm = get_keywords_extractor_llm()
        prompt = KEYWORD_EXTRACTION_PROMPT_TEMPLATE.format_messages(
            bio=prompt_inputs["bio"],
            tweets_text=prompt_inputs["tweets_text"]
        )
        response = llm.invoke(prompt)

        if response and response.keywords:
            # Ensure we only take up to 5 keywords as a safeguard, though prompt asks for 3-5
            keywords = response.keywords[:5]
            print(f"Keywords extracted: {keywords}")
            return {**state, "top_keywords": keywords, "error": None}
        else:
            print("No keywords extracted or LLM response was empty.")
            return {**state, "top_keywords": [], "error": None} # Return empty list

    except Exception as e:
        print(f"Error during keyword extraction: {type(e).__name__} - {e}")
        return {**state, "top_keywords": None, "error": f"Keyword extraction LLM call failed: {str(e)}"}

def sentiment_analyzer_node(state: ProfileAnalysisState) -> ProfileAnalysisState:
    """
    Analyzes the sentiment of the user's bio and tweets using an LLM,
    outputting a single scaled score from 0 (negative) to 100 (positive).
    """
    print("--- Running Sentiment Analyzer Node ---")
    user_bio = state.get("user_bio")
    recent_tweets = state.get("recent_tweets")

    if not user_bio and not (recent_tweets and len(recent_tweets) > 0):
        print("No text available for sentiment analysis.")
        return {**state, "sentiment_scaled_score": None, "error": "No text to analyze for sentiment."}

    prompt_inputs = _prepare_prompt_inputs(user_bio, recent_tweets)

    try:
        llm = get_sentiment_analyzer_llm()
        prompt = SENTIMENT_ANALYSIS_PROMPT_TEMPLATE.format_messages(
            bio=prompt_inputs["bio"],
            tweets_text=prompt_inputs["tweets_text"]
        )
        response = llm.invoke(prompt)

        if response and isinstance(response.scaled_sentiment_score, (float, int)):
            # Ensure the score is within the 0-100 range
            score = round(max(0.0, min(100.0, float(response.scaled_sentiment_score))), 2)
            print(f"Sentiment analysis successful. Scaled score: {score}")
            return {**state, "sentiment_scaled_score": score, "error": None}
        else:
            error_msg = "Sentiment analysis LLM response was empty, invalid, or did not contain a valid score."
            if response:
                error_msg += f" Received response: {response}"
            print(error_msg)
            return {**state, "sentiment_scaled_score": None, "error": error_msg}

    except Exception as e:
        print(f"Error during sentiment analysis: {type(e).__name__} - {e}")
        return {**state, "sentiment_scaled_score": None, "error": f"Sentiment analysis LLM call failed: {str(e)}"} 