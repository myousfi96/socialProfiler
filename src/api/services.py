import os
import sys
from typing import Dict, Any
from fastapi import HTTPException

# --- PATH MODIFICATION FOR SIBLING MODULE IMPORT ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Import from pipeline
from src.pipeline import create_profiling_graph
from src.pipeline.models import ProfileAnalysisState

# Import Langfuse callback handler
from langfuse.callback import CallbackHandler

# Global variable to store the compiled graph
profiling_graph_app = None

def initialize_graph():
    """Initialize and compile the LangGraph application."""
    global profiling_graph_app
    
    try:
        profiling_graph_app = create_profiling_graph().compile()
        print("LangGraph application compiled successfully.")
        return True
    except Exception as e:
        print(f"Error initializing LangGraph: {e}")
        return False

def get_graph_app():
    """Get the compiled graph application, initializing if needed."""
    global profiling_graph_app
    
    if profiling_graph_app is None:
        initialize_graph()
    
    return profiling_graph_app

async def analyze_profile_service(username: str, tweet_count: int) -> Dict[str, Any]:
    """
    Service function to analyze a profile using the LangGraph pipeline.
    
    Args:
        username: The Twitter/X username to analyze
        tweet_count: Number of tweets to fetch for analysis
        
    Returns:
        The final state from the graph execution
        
    Raises:
        HTTPException: If the graph is not available or analysis fails
    """
    graph_app = get_graph_app()
    
    if not graph_app:
        raise HTTPException(
            status_code=503, 
            detail="Graph application is not available due to initialization error."
        )

    print(f"Starting analysis for username: {username}")

    # Prepare initial state
    initial_state: ProfileAnalysisState = {
        "username": username,
        "user_bio": None, 
        "user_display_name": None,
        "user_profile_image_url": None,
        "recent_tweets": None,
        "tweet_count_requested": tweet_count,
        "category_scores": None,
        "mbti_result": None,
        "top_keywords": None,
        "sentiment_scaled_score": None,
        "error": None
    }

    try:
        # Configure Langfuse callback
        langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")  # Use default if not set
        langfuse_handler = None
        callbacks = []
        
        if langfuse_public_key and langfuse_secret_key:
            try:
                langfuse_handler = CallbackHandler(
                    public_key=langfuse_public_key,
                    secret_key=langfuse_secret_key,
                    host=langfuse_host,
                    session_id=f"profile-analysis-{username}"  # Create a session per user analysis
                )
                callbacks.append(langfuse_handler)
                print(f"Langfuse callback configured for session: profile-analysis-{username}")
            except Exception as e:
                print(f"Warning: Failed to initialize Langfuse callback: {e}")
        else:
            print("Langfuse credentials not found in environment variables. Running without Langfuse tracking.")
        
        # Invoke the graph asynchronously with callbacks
        config = {"callbacks": callbacks} if callbacks else {}
        final_state = await graph_app.ainvoke(initial_state, config=config)
        print(f"Graph invocation complete for user: {username}")

        # Check for errors in the final state
        if final_state.get("error"):
            if "Data fetching failed" in final_state["error"] or "Username not provided" in final_state["error"]:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Could not retrieve data for user {username}: {final_state['error']}"
                )
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Analysis pipeline error: {final_state['error']}"
                )

        return final_state
        
    except HTTPException:
        # Re-raise HTTP exceptions directly
        raise
    except Exception as e:
        print(f"Unhandled error during analysis for {username}: {type(e).__name__} - {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred: {str(e)}"
        ) 