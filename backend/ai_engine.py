"""
AI Engine for PPT Generation System
Handles prediction, learning, and autonomous operation generation
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import random
from dataclasses import dataclass
import pickle
import os

logger = logging.getLogger(__name__)

@dataclass
class AtomPrediction:
    """Structure for atomic operation predictions"""
    atom: Dict[str, Any]
    confidence: float
    reasoning: str
    alternatives: List[Dict[str, Any]]

@dataclass
class AIContext:
    """Context for AI decision making"""
    current_slide: Dict[str, Any]
    presentation: Dict[str, Any]
    user_behavior: Dict[str, Any]

class SimpleNeuralNetwork:
    """Simple neural network for atomic operation prediction"""
    
    def __init__(self, input_size: int = 50, hidden_size: int = 100, output_size: int = 20):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Initialize weights randomly
        self.W1 = np.random.randn(input_size, hidden_size) * 0.1
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.1
        self.b2 = np.zeros((1, output_size))
        
        self.learning_rate = 0.001
        
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def softmax(self, x):
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    def forward(self, X):
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.softmax(self.z2)
        return self.a2
    
    def predict(self, X):
        return self.forward(X)
    
    def train(self, X, y, epochs=100):
        """Simple training loop"""
        for epoch in range(epochs):
            # Forward pass
            output = self.forward(X)
            
            # Compute loss (cross-entropy)
            loss = -np.mean(np.sum(y * np.log(output + 1e-8), axis=1))
            
            # Backward pass
            m = X.shape[0]
            
            # Output layer gradients
            dz2 = output - y
            dW2 = np.dot(self.a1.T, dz2) / m
            db2 = np.sum(dz2, axis=0, keepdims=True) / m
            
            # Hidden layer gradients
            dz1 = np.dot(dz2, self.W2.T) * self.a1 * (1 - self.a1)
            dW1 = np.dot(X.T, dz1) / m
            db1 = np.sum(dz1, axis=0, keepdims=True) / m
            
            # Update weights
            self.W2 -= self.learning_rate * dW2
            self.b2 -= self.learning_rate * db2
            self.W1 -= self.learning_rate * dW1
            self.b1 -= self.learning_rate * db1
            
            if epoch % 20 == 0:
                logger.debug(f"Epoch {epoch}, Loss: {loss:.4f}")

class PatternMatcher:
    """Pattern matching for operation sequences"""
    
    def __init__(self):
        self.patterns = {}
        self.sequence_memory = []
        
    def add_operation(self, operation: Dict[str, Any]):
        """Add operation to sequence memory"""
        self.sequence_memory.append(operation)
        
        # Keep only recent operations
        if len(self.sequence_memory) > 100:
            self.sequence_memory = self.sequence_memory[-100:]
    
    def find_patterns(self, min_length: int = 2, min_frequency: int = 2) -> List[Dict[str, Any]]:
        """Find common operation patterns"""
        patterns = {}
        
        # Look for sequences of different lengths
        for length in range(min_length, min(6, len(self.sequence_memory))):
            for i in range(len(self.sequence_memory) - length + 1):
                sequence = self.sequence_memory[i:i+length]
                
                # Create pattern key
                pattern_key = tuple(
                    (op.get('op'), op.get('type')) for op in sequence
                )
                
                if pattern_key in patterns:
                    patterns[pattern_key]['frequency'] += 1
                else:
                    patterns[pattern_key] = {
                        'sequence': sequence,
                        'frequency': 1,
                        'length': length
                    }
        
        # Filter by minimum frequency
        frequent_patterns = [
            {
                'pattern': pattern_key,
                'data': data,
                'confidence': min(data['frequency'] / 10.0, 1.0)
            }
            for pattern_key, data in patterns.items()
            if data['frequency'] >= min_frequency
        ]
        
        return sorted(frequent_patterns, key=lambda x: x['confidence'], reverse=True)

class AIEngine:
    """Main AI engine for the PPT system"""
    
    def __init__(self):
        self.model = SimpleNeuralNetwork()
        self.pattern_matcher = PatternMatcher()
        self.operation_history = []
        self.training_data = []
        self.is_initialized = False
        
        # Operation mappings
        self.operation_types = [
            'ADD_text', 'ADD_image', 'ADD_shape', 'ADD_chart', 'ADD_table',
            'MODIFY_position', 'MODIFY_style', 'MODIFY_content',
            'CREATE_slide', 'DELETE_slide', 'REORDER_slides',
            'APPLY_theme', 'APPLY_layout', 'APPLY_animation'
        ]
        
        # Performance metrics
        self.metrics = {
            'total_predictions': 0,
            'successful_predictions': 0,
            'training_samples': 0,
            'accuracy': 0.0,
            'last_training': None
        }
        
        # Model persistence
        self.model_path = "ai_model.pkl"
        
    async def initialize(self):
        """Initialize the AI engine"""
        try:
            # Load existing model if available
            if os.path.exists(self.model_path):
                await self.load_model()
            
            self.is_initialized = True
            logger.info("✅ AI Engine initialized")
            
        except Exception as e:
            logger.error(f"❌ AI Engine initialization failed: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if AI is ready for predictions"""
        return (
            self.is_initialized and 
            self.metrics['training_samples'] >= 10  # Minimum training samples
        )
    
    async def learn_from_operation(self, operation: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from a user operation"""
        try:
            # Add to operation history
            self.operation_history.append({
                'operation': operation,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Add to pattern matcher
            self.pattern_matcher.add_operation(operation)
            
            # Create training sample
            features = self._extract_features(operation, result)
            target = self._create_target_vector(operation)
            
            self.training_data.append({
                'features': features,
                'target': target,
                'operation': operation
            })
            
            self.metrics['training_samples'] += 1
            
            # Retrain model periodically
            if len(self.training_data) % 10 == 0:
                await self._retrain_model()
            
            return {
                'learned': True,
                'training_samples': self.metrics['training_samples'],
                'model_ready': self.is_ready()
            }
            
        except Exception as e:
            logger.error(f"Learning failed: {e}")
            return {'learned': False, 'error': str(e)}
    
    async def predict_next_atom(self, context: Dict[str, Any]) -> AtomPrediction:
        """Predict the next atomic operation"""
        try:
            if not self.is_ready():
                # Return rule-based prediction
                return await self._rule_based_prediction(context)
            
            # Extract features from context
            features = self._extract_context_features(context)
            features_array = np.array([features])
            
            # Get model prediction
            predictions = self.model.predict(features_array)[0]
            
            # Get top predictions
            top_indices = np.argsort(predictions)[-3:][::-1]
            
            # Create atomic operation
            main_prediction = self._create_atomic_operation(
                self.operation_types[top_indices[0]], 
                context,
                predictions[top_indices[0]]
            )
            
            # Create alternatives
            alternatives = [
                self._create_atomic_operation(
                    self.operation_types[idx], 
                    context,
                    predictions[idx]
                )
                for idx in top_indices[1:]
            ]
            
            self.metrics['total_predictions'] += 1
            
            return AtomPrediction(
                atom=main_prediction,
                confidence=float(predictions[top_indices[0]]),
                reasoning=self._generate_reasoning(main_prediction, context),
                alternatives=alternatives
            )
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return await self._rule_based_prediction(context)
    
    async def generate_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate multiple AI suggestions"""
        try:
            suggestions = []
            
            # Get main prediction
            main_prediction = await self.predict_next_atom(context)
            suggestions.append(main_prediction.atom)
            
            # Add pattern-based suggestions
            pattern_suggestions = await self._get_pattern_suggestions(context)
            suggestions.extend(pattern_suggestions)
            
            # Add rule-based suggestions
            rule_suggestions = await self._get_rule_based_suggestions(context)
            suggestions.extend(rule_suggestions)
            
            # Remove duplicates and limit
            unique_suggestions = []
            seen = set()
            
            for suggestion in suggestions:
                key = (suggestion.get('op'), suggestion.get('type'))
                if key not in seen:
                    seen.add(key)
                    unique_suggestions.append(suggestion)
                    
                if len(unique_suggestions) >= 5:
                    break
            
            return unique_suggestions
            
        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return []
    
    async def generate_presentation_sequence(
        self, 
        prompt: str, 
        presentation_type: str = "business",
        slide_count: int = 10
    ) -> Dict[str, Any]:
        """Generate a complete presentation sequence"""
        try:
            sequence = {
                'id': f"generated_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'name': f"AI Generated: {prompt[:50]}...",
                'description': f"Generated presentation based on: {prompt}",
                'atoms': [],
                'createdAt': datetime.utcnow().timestamp() * 1000,
                'tags': ['ai-generated', presentation_type]
            }
            
            # Generate sequence based on presentation type
            if presentation_type == "business":
                sequence['atoms'] = await self._generate_business_presentation(prompt, slide_count)
            elif presentation_type == "educational":
                sequence['atoms'] = await self._generate_educational_presentation(prompt, slide_count)
            else:
                sequence['atoms'] = await self._generate_generic_presentation(prompt, slide_count)
            
            return sequence
            
        except Exception as e:
            logger.error(f"Presentation generation failed: {e}")
            raise
    
    async def suggest_template(self, content: str) -> str:
        """Suggest a template based on content analysis"""
        try:
            content_lower = content.lower()
            
            # Simple keyword-based template suggestion
            if any(word in content_lower for word in ['sales', 'revenue', 'profit', 'business']):
                return 'business-report'
            elif any(word in content_lower for word in ['learn', 'education', 'course', 'lesson']):
                return 'educational'
            elif any(word in content_lower for word in ['compare', 'vs', 'versus', 'comparison']):
                return 'comparison'
            elif any(word in content_lower for word in ['timeline', 'roadmap', 'schedule']):
                return 'timeline'
            else:
                return 'minimal'
                
        except Exception as e:
            logger.error(f"Template suggestion failed: {e}")
            return 'blank'
    
    async def enhance_content(self, element_id: str, content: str) -> str:
        """Enhance content using AI"""
        try:
            # Simple content enhancement rules
            enhanced = content.strip()
            
            # Capitalize first letter
            if enhanced and not enhanced[0].isupper():
                enhanced = enhanced[0].upper() + enhanced[1:]
            
            # Add period if missing
            if enhanced and not enhanced.endswith(('.', '!', '?')):
                enhanced += '.'
            
            # Simple improvements
            improvements = {
                'utilize': 'use',
                'facilitate': 'help',
                'implement': 'do',
                'optimize': 'improve'
            }
            
            for old, new in improvements.items():
                enhanced = enhanced.replace(old, new)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Content enhancement failed: {e}")
            return content
    
    async def get_operation_patterns(self, db) -> List[Dict[str, Any]]:
        """Get discovered operation patterns"""
        try:
            patterns = self.pattern_matcher.find_patterns()
            return patterns
        except Exception as e:
            logger.error(f"Failed to get patterns: {e}")
            return []
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get AI performance metrics"""
        return {
            **self.metrics,
            'model_ready': self.is_ready(),
            'operation_history_size': len(self.operation_history),
            'training_data_size': len(self.training_data),
            'patterns_discovered': len(self.pattern_matcher.patterns)
        }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        return {
            'prediction_accuracy': self.metrics['accuracy'],
            'total_predictions': self.metrics['total_predictions'],
            'successful_predictions': self.metrics['successful_predictions'],
            'training_samples': self.metrics['training_samples'],
            'model_size': 'Simple Neural Network',
            'last_training': self.metrics['last_training'],
            'memory_usage': f"{len(self.operation_history)} operations in memory"
        }
    
    async def save_model(self):
        """Save the trained model"""
        try:
            model_data = {
                'model': self.model,
                'metrics': self.metrics,
                'operation_types': self.operation_types,
                'training_data': self.training_data[-100:]  # Keep recent training data
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
                
            logger.info("Model saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    async def load_model(self):
        """Load a saved model"""
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.metrics = model_data['metrics']
            self.operation_types = model_data['operation_types']
            self.training_data = model_data.get('training_data', [])
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    
    async def cleanup(self):
        """Cleanup AI engine resources"""
        try:
            await self.save_model()
            logger.info("AI Engine cleanup completed")
        except Exception as e:
            logger.error(f"AI Engine cleanup failed: {e}")
    
    # Private methods
    
    def _extract_features(self, operation: Dict[str, Any], result: Dict[str, Any]) -> List[float]:
        """Extract features from operation and result"""
        features = [0.0] * 50  # Fixed size feature vector
        
        # Operation type features
        op_type = operation.get('op', '')
        if op_type in ['ADD', 'REMOVE', 'MODIFY', 'CREATE', 'DELETE', 'REORDER', 'APPLY']:
            features[['ADD', 'REMOVE', 'MODIFY', 'CREATE', 'DELETE', 'REORDER', 'APPLY'].index(op_type)] = 1.0
        
        # Element type features
        element_type = operation.get('type', '')
        element_types = ['text', 'image', 'shape', 'chart', 'table', 'slide', 'theme']
        if element_type in element_types:
            features[7 + element_types.index(element_type)] = 1.0
        
        # Context features (simplified)
        data = operation.get('data', {})
        if isinstance(data, dict):
            features[14] = len(str(data)) / 1000.0  # Data complexity
            features[15] = 1.0 if 'x' in data else 0.0  # Has position
            features[16] = 1.0 if 'width' in data else 0.0  # Has size
        
        # Success feature
        features[17] = 1.0 if result.get('success', True) else 0.0
        
        return features
    
    def _create_target_vector(self, operation: Dict[str, Any]) -> List[float]:
        """Create target vector for training"""
        target = [0.0] * len(self.operation_types)
        
        op_type = operation.get('op', '')
        element_type = operation.get('type', '')
        
        # Create combined operation key
        op_key = f"{op_type}_{element_type}"
        
        if op_key in self.operation_types:
            target[self.operation_types.index(op_key)] = 1.0
        
        return target
    
    def _extract_context_features(self, context: Dict[str, Any]) -> List[float]:
        """Extract features from context"""
        features = [0.0] * 50
        
        current_slide = context.get('currentSlide', {})
        elements = current_slide.get('elements', [])
        
        # Slide features
        features[0] = len(elements) / 10.0  # Element count (normalized)
        features[1] = 1.0 if current_slide.get('layout') == 'blank' else 0.0
        
        # Element type counts
        element_types = ['text', 'image', 'shape', 'chart', 'table']
        for i, elem_type in enumerate(element_types):
            count = sum(1 for el in elements if el.get('type') == elem_type)
            features[2 + i] = count / 5.0  # Normalized count
        
        # Presentation features
        presentation = context.get('presentation', {})
        features[7] = presentation.get('totalSlides', 1) / 20.0  # Slide count
        
        return features
    
    def _create_atomic_operation(self, operation_type: str, context: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        """Create an atomic operation from prediction"""
        op_parts = operation_type.split('_', 1)
        op = op_parts[0]
        element_type = op_parts[1] if len(op_parts) > 1 else 'text'
        
        current_slide = context.get('currentSlide', {})
        slide_index = current_slide.get('index', 0)
        
        operation = {
            'op': op,
            'type': element_type,
            'target': slide_index,
            'timestamp': datetime.utcnow().timestamp() * 1000,
            'confidence': confidence
        }
        
        # Add operation-specific data
        if op == 'ADD':
            operation['data'] = self._generate_add_data(element_type, context)
        elif op == 'MODIFY':
            operation['data'] = self._generate_modify_data(element_type, context)
        elif op == 'CREATE':
            operation['data'] = {'layout': 'blank'}
        elif op == 'APPLY':
            operation['data'] = self._generate_apply_data(element_type, context)
        
        return operation
    
    def _generate_add_data(self, element_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for ADD operations"""
        base_data = {
            'x': random.randint(100, 400),
            'y': random.randint(100, 300)
        }
        
        if element_type == 'text':
            return {
                **base_data,
                'content': 'New text element',
                'width': 300,
                'height': 60,
                'fontSize': 16,
                'color': '#333333'
            }
        elif element_type == 'image':
            return {
                **base_data,
                'src': 'placeholder.jpg',
                'width': 200,
                'height': 150
            }
        elif element_type == 'shape':
            return {
                **base_data,
                'shape': 'rectangle',
                'width': 150,
                'height': 100,
                'fill': '#1976D2'
            }
        elif element_type == 'chart':
            return {
                **base_data,
                'chartType': 'bar',
                'width': 400,
                'height': 250,
                'data': {
                    'labels': ['A', 'B', 'C'],
                    'datasets': [{'data': [10, 20, 30]}]
                }
            }
        
        return base_data
    
    def _generate_modify_data(self, element_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for MODIFY operations"""
        return {
            'fontSize': 18,
            'color': '#1976D2'
        }
    
    def _generate_apply_data(self, element_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for APPLY operations"""
        if element_type == 'theme':
            return {
                'name': 'professional',
                'colorScheme': {
                    'primary': '#1976D2',
                    'secondary': '#424242',
                    'background': '#FFFFFF',
                    'text': '#333333'
                }
            }
        return {}
    
    def _generate_reasoning(self, operation: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate reasoning for the prediction"""
        op = operation.get('op')
        element_type = operation.get('type')
        
        current_slide = context.get('currentSlide', {})
        elements = current_slide.get('elements', [])
        
        if op == 'ADD':
            if len(elements) == 0:
                return f"The slide is empty, adding a {element_type} element would be a good start"
            else:
                return f"Based on current content, a {element_type} element would enhance the slide"
        elif op == 'MODIFY':
            return f"Existing elements could benefit from {element_type} modifications"
        elif op == 'CREATE':
            return "The presentation could benefit from an additional slide"
        
        return f"AI suggests this {op} operation based on learned patterns"
    
    async def _rule_based_prediction(self, context: Dict[str, Any]) -> AtomPrediction:
        """Fallback rule-based prediction when AI model isn't ready"""
        current_slide = context.get('currentSlide', {})
        elements = current_slide.get('elements', [])
        
        # Simple rules
        if len(elements) == 0:
            # Empty slide - suggest adding title
            operation = {
                'op': 'ADD',
                'type': 'text',
                'target': current_slide.get('index', 0),
                'data': {
                    'content': 'Slide Title',
                    'x': 100,
                    'y': 100,
                    'width': 600,
                    'height': 80,
                    'fontSize': 32,
                    'style': 'heading'
                },
                'timestamp': datetime.utcnow().timestamp() * 1000
            }
            return AtomPrediction(
                atom=operation,
                confidence=0.8,
                reasoning="Empty slide detected, suggesting title text",
                alternatives=[]
            )
        
        # Default suggestion
        operation = {
            'op': 'ADD',
            'type': 'text',
            'target': current_slide.get('index', 0),
            'data': {
                'content': 'Additional content',
                'x': 100,
                'y': 200,
                'width': 400,
                'height': 60,
                'fontSize': 16
            },
            'timestamp': datetime.utcnow().timestamp() * 1000
        }
        
        return AtomPrediction(
            atom=operation,
            confidence=0.6,
            reasoning="Rule-based suggestion for additional content",
            alternatives=[]
        )
    
    async def _get_pattern_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get suggestions based on discovered patterns"""
        patterns = self.pattern_matcher.find_patterns()
        suggestions = []
        
        for pattern in patterns[:2]:  # Top 2 patterns
            if pattern['confidence'] > 0.5:
                # Convert pattern to suggestion
                sequence = pattern['data']['sequence']
                if sequence:
                    next_op = sequence[0]  # Suggest first operation in pattern
                    suggestions.append({
                        **next_op,
                        'timestamp': datetime.utcnow().timestamp() * 1000,
                        'confidence': pattern['confidence']
                    })
        
        return suggestions
    
    async def _get_rule_based_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get rule-based suggestions"""
        current_slide = context.get('currentSlide', {})
        elements = current_slide.get('elements', [])
        suggestions = []
        
        # Suggest image if only text elements
        text_count = sum(1 for el in elements if el.get('type') == 'text')
        image_count = sum(1 for el in elements if el.get('type') == 'image')
        
        if text_count > 0 and image_count == 0:
            suggestions.append({
                'op': 'ADD',
                'type': 'image',
                'target': current_slide.get('index', 0),
                'data': {
                    'x': 400,
                    'y': 150,
                    'width': 300,
                    'height': 200,
                    'src': 'placeholder.jpg'
                },
                'timestamp': datetime.utcnow().timestamp() * 1000,
                'confidence': 0.7
            })
        
        return suggestions
    
    async def _retrain_model(self):
        """Retrain the neural network model"""
        try:
            if len(self.training_data) < 5:
                return
            
            # Prepare training data
            X = np.array([sample['features'] for sample in self.training_data])
            y = np.array([sample['target'] for sample in self.training_data])
            
            # Train model
            self.model.train(X, y, epochs=50)
            
            # Update metrics
            self.metrics['last_training'] = datetime.utcnow().isoformat()
            
            # Calculate accuracy (simplified)
            predictions = self.model.predict(X)
            predicted_classes = np.argmax(predictions, axis=1)
            actual_classes = np.argmax(y, axis=1)
            accuracy = np.mean(predicted_classes == actual_classes)
            self.metrics['accuracy'] = float(accuracy)
            
            logger.info(f"Model retrained. Accuracy: {accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"Model retraining failed: {e}")
    
    async def _generate_business_presentation(self, prompt: str, slide_count: int) -> List[Dict[str, Any]]:
        """Generate business presentation sequence"""
        atoms = []
        
        # Apply business theme
        atoms.append({
            'op': 'APPLY',
            'type': 'theme',
            'target': 'all',
            'data': {
                'name': 'corporate-blue',
                'colorScheme': {
                    'primary': '#1976D2',
                    'secondary': '#424242',
                    'background': '#FFFFFF',
                    'text': '#333333'
                }
            },
            'timestamp': datetime.utcnow().timestamp() * 1000
        })
        
        # Title slide
        atoms.append({
            'op': 'ADD',
            'type': 'text',
            'target': 0,
            'data': {
                'content': prompt[:50] + '...' if len(prompt) > 50 else prompt,
                'x': 100,
                'y': 200,
                'width': 800,
                'height': 100,
                'fontSize': 36,
                'style': 'title'
            },
            'timestamp': datetime.utcnow().timestamp() * 1000
        })
        
        # Add more slides
        for i in range(1, slide_count):
            atoms.append({
                'op': 'CREATE',
                'type': 'slide',
                'target': i - 1,
                'data': {'layout': 'content'},
                'timestamp': datetime.utcnow().timestamp() * 1000
            })
            
            # Add content to each slide
            atoms.append({
                'op': 'ADD',
                'type': 'text',
                'target': i,
                'data': {
                    'content': f'Slide {i + 1} Content',
                    'x': 100,
                    'y': 100,
                    'width': 600,
                    'height': 60,
                    'fontSize': 24,
                    'style': 'heading'
                },
                'timestamp': datetime.utcnow().timestamp() * 1000
            })
        
        return atoms
    
    async def _generate_educational_presentation(self, prompt: str, slide_count: int) -> List[Dict[str, Any]]:
        """Generate educational presentation sequence"""
        # Similar to business but with educational styling
        return await self._generate_business_presentation(prompt, slide_count)
    
    async def _generate_generic_presentation(self, prompt: str, slide_count: int) -> List[Dict[str, Any]]:
        """Generate generic presentation sequence"""
        return await self._generate_business_presentation(prompt, slide_count)