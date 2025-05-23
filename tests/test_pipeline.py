import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Import pipeline components
from src.pipeline.graph import create_profiling_graph
from src.pipeline.models import ProfileAnalysisState, CategoryScoreWithEvidence, CategoryScores, TopKeywords, MBTIResult
from src.pipeline.nodes import (
    data_fetcher_node,
    category_scorer_node,
    mbti_classifier_node,
    keywords_extractor_node,
    sentiment_analyzer_node
)


class TestPipelineModels:
    """Test pipeline data models."""
    
    def test_category_score_with_evidence_creation(self):
        """Test CategoryScoreWithEvidence model creation."""
        score = CategoryScoreWithEvidence(
            category="Technology",
            score=85.5,
            evidence=["tweet about AI", "bio mentions coding"]
        )
        assert score.category == "Technology"
        assert score.score == 85.5
        assert len(score.evidence) == 2
    
    def test_category_scores_creation(self):
        """Test CategoryScores model creation."""
        scores = CategoryScores(
            scores=[
                CategoryScoreWithEvidence(
                    category="Technology", 
                    score=85.0, 
                    evidence=["AI tweet"]
                )
            ]
        )
        assert len(scores.scores) == 1
        assert scores.scores[0].category == "Technology"
    
    def test_top_keywords_creation(self):
        """Test TopKeywords model creation."""
        keywords = TopKeywords(keywords=["AI", "coding", "tech"])
        assert len(keywords.keywords) == 3
        assert "AI" in keywords.keywords
    
    def test_mbti_result_creation(self):
        """Test MBTIResult model creation."""
        mbti = MBTIResult(
            mbti_code="INTJ",
            mbti_name="Architect",
            rationale="Shows strategic thinking and independence"
        )
        assert mbti.mbti_code == "INTJ"
        assert mbti.mbti_name == "Architect"
        assert "strategic" in mbti.rationale


class TestPipelineGraph:
    """Test pipeline graph creation and structure."""
    
    def test_create_profiling_graph(self):
        """Test that the profiling graph is created correctly."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            graph = create_profiling_graph()
            assert graph is not None
            # Verify nodes are added
            expected_nodes = [
                "data_fetcher", "category_scorer", "mbti_classifier", 
                "keywords_extractor", "sentiment_analyzer"
            ]
            # Note: We can't easily test internal graph structure without accessing private attributes
            # This is a basic test to ensure graph creation doesn't fail
    
    def test_create_profiling_graph_returns_state_graph(self):
        """Test that create_profiling_graph returns a StateGraph instance."""
        with patch('src.pipeline.graph.OPENAI_API_KEY', 'test-key'):
            graph = create_profiling_graph()
            assert graph is not None
            assert hasattr(graph, 'add_node')
            assert hasattr(graph, 'add_edge')


class TestPipelineNodes:
    """Test individual pipeline nodes."""
    
    @pytest.fixture
    def sample_state(self) -> ProfileAnalysisState:
        """Create a sample state for testing."""
        return {
            "username": "testuser",
            "user_bio": "AI enthusiast and developer",
            "user_display_name": "Test User",
            "user_profile_image_url": "https://example.com/image.jpg",
            "recent_tweets": ["Love working with AI!", "Just deployed a new model"],
            "tweet_count_requested": 10,
            "category_scores": None,
            "mbti_result": None,
            "top_keywords": None,
            "sentiment_scaled_score": None,
            "error": None
        }
    
    @pytest.mark.asyncio
    async def test_data_fetcher_node_success(self, sample_state):
        """Test successful data fetching."""
        mock_user_details = {
            "bio": "Test bio",
            "display_name": "Test User",
            "profile_image_url": "https://example.com/image.jpg"
        }
        mock_tweets = ["tweet1", "tweet2"]
        
        with patch('src.pipeline.nodes.fetch_user_details', new_callable=AsyncMock) as mock_fetch_user, \
             patch('src.pipeline.nodes.fetch_recent_tweets', new_callable=AsyncMock) as mock_fetch_tweets:
            
            mock_fetch_user.return_value = mock_user_details
            mock_fetch_tweets.return_value = mock_tweets
            
            result = await data_fetcher_node(sample_state)
            
            assert result["user_bio"] == "Test bio"
            assert result["user_display_name"] == "Test User"
            assert result["recent_tweets"] == mock_tweets
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_data_fetcher_node_no_username(self):
        """Test data fetcher with missing username."""
        state = {"username": None, "tweet_count_requested": 10}
        result = await data_fetcher_node(state)
        
        assert result["error"] == "Username not provided."
        assert result["user_bio"] is None
        assert result["recent_tweets"] == []
    
    @pytest.mark.asyncio
    async def test_data_fetcher_node_exception(self, sample_state):
        """Test data fetcher with exception."""
        with patch('src.pipeline.nodes.fetch_user_details', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")
            
            result = await data_fetcher_node(sample_state)
            
            assert "Data fetching failed" in result["error"]
            assert result["user_bio"] is None
    
    def test_category_scorer_node_success(self, sample_state):
        """Test successful category scoring."""
        mock_response = Mock()
        mock_response.scores = [
            Mock(category="tech", score=85.0, evidence=["AI tweet"])
        ]
        
        with patch('src.pipeline.nodes.get_category_scorer_llm') as mock_llm_getter, \
             patch('src.pipeline.nodes._prepare_prompt_inputs') as mock_prep:
            
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_response
            mock_llm_getter.return_value = mock_llm
            mock_prep.return_value = {"bio": "test", "tweets_text": "test"}
            
            result = category_scorer_node(sample_state)
            
            assert "tech" in result["category_scores"]
            assert result["category_scores"]["tech"]["score"] == 85.0
            assert result["error"] is None
    
    def test_category_scorer_node_no_text(self):
        """Test category scorer with no text available."""
        state = {
            "user_bio": None,
            "recent_tweets": [],
            "username": "test"
        }
        result = category_scorer_node(state)
        
        assert result["category_scores"] == {}
        assert "No text to analyze" in result["error"]
    
    def test_mbti_classifier_node_success(self, sample_state):
        """Test successful MBTI classification."""
        mock_response = Mock()
        mock_response.mbti_code = "INTJ"
        mock_response.mbti_name = "Architect"
        mock_response.rationale = "Test rationale"
        
        with patch('src.pipeline.nodes.get_mbti_classifier_llm') as mock_llm_getter, \
             patch('src.pipeline.nodes._prepare_prompt_inputs') as mock_prep, \
             patch('src.pipeline.nodes.MBTI_TYPES', {"INTJ": {"name": "Architect", "portrait": "The Architect"}}):
            
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_response
            mock_llm_getter.return_value = mock_llm
            mock_prep.return_value = {"bio": "test", "tweets_text": "test"}
            
            result = mbti_classifier_node(sample_state)
            
            assert result["mbti_result"]["mbti_code"] == "INTJ"
            assert result["mbti_result"]["mbti_name"] == "Architect"
            assert result["error"] is None
    
    def test_keywords_extractor_node_success(self, sample_state):
        """Test successful keyword extraction."""
        mock_response = Mock()
        mock_response.keywords = ["AI", "coding", "tech"]
        
        with patch('src.pipeline.nodes.get_keywords_extractor_llm') as mock_llm_getter, \
             patch('src.pipeline.nodes._prepare_prompt_inputs') as mock_prep:
            
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_response
            mock_llm_getter.return_value = mock_llm
            mock_prep.return_value = {"bio": "test", "tweets_text": "test"}
            
            result = keywords_extractor_node(sample_state)
            
            assert result["top_keywords"] == ["AI", "coding", "tech"]
            assert result["error"] is None
    
    def test_keywords_extractor_node_no_text(self):
        """Test keyword extractor with no text available."""
        state = {
            "user_bio": None,
            "recent_tweets": [],
            "username": "test"
        }
        result = keywords_extractor_node(state)
        
        assert result["top_keywords"] == []
        assert "No text to analyze" in result["error"]
    
    def test_sentiment_analyzer_node_success(self, sample_state):
        """Test successful sentiment analysis."""
        mock_response = Mock()
        mock_response.scaled_sentiment_score = 75.5
        
        with patch('src.pipeline.nodes.get_sentiment_analyzer_llm') as mock_llm_getter, \
             patch('src.pipeline.nodes._prepare_prompt_inputs') as mock_prep:
            
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_response
            mock_llm_getter.return_value = mock_llm
            mock_prep.return_value = {"bio": "test", "tweets_text": "test"}
            
            result = sentiment_analyzer_node(sample_state)
            
            assert result["sentiment_scaled_score"] == 75.5
            assert result["error"] is None
    
    def test_sentiment_analyzer_node_score_bounds(self, sample_state):
        """Test sentiment analyzer respects score bounds."""
        mock_response = Mock()
        mock_response.scaled_sentiment_score = 150.0  # Over limit
        
        with patch('src.pipeline.nodes.get_sentiment_analyzer_llm') as mock_llm_getter, \
             patch('src.pipeline.nodes._prepare_prompt_inputs') as mock_prep:
            
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_response
            mock_llm_getter.return_value = mock_llm
            mock_prep.return_value = {"bio": "test", "tweets_text": "test"}
            
            result = sentiment_analyzer_node(sample_state)
            
            assert result["sentiment_scaled_score"] == 100.0  # Should be capped
            assert result["error"] is None 