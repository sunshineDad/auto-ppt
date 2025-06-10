"""
Pytest configuration and fixtures for AI-PPT System testing
"""

import pytest
import asyncio
import tempfile
import os
import json
from typing import Dict, Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import backend modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
from database import Base, get_db
from ai_engine import AIEngine
from atomic_processor import AtomicProcessor
from models import AtomicOperation, Presentation

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_ai_ppt.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

@pytest.fixture
async def test_client(db_session):
    """Create test client with dependency overrides"""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sync_test_client():
    """Create synchronous test client for simple tests"""
    return TestClient(app)

@pytest.fixture
async def ai_engine():
    """Create AI engine instance for testing"""
    engine = AIEngine()
    await engine.initialize()
    return engine

@pytest.fixture
async def atomic_processor():
    """Create atomic processor instance for testing"""
    return AtomicProcessor()

@pytest.fixture
def sample_presentation_data():
    """Sample presentation data for testing"""
    return {
        "title": "Test Presentation",
        "slides": [
            {
                "id": "slide-1",
                "elements": [
                    {
                        "id": "element-1",
                        "type": "text",
                        "content": "Hello World",
                        "position": {"x": 100, "y": 100},
                        "style": {"fontSize": 24, "color": "#000000"}
                    }
                ]
            }
        ],
        "theme": {
            "name": "default",
            "colors": {
                "primary": "#007bff",
                "secondary": "#6c757d"
            }
        },
        "metadata": {
            "author": "test-user",
            "version": "1.0.0",
            "tags": ["test", "sample"]
        }
    }

@pytest.fixture
def sample_atomic_operation():
    """Sample atomic operation for testing"""
    return {
        "operation": {
            "op": "ADD",
            "type": "text",
            "target": "slide-1",
            "data": {
                "content": "New text element",
                "position": {"x": 200, "y": 200},
                "style": {"fontSize": 18, "color": "#333333"}
            },
            "timestamp": 1640995200000,  # 2022-01-01 00:00:00
            "userId": "test-user",
            "sessionId": "test-session"
        },
        "presentationId": "test-presentation",
        "slideIndex": 0,
        "context": {
            "currentSlide": {"id": "slide-1", "elements": []},
            "presentation": {"title": "Test Presentation"},
            "userBehavior": {"lastAction": "click", "frequency": 1}
        },
        "result": {
            "success": True,
            "elementId": "element-new",
            "processingTime": 50
        }
    }

@pytest.fixture
def mock_deepseek_response():
    """Mock DeepSeek API response"""
    return {
        "id": "chatcmpl-test",
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
                        "content": "AI generated content",
                        "reasoning": "Based on the context, adding text would be appropriate",
                        "confidence": 0.85
                    })
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }

@pytest.fixture
def temp_file():
    """Create temporary file for testing"""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection for testing"""
    mock_ws = AsyncMock()
    mock_ws.accept = AsyncMock()
    mock_ws.send_text = AsyncMock()
    mock_ws.send_json = AsyncMock()
    mock_ws.receive_text = AsyncMock()
    mock_ws.receive_json = AsyncMock()
    mock_ws.close = AsyncMock()
    return mock_ws

@pytest.fixture
def performance_test_data():
    """Generate performance test data"""
    operations = []
    for i in range(100):
        operations.append({
            "operation": {
                "op": "ADD" if i % 2 == 0 else "MODIFY",
                "type": "text",
                "target": f"slide-{i % 5}",
                "data": {"content": f"Test content {i}"},
                "timestamp": 1640995200000 + i * 1000,
                "userId": "perf-test-user",
                "sessionId": "perf-test-session"
            },
            "presentationId": "perf-test-presentation",
            "slideIndex": i % 5,
            "context": {"test": True},
            "result": {"success": True}
        })
    return operations

@pytest.fixture
def edge_case_operations():
    """Edge case operations for testing"""
    return [
        # Empty operation
        {
            "operation": {},
            "presentationId": "",
            "slideIndex": -1,
            "context": None,
            "result": {"success": False}
        },
        # Invalid data types
        {
            "operation": {
                "op": None,
                "type": 123,
                "target": [],
                "data": "invalid",
                "timestamp": "not-a-number",
                "userId": None,
                "sessionId": False
            },
            "presentationId": None,
            "slideIndex": "invalid",
            "context": "not-a-dict",
            "result": None
        },
        # Extremely large data
        {
            "operation": {
                "op": "ADD",
                "type": "text",
                "target": "slide-1",
                "data": {"content": "x" * 10000},  # Very large content
                "timestamp": 1640995200000,
                "userId": "test-user",
                "sessionId": "test-session"
            },
            "presentationId": "test-presentation",
            "slideIndex": 0,
            "context": {"large_data": list(range(1000))},
            "result": {"success": True}
        }
    ]

# Utility functions for tests
def assert_operation_structure(operation: Dict[str, Any]):
    """Assert that operation has required structure"""
    assert "operation" in operation
    assert "op" in operation["operation"]
    assert "type" in operation["operation"]
    assert "target" in operation["operation"]

def assert_api_response_structure(response: Dict[str, Any]):
    """Assert that API response has required structure"""
    assert "success" in response
    assert "data" in response or "error" in response

def create_test_presentation(title: str = "Test Presentation") -> Dict[str, Any]:
    """Create a test presentation with standard structure"""
    return {
        "title": title,
        "slides": [
            {
                "id": f"slide-{i}",
                "elements": []
            }
            for i in range(3)
        ],
        "theme": {"name": "default"},
        "metadata": {
            "author": "test-user",
            "version": "1.0.0",
            "tags": ["test"]
        }
    }

# Async test utilities
async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
    """Wait for a condition to become true"""
    import time
    start_time = time.time()
    while time.time() - start_time < timeout:
        if await condition_func() if asyncio.iscoroutinefunction(condition_func) else condition_func():
            return True
        await asyncio.sleep(interval)
    return False

# Mock external services
@pytest.fixture
def mock_external_services():
    """Mock external services for testing"""
    return {
        "deepseek_api": AsyncMock(),
        "redis_cache": AsyncMock(),
        "file_storage": AsyncMock()
    }