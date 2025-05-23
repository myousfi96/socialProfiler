# Social Profiler 🤖

A Python application that analyzes X (Twitter) profiles to determine personality, interests, sentiment, and more using AI.

## Features

- **Profile Analysis**: Analyze X profiles based on recent tweets
- **Sentiment Analysis**: Determine emotional sentiment from tweet content
- **Topic Classification**: Identify main topics and interests
- **Personality Insights**: Generate personality profiles
- **Web Interface**: Streamlit frontend for easy interaction
- **REST API**: FastAPI backend for programmatic access

## Installation

### Prerequisites

- Python 3.11+
- pip

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd weareera
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Variables**

Create a `.env` file in the root directory with the following variables:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
X_USERNAME=your_x_username
X_PASSWORD=your_x_password
X_EMAIL=your_x_email
X_EMAIL_PASSWORD=your_x_email_password

# Optional
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key  # For observability
LANGFUSE_SECRET_KEY=your_langfuse_secret_key  # For observability
MODEL_NAME=gpt-4.1  # Default: gpt-4.1
```

## Running the Application

### Option 1: Web Interface (Streamlit)

```bash
streamlit run src/frontend/app.py
```

The web interface will be available at `http://localhost:8501`

### Option 2: API Server (FastAPI)

```bash
uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`

## Usage

### Web Interface
1. Enter an X username (without @)
2. Specify number of tweets to analyze
3. Click "Analyze Profile"
4. View results including sentiment analysis, topics, and personality insights

### API
Make POST requests to `/analyze` endpoint:

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"username": "example_user", "tweet_count": 10}'
```

## Testing

```bash
pytest tests/
```

## Project Structure

```
weareera/
├── src/
│   ├── api/          # FastAPI backend
│   ├── frontend/     # Streamlit web interface
│   ├── pipeline/     # AI analysis pipeline
│   └── data_fetcher/ # X data collection
├── tests/            # Test files
├── requirements.txt  # Python dependencies
└── README.md        # This file
``` 