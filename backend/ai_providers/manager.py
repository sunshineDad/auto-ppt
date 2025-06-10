"""
AI Provider Manager
Manages multiple AI providers with load balancing, fallback, and monitoring
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Type, Union
from enum import Enum
import time
import random
from dataclasses import dataclass, field

from .base import (
    BaseAIProvider, 
    AIProviderType, 
    AIRequest, 
    AIResponse, 
    ProviderConfig,
    AIProviderError
)
from .deepseek import DeepSeekProvider

logger = logging.getLogger(__name__)

class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_LOADED = "least_loaded"
    FASTEST_RESPONSE = "fastest_response"
    COST_OPTIMIZED = "cost_optimized"

@dataclass
class ProviderMetrics:
    """Metrics for a provider"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    total_cost: float = 0.0
    last_used: Optional[float] = None
    health_score: float = 1.0
    consecutive_failures: int = 0

@dataclass
class ProviderInstance:
    """Provider instance with metadata"""
    provider: BaseAIProvider
    config: ProviderConfig
    metrics: ProviderMetrics = field(default_factory=ProviderMetrics)
    is_healthy: bool = True
    priority: int = 1
    weight: float = 1.0

class AIProviderManager:
    """
    Manages multiple AI providers with advanced features:
    - Load balancing across providers
    - Automatic failover
    - Health monitoring
    - Cost optimization
    - Performance tracking
    """
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED):
        self.providers: Dict[str, ProviderInstance] = {}
        self.strategy = strategy
        self.round_robin_index = 0
        
        # Health monitoring
        self.health_check_interval = 300  # 5 minutes
        self.health_check_task = None
        self.unhealthy_threshold = 3  # consecutive failures
        
        # Circuit breaker
        self.circuit_breaker = {
            'failure_threshold': 5,
            'recovery_timeout': 60,
            'half_open_max_calls': 3
        }
        
        # Provider registry
        self.provider_classes: Dict[AIProviderType, Type[BaseAIProvider]] = {
            AIProviderType.DEEPSEEK: DeepSeekProvider,
            # Add more providers here as they're implemented
        }
        
        # Global metrics
        self.global_metrics = {
            'total_requests': 0,
            'total_successful': 0,
            'total_failed': 0,
            'total_cost': 0.0,
            'average_response_time': 0.0
        }
    
    async def add_provider(
        self, 
        name: str, 
        provider_type: AIProviderType, 
        config: ProviderConfig,
        priority: int = 1,
        weight: float = 1.0
    ) -> bool:
        """
        Add a new AI provider
        
        Args:
            name: Unique name for the provider
            provider_type: Type of AI provider
            config: Provider configuration
            priority: Priority level (higher = more preferred)
            weight: Weight for load balancing
            
        Returns:
            bool: True if provider added successfully
        """
        try:
            if name in self.providers:
                logger.warning(f"Provider {name} already exists, updating...")
            
            # Create provider instance
            provider_class = self.provider_classes.get(provider_type)
            if not provider_class:
                raise ValueError(f"Unsupported provider type: {provider_type}")
            
            provider = provider_class(config)
            
            # Initialize provider
            success = await provider.initialize()
            if not success:
                logger.error(f"Failed to initialize provider {name}")
                return False
            
            # Add to registry
            self.providers[name] = ProviderInstance(
                provider=provider,
                config=config,
                priority=priority,
                weight=weight
            )
            
            logger.info(f"✅ Added AI provider: {name} ({provider_type.value})")
            
            # Start health monitoring if this is the first provider
            if len(self.providers) == 1 and not self.health_check_task:
                self.health_check_task = asyncio.create_task(self._health_monitor())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add provider {name}: {e}")
            return False
    
    async def remove_provider(self, name: str) -> bool:
        """Remove a provider"""
        try:
            if name not in self.providers:
                logger.warning(f"Provider {name} not found")
                return False
            
            # Cleanup provider
            provider_instance = self.providers[name]
            if hasattr(provider_instance.provider, '__aexit__'):
                await provider_instance.provider.__aexit__(None, None, None)
            
            del self.providers[name]
            logger.info(f"Removed AI provider: {name}")
            
            # Stop health monitoring if no providers left
            if not self.providers and self.health_check_task:
                self.health_check_task.cancel()
                self.health_check_task = None
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove provider {name}: {e}")
            return False
    
    async def generate_completion(
        self, 
        request: AIRequest, 
        preferred_provider: Optional[str] = None,
        fallback: bool = True
    ) -> AIResponse:
        """
        Generate completion using the best available provider
        
        Args:
            request: AI request
            preferred_provider: Preferred provider name
            fallback: Whether to try other providers if preferred fails
            
        Returns:
            AIResponse: Generated response
        """
        start_time = time.time()
        
        try:
            # Get provider selection order
            providers = self._select_providers(preferred_provider, fallback)
            
            if not providers:
                raise AIProviderError("No healthy providers available")
            
            last_error = None
            
            # Try providers in order
            for provider_name in providers:
                try:
                    provider_instance = self.providers[provider_name]
                    
                    if not provider_instance.is_healthy:
                        continue
                    
                    # Generate completion
                    response = await provider_instance.provider.generate_completion(request)
                    
                    # Update metrics
                    response_time = time.time() - start_time
                    await self._update_provider_metrics(
                        provider_name, True, response_time, response.usage
                    )
                    
                    # Add provider info to response
                    response.metadata = response.metadata or {}
                    response.metadata['provider_name'] = provider_name
                    response.metadata['response_time'] = response_time
                    
                    return response
                    
                except Exception as e:
                    last_error = e
                    response_time = time.time() - start_time
                    await self._update_provider_metrics(
                        provider_name, False, response_time, {}
                    )
                    
                    logger.warning(f"Provider {provider_name} failed: {e}")
                    
                    if not fallback:
                        break
                    
                    continue
            
            # All providers failed
            self._update_global_metrics(False, time.time() - start_time)
            raise AIProviderError(f"All providers failed. Last error: {last_error}")
            
        except Exception as e:
            logger.error(f"Completion generation failed: {e}")
            raise
    
    async def generate_stream(
        self, 
        request: AIRequest, 
        preferred_provider: Optional[str] = None
    ):
        """Generate streaming completion"""
        try:
            provider_name = preferred_provider or self._select_best_provider()
            
            if not provider_name or provider_name not in self.providers:
                raise AIProviderError("No suitable provider for streaming")
            
            provider_instance = self.providers[provider_name]
            
            async for chunk in provider_instance.provider.generate_stream(request):
                yield chunk
                
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            yield f"Error: {str(e)}"
    
    async def estimate_cost(self, request: AIRequest) -> Dict[str, Any]:
        """Estimate cost across all providers"""
        estimates = {}
        
        for name, instance in self.providers.items():
            if instance.is_healthy:
                try:
                    estimate = await instance.provider.estimate_cost(request)
                    estimates[name] = estimate
                except Exception as e:
                    logger.warning(f"Cost estimation failed for {name}: {e}")
        
        return estimates
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        
        for name, instance in self.providers.items():
            try:
                health = await instance.provider.health_check()
                status[name] = {
                    **health,
                    'metrics': instance.metrics.__dict__,
                    'priority': instance.priority,
                    'weight': instance.weight,
                    'is_healthy': instance.is_healthy
                }
            except Exception as e:
                status[name] = {
                    'status': 'error',
                    'error': str(e),
                    'is_healthy': False
                }
        
        return status
    
    async def get_global_metrics(self) -> Dict[str, Any]:
        """Get global metrics across all providers"""
        return {
            **self.global_metrics,
            'active_providers': len([p for p in self.providers.values() if p.is_healthy]),
            'total_providers': len(self.providers),
            'strategy': self.strategy.value
        }
    
    def _select_providers(
        self, 
        preferred: Optional[str], 
        fallback: bool
    ) -> List[str]:
        """Select providers in order of preference"""
        if preferred and preferred in self.providers:
            if fallback:
                others = [name for name in self.providers.keys() if name != preferred]
                return [preferred] + self._order_providers(others)
            else:
                return [preferred]
        
        return self._order_providers(list(self.providers.keys()))
    
    def _order_providers(self, provider_names: List[str]) -> List[str]:
        """Order providers based on strategy"""
        healthy_providers = [
            name for name in provider_names 
            if self.providers[name].is_healthy
        ]
        
        if not healthy_providers:
            return []
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_order(healthy_providers)
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return self._random_order(healthy_providers)
        elif self.strategy == LoadBalancingStrategy.LEAST_LOADED:
            return self._least_loaded_order(healthy_providers)
        elif self.strategy == LoadBalancingStrategy.FASTEST_RESPONSE:
            return self._fastest_response_order(healthy_providers)
        elif self.strategy == LoadBalancingStrategy.COST_OPTIMIZED:
            return self._cost_optimized_order(healthy_providers)
        else:
            return healthy_providers
    
    def _round_robin_order(self, providers: List[str]) -> List[str]:
        """Round-robin ordering"""
        if not providers:
            return []
        
        self.round_robin_index = (self.round_robin_index + 1) % len(providers)
        return providers[self.round_robin_index:] + providers[:self.round_robin_index]
    
    def _random_order(self, providers: List[str]) -> List[str]:
        """Random ordering with weights"""
        weighted_providers = []
        for name in providers:
            instance = self.providers[name]
            weighted_providers.extend([name] * int(instance.weight * 10))
        
        random.shuffle(weighted_providers)
        return list(dict.fromkeys(weighted_providers))  # Remove duplicates, preserve order
    
    def _least_loaded_order(self, providers: List[str]) -> List[str]:
        """Order by least loaded (fewest active requests)"""
        return sorted(
            providers,
            key=lambda name: self.providers[name].metrics.total_requests - 
                           self.providers[name].metrics.successful_requests -
                           self.providers[name].metrics.failed_requests
        )
    
    def _fastest_response_order(self, providers: List[str]) -> List[str]:
        """Order by fastest average response time"""
        return sorted(
            providers,
            key=lambda name: self.providers[name].metrics.average_response_time
        )
    
    def _cost_optimized_order(self, providers: List[str]) -> List[str]:
        """Order by cost efficiency"""
        return sorted(
            providers,
            key=lambda name: self.providers[name].metrics.total_cost / 
                           max(self.providers[name].metrics.successful_requests, 1)
        )
    
    def _select_best_provider(self) -> Optional[str]:
        """Select the best provider based on current strategy"""
        ordered = self._order_providers(list(self.providers.keys()))
        return ordered[0] if ordered else None
    
    async def _update_provider_metrics(
        self, 
        provider_name: str, 
        success: bool, 
        response_time: float, 
        usage: Dict[str, Any]
    ):
        """Update provider metrics"""
        if provider_name not in self.providers:
            return
        
        instance = self.providers[provider_name]
        metrics = instance.metrics
        
        # Update request counts
        metrics.total_requests += 1
        if success:
            metrics.successful_requests += 1
            metrics.consecutive_failures = 0
        else:
            metrics.failed_requests += 1
            metrics.consecutive_failures += 1
        
        # Update response time
        if metrics.total_requests == 1:
            metrics.average_response_time = response_time
        else:
            metrics.average_response_time = (
                (metrics.average_response_time * (metrics.total_requests - 1) + response_time) /
                metrics.total_requests
            )
        
        # Update cost (if available)
        if 'cost' in usage:
            metrics.total_cost += usage['cost']
        
        # Update health score
        success_rate = metrics.successful_requests / metrics.total_requests
        metrics.health_score = success_rate * (1 - min(metrics.consecutive_failures / 10, 0.5))
        
        # Update health status
        if metrics.consecutive_failures >= self.unhealthy_threshold:
            instance.is_healthy = False
            logger.warning(f"Provider {provider_name} marked as unhealthy")
        
        metrics.last_used = time.time()
        
        # Update global metrics
        self._update_global_metrics(success, response_time)
    
    def _update_global_metrics(self, success: bool, response_time: float):
        """Update global metrics"""
        self.global_metrics['total_requests'] += 1
        
        if success:
            self.global_metrics['total_successful'] += 1
        else:
            self.global_metrics['total_failed'] += 1
        
        # Update average response time
        total = self.global_metrics['total_requests']
        current_avg = self.global_metrics['average_response_time']
        self.global_metrics['average_response_time'] = (
            (current_avg * (total - 1) + response_time) / total
        )
    
    async def _health_monitor(self):
        """Background health monitoring task"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                for name, instance in self.providers.items():
                    try:
                        health = await instance.provider.health_check()
                        
                        # Update health status
                        if health['status'] == 'healthy':
                            instance.is_healthy = True
                            instance.metrics.consecutive_failures = 0
                        else:
                            instance.metrics.consecutive_failures += 1
                            if instance.metrics.consecutive_failures >= self.unhealthy_threshold:
                                instance.is_healthy = False
                        
                    except Exception as e:
                        logger.error(f"Health check failed for {name}: {e}")
                        instance.metrics.consecutive_failures += 1
                        if instance.metrics.consecutive_failures >= self.unhealthy_threshold:
                            instance.is_healthy = False
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        # Cancel health monitoring
        if self.health_check_task:
            self.health_check_task.cancel()
        
        # Cleanup all providers
        for name in list(self.providers.keys()):
            await self.remove_provider(name)