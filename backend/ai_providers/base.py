"""
Base AI Provider Interface
Defines the contract for all AI providers in the system
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AIProviderType(Enum):
    """Supported AI provider types"""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"

@dataclass
class AIRequest:
    """Standardized AI request structure"""
    prompt: str
    context: Dict[str, Any]
    operation_type: str
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    stream: bool = False
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AIResponse:
    """Standardized AI response structure"""
    content: str
    confidence: float
    reasoning: str
    alternatives: List[Dict[str, Any]]
    usage: Dict[str, Any]
    provider: str
    model: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProviderConfig:
    """Configuration for AI providers"""
    api_key: str
    base_url: Optional[str] = None
    model: Optional[str] = None
    max_retries: int = 3
    timeout: float = 30.0
    rate_limit: Optional[Dict[str, Any]] = None
    custom_headers: Optional[Dict[str, str]] = None

class AIProviderError(Exception):
    """Base exception for AI provider errors"""
    pass

class AuthenticationError(AIProviderError):
    """Authentication failed"""
    pass

class RateLimitError(AIProviderError):
    """Rate limit exceeded"""
    pass

class ModelError(AIProviderError):
    """Model-specific error"""
    pass

class NetworkError(AIProviderError):
    """Network-related error"""
    pass

class BaseAIProvider(ABC):
    """
    Abstract base class for all AI providers
    
    This class defines the interface that all AI providers must implement
    to ensure consistent behavior across different AI services.
    """
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.provider_type = self._get_provider_type()
        self.is_initialized = False
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens_used': 0,
            'average_response_time': 0.0,
            'rate_limit_hits': 0
        }
    
    @abstractmethod
    def _get_provider_type(self) -> AIProviderType:
        """Return the provider type"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the AI provider
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def generate_completion(self, request: AIRequest) -> AIResponse:
        """
        Generate AI completion for the given request
        
        Args:
            request: Standardized AI request
            
        Returns:
            AIResponse: Standardized AI response
            
        Raises:
            AIProviderError: If generation fails
        """
        pass
    
    @abstractmethod
    async def generate_stream(self, request: AIRequest) -> AsyncGenerator[str, None]:
        """
        Generate streaming AI completion
        
        Args:
            request: Standardized AI request
            
        Yields:
            str: Partial response chunks
            
        Raises:
            AIProviderError: If streaming fails
        """
        pass
    
    @abstractmethod
    async def validate_api_key(self) -> bool:
        """
        Validate the API key
        
        Returns:
            bool: True if API key is valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """
        Get list of available models
        
        Returns:
            List[str]: Available model names
        """
        pass
    
    @abstractmethod
    async def estimate_cost(self, request: AIRequest) -> Dict[str, Any]:
        """
        Estimate the cost for a request
        
        Args:
            request: AI request to estimate
            
        Returns:
            Dict containing cost estimation details
        """
        pass
    
    # Common utility methods
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the provider
        
        Returns:
            Dict containing health status
        """
        try:
            is_valid = await self.validate_api_key()
            models = await self.get_available_models()
            
            return {
                'status': 'healthy' if is_valid else 'unhealthy',
                'provider': self.provider_type.value,
                'api_key_valid': is_valid,
                'available_models': len(models),
                'initialized': self.is_initialized,
                'metrics': self.metrics
            }
        except Exception as e:
            logger.error(f"Health check failed for {self.provider_type.value}: {e}")
            return {
                'status': 'unhealthy',
                'provider': self.provider_type.value,
                'error': str(e),
                'initialized': self.is_initialized
            }
    
    def update_metrics(self, success: bool, tokens_used: int, response_time: float):
        """Update provider metrics"""
        self.metrics['total_requests'] += 1
        if success:
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
        
        self.metrics['total_tokens_used'] += tokens_used
        
        # Update average response time
        total_requests = self.metrics['total_requests']
        current_avg = self.metrics['average_response_time']
        self.metrics['average_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get provider metrics"""
        success_rate = 0.0
        if self.metrics['total_requests'] > 0:
            success_rate = (
                self.metrics['successful_requests'] / self.metrics['total_requests']
            ) * 100
        
        return {
            **self.metrics,
            'success_rate': success_rate,
            'provider': self.provider_type.value,
            'model': self.config.model
        }
    
    def _create_error_response(self, error: Exception, request: AIRequest) -> AIResponse:
        """Create error response"""
        return AIResponse(
            content=f"Error: {str(error)}",
            confidence=0.0,
            reasoning=f"Request failed due to: {type(error).__name__}",
            alternatives=[],
            usage={'error': True, 'tokens': 0},
            provider=self.provider_type.value,
            model=self.config.model or "unknown",
            metadata={'error': str(error), 'error_type': type(error).__name__}
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Cleanup if needed
        pass