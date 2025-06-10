# AI-PPT System Testing Documentation

## Overview

This document provides comprehensive information about the testing infrastructure, methodologies, and best practices for the AI-PPT System. The testing framework ensures system reliability, performance, and quality through automated testing at multiple levels.

## Testing Architecture

### Test Pyramid Structure

```
                    ┌─────────────────┐
                    │   E2E Tests     │ 10%
                    │  (Workflows)    │
                ┌───┴─────────────────┴───┐
                │  Integration Tests      │ 20%
                │   (API & Services)      │
            ┌───┴─────────────────────────┴───┐
            │        Unit Tests               │ 70%
            │   (Components & Functions)      │
            └─────────────────────────────────┘
```

### Test Categories

#### 1. Unit Tests (70%)
- **Purpose**: Test individual components in isolation
- **Location**: `tests/unit/`
- **Coverage**: Functions, classes, and modules
- **Tools**: pytest, unittest.mock, pytest-asyncio

#### 2. Integration Tests (20%)
- **Purpose**: Test component interactions and API endpoints
- **Location**: `tests/integration/`
- **Coverage**: API endpoints, database operations, service integration
- **Tools**: httpx, AsyncClient, database fixtures

#### 3. End-to-End Tests (10%)
- **Purpose**: Test complete user workflows
- **Location**: `tests/e2e/`
- **Coverage**: Full user journeys, real-world scenarios
- **Tools**: WebDriver, API clients, workflow automation

#### 4. Performance Tests
- **Purpose**: Validate system performance under load
- **Location**: `tests/performance/`
- **Coverage**: Load testing, stress testing, benchmarks
- **Tools**: Custom performance monitoring, asyncio

## Test Infrastructure

### Core Testing Components

#### Test Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
asyncio_mode = auto
addopts = 
    --verbose
    --cov=backend
    --cov-report=html
    --cov-fail-under=80
    --json-report
    --html=test-report.html
```

#### Test Fixtures (`tests/conftest.py`)
- **Database fixtures**: Test database setup and teardown
- **Client fixtures**: HTTP and WebSocket test clients
- **Mock fixtures**: AI provider mocks and external service mocks
- **Data fixtures**: Sample data for testing

#### Test Runner (`run_tests.py`)
- **Comprehensive execution**: Runs all test types with monitoring
- **Performance tracking**: Monitors memory, CPU, and response times
- **Report generation**: Creates detailed HTML and JSON reports
- **Recommendations**: Provides actionable improvement suggestions

### Test Execution

#### Quick Test Run
```bash
# Run only unit tests for quick feedback
python run_tests.py --quick

# Or using pytest directly
pytest tests/unit/ -v
```

#### Comprehensive Test Run
```bash
# Run all test types with coverage
python run_tests.py

# Run specific test types
python run_tests.py --types unit integration

# Run with verbose output
python run_tests.py --verbose
```

#### Continuous Integration
```bash
# CI-friendly execution
python run_tests.py --types all --no-coverage > test-results.log
```

## Test Implementation Guide

### Unit Test Examples

#### Testing AI Engine
```python
import pytest
from backend.ai_engine import AIEngine, AtomPrediction

class TestAIEngine:
    @pytest.fixture
    async def ai_engine(self):
        engine = AIEngine()
        await engine.initialize()
        return engine
    
    @pytest.mark.asyncio
    async def test_predict_next_atom(self, ai_engine):
        context = {
            'currentSlide': {'id': 'slide-1', 'elements': []},
            'presentation': {'title': 'Test Presentation'}
        }
        
        prediction = await ai_engine.predict_next_atom(context)
        
        assert isinstance(prediction, AtomPrediction)
        assert prediction.atom is not None
        assert 'op' in prediction.atom
        assert prediction.confidence >= 0.0
```

#### Testing DeepSeek Provider
```python
import pytest
from unittest.mock import AsyncMock, patch
from backend.ai_providers.deepseek import DeepSeekProvider
from backend.ai_providers.base import ProviderConfig, AIRequest

class TestDeepSeekProvider:
    @pytest.fixture
    def provider_config(self):
        return ProviderConfig(
            api_key="test-key",
            model="deepseek-chat"
        )
    
    @pytest.mark.asyncio
    async def test_generate_completion_success(self, provider_config):
        provider = DeepSeekProvider(provider_config)
        
        # Mock HTTP client
        mock_response = {
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"total_tokens": 100}
        }
        
        with patch.object(provider, '_make_request_with_retries', return_value=mock_response):
            request = AIRequest(
                prompt="Test prompt",
                context={},
                operation_type="test"
            )
            
            response = await provider.generate_completion(request)
            
            assert response.content == "Test response"
            assert response.provider == "deepseek"
```

### Integration Test Examples

#### Testing API Endpoints
```python
import pytest
from httpx import AsyncClient

class TestOperationEndpoints:
    @pytest.mark.asyncio
    async def test_process_operation(self, test_client, sample_atomic_operation):
        response = await test_client.post(
            "/api/operations/process",
            json=sample_atomic_operation
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "operation_id" in data
        assert "processing_time" in data
    
    @pytest.mark.asyncio
    async def test_get_operation_stats(self, test_client):
        response = await test_client.get("/api/operations/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_operations" in data
        assert "operations_by_type" in data
        assert "average_execution_time_ms" in data
```

#### Testing Database Operations
```python
import pytest
from backend.atomic_processor import AtomicProcessor

class TestAtomicProcessor:
    @pytest.mark.asyncio
    async def test_process_operation(self, db_session, sample_atomic_operation):
        processor = AtomicProcessor()
        
        result = await processor.process_operation(sample_atomic_operation, db_session)
        
        assert result["success"] is True
        assert "operation_id" in result
        
        # Verify operation was stored
        stats = await processor.get_operation_stats(db_session)
        assert stats["total_operations"] >= 1
```

### End-to-End Test Examples

#### Testing Complete Workflows
```python
import pytest
import asyncio

class TestPresentationCreationWorkflow:
    @pytest.mark.asyncio
    async def test_create_presentation_with_ai(self, test_client):
        # Step 1: Get AI template suggestion
        template_response = await test_client.post(
            "/api/ai/suggest-template",
            json={"content": "business quarterly results"}
        )
        
        assert template_response.status_code == 200
        template = template_response.json()["template"]
        
        # Step 2: Create presentation
        presentation_data = {
            "title": "Q4 Results",
            "slides": [{"id": "slide-1", "elements": []}],
            "theme": {"name": template}
        }
        
        create_response = await test_client.post(
            "/api/presentations",
            json=presentation_data
        )
        
        assert create_response.status_code == 200
        presentation_id = create_response.json()["id"]
        
        # Step 3: Get AI suggestions and apply
        suggestions_response = await test_client.post(
            "/api/ai/suggestions",
            json={"context": {"currentSlide": {"id": "slide-1"}}}
        )
        
        assert suggestions_response.status_code == 200
        suggestions = suggestions_response.json()
        assert len(suggestions) > 0
        
        # Step 4: Apply first suggestion
        operation = {
            "operation": suggestions[0],
            "presentationId": presentation_id,
            "slideIndex": 0
        }
        
        operation_response = await test_client.post(
            "/api/operations/process",
            json=operation
        )
        
        assert operation_response.status_code == 200
        assert operation_response.json()["success"] is True
```

### Performance Test Examples

#### Load Testing
```python
import pytest
import asyncio
import time

class TestPerformance:
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, test_client, performance_test_data):
        start_time = time.time()
        
        # Create 50 concurrent operations
        tasks = []
        for operation_data in performance_test_data[:50]:
            task = test_client.post("/api/operations/process", json=operation_data)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify performance requirements
        successful_responses = [r for r in responses if r.status_code == 200]
        success_rate = len(successful_responses) / len(responses)
        throughput = len(successful_responses) / duration
        
        assert success_rate > 0.9  # 90% success rate
        assert throughput > 10     # 10 operations per second
        assert duration < 30       # Complete within 30 seconds
```

## Test Data Management

### Fixtures and Factories

#### Database Fixtures
```python
@pytest.fixture
async def db_session(test_engine):
    async_session = sessionmaker(test_engine, class_=AsyncSession)
    async with async_session() as session:
        yield session

@pytest.fixture
def sample_presentation_data():
    return {
        "title": "Test Presentation",
        "slides": [{"id": "slide-1", "elements": []}],
        "theme": {"name": "default"},
        "metadata": {"author": "test-user"}
    }
```

#### Mock Fixtures
```python
@pytest.fixture
def mock_deepseek_response():
    return {
        "choices": [{"message": {"content": "AI response"}}],
        "usage": {"total_tokens": 100}
    }

@pytest.fixture
def mock_websocket():
    mock_ws = AsyncMock()
    mock_ws.send_json = AsyncMock()
    mock_ws.receive_json = AsyncMock()
    return mock_ws
```

### Test Data Factories

#### Using Factory Boy
```python
import factory
from backend.models import Presentation, AtomicOperation

class PresentationFactory(factory.Factory):
    class Meta:
        model = Presentation
    
    title = factory.Faker('sentence', nb_words=3)
    user_id = factory.Faker('uuid4')
    slide_count = factory.Faker('random_int', min=1, max=20)
    element_count = factory.Faker('random_int', min=0, max=100)

class AtomicOperationFactory(factory.Factory):
    class Meta:
        model = AtomicOperation
    
    operation = factory.Faker('random_element', elements=['ADD', 'MODIFY', 'DELETE'])
    element_type = factory.Faker('random_element', elements=['text', 'image', 'shape'])
    user_id = factory.Faker('uuid4')
    success = True
```

## Test Coverage

### Coverage Requirements

- **Minimum Line Coverage**: 80%
- **Minimum Branch Coverage**: 70%
- **Critical Path Coverage**: 95%

### Coverage Reporting

#### HTML Report
```bash
# Generate HTML coverage report
pytest --cov=backend --cov-report=html
# View at htmlcov/index.html
```

#### Terminal Report
```bash
# Show coverage in terminal
pytest --cov=backend --cov-report=term-missing
```

#### XML Report (for CI)
```bash
# Generate XML report for CI systems
pytest --cov=backend --cov-report=xml
```

### Coverage Exclusions

```python
# Exclude from coverage
def debug_function():  # pragma: no cover
    print("Debug information")

# Exclude abstract methods
@abstractmethod
def abstract_method(self):  # pragma: no cover
    pass
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
    
    - name: Run tests
      run: |
        python run_tests.py --types all
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Quality Gates

#### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: pytest-unit
        entry: python run_tests.py --quick
        language: system
        pass_filenames: false
        always_run: true
```

#### Branch Protection Rules
- All tests must pass
- Coverage must be ≥ 80%
- No critical security vulnerabilities
- Code review required

## Performance Testing

### Benchmarking Framework

#### Response Time Benchmarks
```python
async def benchmark_api_response_time():
    start_time = time.time()
    
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
    
    end_time = time.time()
    response_time = end_time - start_time
    
    # Assert performance requirements
    assert response_time < 1.0  # Must respond within 1 second
    
    return response_time
```

#### Throughput Benchmarks
```python
async def benchmark_concurrent_operations():
    operations = [create_test_operation() for _ in range(100)]
    
    start_time = time.time()
    
    async with httpx.AsyncClient() as client:
        tasks = [
            client.post("/api/operations/process", json=op)
            for op in operations
        ]
        responses = await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    
    successful = len([r for r in responses if r.status_code == 200])
    throughput = successful / duration
    
    assert throughput > 50  # Must handle 50 operations per second
    
    return throughput
```

### Memory and Resource Testing

```python
import psutil

def test_memory_usage():
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Perform memory-intensive operations
    large_data = create_large_test_data()
    
    peak_memory = process.memory_info().rss
    memory_increase = (peak_memory - initial_memory) / 1024 / 1024  # MB
    
    # Cleanup
    del large_data
    
    assert memory_increase < 100  # Must not use more than 100MB
```

## Test Maintenance

### Test Organization

#### Directory Structure
```
tests/
├── conftest.py              # Global fixtures
├── unit/                    # Unit tests
│   ├── test_ai_engine.py
│   ├── test_deepseek_provider.py
│   └── test_atomic_processor.py
├── integration/             # Integration tests
│   ├── test_api_endpoints.py
│   └── test_database_operations.py
├── e2e/                     # End-to-end tests
│   └── test_complete_workflows.py
├── performance/             # Performance tests
│   └── test_benchmarks.py
└── fixtures/                # Test data
    ├── sample_presentations.json
    └── mock_responses.json
```

#### Naming Conventions
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Fixtures: `*_fixture` or descriptive names
- Markers: Use descriptive markers (`@pytest.mark.slow`)

### Test Maintenance Best Practices

#### 1. Keep Tests Independent
```python
# Good: Each test is independent
def test_create_presentation():
    presentation = create_test_presentation()
    assert presentation.id is not None

def test_update_presentation():
    presentation = create_test_presentation()
    updated = update_presentation(presentation.id, {"title": "New Title"})
    assert updated.title == "New Title"
```

#### 2. Use Descriptive Test Names
```python
# Good: Descriptive test names
def test_ai_prediction_returns_valid_operation_for_empty_slide():
    pass

def test_deepseek_provider_handles_rate_limit_error_gracefully():
    pass

def test_presentation_creation_fails_with_invalid_slide_data():
    pass
```

#### 3. Test Edge Cases
```python
def test_operation_processing_with_empty_data():
    operation = {"operation": {}}
    result = process_operation(operation)
    assert result["success"] is False

def test_ai_prediction_with_malformed_context():
    context = None
    prediction = ai_engine.predict_next_atom(context)
    assert prediction is not None  # Should handle gracefully
```

#### 4. Mock External Dependencies
```python
@patch('backend.ai_providers.deepseek.httpx.AsyncClient')
async def test_deepseek_api_call(mock_client):
    mock_client.return_value.post.return_value.json.return_value = {
        "choices": [{"message": {"content": "Test response"}}]
    }
    
    provider = DeepSeekProvider(config)
    response = await provider.generate_completion(request)
    
    assert response.content == "Test response"
```

## Troubleshooting

### Common Test Issues

#### 1. Async Test Failures
```python
# Problem: Forgetting @pytest.mark.asyncio
def test_async_function():  # Missing decorator
    result = await async_function()
    assert result is not None

# Solution: Add asyncio marker
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

#### 2. Database Test Issues
```python
# Problem: Tests affecting each other
def test_create_user():
    user = create_user("test@example.com")
    assert user.email == "test@example.com"

def test_user_exists():
    user = get_user("test@example.com")  # May fail if previous test didn't clean up
    assert user is not None

# Solution: Use proper fixtures and cleanup
@pytest.fixture
async def clean_database(db_session):
    yield db_session
    # Cleanup after test
    await db_session.rollback()
```

#### 3. Mock Configuration Issues
```python
# Problem: Mock not applied correctly
@patch('wrong.module.path')
def test_with_mock(mock_function):
    # Mock not working because path is wrong
    pass

# Solution: Use correct import path
@patch('backend.ai_providers.deepseek.httpx.AsyncClient')
def test_with_mock(mock_client):
    # Mock works correctly
    pass
```

### Debugging Test Failures

#### 1. Use Verbose Output
```bash
pytest -v -s tests/unit/test_ai_engine.py::TestAIEngine::test_predict_next_atom
```

#### 2. Add Debug Prints
```python
def test_complex_operation():
    result = complex_function()
    print(f"Debug: result = {result}")  # Will show with -s flag
    assert result.success is True
```

#### 3. Use Debugger
```python
def test_with_debugger():
    import pdb; pdb.set_trace()  # Breakpoint
    result = function_to_debug()
    assert result is not None
```

#### 4. Check Test Logs
```bash
# Run with logging enabled
pytest --log-cli-level=DEBUG tests/
```

## Best Practices Summary

### Test Writing Guidelines

1. **Write tests first** (TDD approach when possible)
2. **Keep tests simple** and focused on one thing
3. **Use descriptive names** that explain what is being tested
4. **Test edge cases** and error conditions
5. **Mock external dependencies** to ensure test isolation
6. **Use fixtures** for common test setup
7. **Keep tests fast** - unit tests should run in milliseconds
8. **Maintain test independence** - tests should not depend on each other
9. **Update tests** when code changes
10. **Review test coverage** regularly and aim for high coverage

### Performance Guidelines

1. **Unit tests**: < 100ms each
2. **Integration tests**: < 1s each
3. **E2E tests**: < 30s each
4. **Total test suite**: < 10 minutes
5. **Parallel execution**: Use when possible for faster feedback

### Maintenance Guidelines

1. **Regular cleanup**: Remove obsolete tests
2. **Refactor tests**: Keep them maintainable
3. **Update fixtures**: Keep test data current
4. **Monitor flaky tests**: Fix or remove unreliable tests
5. **Document complex tests**: Add comments for complex test logic

This comprehensive testing framework ensures the AI-PPT System maintains high quality, reliability, and performance while enabling confident development and deployment.