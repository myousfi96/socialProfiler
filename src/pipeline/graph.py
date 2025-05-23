import os
import sys
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Load environment variables
load_dotenv()

# Import from refactored modules
from .constants import OPENAI_API_KEY
from .models import ProfileAnalysisState
from .nodes import (
    data_fetcher_node,
    category_scorer_node,
    mbti_classifier_node,
    keywords_extractor_node,
    sentiment_analyzer_node
)

# Validate API key
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# --- Graph Definition ---
def create_profiling_graph() -> StateGraph:
    """
    Creates and configures the LangGraph for profile analysis.
    """
    workflow = StateGraph(ProfileAnalysisState)

    # Add nodes
    workflow.add_node("data_fetcher", data_fetcher_node)
    workflow.add_node("category_scorer", category_scorer_node)
    workflow.add_node("mbti_classifier", mbti_classifier_node)
    workflow.add_node("keywords_extractor", keywords_extractor_node)
    workflow.add_node("sentiment_analyzer", sentiment_analyzer_node)

    # Define edges
    workflow.set_entry_point("data_fetcher")
    workflow.add_edge("data_fetcher", "category_scorer")
    workflow.add_edge("category_scorer", "mbti_classifier")
    workflow.add_edge("mbti_classifier", "keywords_extractor")
    workflow.add_edge("keywords_extractor", "sentiment_analyzer")
    workflow.add_edge("sentiment_analyzer", END)

    return workflow
