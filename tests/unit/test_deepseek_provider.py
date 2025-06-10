"""
Unit tests for DeepSeek AI Provider
Tests the DeepSeek API integration, error handling, and rate limiting
"""

import pytest
import asyncio
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from backend.ai_providers.deepseek import DeepSeekProvider, create_deepseek_provider
from backend.ai_providers.base import (
    ProviderConfig, 
    AIRequest, 
    AIResponse,
    AuthenticationError,
    RateLimitError,
    ModelError,
    NetworkError
)

class TestDeepSeekProvider:
    """Test DeepSeek provider implementation"""
    
    @pytest.fixture
    def provider_config(self):
        """Create test provider configuration"""
        return ProviderConfig(
            api_key="test-api-key",
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
            max_retries=3,
            timeout=30.0
        )
    
    @pytest.fixture
    def provider(self, provider_config):
        """Create DeepSeek provider instance"""
        return DeepSeekProvider(provider_config)
    
    @pytest.fixture
    def sample_request(self):
        """Create sample AI request"""
        return AIRequest(
            prompt="Create a text element for a business presentation",
            context={
                "currentSlide": {"id": "slide-1", "elements": []},
                "presentation": {"title": "Business Report"},
                "userBehavior": {"lastAction": "click"}
            },
            operation_type="content_generation",
            max_tokens=1000,
            temperature=0.7
        )
    
    @pytest.fixture
    def mock_api_response(self):
        """Mock successful API response"""
        return {
            "id": "chatcmpl-test123",
            "object": "chat.completion",
            "created": 1640995200,
            "model": "deepseek-chat",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": json.dumps({
                            "operation": "ADD",
                            "type": "text",
                            "content": "Quarterly Revenue Analysis",
                            "reasoning": "Based on business context, a title would be appropriate",
                            "confidence": 0.85,
                            "alternatives": [
                                {"operation": "ADD", "type": "chart", "content": "Revenue chart"}
                            ]
                        })
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 75,
                "total_tokens": 225
            }
        }
    
    def test_initialization(self, provider):
        """Test provider initialization"""
        assert provider.provider_type.value == "deepseek"
        assert provider.base_url == "https://api.deepseek.com/v1"
        assert provider.model == "deepseek-chat"
        assert not provider.is_initialized
        assert provider.client is None
    
    def test_provider_type(self, provider):
        """Test provider type identification"""
        from backend.ai_providers.base import AIProviderType
        assert provider._get_provider_type() == AIProviderType.DEEPSEEK
    
    @pytest.mark.asyncio
    async def test_initialization_success(self, provider):
        """Test successful provider initialization"""
        with patch.object(provider, 'validate_api_key', return_value=True):
            success = await provider.initialize()
            
            assert success
            assert provider.is_initialized
            assert provider.client is not None
            assert isinstance(provider.client, httpx.AsyncClient)
    
    @pytest.mark.asyncio
    async def test_initialization_failure(self, provider):
        """Test failed provider initialization"""
        with patch.object(provider, 'validate_api_key', return_value=False):
            success = await provider.initialize()
            
            assert not success
            assert not provider.is_initialized
    
    @pytest.mark.asyncio
    async def test_validate_api_key_success(self, provider):
        """Test successful API key validation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        provider.client = mock_client
        
        is_valid = await provider.validate_api_key()
        
        assert is_valid
        mock_client.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_api_key_failure(self, provider):
        """Test failed API key validation"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=mock_response
        )
        provider.client = mock_client
        
        is_valid = await provider.validate_api_key()
        
        assert not is_valid
    
    @pytest.mark.asyncio
    async def test_get_available_models_success(self, provider):
        """Test getting available models"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "deepseek-chat"},
                {"id": "deepseek-coder"}
            ]
        }
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        provider.client = mock_client
        
        models = await provider.get_available_models()
        
        assert "deepseek-chat" in models
        assert "deepseek-coder" in models
    
    @pytest.mark.asyncio
    async def test_get_available_models_fallback(self, provider):
        """Test fallback when models API fails"""
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("API error")
        provider.client = mock_client
        
        models = await provider.get_available_models()
        
        # Should return known models as fallback
        assert "deepseek-chat" in models
        assert "deepseek-coder" in models
    
    @pytest.mark.asyncio
    async def test_generate_completion_success(self, provider, sample_request, mock_api_response):
        """Test successful completion generation"""
        mock_client = AsyncMock()
        mock_client.post.return_value.json.return_value = mock_api_response
        provider.client = mock_client
        provider.is_initialized = True
        
        # Mock rate limiting check
        with patch.object(provider, '_check_rate_limits'):
            response = await provider.generate_completion(sample_request)
        
        assert isinstance(response, AIResponse)
        assert response.content == "Quarterly Revenue Analysis"
        assert response.confidence == 0.85
        assert response.provider == "deepseek"
        assert response.model == "deepseek-chat"
        assert len(response.alternatives) > 0
    
    @pytest.mark.asyncio
    async def test_generate_completion_rate_limit(self, provider, sample_request):
        """Test rate limiting during completion"""
        provider.is_initialized = True
        
        # Simulate rate limit exceeded
        with patch.object(provider, '_check_rate_limits', side_effect=RateLimitError("Rate limit exceeded")):
            response = await provider.generate_completion(sample_request)
        
        # Should return error response
        assert isinstance(response, AIResponse)
        assert "Error:" in response.content
        assert response.confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_generate_completion_network_error(self, provider, sample_request):
        """Test network error handling"""
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.ConnectError("Connection failed")
        provider.client = mock_client
        provider.is_initialized = True
        
        with patch.object(provider, '_check_rate_limits'):
            response = await provider.generate_completion(sample_request)
        
        # Should return error response after retries
        assert isinstance(response, AIResponse)
        assert "Error:" in response.content
        assert response.confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_generate_stream_success(self, provider, sample_request):
        """Test successful streaming generation"""
        # Mock streaming response
        mock_lines = [
            "data: " + json.dumps({
                "choices": [{"delta": {"content": "Hello"}}]
            }),
            "data: " + json.dumps({
                "choices": [{"delta": {"content": " world"}}]
            }),
            "data: [DONE]"
        ]
        
        async def mock_aiter_lines():
            for line in mock_lines:
                yield line
        
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.aiter_lines = mock_aiter_lines
        
        mock_client = AsyncMock()
        mock_client.stream.return_value.__aenter__.return_value = mock_response
        provider.client = mock_client
        provider.is_initialized = True
        
        with patch.object(provider, '_check_rate_limits'):
            chunks = []
            async for chunk in provider.generate_stream(sample_request):
                chunks.append(chunk)
        
        assert chunks == ["Hello", " world"]
    
    @pytest.mark.asyncio
    async def test_generate_stream_error(self, provider, sample_request):
        """Test streaming error handling"""
        mock_client = AsyncMock()
        mock_client.stream.side_effect = Exception("Streaming failed")
        provider.client = mock_client
        provider.is_initialized = True
        
        with patch.object(provider, '_check_rate_limits'):
            chunks = []
            async for chunk in provider.generate_stream(sample_request):
                chunks.append(chunk)
        
        assert len(chunks) == 1
        assert "Error:" in chunks[0]
    
    @pytest.mark.asyncio
    async def test_estimate_cost(self, provider, sample_request):
        """Test cost estimation"""
        cost_estimate = await provider.estimate_cost(sample_request)
        
        assert 'estimated_prompt_tokens' in cost_estimate
        assert 'estimated_completion_tokens' in cost_estimate
        assert 'estimated_total_tokens' in cost_estimate
        assert 'estimated_cost_usd' in cost_estimate
        assert 'model' in cost_estimate
        assert 'currency' in cost_estimate
        
        assert cost_estimate['estimated_completion_tokens'] == 1000  # max_tokens
        assert cost_estimate['model'] == "deepseek-chat"
        assert cost_estimate['currency'] == "USD"
        assert cost_estimate['estimated_cost_usd'] > 0
    
    def test_rate_limiting_initialization(self, provider):
        """Test rate limiter initialization"""
        rate_limiter = provider.rate_limiter
        
        assert rate_limiter['requests_per_minute'] == 60
        assert rate_limiter['tokens_per_minute'] == 100000
        assert rate_limiter['current_requests'] == 0
        assert rate_limiter['current_tokens'] == 0
        assert 'window_start' in rate_limiter
    
    @pytest.mark.asyncio
    async def test_rate_limiting_enforcement(self, provider, sample_request):
        """Test rate limiting enforcement"""
        # Set rate limiter to exceeded state
        provider.rate_limiter['current_requests'] = 60
        provider.rate_limiter['window_start'] = time.time()
        
        with pytest.raises(RateLimitError):
            await provider._check_rate_limits(sample_request)
    
    @pytest.mark.asyncio
    async def test_rate_limiting_window_reset(self, provider, sample_request):
        """Test rate limiting window reset"""
        # Set rate limiter to exceeded state with old window
        provider.rate_limiter['current_requests'] = 60
        provider.rate_limiter['window_start'] = time.time() - 70  # 70 seconds ago
        
        # Should reset and allow request
        await provider._check_rate_limits(sample_request)
        
        assert provider.rate_limiter['current_requests'] == 1
        assert provider.rate_limiter['current_tokens'] > 0
    
    @pytest.mark.asyncio
    async def test_token_rate_limiting(self, provider):
        """Test token-based rate limiting"""
        # Create request with many tokens
        large_request = AIRequest(
            prompt="x" * 10000,  # Very large prompt
            context={},
            operation_type="test",
            max_tokens=50000  # Large completion
        )
        
        with pytest.raises(RateLimitError):
            await provider._check_rate_limits(large_request)
    
    def test_system_prompt_creation(self, provider):
        """Test system prompt creation for different operation types"""
        test_cases = [
            "content_generation",
            "design_suggestion", 
            "layout_optimization",
            "template_selection",
            "automation",
            "unknown_type"
        ]
        
        for operation_type in test_cases:
            prompt = provider._create_system_prompt(operation_type)
            
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            assert "JSON format" in prompt
            assert "PowerPoint" in prompt or "PPT" in prompt
    
    def test_user_prompt_formatting(self, provider, sample_request):
        """Test user prompt formatting with context"""
        formatted = provider._format_user_prompt(sample_request)
        
        assert sample_request.prompt in formatted
        assert "Context:" in formatted
        assert "currentSlide" in formatted
    
    @pytest.mark.asyncio
    async def test_request_preparation(self, provider, sample_request):
        """Test API request preparation"""
        request_payload = await provider._prepare_request(sample_request)
        
        assert 'model' in request_payload
        assert 'messages' in request_payload
        assert 'max_tokens' in request_payload
        assert 'temperature' in request_payload
        assert 'stream' in request_payload
        
        assert request_payload['model'] == "deepseek-chat"
        assert len(request_payload['messages']) == 2  # system + user
        assert request_payload['messages'][0]['role'] == 'system'
        assert request_payload['messages'][1]['role'] == 'user'
        assert request_payload['max_tokens'] <= 4096  # Should respect model limits
    
    @pytest.mark.asyncio
    async def test_request_preparation_streaming(self, provider, sample_request):
        """Test API request preparation for streaming"""
        request_payload = await provider._prepare_request(sample_request, stream=True)
        
        assert request_payload['stream'] is True
        assert 'response_format' not in request_payload  # Should not be set for streaming
    
    @pytest.mark.asyncio
    async def test_retry_logic_success_after_failure(self, provider):
        """Test retry logic with eventual success"""
        mock_client = AsyncMock()
        
        # First call fails, second succeeds
        mock_client.post.side_effect = [
            httpx.ConnectError("Connection failed"),
            MagicMock(status_code=200, json=lambda: {"test": "response"})
        ]
        
        provider.client = mock_client
        
        payload = {"test": "payload"}
        response = await provider._make_request_with_retries(payload)
        
        assert response == {"test": "response"}
        assert mock_client.post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_logic_all_failures(self, provider):
        """Test retry logic when all attempts fail"""
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.ConnectError("Connection failed")
        provider.client = mock_client
        
        payload = {"test": "payload"}
        
        with pytest.raises(NetworkError):
            await provider._make_request_with_retries(payload)
        
        assert mock_client.post.call_count == provider.config.max_retries
    
    @pytest.mark.asyncio
    async def test_retry_logic_no_retry_on_auth_error(self, provider):
        """Test that authentication errors are not retried"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        provider.client = mock_client
        
        payload = {"test": "payload"}
        
        with pytest.raises(AuthenticationError):
            await provider._make_request_with_retries(payload)
        
        # Should only try once, no retries
        assert mock_client.post.call_count == 1
    
    @pytest.mark.asyncio
    async def test_response_processing_valid_json(self, provider, sample_request, mock_api_response):
        """Test processing valid JSON response"""
        response = await provider._process_response(mock_api_response, sample_request)
        
        assert isinstance(response, AIResponse)
        assert response.content == "Quarterly Revenue Analysis"
        assert response.confidence == 0.85
        assert response.reasoning == "Based on business context, a title would be appropriate"
        assert len(response.alternatives) == 1
        assert response.provider == "deepseek"
        assert response.model == "deepseek-chat"
    
    @pytest.mark.asyncio
    async def test_response_processing_invalid_json(self, provider, sample_request):
        """Test processing response with invalid JSON"""
        invalid_response = {
            "choices": [
                {
                    "message": {"content": "Invalid JSON content"},
                    "finish_reason": "stop"
                }
            ],
            "usage": {"total_tokens": 100}
        }
        
        response = await provider._process_response(invalid_response, sample_request)
        
        assert isinstance(response, AIResponse)
        assert response.content == "Invalid JSON content"
        assert response.confidence == 0.5  # Default fallback
    
    @pytest.mark.asyncio
    async def test_response_processing_malformed_response(self, provider, sample_request):
        """Test processing malformed response"""
        malformed_response = {"invalid": "structure"}
        
        with pytest.raises(ModelError):
            await provider._process_response(malformed_response, sample_request)
    
    def test_metrics_update(self, provider):
        """Test metrics updating"""
        initial_total = provider.metrics['total_requests']
        initial_successful = provider.metrics['successful_requests']
        
        provider.update_metrics(True, 100, 1.5)
        
        assert provider.metrics['total_requests'] == initial_total + 1
        assert provider.metrics['successful_requests'] == initial_successful + 1
        assert provider.metrics['total_tokens_used'] == 100
        assert provider.metrics['average_response_time'] == 1.5
    
    def test_metrics_calculation(self, provider):
        """Test metrics calculation"""
        # Add some test data
        provider.update_metrics(True, 100, 1.0)
        provider.update_metrics(True, 200, 2.0)
        provider.update_metrics(False, 0, 3.0)
        
        metrics = provider.get_metrics()
        
        assert metrics['total_requests'] == 3
        assert metrics['successful_requests'] == 2
        assert metrics['failed_requests'] == 1
        assert metrics['success_rate'] == pytest.approx(66.67, rel=1e-2)
        assert metrics['average_response_time'] == 2.0  # (1+2+3)/3
        assert metrics['provider'] == "deepseek"
    
    @pytest.mark.asyncio
    async def test_context_manager(self, provider_config):
        """Test async context manager usage"""
        with patch('backend.ai_providers.deepseek.DeepSeekProvider.validate_api_key', return_value=True):
            async with DeepSeekProvider(provider_config) as provider:
                assert provider.is_initialized
                assert provider.client is not None
        
        # Client should be closed after context exit
        # Note: In real implementation, client would be closed in __aexit__

class TestDeepSeekProviderFactory:
    """Test the factory function for creating DeepSeek providers"""
    
    def test_create_deepseek_provider_minimal(self):
        """Test creating provider with minimal configuration"""
        provider = create_deepseek_provider("test-api-key")
        
        assert isinstance(provider, DeepSeekProvider)
        assert provider.config.api_key == "test-api-key"
        assert provider.config.model == "deepseek-chat"
        assert provider.config.max_retries == 3
        assert provider.config.timeout == 30.0
    
    def test_create_deepseek_provider_full_config(self):
        """Test creating provider with full configuration"""
        provider = create_deepseek_provider(
            api_key="test-api-key",
            base_url="https://custom.api.com",
            model="deepseek-coder",
            max_retries=5,
            timeout=60.0,
            custom_headers={"X-Custom": "header"}
        )
        
        assert provider.config.api_key == "test-api-key"
        assert provider.config.base_url == "https://custom.api.com"
        assert provider.config.model == "deepseek-coder"
        assert provider.config.max_retries == 5
        assert provider.config.timeout == 60.0
        assert provider.config.custom_headers == {"X-Custom": "header"}