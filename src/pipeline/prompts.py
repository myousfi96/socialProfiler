from langchain_core.prompts import ChatPromptTemplate
from .constants import MBTI_TYPES_JSON_STR

# --- Category Scorer Prompt ---
CATEGORY_SCORING_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", 
     """You are an expert text analyst. Your task is to analyze the provided text (a user's bio and their recent tweets) and identify relevant categories from the provided list.

Categories List: {categories}

For EACH category you identify as relevant based on the text:
1. Provide a relevance score from 0 to 100 (where 0 is not relevant, and 100 is highly relevant).
2. Extract and list specific text segments (evidence) from the user's bio or tweets that justify the score and relevance of that category. These segments should be direct quotes.

If no categories are relevant, return an empty list of scores.
Output the results in the requested JSON format, including only the categories you deemed relevant.
"""),
    ("human", "Please analyze the following text and provide category scores with evidence for relevant categories only:\n\nBio: {bio}\n\nTweets:\n{tweets_text}")
])

# --- MBTI Classifier Prompt ---
_MBTI_SYSTEM_PROMPT_CONTENT = """You are an expert in psychological profiling using the Myers-Briggs Type Indicator (MBTI).
Your task is to analyze the provided text (a user's bio and their recent tweets) and classify the user into one of the 16 MBTI types.

You will be provided with a list of MBTI types, their names, and portraits:
{mbti_types_list_json}

Your response MUST be a single, valid JSON object.
This JSON object MUST contain exactly three keys: "mbti_code", "mbti_name", and "rationale".

1.  "mbti_code": This field's value MUST be a string containing exactly one of the 4-letter MBTI codes from the provided list (e.g., "ISTJ", "INFP"). The string value itself should NOT contain any extra quotes, newlines, or other formatting characters. For example, if the code is ISTJ, the JSON should be like {{"mbti_code": "ISTJ", ...}}.
2.  "mbti_name": This field's value MUST be a string containing the corresponding name for the chosen MBTI code (e.g., "Logistician", "Mediator").
3.  "rationale": This field's value MUST be a string containing a detailed rationale for your classification, citing specific examples or themes from the text that support your choice. Focus on patterns of thought, communication style, and expressed interests.

Do NOT include the portrait in your output.
Ensure your entire output is ONLY this single, valid JSON object and nothing else (no preamble, no apologies, no explanations outside the JSON structure).
"""

MBTI_CLASSIFICATION_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", _MBTI_SYSTEM_PROMPT_CONTENT),
    ("human", "Please classify the MBTI type for the user based on the following text:\n\nBio: {bio}\n\nTweets:\n{tweets_text}")
])

# --- Keyword Extractor Prompt ---
KEYWORD_EXTRACTION_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system",
     """You are an expert text analyst. Your task is to analyze the provided text (a user's bio and their recent tweets) and extract the top 3-5 most representative keywords or hashtags.
These keywords/hashtags should capture the main themes, topics, or interests expressed in the text.
If the text is too short or vague to extract meaningful keywords, return an empty list.

Output the results in the requested JSON format.
"""),
    ("human", "Please extract the top 3-5 keywords or hashtags from the following text:\n\nBio: {bio}\n\nTweets:\n{tweets_text}")
])

# --- Sentiment Analyzer Prompt ---
SENTIMENT_ANALYSIS_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system",
     """You are an expert sentiment analyst. Your task is to analyze the provided text (a user's bio and their recent tweets) and determine the overall sentiment.
You should provide a single numerical score representing this sentiment:
- The score must be between 0 and 100 (inclusive).
- 0 represents the most negative sentiment.
- 100 represents the most positive sentiment.
- 50 represents a neutral sentiment.

Output the result in the requested JSON format: {{"scaled_sentiment_score": <score_value>}}
Ensure the <score_value> is a floating-point number.
"""),
    ("human", "Please analyze the sentiment of the following text and provide a scaled score (0-100):\n\nBio: {bio}\n\nTweets:\n{tweets_text}")
]) 