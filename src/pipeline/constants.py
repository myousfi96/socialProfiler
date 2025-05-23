import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4.1")

# --- Categories ---
CATEGORIES = [
    "politics", "sports", "tech", "business", "finance", "crypto", "startups", 
    "science", "health", "fitness", "nutrition", "food", "travel", "sustainability", 
    "art", "photography", "music", "film_tv", "literature", "gaming", "fashion", 
    "beauty", "parenting", "education", "productivity", "mindfulness", "humor", 
    "pets", "autos", "diy_home"
]

# --- MBTI Types ---
MBTI_TYPES: Dict[str, Dict[str, str]] = {
    "ISTJ": {"name": "Logistician", "portrait": "Practical, detail-oriented planners who trust facts and honour commitments."},
    "ISFJ": {"name": "Defender", "portrait": "Warm protectors who combine attentiveness to people with quiet meticulousness."},
    "INFJ": {"name": "Advocate", "portrait": "Insightful idealists driven by deep values and a wish to help society progress."},
    "INTJ": {"name": "Architect", "portrait": "Strategic, independent thinkers who enjoy mastering complex systems and long-range plans."},
    "ISTP": {"name": "Virtuoso", "portrait": "Calm troubleshooters who learn by doing and love taking things apart to see how they work."},
    "ISFP": {"name": "Adventurer", "portrait": "Gentle, spontaneous creatives who live in the moment and express themselves through aesthetics."},
    "INFP": {"name": "Mediator", "portrait": "Imaginative, empathetic individualists guided by inner ideals and a search for meaning."},
    "INTP": {"name": "Logician", "portrait": "Analytical explorers who relish theories, abstractions and playful intellectual debate."},
    "ESTP": {"name": "Entrepreneur", "portrait": "Energetic problem-solvers who thrive on action, improvisation and real-time results."},
    "ESFP": {"name": "Entertainer", "portrait": "Outgoing, fun-loving enthusiasts who turn everyday moments into engaging experiences."},
    "ENFP": {"name": "Campaigner", "portrait": "Expressive, optimistic catalysts who inspire others with big ideas and personal warmth."},
    "ENTP": {"name": "Debater", "portrait": "Quick-witted innovators who challenge assumptions and spark lively discussions."},
    "ESTJ": {"name": "Executive", "portrait": "Decisive organisers who value efficiency, structure and clear standards of conduct."},
    "ESFJ": {"name": "Consul", "portrait": "Sociable caretakers who build harmony by noticing—and meeting—people's practical needs."},
    "ENFJ": {"name": "Protagonist", "portrait": "Charismatic mentors who unify groups around shared goals and personal growth."},
    "ENTJ": {"name": "Commander", "portrait": "Bold, strategic leaders who set ambitious visions and mobilise resources to achieve them."}
}

MBTI_TYPES_JSON_STR = json.dumps(MBTI_TYPES, indent=2)

# --- Project Root Path ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)) 