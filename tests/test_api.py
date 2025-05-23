import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
import httpx

# Import API components
from src.api.models import AnalyzeRequest, AnalysisResponse
from src.api.services import initialize_graph, get_graph_app, analyze_profile_service
from src.api.main import app


class TestAPIModels:
    """Test API data models."""
    
    def test_analyze_request_creation(self):
        """Test AnalyzeRequest model creation."""
        request = AnalyzeRequest(username="testuser", tweet_count=15)
        assert request.username == "testuser"
        assert request.tweet_count == 15
    
    def test_analyze_request_default_tweet_count(self):
        """Test AnalyzeRequest with default tweet count."""
        request = AnalyzeRequest(username="testuser")
        assert request.username == "testuser"
        assert request.tweet_count == 10  # Default value
    
    def test_analyze_request_validation(self):
        """Test AnalyzeRequest validation."""
        # Test valid range
        request = AnalyzeRequest(username="test", tweet_count=25)
        assert request.tweet_count == 25
        
        # Test invalid range (should be handled by Pydantic)
        with pytest.raises(ValueError):
            AnalyzeRequest(username="test", tweet_count=0)
        
        with pytest.raises(ValueError):
            AnalyzeRequest(username="test", tweet_count=51)
    
    def test_analysis_response_creation(self):
        """Test AnalysisResponse model creation."""
        response = AnalysisResponse(
            username="testuser",
            user_bio="Test bio",
            user_display_name="Test User",
            recent_tweets=["tweet1", "tweet2"],
            category_scores={"Technology": {"score": 85.0, "evidence": ["AI tweet"]}},
            mbti_result={"mbti_code": "INTJ", "mbti_name": "Architect"},
            top_keywords=["AI", "tech"],
            sentiment_scaled_score=75.5
        )
        assert response.username == "testuser"
        assert response.user_bio == "Test bio"
        assert len(response.recent_tweets) == 2
        assert response.sentiment_scaled_score == 75.5


class TestAPIServices:
    """Test API service functions."""
    
    def test_initialize_graph_success(self):
        """Test successful graph initialization."""
        with patch('src.api.services.create_profiling_graph') as mock_create:
            mock_graph = Mock()
            mock_compiled_graph = Mock()
            mock_graph.compile.return_value = mock_compiled_graph
            mock_create.return_value = mock_graph
            
            result = initialize_graph()
            
            assert result is True
            mock_create.assert_called_once()
            mock_graph.compile.assert_called_once()
    
    def test_initialize_graph_failure(self):
        """Test graph initialization failure."""
        with patch('src.api.services.create_profiling_graph') as mock_create:
            mock_create.side_effect = Exception("Graph creation failed")
            
            result = initialize_graph()
            
            assert result is False
    
    def test_get_graph_app_existing(self):
        """Test getting graph app when already initialized."""
        with patch('src.api.services.profiling_graph_app', new=Mock()) as mock_app:
            result = get_graph_app()
            assert result == mock_app
    
    def test_get_graph_app_initialize(self):
        """Test getting graph app when not initialized."""
        with patch('src.api.services.profiling_graph_app', new=None), \
             patch('src.api.services.initialize_graph') as mock_init:
            mock_init.return_value = True
            
            result = get_graph_app()
            mock_init.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_profile_service_success(self):
        """Test successful profile analysis."""
        mock_final_state = {
            "username": "testuser",
            "user_bio": "Test bio",
            "user_display_name": "Test User",
            "recent_tweets": ["tweet1"],
            "category_scores": {"Technology": {"score": 85.0}},
            "mbti_result": {"mbti_code": "INTJ"},
            "top_keywords": ["AI"],
            "sentiment_scaled_score": 75.5,
            "error": None
        }
        
        mock_graph_app = Mock()
        mock_graph_app.ainvoke = AsyncMock(return_value=mock_final_state)
        
        with patch('src.api.services.get_graph_app', return_value=mock_graph_app), \
             patch.dict('os.environ', {
                 'LANGFUSE_PUBLIC_KEY': 'test_key',
                 'LANGFUSE_SECRET_KEY': 'test_secret'
             }), \
             patch('src.api.services.CallbackHandler') as mock_handler:
            
            result = await analyze_profile_service("testuser", 10)
            
            assert result["username"] == "testuser"
            assert result["user_bio"] == "Test bio"
            assert result["error"] is None
            mock_graph_app.ainvoke.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_profile_service_no_graph(self):
        """Test profile analysis when graph is not available."""
        with patch('src.api.services.get_graph_app', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await analyze_profile_service("testuser", 10)
            
            assert exc_info.value.status_code == 503
            assert "Graph application is not available" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_analyze_profile_service_data_fetching_error(self):
        """Test profile analysis with data fetching error."""
        mock_final_state = {
            "username": "testuser",
            "error": "Data fetching failed: User not found"
        }
        
        mock_graph_app = Mock()
        mock_graph_app.ainvoke = AsyncMock(return_value=mock_final_state)
        
        with patch('src.api.services.get_graph_app', return_value=mock_graph_app):
            with pytest.raises(HTTPException) as exc_info:
                await analyze_profile_service("testuser", 10)
            
            assert exc_info.value.status_code == 404
            assert "Could not retrieve data" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_analyze_profile_service_pipeline_error(self):
        """Test profile analysis with pipeline error."""
        mock_final_state = {
            "username": "testuser",
            "error": "LLM call failed: API error"
        }
        
        mock_graph_app = Mock()
        mock_graph_app.ainvoke = AsyncMock(return_value=mock_final_state)
        
        with patch('src.api.services.get_graph_app', return_value=mock_graph_app):
            with pytest.raises(HTTPException) as exc_info:
                await analyze_profile_service("testuser", 10)
            
            assert exc_info.value.status_code == 500
            assert "Analysis pipeline error" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_analyze_profile_service_unexpected_error(self):
        """Test profile analysis with unexpected error."""
        mock_graph_app = Mock()
        mock_graph_app.ainvoke = AsyncMock(side_effect=Exception("Unexpected error"))
        
        with patch('src.api.services.get_graph_app', return_value=mock_graph_app):
            with pytest.raises(HTTPException) as exc_info:
                await analyze_profile_service("testuser", 10)
            
            assert exc_info.value.status_code == 500
            assert "An unexpected error occurred" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_analyze_profile_service_without_langfuse(self):
        """Test profile analysis without Langfuse credentials."""
        mock_final_state = {
            "username": "testuser",
            "user_bio": "Test bio",
            "error": None
        }
        
        mock_graph_app = Mock()
        mock_graph_app.ainvoke = AsyncMock(return_value=mock_final_state)
        
        with patch('src.api.services.get_graph_app', return_value=mock_graph_app), \
             patch.dict('os.environ', {}, clear=True):
            
            result = await analyze_profile_service("testuser", 10)
            
            assert result["username"] == "testuser"
            # Should succeed without Langfuse
            mock_graph_app.ainvoke.assert_called_once()


class TestAPIRoutes:
    """Test API route endpoints."""
    
    @pytest.mark.asyncio
    async def test_analyze_profile_endpoint_success(self):
        """Test successful analyze profile endpoint."""
        mock_final_state = {
            "username": "testuser",
            "user_bio": "Test bio",
            "user_display_name": "Test User",
            "user_profile_image_url": "https://example.com/image.jpg",
            "recent_tweets": ["tweet1"],
            "category_scores": {"tech": {"score": 85.0}},
            "mbti_result": {"mbti_code": "INTJ", "mbti_name": "Architect"},
            "top_keywords": ["AI"],
            "sentiment_scaled_score": 75.5,
            "error": None
        }
        
        with patch('src.api.routes.analyze_profile_service', new_callable=AsyncMock) as mock_service:
            mock_service.return_value = mock_final_state
            
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/analyze",
                    json={"username": "testuser", "tweet_count": 10}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["username"] == "testuser"
                assert data["user_bio"] == "Test bio"
                assert data["sentiment_scaled_score"] == 75.5
    
    @pytest.mark.asyncio
    async def test_analyze_profile_endpoint_validation_error(self):
        """Test analyze profile endpoint with validation error."""
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/analyze",
                json={"username": "testuser", "tweet_count": 100}  # Invalid count
            )
            
            assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_analyze_profile_endpoint_service_error(self):
        """Test analyze profile endpoint with service error."""
        with patch('src.api.routes.analyze_profile_service', new_callable=AsyncMock) as mock_service:
            mock_service.side_effect = HTTPException(status_code=404, detail="User not found")
            
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/analyze",
                    json={"username": "nonexistent", "tweet_count": 10}
                )
                
                assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_analyze_profile_endpoint_missing_username(self):
        """Test analyze profile endpoint with missing username."""
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/analyze",
                json={"tweet_count": 10}  # Missing username
            )
            
            assert response.status_code == 422  # Validation error
    
    def test_health_check_endpoint(self):
        """Test that the app starts successfully."""
        # This is a basic test to ensure the FastAPI app can be created
        # In a real scenario, you might have a health check endpoint
        assert app is not None 