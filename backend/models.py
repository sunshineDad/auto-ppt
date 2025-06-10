"""
Database models for AI-PPT System
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

Base = declarative_base()

class AtomicOperation(Base):
    """Model for storing atomic operations"""
    __tablename__ = "atomic_operations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    operation = Column(String, nullable=False)  # ADD, REMOVE, MODIFY, etc.
    element_type = Column(String, nullable=False)  # text, image, shape, etc.
    target = Column(String, nullable=False)  # target identifier
    data = Column(JSON, nullable=True)  # operation data
    timestamp = Column(DateTime, default=func.now())
    user_id = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    presentation_id = Column(String, nullable=True)
    slide_index = Column(Integer, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # Context information
    context = Column(JSON, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "operation": self.operation,
            "element_type": self.element_type,
            "target": self.target,
            "data": self.data,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "presentation_id": self.presentation_id,
            "slide_index": self.slide_index,
            "execution_time_ms": self.execution_time_ms,
            "success": self.success,
            "error_message": self.error_message,
            "context": self.context
        }

class Presentation(Base):
    """Model for storing presentations"""
    __tablename__ = "presentations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    data = Column(JSON, nullable=False)  # Complete presentation data
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(String, nullable=True)
    version = Column(String, default="1.0.0")
    tags = Column(JSON, nullable=True)
    
    # Metadata
    slide_count = Column(Integer, default=0)
    element_count = Column(Integer, default=0)
    theme_name = Column(String, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "data": self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
            "version": self.version,
            "tags": self.tags,
            "slide_count": self.slide_count,
            "element_count": self.element_count,
            "theme_name": self.theme_name
        }

class OperationSequence(Base):
    """Model for storing operation sequences (patterns)"""
    __tablename__ = "operation_sequences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    operations = Column(JSON, nullable=False)  # List of atomic operations
    created_at = Column(DateTime, default=func.now())
    user_id = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    usage_count = Column(Integer, default=0)
    
    # Pattern metadata
    pattern_type = Column(String, nullable=True)  # manual, ai_generated, discovered
    confidence_score = Column(Float, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "operations": self.operations,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user_id": self.user_id,
            "tags": self.tags,
            "usage_count": self.usage_count,
            "pattern_type": self.pattern_type,
            "confidence_score": self.confidence_score
        }

class UserSession(Base):
    """Model for tracking user sessions"""
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime, nullable=True)
    presentation_id = Column(String, nullable=True)
    operation_count = Column(Integer, default=0)
    
    # Session metadata
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "presentation_id": self.presentation_id,
            "operation_count": self.operation_count,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address
        }

class AIModel(Base):
    """Model for storing AI model metadata"""
    __tablename__ = "ai_models"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # prediction, generation, etc.
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Model performance metrics
    accuracy = Column(Float, nullable=True)
    training_samples = Column(Integer, default=0)
    prediction_count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)
    
    # Model configuration
    config = Column(JSON, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "model_type": self.model_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "accuracy": self.accuracy,
            "training_samples": self.training_samples,
            "prediction_count": self.prediction_count,
            "success_rate": self.success_rate,
            "config": self.config
        }

class UserPreferences(Base):
    """Model for storing user preferences"""
    __tablename__ = "user_preferences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, unique=True)
    preferences = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "preferences": self.preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class OperationPattern(Base):
    """Model for discovered operation patterns"""
    __tablename__ = "operation_patterns"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pattern_name = Column(String, nullable=False)
    pattern_data = Column(JSON, nullable=False)
    frequency = Column(Integer, default=1)
    confidence = Column(Float, nullable=False)
    discovered_at = Column(DateTime, default=func.now())
    last_seen = Column(DateTime, default=func.now())
    
    # Pattern classification
    category = Column(String, nullable=True)  # layout, styling, content, etc.
    complexity = Column(String, nullable=True)  # simple, medium, complex
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "pattern_name": self.pattern_name,
            "pattern_data": self.pattern_data,
            "frequency": self.frequency,
            "confidence": self.confidence,
            "discovered_at": self.discovered_at.isoformat() if self.discovered_at else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "category": self.category,
            "complexity": self.complexity
        }

class LearningData(Base):
    """Model for storing AI learning data"""
    __tablename__ = "learning_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    operation_id = Column(String, ForeignKey("atomic_operations.id"))
    input_features = Column(JSON, nullable=False)
    output_target = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Learning metadata
    model_version = Column(String, nullable=True)
    training_batch = Column(String, nullable=True)
    validation_score = Column(Float, nullable=True)
    
    # Relationship
    operation = relationship("AtomicOperation", backref="learning_data")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "operation_id": self.operation_id,
            "input_features": self.input_features,
            "output_target": self.output_target,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "model_version": self.model_version,
            "training_batch": self.training_batch,
            "validation_score": self.validation_score
        }