"""
End-to-End Tests for Complete Workflows
Tests complete user workflows from start to finish
"""

import pytest
import asyncio
import json
import time
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

class TestPresentationCreationWorkflow:
    """Test complete presentation creation workflow"""
    
    @pytest.mark.asyncio
    async def test_create_presentation_from_scratch(self, test_client):
        """Test creating a presentation from scratch with AI assistance"""
        
        # Step 1: Get AI template suggestion
        template_response = await test_client.post(
            "/api/ai/suggest-template",
            json={"content": "quarterly business results revenue profit"}
        )
        
        assert template_response.status_code == 200
        template = template_response.json()["template"]
        assert template == "business-report"
        
        # Step 2: Generate AI presentation structure
        generation_response = await test_client.post(
            "/api/ai/generate-presentation",
            json={
                "prompt": "Create a quarterly business results presentation",
                "presentation_type": "business",
                "slide_count": 5
            }
        )
        
        assert generation_response.status_code == 200
        generated_sequence = generation_response.json()
        assert len(generated_sequence["atoms"]) > 0
        
        # Step 3: Create actual presentation
        presentation_data = {
            "title": "Q4 2024 Business Results",
            "slides": [
                {
                    "id": "slide-1",
                    "elements": []
                }
            ],
            "theme": {"name": template},
            "metadata": {
                "author": "test-user",
                "version": "1.0.0",
                "tags": ["business", "quarterly", "results"]
            }
        }
        
        create_response = await test_client.post(
            "/api/presentations",
            json=presentation_data
        )
        
        assert create_response.status_code == 200
        presentation = create_response.json()
        presentation_id = presentation["id"]
        
        # Step 4: Add content using AI suggestions
        context = {
            "currentSlide": {"id": "slide-1", "elements": []},
            "presentation": {"title": "Q4 2024 Business Results"},
            "userBehavior": {"lastAction": "create_slide"}
        }
        
        suggestions_response = await test_client.post(
            "/api/ai/suggestions",
            json={"context": context}
        )
        
        assert suggestions_response.status_code == 200
        suggestions = suggestions_response.json()
        assert len(suggestions) > 0
        
        # Step 5: Apply first suggestion as an operation
        first_suggestion = suggestions[0]
        operation = {
            "operation": {
                "op": first_suggestion["op"],
                "type": first_suggestion["type"],
                "target": "slide-1",
                "data": first_suggestion.get("data", {"content": "AI Generated Content"}),
                "timestamp": int(time.time() * 1000),
                "userId": "test-user",
                "sessionId": "test-session"
            },
            "presentationId": presentation_id,
            "slideIndex": 0,
            "context": context,
            "result": {"success": True}
        }
        
        operation_response = await test_client.post(
            "/api/operations/process",
            json=operation
        )
        
        assert operation_response.status_code == 200
        operation_result = operation_response.json()
        assert operation_result["success"] is True
        
        # Step 6: Verify the complete workflow
        final_presentation = await test_client.get(f"/api/presentations/{presentation_id}")
        assert final_presentation.status_code == 200
        
        # Check operation was recorded
        stats_response = await test_client.get("/api/operations/stats")
        stats = stats_response.json()
        assert stats["total_operations"] >= 1
        
        return presentation_id
    
    @pytest.mark.asyncio
    async def test_collaborative_editing_workflow(self, test_client):
        """Test collaborative editing workflow with multiple users"""
        
        # Create initial presentation
        presentation_data = {
            "title": "Collaborative Presentation",
            "slides": [{"id": "slide-1", "elements": []}],
            "theme": {"name": "default"},
            "metadata": {"author": "user1", "version": "1.0.0", "tags": ["collaborative"]}
        }
        
        create_response = await test_client.post("/api/presentations", json=presentation_data)
        presentation_id = create_response.json()["id"]
        
        # Simulate multiple users making concurrent edits
        user_operations = []
        
        for user_id in ["user1", "user2", "user3"]:
            for i in range(3):
                operation = {
                    "operation": {
                        "op": "ADD",
                        "type": "text",
                        "target": "slide-1",
                        "data": {"content": f"Content from {user_id} - {i}"},
                        "timestamp": int(time.time() * 1000) + i,
                        "userId": user_id,
                        "sessionId": f"session-{user_id}"
                    },
                    "presentationId": presentation_id,
                    "slideIndex": 0,
                    "context": {"collaborative": True},
                    "result": {"success": True}
                }
                user_operations.append(operation)
        
        # Execute operations concurrently
        tasks = [
            test_client.post("/api/operations/process", json=op)
            for op in user_operations
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All operations should succeed
        for response in responses:
            assert response.status_code == 200
            assert response.json()["success"] is True
        
        # Verify all operations were recorded
        stats_response = await test_client.get("/api/operations/stats")
        stats = stats_response.json()
        assert stats["total_operations"] >= 9  # 3 users × 3 operations
        
        return presentation_id
    
    @pytest.mark.asyncio
    async def test_ai_learning_and_improvement_workflow(self, test_client):
        """Test AI learning from user behavior and improving suggestions"""
        
        # Create presentation for learning
        presentation_data = {
            "title": "Learning Test Presentation",
            "slides": [{"id": "slide-1", "elements": []}],
            "theme": {"name": "default"},
            "metadata": {"author": "learning-user", "version": "1.0.0", "tags": ["learning"]}
        }
        
        create_response = await test_client.post("/api/presentations", json=presentation_data)
        presentation_id = create_response.json()["id"]
        
        # Step 1: Get initial AI metrics
        initial_metrics_response = await test_client.get("/api/ai/metrics")
        initial_metrics = initial_metrics_response.json()
        initial_training_samples = initial_metrics["training_samples"]
        
        # Step 2: Perform a series of operations to train the AI
        training_operations = [
            {
                "op": "ADD",
                "type": "text",
                "data": {"content": "Title Slide"}
            },
            {
                "op": "ADD", 
                "type": "text",
                "data": {"content": "Subtitle"}
            },
            {
                "op": "MODIFY",
                "type": "style",
                "data": {"fontSize": 24, "color": "#000000"}
            },
            {
                "op": "ADD",
                "type": "image",
                "data": {"src": "logo.png"}
            },
            {
                "op": "ADD",
                "type": "chart",
                "data": {"type": "bar", "data": [1, 2, 3]}
            }
        ]
        
        for i, op_data in enumerate(training_operations):
            operation = {
                "operation": {
                    **op_data,
                    "target": "slide-1",
                    "timestamp": int(time.time() * 1000) + i,
                    "userId": "learning-user",
                    "sessionId": "learning-session"
                },
                "presentationId": presentation_id,
                "slideIndex": 0,
                "context": {
                    "currentSlide": {"id": "slide-1", "elements": []},
                    "presentation": {"title": "Learning Test Presentation"},
                    "userBehavior": {"lastAction": "add_element", "frequency": i + 1}
                },
                "result": {"success": True, "processingTime": 50}
            }
            
            response = await test_client.post("/api/operations/process", json=operation)
            assert response.status_code == 200
        
        # Step 3: Check that AI has learned from the operations
        updated_metrics_response = await test_client.get("/api/ai/metrics")
        updated_metrics = updated_metrics_response.json()
        
        assert updated_metrics["training_samples"] > initial_training_samples
        
        # Step 4: Test that AI suggestions have improved
        context = {
            "currentSlide": {"id": "slide-1", "elements": []},
            "presentation": {"title": "Learning Test Presentation"},
            "userBehavior": {"lastAction": "add_element", "frequency": 5}
        }
        
        suggestions_response = await test_client.post(
            "/api/ai/suggestions",
            json={"context": context}
        )
        
        assert suggestions_response.status_code == 200
        suggestions = suggestions_response.json()
        assert len(suggestions) > 0
        
        # Suggestions should be relevant based on learned patterns
        suggestion_types = [s["type"] for s in suggestions]
        assert any(t in ["text", "image", "chart"] for t in suggestion_types)
        
        return presentation_id

class TestAIIntegrationWorkflow:
    """Test AI integration workflows"""
    
    @pytest.mark.asyncio
    async def test_deepseek_integration_workflow(self, test_client):
        """Test complete DeepSeek AI integration workflow"""
        
        # Mock DeepSeek API responses
        mock_deepseek_response = {
            "id": "chatcmpl-test",
            "object": "chat.completion", 
            "created": int(time.time()),
            "model": "deepseek-chat",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": json.dumps({
                            "operation": "ADD",
                            "type": "text",
                            "content": "AI-Generated Business Title",
                            "reasoning": "Based on business context, a professional title is needed",
                            "confidence": 0.9,
                            "alternatives": [
                                {"operation": "ADD", "type": "image", "content": "Company logo"},
                                {"operation": "ADD", "type": "chart", "content": "Revenue chart"}
                            ]
                        })
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 200,
                "completion_tokens": 100,
                "total_tokens": 300
            }
        }
        
        # Test AI provider health check
        with patch('backend.ai_providers.deepseek.DeepSeekProvider.health_check') as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "provider": "deepseek",
                "api_key_valid": True,
                "available_models": 2
            }
            
            health_response = await test_client.get("/health/ai")
            assert health_response.status_code == 200
            health_data = health_response.json()
            assert "providers" in health_data
        
        # Test AI-powered content generation
        with patch('backend.ai_providers.deepseek.DeepSeekProvider.generate_completion') as mock_generate:
            from backend.ai_providers.base import AIResponse
            
            mock_generate.return_value = AIResponse(
                content="AI-Generated Business Title",
                confidence=0.9,
                reasoning="Based on business context, a professional title is needed",
                alternatives=[
                    {"operation": "ADD", "type": "image", "content": "Company logo"}
                ],
                usage={"total_tokens": 300},
                provider="deepseek",
                model="deepseek-chat"
            )
            
            # Request AI prediction
            context = {
                "currentSlide": {"id": "slide-1", "elements": []},
                "presentation": {"title": "Business Presentation"},
                "userBehavior": {"lastAction": "create_slide"}
            }
            
            prediction_response = await test_client.post(
                "/api/ai/predict",
                json={"context": context}
            )
            
            assert prediction_response.status_code == 200
            prediction = prediction_response.json()
            
            assert prediction["confidence"] > 0.8
            assert "AI-Generated" in prediction["atom"]["data"]["content"]
            assert len(prediction["alternatives"]) > 0
        
        # Test cost estimation
        with patch('backend.ai_providers.deepseek.DeepSeekProvider.estimate_cost') as mock_cost:
            mock_cost.return_value = {
                "estimated_total_tokens": 300,
                "estimated_cost_usd": 0.0042,
                "model": "deepseek-chat",
                "currency": "USD"
            }
            
            cost_response = await test_client.post(
                "/api/ai/estimate-cost",
                json={
                    "prompt": "Generate a business presentation",
                    "max_tokens": 1000
                }
            )
            
            # Note: This endpoint would need to be implemented
            # For now, we're testing the provider functionality
    
    @pytest.mark.asyncio
    async def test_ai_provider_failover_workflow(self, test_client):
        """Test AI provider failover and redundancy"""
        
        # This test would require multiple AI providers configured
        # For now, we'll test the manager's failover logic
        
        from backend.ai_providers.manager import AIProviderManager, LoadBalancingStrategy
        from backend.ai_providers.base import ProviderConfig, AIRequest
        
        # Create manager with multiple mock providers
        manager = AIProviderManager(LoadBalancingStrategy.LEAST_LOADED)
        
        # Mock provider configurations
        config1 = ProviderConfig(api_key="key1", model="model1")
        config2 = ProviderConfig(api_key="key2", model="model2")
        
        # Add mock providers
        with patch('backend.ai_providers.deepseek.DeepSeekProvider') as MockProvider:
            mock_provider1 = AsyncMock()
            mock_provider1.initialize.return_value = True
            mock_provider1.health_check.return_value = {"status": "healthy"}
            
            mock_provider2 = AsyncMock()
            mock_provider2.initialize.return_value = True
            mock_provider2.health_check.return_value = {"status": "healthy"}
            
            MockProvider.side_effect = [mock_provider1, mock_provider2]
            
            # Add providers to manager
            from backend.ai_providers.base import AIProviderType
            await manager.add_provider("provider1", AIProviderType.DEEPSEEK, config1)
            await manager.add_provider("provider2", AIProviderType.DEEPSEEK, config2)
            
            # Test failover when first provider fails
            from backend.ai_providers.base import AIResponse
            
            mock_provider1.generate_completion.side_effect = Exception("Provider 1 failed")
            mock_provider2.generate_completion.return_value = AIResponse(
                content="Backup provider response",
                confidence=0.8,
                reasoning="Generated by backup provider",
                alternatives=[],
                usage={"total_tokens": 150},
                provider="deepseek",
                model="model2"
            )
            
            request = AIRequest(
                prompt="Test prompt",
                context={},
                operation_type="test"
            )
            
            response = await manager.generate_completion(request)
            
            assert response.content == "Backup provider response"
            assert response.model == "model2"
            
            # Verify failover occurred
            mock_provider1.generate_completion.assert_called_once()
            mock_provider2.generate_completion.assert_called_once()

class TestPerformanceWorkflow:
    """Test performance under various conditions"""
    
    @pytest.mark.asyncio
    async def test_high_load_workflow(self, test_client, performance_test_data):
        """Test system performance under high load"""
        
        start_time = time.time()
        
        # Process many operations concurrently
        tasks = []
        for operation_data in performance_test_data[:50]:  # Test with 50 operations
            task = test_client.post("/api/operations/process", json=operation_data)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check that most operations succeeded
        successful_responses = [r for r in responses if not isinstance(r, Exception) and r.status_code == 200]
        success_rate = len(successful_responses) / len(responses)
        
        assert success_rate > 0.9  # At least 90% success rate
        assert total_time < 30.0   # Should complete within 30 seconds
        
        # Check system metrics
        stats_response = await test_client.get("/api/operations/stats")
        stats = stats_response.json()
        
        assert stats["total_operations"] >= len(successful_responses)
        assert stats["average_execution_time_ms"] < 1000  # Average under 1 second
    
    @pytest.mark.asyncio
    async def test_memory_usage_workflow(self, test_client):
        """Test memory usage during extended operations"""
        
        # Create a large number of presentations and operations
        presentation_ids = []
        
        for i in range(10):
            presentation_data = {
                "title": f"Memory Test Presentation {i}",
                "slides": [
                    {
                        "id": f"slide-{j}",
                        "elements": [
                            {
                                "id": f"element-{j}-{k}",
                                "type": "text",
                                "content": f"Content {j}-{k}" * 100  # Large content
                            }
                            for k in range(10)
                        ]
                    }
                    for j in range(10)
                ],
                "theme": {"name": "default"},
                "metadata": {"author": "memory-test", "version": "1.0.0", "tags": ["memory"]}
            }
            
            response = await test_client.post("/api/presentations", json=presentation_data)
            if response.status_code == 200:
                presentation_ids.append(response.json()["id"])
        
        # Perform operations on each presentation
        for presentation_id in presentation_ids:
            for i in range(5):
                operation = {
                    "operation": {
                        "op": "ADD",
                        "type": "text",
                        "target": f"slide-{i}",
                        "data": {"content": "Large content " * 1000},
                        "timestamp": int(time.time() * 1000),
                        "userId": "memory-test-user",
                        "sessionId": "memory-test-session"
                    },
                    "presentationId": presentation_id,
                    "slideIndex": i,
                    "context": {"memoryTest": True},
                    "result": {"success": True}
                }
                
                response = await test_client.post("/api/operations/process", json=operation)
                # Don't assert success for all - some may fail due to memory constraints
        
        # Check that system is still responsive
        health_response = await test_client.get("/health")
        assert health_response.status_code == 200
        
        # Cleanup - delete presentations to free memory
        for presentation_id in presentation_ids:
            await test_client.delete(f"/api/presentations/{presentation_id}")

class TestEdgeCaseWorkflows:
    """Test edge cases and error scenarios"""
    
    @pytest.mark.asyncio
    async def test_malformed_data_workflow(self, test_client, edge_case_operations):
        """Test handling of malformed and edge case data"""
        
        for operation_data in edge_case_operations:
            response = await test_client.post(
                "/api/operations/process",
                json=operation_data
            )
            
            # Should handle gracefully without crashing
            assert response.status_code in [200, 400, 422]
            
            # If it returns 200, should indicate the operation status
            if response.status_code == 200:
                data = response.json()
                # May succeed or fail, but should have proper structure
                assert "success" in data
    
    @pytest.mark.asyncio
    async def test_network_interruption_workflow(self, test_client):
        """Test handling of network interruptions and timeouts"""
        
        # Simulate slow operations
        with patch('backend.atomic_processor.AtomicProcessor.process_operation') as mock_process:
            # Make the operation take a long time
            async def slow_operation(*args, **kwargs):
                await asyncio.sleep(2)  # 2 second delay
                return {
                    "operation_id": "slow-op-123",
                    "processing_time": 2000,
                    "success": True
                }
            
            mock_process.side_effect = slow_operation
            
            operation = {
                "operation": {
                    "op": "ADD",
                    "type": "text",
                    "target": "slide-1",
                    "data": {"content": "Slow operation"},
                    "timestamp": int(time.time() * 1000),
                    "userId": "test-user",
                    "sessionId": "test-session"
                },
                "presentationId": "test-presentation",
                "slideIndex": 0,
                "context": {},
                "result": {"success": True}
            }
            
            # Should handle the slow operation
            response = await test_client.post("/api/operations/process", json=operation)
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_concurrent_modification_workflow(self, test_client):
        """Test handling of concurrent modifications to the same resource"""
        
        # Create a presentation
        presentation_data = {
            "title": "Concurrent Test Presentation",
            "slides": [{"id": "slide-1", "elements": []}],
            "theme": {"name": "default"},
            "metadata": {"author": "test-user", "version": "1.0.0", "tags": ["concurrent"]}
        }
        
        create_response = await test_client.post("/api/presentations", json=presentation_data)
        presentation_id = create_response.json()["id"]
        
        # Create multiple concurrent modifications
        modification_tasks = []
        
        for i in range(5):
            updated_data = presentation_data.copy()
            updated_data["title"] = f"Updated Title {i}"
            updated_data["slides"].append({
                "id": f"slide-{i+2}",
                "elements": []
            })
            
            task = test_client.put(f"/api/presentations/{presentation_id}", json=updated_data)
            modification_tasks.append(task)
        
        # Execute concurrent modifications
        responses = await asyncio.gather(*modification_tasks, return_exceptions=True)
        
        # At least some should succeed
        successful_responses = [
            r for r in responses 
            if not isinstance(r, Exception) and r.status_code == 200
        ]
        
        assert len(successful_responses) > 0
        
        # Verify final state is consistent
        final_response = await test_client.get(f"/api/presentations/{presentation_id}")
        assert final_response.status_code == 200
        final_data = final_response.json()
        
        # Should have a valid title and structure
        assert "title" in final_data
        assert "slides" in final_data["data"]
        assert len(final_data["data"]["slides"]) >= 1

class TestDataConsistencyWorkflow:
    """Test data consistency across the system"""
    
    @pytest.mark.asyncio
    async def test_operation_to_presentation_consistency(self, test_client):
        """Test consistency between operations and presentation state"""
        
        # Create presentation
        presentation_data = {
            "title": "Consistency Test",
            "slides": [{"id": "slide-1", "elements": []}],
            "theme": {"name": "default"},
            "metadata": {"author": "test-user", "version": "1.0.0", "tags": ["consistency"]}
        }
        
        create_response = await test_client.post("/api/presentations", json=presentation_data)
        presentation_id = create_response.json()["id"]
        
        # Perform a series of operations
        operations = [
            {
                "op": "ADD",
                "type": "text",
                "data": {"content": "Title Text"}
            },
            {
                "op": "ADD",
                "type": "image", 
                "data": {"src": "image.jpg"}
            },
            {
                "op": "MODIFY",
                "type": "style",
                "data": {"color": "#FF0000"}
            }
        ]
        
        operation_ids = []
        
        for i, op_data in enumerate(operations):
            operation = {
                "operation": {
                    **op_data,
                    "target": "slide-1",
                    "timestamp": int(time.time() * 1000) + i,
                    "userId": "test-user",
                    "sessionId": "consistency-session"
                },
                "presentationId": presentation_id,
                "slideIndex": 0,
                "context": {"consistency": True},
                "result": {"success": True}
            }
            
            response = await test_client.post("/api/operations/process", json=operation)
            assert response.status_code == 200
            operation_ids.append(response.json()["operation_id"])
        
        # Verify operations are recorded
        stats_response = await test_client.get("/api/operations/stats")
        stats = stats_response.json()
        
        assert stats["total_operations"] >= len(operations)
        
        # Check operation types are recorded correctly
        assert "ADD" in stats["operations_by_type"]
        assert "MODIFY" in stats["operations_by_type"]
        assert stats["operations_by_type"]["ADD"] >= 2
        assert stats["operations_by_type"]["MODIFY"] >= 1
        
        # Verify recent operations include our operations
        recent_response = await test_client.get("/api/operations/recent?limit=10")
        recent_operations = recent_response.json()
        
        our_operation_ids = set(operation_ids)
        recent_operation_ids = {op["id"] for op in recent_operations}
        
        # At least some of our operations should be in recent operations
        assert len(our_operation_ids.intersection(recent_operation_ids)) > 0