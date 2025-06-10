"""
DeepSeek AI Provider Implementation
Provides integration with DeepSeek's AI API for PPT generation
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, AsyncGenerator
import httpx
import logging
from datetime import datetime, timedelta

from .base import (
    BaseAIProvider, 
    AIProviderType, 
    AIRequest, 
    AIResponse, 
    ProviderConfig,
    AuthenticationError,
    RateLimitError,
    ModelError,
    NetworkError
)

logger = logging.getLogger(__name__)

class DeepSeekProvider(BaseAIProvider):
    """
    DeepSeek AI Provider
    
    Implements the BaseAIProvider interface for DeepSeek's API.
    Provides secure, efficient, and robust integration with rate limiting,
    retry logic, and comprehensive error handling.
    """
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.deepseek.com/v1"
        self.model = config.model or "deepseek-chat"
        self.client = None
        
        # Rate limiting
        self.rate_limiter = {
            'requests_per_minute': 60,
            'tokens_per_minute': 100000,
            'current_requests': 0,
            'current_tokens': 0,
            'window_start': time.time()
        }
        
        # Retry configuration
        self.retry_delays = [1, 2, 4, 8, 16]  # Exponential backoff
        
        # Model capabilities
        self.model_info = {
            'deepseek-chat': {
                'max_tokens': 4096,
                'context_length': 32768,
                'cost_per_1k_tokens': 0.0014,
                'supports_streaming': True
            },
            'deepseek-coder': {
                'max_tokens': 4096,
                'context_length': 16384,
                'cost_per_1k_tokens': 0.0014,
                'supports_streaming': True
            }
        }
    
    def _get_provider_type(self) -> AIProviderType:
        return AIProviderType.DEEPSEEK
    
    async def initialize(self) -> bool:
        """Initialize the DeepSeek provider"""
        try:
            # Create HTTP client with proper configuration
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "AI-PPT-System/1.0.0",
                    **(self.config.custom_headers or {})
                },
                timeout=httpx.Timeout(self.config.timeout),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            )
            
            # Validate API key
            is_valid = await self.validate_api_key()
            if not is_valid:
                raise AuthenticationError("Invalid API key")
            
            self.is_initialized = True
            logger.info("✅ DeepSeek provider initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ DeepSeek provider initialization failed: {e}")
            self.is_initialized = False
            return False
    
    async def validate_api_key(self) -> bool:
        """Validate the DeepSeek API key"""
        try:
            if not self.client:
                return False
            
            # Test with a minimal request
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1
                }
            )
            
            return response.status_code in [200, 400]  # 400 might be due to minimal request
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return False
            return True  # Other errors might not be auth-related
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return False
    
    async def get_available_models(self) -> List[str]:
        """Get available DeepSeek models"""
        try:
            if not self.client:
                return []
            
            response = await self.client.get("/models")
            if response.status_code == 200:
                data = response.json()
                return [model["id"] for model in data.get("data", [])]
            else:
                # Return known models if API doesn't support model listing
                return list(self.model_info.keys())
                
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return list(self.model_info.keys())
    
    async def generate_completion(self, request: AIRequest) -> AIResponse:
        """Generate completion using DeepSeek API"""
        start_time = time.time()
        
        try:
            # Check rate limits
            await self._check_rate_limits(request)
            
            # Prepare the request
            api_request = await self._prepare_request(request)
            
            # Make the API call with retries
            response_data = await self._make_request_with_retries(api_request)
            
            # Process the response
            ai_response = await self._process_response(response_data, request)
            
            # Update metrics
            response_time = time.time() - start_time
            tokens_used = response_data.get("usage", {}).get("total_tokens", 0)
            self.update_metrics(True, tokens_used, response_time)
            
            return ai_response
            
        except Exception as e:
            response_time = time.time() - start_time
            self.update_metrics(False, 0, response_time)
            logger.error(f"DeepSeek completion failed: {e}")
            return self._create_error_response(e, request)
    
    async def generate_stream(self, request: AIRequest) -> AsyncGenerator[str, None]:
        """Generate streaming completion"""
        try:
            # Check rate limits
            await self._check_rate_limits(request)
            
            # Prepare streaming request
            api_request = await self._prepare_request(request, stream=True)
            
            # Make streaming request
            async with self.client.stream(
                "POST", 
                "/chat/completions", 
                json=api_request
            ) as response:
                if response.status_code != 200:
                    raise ModelError(f"API returned status {response.status_code}")
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError):
                            continue
                            
        except Exception as e:
            logger.error(f"DeepSeek streaming failed: {e}")
            yield f"Error: {str(e)}"
    
    async def estimate_cost(self, request: AIRequest) -> Dict[str, Any]:
        """Estimate cost for the request"""
        try:
            model_info = self.model_info.get(self.model, self.model_info['deepseek-chat'])
            
            # Estimate token count (rough approximation)
            prompt_tokens = len(request.prompt.split()) * 1.3  # Rough token estimation
            max_completion_tokens = request.max_tokens or 1000
            
            total_tokens = prompt_tokens + max_completion_tokens
            cost_per_1k = model_info['cost_per_1k_tokens']
            estimated_cost = (total_tokens / 1000) * cost_per_1k
            
            return {
                'estimated_prompt_tokens': int(prompt_tokens),
                'estimated_completion_tokens': max_completion_tokens,
                'estimated_total_tokens': int(total_tokens),
                'estimated_cost_usd': round(estimated_cost, 6),
                'model': self.model,
                'currency': 'USD'
            }
            
        except Exception as e:
            logger.error(f"Cost estimation failed: {e}")
            return {'error': str(e)}
    
    async def _check_rate_limits(self, request: AIRequest):
        """Check and enforce rate limits"""
        current_time = time.time()
        
        # Reset window if needed
        if current_time - self.rate_limiter['window_start'] >= 60:
            self.rate_limiter['current_requests'] = 0
            self.rate_limiter['current_tokens'] = 0
            self.rate_limiter['window_start'] = current_time
        
        # Check request limit
        if self.rate_limiter['current_requests'] >= self.rate_limiter['requests_per_minute']:
            self.metrics['rate_limit_hits'] += 1
            wait_time = 60 - (current_time - self.rate_limiter['window_start'])
            raise RateLimitError(f"Rate limit exceeded. Wait {wait_time:.1f} seconds")
        
        # Estimate tokens for this request
        estimated_tokens = len(request.prompt.split()) * 1.3 + (request.max_tokens or 1000)
        
        # Check token limit
        if (self.rate_limiter['current_tokens'] + estimated_tokens > 
            self.rate_limiter['tokens_per_minute']):
            self.metrics['rate_limit_hits'] += 1
            wait_time = 60 - (current_time - self.rate_limiter['window_start'])
            raise RateLimitError(f"Token rate limit exceeded. Wait {wait_time:.1f} seconds")
        
        # Update counters
        self.rate_limiter['current_requests'] += 1
        self.rate_limiter['current_tokens'] += estimated_tokens
    
    async def _prepare_request(self, request: AIRequest, stream: bool = False) -> Dict[str, Any]:
        """Prepare API request payload"""
        
        # Create system prompt for PPT operations
        system_prompt = self._create_system_prompt(request.operation_type)
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": self._format_user_prompt(request)}
        ]
        
        # Build request payload
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": min(request.max_tokens or 1000, 
                            self.model_info.get(self.model, {}).get('max_tokens', 4096)),
            "temperature": request.temperature or 0.7,
            "stream": stream,
            "response_format": {"type": "json_object"} if not stream else None
        }
        
        return payload
    
    async def _make_request_with_retries(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with retry logic"""
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                response = await self.client.post("/chat/completions", json=payload)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status_code >= 500:
                    raise NetworkError(f"Server error: {response.status_code}")
                else:
                    raise ModelError(f"API error: {response.status_code} - {response.text}")
                    
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = NetworkError(f"Network error: {str(e)}")
                if attempt < self.config.max_retries - 1:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    logger.warning(f"Request failed, retrying in {delay}s (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                    continue
            except (RateLimitError, AuthenticationError):
                raise  # Don't retry these
            except Exception as e:
                last_exception = e
                if attempt < self.config.max_retries - 1:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    await asyncio.sleep(delay)
                    continue
        
        raise last_exception or ModelError("All retry attempts failed")
    
    async def _process_response(self, response_data: Dict[str, Any], request: AIRequest) -> AIResponse:
        """Process API response into standardized format"""
        try:
            choice = response_data["choices"][0]
            content = choice["message"]["content"]
            
            # Parse JSON response
            try:
                parsed_content = json.loads(content)
            except json.JSONDecodeError:
                # Fallback to raw content if not valid JSON
                parsed_content = {"content": content, "confidence": 0.5}
            
            # Extract structured data
            operation_content = parsed_content.get("content", content)
            confidence = parsed_content.get("confidence", 0.7)
            reasoning = parsed_content.get("reasoning", "AI-generated response")
            alternatives = parsed_content.get("alternatives", [])
            
            return AIResponse(
                content=operation_content,
                confidence=confidence,
                reasoning=reasoning,
                alternatives=alternatives,
                usage=response_data.get("usage", {}),
                provider=self.provider_type.value,
                model=self.model,
                metadata={
                    "finish_reason": choice.get("finish_reason"),
                    "request_id": response_data.get("id"),
                    "created": response_data.get("created")
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to process response: {e}")
            raise ModelError(f"Response processing failed: {str(e)}")
    
    def _create_system_prompt(self, operation_type: str) -> str:
        """Create system prompt for PPT operations"""
        base_prompt = """You are an AI assistant specialized in PowerPoint presentation generation and editing. 
You understand atomic operations for PPT creation and can suggest appropriate actions based on context.

Your responses should be in JSON format with the following structure:
{
    "operation": "ADD|MODIFY|DELETE|MOVE|STYLE",
    "type": "text|image|shape|chart|table|slide",
    "content": "specific content or action",
    "reasoning": "explanation of why this action is appropriate",
    "confidence": 0.0-1.0,
    "alternatives": [{"operation": "...", "type": "...", "content": "..."}]
}

Focus on creating professional, visually appealing presentations that follow design best practices."""
        
        operation_specific = {
            "content_generation": "Focus on generating relevant, engaging content for presentations.",
            "design_suggestion": "Suggest design improvements and visual enhancements.",
            "layout_optimization": "Recommend layout changes for better visual hierarchy.",
            "template_selection": "Suggest appropriate templates based on content type.",
            "automation": "Provide automated sequences of operations for efficient PPT creation."
        }
        
        specific_prompt = operation_specific.get(operation_type, "")
        return f"{base_prompt}\n\n{specific_prompt}"
    
    def _format_user_prompt(self, request: AIRequest) -> str:
        """Format user prompt with context"""
        context_str = ""
        if request.context:
            context_str = f"\nContext: {json.dumps(request.context, indent=2)}"
        
        return f"{request.prompt}{context_str}"
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.aclose()

# Factory function for easy instantiation
def create_deepseek_provider(api_key: str, **kwargs) -> DeepSeekProvider:
    """
    Create a DeepSeek provider instance
    
    Args:
        api_key: DeepSeek API key
        **kwargs: Additional configuration options
        
    Returns:
        DeepSeekProvider: Configured provider instance
    """
    config = ProviderConfig(
        api_key=api_key,
        base_url=kwargs.get('base_url'),
        model=kwargs.get('model', 'deepseek-chat'),
        max_retries=kwargs.get('max_retries', 3),
        timeout=kwargs.get('timeout', 30.0),
        rate_limit=kwargs.get('rate_limit'),
        custom_headers=kwargs.get('custom_headers')
    )
    
    return DeepSeekProvider(config)