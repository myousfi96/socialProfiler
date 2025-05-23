import os
from langchain_openai import ChatOpenAI
from .models import CategoryScores, MBTIResult, TopKeywords, SentimentDirectScaledScore
from .constants import OPENAI_API_KEY, MODEL_NAME

def get_category_scorer_llm():
    """Returns a configured LLM for category scoring with structured output."""
    return ChatOpenAI(
        model=MODEL_NAME,
        temperature=0,
        api_key=OPENAI_API_KEY
    ).with_structured_output(CategoryScores)

def get_mbti_classifier_llm():
    """Returns a configured LLM for MBTI classification with structured output."""
    return ChatOpenAI(
        model=MODEL_NAME, 
        temperature=0.1, 
        api_key=OPENAI_API_KEY
    ).with_structured_output(MBTIResult)

def get_keywords_extractor_llm():
    """Returns a configured LLM for keyword extraction with structured output."""
    return ChatOpenAI(
        model=MODEL_NAME,
        temperature=0,
        api_key=OPENAI_API_KEY
    ).with_structured_output(TopKeywords)

def get_sentiment_analyzer_llm():
    """Returns a configured LLM for sentiment analysis with structured output."""
    return ChatOpenAI(
        model=MODEL_NAME,
        temperature=0,
        api_key=OPENAI_API_KEY
    ).with_structured_output(SentimentDirectScaledScore) 