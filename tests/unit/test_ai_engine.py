"""
Unit tests for AI Engine
Tests the core AI functionality including learning, prediction, and pattern matching
"""

import pytest
import asyncio
import json
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from backend.ai_engine import (
    AIEngine, 
    SimpleNeuralNetwork, 
    PatternMatcher, 
    AtomPrediction,
    AIContext
)

class TestSimpleNeuralNetwork:
    """Test the simple neural network implementation"""
    
    def test_initialization(self):
        """Test network initialization"""
        nn = SimpleNeuralNetwork(input_size=10, hidden_size=20, output_size=5)
        
        assert nn.input_size == 10
        assert nn.hidden_size == 20
        assert nn.output_size == 5
        assert nn.W1.shape == (10, 20)
        assert nn.W2.shape == (20, 5)
        assert nn.b1.shape == (1, 20)
        assert nn.b2.shape == (1, 5)
    
    def test_sigmoid_function(self):
        """Test sigmoid activation function"""
        nn = SimpleNeuralNetwork()
        
        # Test normal values
        result = nn.sigmoid(np.array([0, 1, -1]))
        expected = np.array([0.5, 0.7310585786300049, 0.2689414213699951])
        np.testing.assert_array_almost_equal(result, expected)
        
        # Test extreme values (should be clipped)
        result = nn.sigmoid(np.array([1000, -1000]))
        assert result[0] == 1.0  # Should be clipped to prevent overflow
        assert result[1] == 0.0
    
    def test_softmax_function(self):
        """Test softmax activation function"""
        nn = SimpleNeuralNetwork()
        
        # Test 2D input
        input_data = np.array([[1, 2, 3], [4, 5, 6]])
        result = nn.softmax(input_data)
        
        # Check that each row sums to 1
        row_sums = np.sum(result, axis=1)
        np.testing.assert_array_almost_equal(row_sums, [1.0, 1.0])
        
        # Check that all values are positive
        assert np.all(result >= 0)
    
    def test_forward_pass(self):
        """Test forward pass through network"""
        nn = SimpleNeuralNetwork(input_size=3, hidden_size=4, output_size=2)
        
        # Test input
        X = np.array([[1, 2, 3], [4, 5, 6]])
        output = nn.forward(X)
        
        # Check output shape
        assert output.shape == (2, 2)
        
        # Check that outputs are probabilities (sum to 1)
        row_sums = np.sum(output, axis=1)
        np.testing.assert_array_almost_equal(row_sums, [1.0, 1.0])
    
    def test_prediction(self):
        """Test prediction method"""
        nn = SimpleNeuralNetwork(input_size=3, hidden_size=4, output_size=2)
        
        X = np.array([[1, 2, 3]])
        prediction = nn.predict(X)
        
        assert prediction.shape == (1, 2)
        assert np.sum(prediction) == pytest.approx(1.0, rel=1e-6)
    
    def test_training(self):
        """Test training process"""
        nn = SimpleNeuralNetwork(input_size=2, hidden_size=3, output_size=2)
        
        # Simple training data (XOR-like problem)
        X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        y = np.array([[1, 0], [0, 1], [0, 1], [1, 0]])
        
        # Get initial loss
        initial_output = nn.forward(X)
        initial_loss = -np.mean(np.sum(y * np.log(initial_output + 1e-8), axis=1))
        
        # Train
        nn.train(X, y, epochs=50)
        
        # Get final loss
        final_output = nn.forward(X)
        final_loss = -np.mean(np.sum(y * np.log(final_output + 1e-8), axis=1))
        
        # Loss should decrease
        assert final_loss < initial_loss

class TestPatternMatcher:
    """Test the pattern matching functionality"""
    
    def test_initialization(self):
        """Test pattern matcher initialization"""
        pm = PatternMatcher()
        
        assert pm.patterns == {}
        assert pm.sequence_memory == []
    
    def test_add_operation(self):
        """Test adding operations to sequence memory"""
        pm = PatternMatcher()
        
        operation = {
            'op': 'ADD',
            'type': 'text',
            'target': 'slide-1'
        }
        
        pm.add_operation(operation)
        
        assert len(pm.sequence_memory) == 1
        assert pm.sequence_memory[0] == operation
    
    def test_sequence_memory_limit(self):
        """Test that sequence memory is limited to 100 operations"""
        pm = PatternMatcher()
        
        # Add 150 operations
        for i in range(150):
            pm.add_operation({'op': f'operation_{i}'})
        
        # Should only keep the last 100
        assert len(pm.sequence_memory) == 100
        assert pm.sequence_memory[0]['op'] == 'operation_50'
        assert pm.sequence_memory[-1]['op'] == 'operation_149'
    
    def test_find_patterns_simple(self):
        """Test finding simple patterns"""
        pm = PatternMatcher()
        
        # Add a repeating pattern
        pattern = [
            {'op': 'ADD', 'type': 'text'},
            {'op': 'MODIFY', 'type': 'style'}
        ]
        
        # Repeat the pattern 3 times
        for _ in range(3):
            for operation in pattern:
                pm.add_operation(operation)
        
        patterns = pm.find_patterns(min_length=2, min_frequency=2)
        
        assert len(patterns) > 0
        
        # Should find the repeating pattern
        found_pattern = patterns[0]
        assert found_pattern['data']['frequency'] >= 2
        assert found_pattern['data']['length'] == 2
    
    def test_find_patterns_no_patterns(self):
        """Test when no patterns are found"""
        pm = PatternMatcher()
        
        # Add unique operations
        for i in range(10):
            pm.add_operation({'op': f'unique_op_{i}', 'type': 'text'})
        
        patterns = pm.find_patterns(min_frequency=2)
        
        # Should find no patterns with frequency >= 2
        assert len(patterns) == 0
    
    def test_pattern_confidence_calculation(self):
        """Test pattern confidence calculation"""
        pm = PatternMatcher()
        
        # Add a pattern that repeats 5 times
        for _ in range(5):
            pm.add_operation({'op': 'ADD', 'type': 'text'})
            pm.add_operation({'op': 'STYLE', 'type': 'color'})
        
        patterns = pm.find_patterns(min_frequency=2)
        
        if patterns:
            # Confidence should be based on frequency
            pattern = patterns[0]
            expected_confidence = min(pattern['data']['frequency'] / 10.0, 1.0)
            assert pattern['confidence'] == expected_confidence

class TestAIEngine:
    """Test the main AI engine functionality"""
    
    @pytest.fixture
    async def ai_engine(self):
        """Create AI engine for testing"""
        engine = AIEngine()
        await engine.initialize()
        return engine
    
    @pytest.mark.asyncio
    async def test_initialization(self, ai_engine):
        """Test AI engine initialization"""
        assert ai_engine.is_initialized
        assert isinstance(ai_engine.model, SimpleNeuralNetwork)
        assert isinstance(ai_engine.pattern_matcher, PatternMatcher)
        assert ai_engine.operation_history == []
        assert ai_engine.training_data == []
    
    @pytest.mark.asyncio
    async def test_is_ready_insufficient_data(self, ai_engine):
        """Test is_ready with insufficient training data"""
        assert not ai_engine.is_ready()  # Should need at least 10 samples
    
    @pytest.mark.asyncio
    async def test_learn_from_operation(self, ai_engine):
        """Test learning from user operations"""
        operation = {
            'op': 'ADD',
            'type': 'text',
            'target': 'slide-1',
            'data': {'content': 'Hello World'},
            'timestamp': datetime.utcnow().timestamp() * 1000,
            'userId': 'test-user',
            'sessionId': 'test-session'
        }
        
        result = {
            'success': True,
            'elementId': 'element-1',
            'processingTime': 50
        }
        
        learning_result = await ai_engine.learn_from_operation(operation, result)
        
        assert learning_result['learned'] is True
        assert learning_result['training_samples'] == 1
        assert learning_result['model_ready'] is False  # Still need more samples
        
        # Check that data was stored
        assert len(ai_engine.operation_history) == 1
        assert len(ai_engine.training_data) == 1
        assert ai_engine.metrics['training_samples'] == 1
    
    @pytest.mark.asyncio
    async def test_learn_multiple_operations(self, ai_engine):
        """Test learning from multiple operations"""
        operations = [
            {
                'op': 'ADD',
                'type': 'text',
                'target': f'slide-{i}',
                'data': {'content': f'Content {i}'},
                'timestamp': datetime.utcnow().timestamp() * 1000,
                'userId': 'test-user',
                'sessionId': 'test-session'
            }
            for i in range(15)  # More than the minimum required
        ]
        
        for operation in operations:
            result = {'success': True}
            await ai_engine.learn_from_operation(operation, result)
        
        assert ai_engine.is_ready()  # Should be ready now
        assert ai_engine.metrics['training_samples'] == 15
    
    @pytest.mark.asyncio
    async def test_predict_next_atom_not_ready(self, ai_engine):
        """Test prediction when model is not ready (should use rule-based)"""
        context = {
            'currentSlide': {'id': 'slide-1', 'elements': []},
            'presentation': {'title': 'Test Presentation'},
            'userBehavior': {'lastAction': 'click'}
        }
        
        prediction = await ai_engine.predict_next_atom(context)
        
        assert isinstance(prediction, AtomPrediction)
        assert prediction.atom is not None
        assert 'op' in prediction.atom
        assert 'type' in prediction.atom
        assert prediction.confidence >= 0.0
        assert prediction.reasoning is not None
    
    @pytest.mark.asyncio
    async def test_predict_next_atom_ready(self, ai_engine):
        """Test prediction when model is ready"""
        # First, train the model with enough data
        for i in range(15):
            operation = {
                'op': 'ADD',
                'type': 'text',
                'target': f'slide-{i}',
                'data': {'content': f'Content {i}'},
                'timestamp': datetime.utcnow().timestamp() * 1000,
                'userId': 'test-user',
                'sessionId': 'test-session'
            }
            result = {'success': True}
            await ai_engine.learn_from_operation(operation, result)
        
        context = {
            'currentSlide': {'id': 'slide-1', 'elements': []},
            'presentation': {'title': 'Test Presentation'},
            'userBehavior': {'lastAction': 'click'}
        }
        
        prediction = await ai_engine.predict_next_atom(context)
        
        assert isinstance(prediction, AtomPrediction)
        assert prediction.atom is not None
        assert len(prediction.alternatives) > 0
        assert prediction.confidence > 0.0
    
    @pytest.mark.asyncio
    async def test_generate_suggestions(self, ai_engine):
        """Test generating multiple suggestions"""
        context = {
            'currentSlide': {'id': 'slide-1', 'elements': []},
            'presentation': {'title': 'Test Presentation'},
            'userBehavior': {'lastAction': 'click'}
        }
        
        suggestions = await ai_engine.generate_suggestions(context)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert len(suggestions) <= 5  # Should limit to 5 suggestions
        
        # Each suggestion should be a valid operation
        for suggestion in suggestions:
            assert 'op' in suggestion
            assert 'type' in suggestion
    
    @pytest.mark.asyncio
    async def test_generate_presentation_sequence(self, ai_engine):
        """Test generating complete presentation sequence"""
        prompt = "Create a business presentation about quarterly results"
        
        sequence = await ai_engine.generate_presentation_sequence(
            prompt, 
            presentation_type="business", 
            slide_count=5
        )
        
        assert 'id' in sequence
        assert 'name' in sequence
        assert 'description' in sequence
        assert 'atoms' in sequence
        assert 'createdAt' in sequence
        assert 'tags' in sequence
        
        assert len(sequence['atoms']) > 0
        assert 'business' in sequence['tags']
        assert prompt[:50] in sequence['name']
    
    @pytest.mark.asyncio
    async def test_suggest_template(self, ai_engine):
        """Test template suggestion based on content"""
        test_cases = [
            ("sales revenue profit business", "business-report"),
            ("learn education course lesson", "educational"),
            ("compare vs versus comparison", "comparison"),
            ("timeline roadmap schedule", "timeline"),
            ("random content", "minimal")
        ]
        
        for content, expected_template in test_cases:
            template = await ai_engine.suggest_template(content)
            assert template == expected_template
    
    @pytest.mark.asyncio
    async def test_enhance_content(self, ai_engine):
        """Test content enhancement"""
        test_cases = [
            ("hello world", "Hello world."),
            ("this is a test", "This is a test."),
            ("Already capitalized.", "Already capitalized."),
            ("Question?", "Question?"),
            ("utilize this feature", "use this feature."),
            ("", "")
        ]
        
        for input_content, expected in test_cases:
            enhanced = await ai_engine.enhance_content("element-1", input_content)
            assert enhanced == expected
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, ai_engine):
        """Test getting AI metrics"""
        metrics = await ai_engine.get_metrics()
        
        required_keys = [
            'total_predictions', 'successful_predictions', 'failed_predictions',
            'training_samples', 'accuracy', 'model_ready', 'operation_history_size',
            'training_data_size', 'patterns_discovered'
        ]
        
        for key in required_keys:
            assert key in metrics
        
        assert isinstance(metrics['model_ready'], bool)
        assert isinstance(metrics['training_samples'], int)
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, ai_engine):
        """Test getting detailed performance metrics"""
        metrics = await ai_engine.get_performance_metrics()
        
        required_keys = [
            'prediction_accuracy', 'total_predictions', 'successful_predictions',
            'training_samples', 'model_size', 'last_training', 'memory_usage'
        ]
        
        for key in required_keys:
            assert key in metrics
    
    @pytest.mark.asyncio
    async def test_error_handling_in_learning(self, ai_engine):
        """Test error handling during learning"""
        # Test with invalid operation data
        invalid_operation = None
        result = {'success': True}
        
        learning_result = await ai_engine.learn_from_operation(invalid_operation, result)
        
        assert learning_result['learned'] is False
        assert 'error' in learning_result
    
    @pytest.mark.asyncio
    async def test_error_handling_in_prediction(self, ai_engine):
        """Test error handling during prediction"""
        # Test with invalid context
        invalid_context = None
        
        prediction = await ai_engine.predict_next_atom(invalid_context)
        
        # Should still return a valid prediction (fallback to rule-based)
        assert isinstance(prediction, AtomPrediction)
        assert prediction.atom is not None
    
    @pytest.mark.asyncio
    async def test_model_retraining(self, ai_engine):
        """Test that model retrains periodically"""
        # Add exactly 10 operations to trigger retraining
        for i in range(10):
            operation = {
                'op': 'ADD',
                'type': 'text',
                'target': f'slide-{i}',
                'data': {'content': f'Content {i}'},
                'timestamp': datetime.utcnow().timestamp() * 1000,
                'userId': 'test-user',
                'sessionId': 'test-session'
            }
            result = {'success': True}
            await ai_engine.learn_from_operation(operation, result)
        
        # Should have triggered retraining
        assert ai_engine.metrics['last_training'] is not None
    
    @pytest.mark.asyncio
    async def test_pattern_integration(self, ai_engine):
        """Test integration with pattern matcher"""
        # Add operations that form a pattern
        pattern_operations = [
            {'op': 'ADD', 'type': 'text'},
            {'op': 'MODIFY', 'type': 'style'},
            {'op': 'ADD', 'type': 'text'},
            {'op': 'MODIFY', 'type': 'style'}
        ]
        
        for operation in pattern_operations:
            result = {'success': True}
            await ai_engine.learn_from_operation(operation, result)
        
        # Check that patterns are detected
        patterns = await ai_engine.get_operation_patterns(None)
        assert isinstance(patterns, list)
    
    @pytest.mark.asyncio
    async def test_context_feature_extraction(self, ai_engine):
        """Test context feature extraction"""
        context = {
            'currentSlide': {
                'id': 'slide-1',
                'elements': [
                    {'type': 'text', 'content': 'Hello'},
                    {'type': 'image', 'src': 'image.jpg'}
                ]
            },
            'presentation': {
                'title': 'Test Presentation',
                'slideCount': 5
            },
            'userBehavior': {
                'lastAction': 'click',
                'frequency': 3
            }
        }
        
        # This tests the internal _extract_context_features method indirectly
        prediction = await ai_engine.predict_next_atom(context)
        
        # Should successfully process the context
        assert isinstance(prediction, AtomPrediction)
        assert prediction.atom is not None