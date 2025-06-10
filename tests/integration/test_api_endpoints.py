"""
Integration tests for API endpoints
Tests the complete API functionality including AI integration
"""

import pytest
import asyncio
import json
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, test_client):
        """Test basic health check endpoint"""
        response = await test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_ai_health_check(self, test_client):
        """Test AI-specific health check"""
        response = await test_client.get("/health/ai")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "ai_ready" in data
        assert "model_status" in data
        assert "providers" in data

class TestOperationEndpoints:
    """Test atomic operation endpoints"""
    
    @pytest.mark.asyncio
    async def test_process_operation(self, test_client, sample_atomic_operation):
        """Test processing an atomic operation"""
        response = await test_client.post(
            "/api/operations/process",
            json=sample_atomic_operation
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert "operation_id" in data
        assert "processing_time" in data
        assert data["success"] is True
    
    @pytest.mark.asyncio
    async def test_process_invalid_operation(self, test_client):
        """Test processing invalid operation data"""
        invalid_operation = {
            "operation": {},  # Missing required fields
            "presentationId": "",
            "slideIndex": -1
        }
        
        response = await test_client.post(
            "/api/operations/process",
            json=invalid_operation
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_get_recent_operations(self, test_client, sample_atomic_operation):
        """Test getting recent operations"""
        # First, create some operations
        for i in range(3):
            operation = sample_atomic_operation.copy()
            operation["operation"]["target"] = f"slide-{i}"
            await test_client.post("/api/operations/process", json=operation)
        
        # Get recent operations
        response = await test_client.get("/api/operations/recent?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 5
    
    @pytest.mark.asyncio
    async def test_get_operation_stats(self, test_client, sample_atomic_operation):
        """Test getting operation statistics"""
        # Create some test operations
        for i in range(5):
            operation = sample_atomic_operation.copy()
            operation["operation"]["op"] = "ADD" if i % 2 == 0 else "MODIFY"
            await test_client.post("/api/operations/process", json=operation)
        
        response = await test_client.get("/api/operations/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_operations" in data
        assert "operations_by_type" in data
        assert "operations_by_element" in data
        assert "recent_operations_24h" in data
        assert "average_execution_time_ms" in data
        assert data["total_operations"] >= 5

class TestPresentationEndpoints:
    """Test presentation management endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_presentation(self, test_client, sample_presentation_data):
        """Test creating a new presentation"""
        response = await test_client.post(
            "/api/presentations",
            json=sample_presentation_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "title" in data
        assert "created_at" in data
        assert data["title"] == sample_presentation_data["title"]
        
        return data["id"]  # Return for use in other tests
    
    @pytest.mark.asyncio
    async def test_get_presentation(self, test_client, sample_presentation_data):
        """Test getting a presentation by ID"""
        # First create a presentation
        create_response = await test_client.post(
            "/api/presentations",
            json=sample_presentation_data
        )
        presentation_id = create_response.json()["id"]
        
        # Get the presentation
        response = await test_client.get(f"/api/presentations/{presentation_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == presentation_id
        assert data["title"] == sample_presentation_data["title"]
        assert "slides" in data["data"]
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_presentation(self, test_client):
        """Test getting a non-existent presentation"""
        response = await test_client.get("/api/presentations/nonexistent-id")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_presentation(self, test_client, sample_presentation_data):
        """Test updating a presentation"""
        # Create presentation
        create_response = await test_client.post(
            "/api/presentations",
            json=sample_presentation_data
        )
        presentation_id = create_response.json()["id"]
        
        # Update presentation
        updated_data = sample_presentation_data.copy()
        updated_data["title"] = "Updated Test Presentation"
        updated_data["slides"].append({
            "id": "slide-2",
            "elements": []
        })
        
        response = await test_client.put(
            f"/api/presentations/{presentation_id}",
            json=updated_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == "Updated Test Presentation"
        assert data["slide_count"] == 2
    
    @pytest.mark.asyncio
    async def test_delete_presentation(self, test_client, sample_presentation_data):
        """Test deleting a presentation"""
        # Create presentation
        create_response = await test_client.post(
            "/api/presentations",
            json=sample_presentation_data
        )
        presentation_id = create_response.json()["id"]
        
        # Delete presentation
        response = await test_client.delete(f"/api/presentations/{presentation_id}")
        
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = await test_client.get(f"/api/presentations/{presentation_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_list_presentations(self, test_client, sample_presentation_data):
        """Test listing presentations"""
        # Create multiple presentations
        for i in range(3):
            presentation_data = sample_presentation_data.copy()
            presentation_data["title"] = f"Test Presentation {i}"
            await test_client.post("/api/presentations", json=presentation_data)
        
        # List presentations
        response = await test_client.get("/api/presentations?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 3

class TestAIEndpoints:
    """Test AI-related endpoints"""
    
    @pytest.mark.asyncio
    async def test_ai_predict_next_atom(self, test_client):
        """Test AI prediction endpoint"""
        context = {
            "currentSlide": {
                "id": "slide-1",
                "elements": []
            },
            "presentation": {
                "title": "Test Presentation"
            },
            "userBehavior": {
                "lastAction": "click",
                "frequency": 1
            }
        }
        
        response = await test_client.post(
            "/api/ai/predict",
            json={"context": context}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "atom" in data
        assert "confidence" in data
        assert "reasoning" in data
        assert "alternatives" in data
        
        # Validate atom structure
        atom = data["atom"]
        assert "op" in atom
        assert "type" in atom
    
    @pytest.mark.asyncio
    async def test_ai_generate_suggestions(self, test_client):
        """Test AI suggestions endpoint"""
        context = {
            "currentSlide": {"id": "slide-1", "elements": []},
            "presentation": {"title": "Business Report"},
            "userBehavior": {"lastAction": "click"}
        }
        
        response = await test_client.post(
            "/api/ai/suggestions",
            json={"context": context}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert len(data) <= 5  # Should limit suggestions
        
        # Each suggestion should be a valid operation
        for suggestion in data:
            assert "op" in suggestion
            assert "type" in suggestion
    
    @pytest.mark.asyncio
    async def test_ai_generate_presentation(self, test_client):
        """Test AI presentation generation"""
        request_data = {
            "prompt": "Create a business presentation about quarterly results",
            "presentation_type": "business",
            "slide_count": 5
        }
        
        response = await test_client.post(
            "/api/ai/generate-presentation",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "name" in data
        assert "atoms" in data
        assert "tags" in data
        
        assert len(data["atoms"]) > 0
        assert "business" in data["tags"]
    
    @pytest.mark.asyncio
    async def test_ai_suggest_template(self, test_client):
        """Test AI template suggestion"""
        response = await test_client.post(
            "/api/ai/suggest-template",
            json={"content": "sales revenue profit business quarterly"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "template" in data
        assert data["template"] == "business-report"
    
    @pytest.mark.asyncio
    async def test_ai_enhance_content(self, test_client):
        """Test AI content enhancement"""
        response = await test_client.post(
            "/api/ai/enhance-content",
            json={
                "element_id": "element-1",
                "content": "hello world"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "enhanced_content" in data
        assert data["enhanced_content"] == "Hello world."
    
    @pytest.mark.asyncio
    async def test_ai_metrics(self, test_client):
        """Test AI metrics endpoint"""
        response = await test_client.get("/api/ai/metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "model_ready" in data
        assert "training_samples" in data
        assert "total_predictions" in data
        assert "accuracy" in data
    
    @pytest.mark.asyncio
    async def test_ai_performance_metrics(self, test_client):
        """Test AI performance metrics endpoint"""
        response = await test_client.get("/api/ai/performance")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "prediction_accuracy" in data
        assert "total_predictions" in data
        assert "training_samples" in data
        assert "model_size" in data

class TestWebSocketEndpoints:
    """Test WebSocket functionality"""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, test_client):
        """Test WebSocket connection establishment"""
        # Note: This is a simplified test. In practice, you'd use a WebSocket test client
        # For now, we'll test the WebSocket manager directly
        from backend.websocket_manager import WebSocketManager
        
        manager = WebSocketManager()
        
        # Mock WebSocket
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        mock_websocket.close = AsyncMock()
        
        # Test connection
        await manager.connect(mock_websocket)
        assert len(manager.active_connections) == 1
        
        # Test broadcast
        await manager.broadcast({"type": "test", "data": "message"})
        mock_websocket.send_json.assert_called_once()
        
        # Test disconnect
        await manager.disconnect(mock_websocket)
        assert len(manager.active_connections) == 0

class TestErrorHandling:
    """Test error handling across endpoints"""
    
    @pytest.mark.asyncio
    async def test_invalid_json_request(self, test_client):
        """Test handling of invalid JSON requests"""
        response = await test_client.post(
            "/api/operations/process",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Unprocessable Entity
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, test_client):
        """Test handling of missing required fields"""
        incomplete_operation = {
            "operation": {
                # Missing required fields
            }
        }
        
        response = await test_client.post(
            "/api/operations/process",
            json=incomplete_operation
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, test_client):
        """Test handling of database errors"""
        # This would require mocking database failures
        # For now, we'll test that the endpoints are resilient
        
        # Try to get a presentation with an invalid ID format
        response = await test_client.get("/api/presentations/invalid-uuid-format")
        
        # Should return 404 or handle gracefully
        assert response.status_code in [404, 400]
    
    @pytest.mark.asyncio
    async def test_ai_service_unavailable(self, test_client):
        """Test handling when AI service is unavailable"""
        with patch('backend.ai_engine.AIEngine.predict_next_atom', side_effect=Exception("AI service down")):
            response = await test_client.post(
                "/api/ai/predict",
                json={"context": {"currentSlide": {"id": "slide-1"}}}
            )
            
            # Should handle AI service errors gracefully
            assert response.status_code in [200, 500, 503]

class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, test_client, sample_atomic_operation):
        """Test handling concurrent operations"""
        # Create multiple concurrent requests
        tasks = []
        for i in range(10):
            operation = sample_atomic_operation.copy()
            operation["operation"]["target"] = f"slide-{i}"
            task = test_client.post("/api/operations/process", json=operation)
            tasks.append(task)
        
        # Execute concurrently
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    @pytest.mark.asyncio
    async def test_large_presentation_handling(self, test_client):
        """Test handling of large presentations"""
        # Create a presentation with many slides and elements
        large_presentation = {
            "title": "Large Test Presentation",
            "slides": [
                {
                    "id": f"slide-{i}",
                    "elements": [
                        {
                            "id": f"element-{i}-{j}",
                            "type": "text",
                            "content": f"Content {i}-{j}",
                            "position": {"x": j * 100, "y": i * 100}
                        }
                        for j in range(20)  # 20 elements per slide
                    ]
                }
                for i in range(50)  # 50 slides
            ],
            "theme": {"name": "default"},
            "metadata": {
                "author": "test-user",
                "version": "1.0.0",
                "tags": ["test", "large"]
            }
        }
        
        response = await test_client.post(
            "/api/presentations",
            json=large_presentation
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["slide_count"] == 50
        assert data["element_count"] == 1000  # 50 * 20
    
    @pytest.mark.asyncio
    async def test_response_time_limits(self, test_client):
        """Test that responses come within reasonable time limits"""
        import time
        
        start_time = time.time()
        
        response = await test_client.get("/health")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second

class TestDataIntegrity:
    """Test data integrity and consistency"""
    
    @pytest.mark.asyncio
    async def test_operation_data_consistency(self, test_client, sample_atomic_operation):
        """Test that operation data is stored and retrieved consistently"""
        # Process an operation
        response = await test_client.post(
            "/api/operations/process",
            json=sample_atomic_operation
        )
        
        assert response.status_code == 200
        operation_id = response.json()["operation_id"]
        
        # Get recent operations and verify our operation is there
        recent_response = await test_client.get("/api/operations/recent?limit=10")
        recent_operations = recent_response.json()
        
        # Find our operation
        our_operation = None
        for op in recent_operations:
            if op["id"] == operation_id:
                our_operation = op
                break
        
        assert our_operation is not None
        assert our_operation["operation"] == sample_atomic_operation["operation"]["op"]
        assert our_operation["element_type"] == sample_atomic_operation["operation"]["type"]
    
    @pytest.mark.asyncio
    async def test_presentation_data_consistency(self, test_client, sample_presentation_data):
        """Test that presentation data is stored and retrieved consistently"""
        # Create presentation
        create_response = await test_client.post(
            "/api/presentations",
            json=sample_presentation_data
        )
        
        presentation_id = create_response.json()["id"]
        
        # Retrieve presentation
        get_response = await test_client.get(f"/api/presentations/{presentation_id}")
        retrieved_data = get_response.json()
        
        # Verify data consistency
        assert retrieved_data["title"] == sample_presentation_data["title"]
        assert len(retrieved_data["data"]["slides"]) == len(sample_presentation_data["slides"])
        assert retrieved_data["data"]["theme"] == sample_presentation_data["theme"]
        assert retrieved_data["data"]["metadata"] == sample_presentation_data["metadata"]