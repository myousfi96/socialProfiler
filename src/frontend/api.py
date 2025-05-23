"""
API client functions for interacting with the backend.
"""
import requests
import streamlit as st
from .config import ANALYZE_ENDPOINT

def call_analyze_api(username: str, tweet_count: int):
    """
    Call the backend API to analyze a user profile.
    
    Args:
        username: X/Twitter username to analyze
        tweet_count: Number of recent tweets to analyze
        
    Returns:
        Analysis results JSON or None if request failed
    """
    try:
        resp = requests.post(
            ANALYZE_ENDPOINT, 
            json={"username": username, "tweet_count": tweet_count}
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            st.error(f"❌ User '{username}' not found or profile is private.")
        elif e.response.status_code == 503:
            st.error("❌ Analysis service temporarily unavailable.")
        else:
            st.error(f"❌ API Error: {e.response.status_code} – {e.response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {e}")
    
    return None 