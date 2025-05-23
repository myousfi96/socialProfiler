from typing import Dict, List

def _prepare_prompt_inputs(user_bio: str | None, recent_tweets: List[str] | None) -> Dict[str, str]:
    """
    Prepares bio and tweets for LLM prompts.
    
    Args:
        user_bio: User's biography text or None
        recent_tweets: List of recent tweets or None
        
    Returns:
        Dictionary with formatted bio and tweets text
    """
    prepared_bio = user_bio if user_bio else "Not provided"
    prepared_tweets_text = "\n".join([f"- {t}" for t in recent_tweets]) if recent_tweets else "None"
    return {"bio": prepared_bio, "tweets_text": prepared_tweets_text} 