"""
Atomic Operations Processor
Handles storage, retrieval, and analysis of atomic operations
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
import uuid

from models import (
    AtomicOperation, 
    Presentation, 
    OperationSequence, 
    UserSession,
    UserPreferences,
    OperationPattern,
    LearningData
)
from database import CacheManager

logger = logging.getLogger(__name__)

class AtomicProcessor:
    """Processor for atomic operations and data management"""
    
    def __init__(self):
        self.cache = CacheManager()
        self.performance_metrics = {
            'total_operations': 0,
            'average_processing_time': 0.0,
            'operations_per_second': 0.0,
            'cache_hit_rate': 0.0
        }
        
    async def process_operation(self, operation_data: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Process and store an atomic operation"""
        start_time = datetime.utcnow()
        
        try:
            # Validate operation data
            if not operation_data or not isinstance(operation_data, dict):
                raise ValueError("Invalid operation data")
            
            # Extract operation details with proper defaults
            op = operation_data.get('op', '')
            op_type = operation_data.get('type', '')
            target = operation_data.get('target', '')
            data = operation_data.get('data', {})
            
            # Ensure data is a dictionary
            if not isinstance(data, dict):
                data = {}
            
            # Create operation record with safe defaults
            operation = AtomicOperation(
                operation=op,
                element_type=op_type,
                target=str(target),
                data=data,
                timestamp=datetime.utcnow(),
                user_id=operation_data.get('userId'),
                session_id=operation_data.get('sessionId'),
                presentation_id=operation_data.get('presentationId'),
                slide_index=operation_data.get('slideIndex', 0),
                context=operation_data.get('context', {}),
                success=True
            )
            
            # Calculate execution time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            operation.execution_time_ms = processing_time
            
            # Store in database
            db.add(operation)
            await db.commit()
            await db.refresh(operation)
            
            # Update performance metrics
            self.performance_metrics['total_operations'] += 1
            self._update_performance_metrics(processing_time)
            
            # Cache recent operations
            await self._cache_operation(operation)
            
            logger.debug(f"Processed operation {operation.id} in {processing_time:.2f}ms")
            
            return {
                'operation_id': operation.id,
                'processing_time': processing_time,
                'success': True
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to process operation: {e}")
            raise
    
    async def get_recent_operations(
        self, 
        limit: int = 10, 
        user_id: Optional[str] = None,
        db: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """Get recent atomic operations"""
        try:
            # Try cache first
            cache_key = f"recent_ops_{user_id}_{limit}"
            cached = await self.cache.get(cache_key)
            if cached:
                self.performance_metrics['cache_hit_rate'] += 1
                return json.loads(cached)
            
            # Query database
            query = select(AtomicOperation).order_by(desc(AtomicOperation.timestamp)).limit(limit)
            
            if user_id:
                query = query.where(AtomicOperation.user_id == user_id)
            
            result = await db.execute(query)
            operations = result.scalars().all()
            
            # Convert to dict
            operations_data = [op.to_dict() for op in operations]
            
            # Cache result
            await self.cache.set(cache_key, json.dumps(operations_data), expire=300)
            
            return operations_data
            
        except Exception as e:
            logger.error(f"Failed to get recent operations: {e}")
            return []
    
    async def get_operation_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get operation statistics"""
        try:
            # Total operations
            total_result = await db.execute(select(func.count(AtomicOperation.id)))
            total_operations = total_result.scalar()
            
            # Operations by type
            type_result = await db.execute(
                select(
                    AtomicOperation.operation,
                    func.count(AtomicOperation.id).label('count')
                ).group_by(AtomicOperation.operation)
            )
            operations_by_type = {row.operation: row.count for row in type_result}
            
            # Operations by element type
            element_result = await db.execute(
                select(
                    AtomicOperation.element_type,
                    func.count(AtomicOperation.id).label('count')
                ).group_by(AtomicOperation.element_type)
            )
            operations_by_element = {row.element_type: row.count for row in element_result}
            
            # Recent activity (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_result = await db.execute(
                select(func.count(AtomicOperation.id))
                .where(AtomicOperation.timestamp >= yesterday)
            )
            recent_operations = recent_result.scalar()
            
            # Average execution time
            avg_time_result = await db.execute(
                select(func.avg(AtomicOperation.execution_time_ms))
                .where(AtomicOperation.execution_time_ms.isnot(None))
            )
            avg_execution_time = avg_time_result.scalar() or 0
            
            return {
                'total_operations': total_operations,
                'operations_by_type': operations_by_type,
                'operations_by_element': operations_by_element,
                'recent_operations_24h': recent_operations,
                'average_execution_time_ms': float(avg_execution_time),
                'performance_metrics': self.performance_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get operation stats: {e}")
            return {}
    
    async def create_presentation(self, presentation_data: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
        """Create a new presentation"""
        try:
            # Count slides and elements
            slides = presentation_data.get('slides', [])
            slide_count = len(slides)
            element_count = sum(len(slide.get('elements', [])) for slide in slides)
            
            presentation = Presentation(
                title=presentation_data.get('title', 'Untitled Presentation'),
                data=presentation_data,
                user_id=presentation_data.get('metadata', {}).get('author'),
                version=presentation_data.get('metadata', {}).get('version', '1.0.0'),
                tags=presentation_data.get('metadata', {}).get('tags', []),
                slide_count=slide_count,
                element_count=element_count,
                theme_name=presentation_data.get('theme', {}).get('name')
            )
            
            db.add(presentation)
            await db.commit()
            await db.refresh(presentation)
            
            logger.info(f"Created presentation {presentation.id}")
            return presentation.to_dict()
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create presentation: {e}")
            raise
    
    async def get_presentation(self, presentation_id: str, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """Get a presentation by ID"""
        try:
            # Try cache first
            cache_key = f"presentation_{presentation_id}"
            cached = await self.cache.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Query database
            result = await db.execute(
                select(Presentation).where(Presentation.id == presentation_id)
            )
            presentation = result.scalar_one_or_none()
            
            if presentation:
                data = presentation.to_dict()
                # Cache for 1 hour
                await self.cache.set(cache_key, json.dumps(data), expire=3600)
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get presentation {presentation_id}: {e}")
            return None
    
    async def update_presentation(
        self, 
        presentation_id: str, 
        presentation_data: Dict[str, Any], 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Update a presentation"""
        try:
            result = await db.execute(
                select(Presentation).where(Presentation.id == presentation_id)
            )
            presentation = result.scalar_one_or_none()
            
            if not presentation:
                raise ValueError(f"Presentation {presentation_id} not found")
            
            # Update fields
            presentation.title = presentation_data.get('title', presentation.title)
            presentation.data = presentation_data
            presentation.updated_at = datetime.utcnow()
            
            # Update metadata
            slides = presentation_data.get('slides', [])
            presentation.slide_count = len(slides)
            presentation.element_count = sum(len(slide.get('elements', [])) for slide in slides)
            presentation.theme_name = presentation_data.get('theme', {}).get('name')
            
            await db.commit()
            await db.refresh(presentation)
            
            # Invalidate cache
            cache_key = f"presentation_{presentation_id}"
            await self.cache.delete(cache_key)
            
            logger.info(f"Updated presentation {presentation_id}")
            return presentation.to_dict()
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update presentation {presentation_id}: {e}")
            raise
    
    async def delete_presentation(self, presentation_id: str, db: AsyncSession) -> bool:
        """Delete a presentation"""
        try:
            result = await db.execute(
                select(Presentation).where(Presentation.id == presentation_id)
            )
            presentation = result.scalar_one_or_none()
            
            if presentation:
                await db.delete(presentation)
                await db.commit()
                
                # Invalidate cache
                cache_key = f"presentation_{presentation_id}"
                await self.cache.delete(cache_key)
                
                logger.info(f"Deleted presentation {presentation_id}")
                return True
            
            return False
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete presentation {presentation_id}: {e}")
            raise
    
    async def list_presentations(
        self,
        limit: int = 20,
        offset: int = 0,
        user_id: Optional[str] = None,
        db: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """List presentations"""
        try:
            query = select(Presentation).order_by(desc(Presentation.updated_at)).limit(limit).offset(offset)
            
            if user_id:
                query = query.where(Presentation.user_id == user_id)
            
            result = await db.execute(query)
            presentations = result.scalars().all()
            
            return [p.to_dict() for p in presentations]
            
        except Exception as e:
            logger.error(f"Failed to list presentations: {e}")
            return []
    
    async def get_operation_sequences(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get saved operation sequences"""
        try:
            result = await db.execute(
                select(OperationSequence)
                .order_by(desc(OperationSequence.created_at))
                .limit(50)
            )
            sequences = result.scalars().all()
            
            return [seq.to_dict() for seq in sequences]
            
        except Exception as e:
            logger.error(f"Failed to get operation sequences: {e}")
            return []
    
    async def store_learning_data(self, operation_data: Dict[str, Any], db: AsyncSession):
        """Store data for AI learning"""
        try:
            learning_data = LearningData(
                operation_id=operation_data.get('operation_id'),
                input_features=operation_data.get('input_features', {}),
                output_target=operation_data.get('output_target', {}),
                model_version=operation_data.get('model_version', '1.0.0')
            )
            
            db.add(learning_data)
            await db.commit()
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to store learning data: {e}")
    
    async def get_user_preferences(self, user_id: Optional[str], db: AsyncSession) -> Dict[str, Any]:
        """Get user preferences"""
        try:
            if not user_id:
                return self._get_default_preferences()
            
            result = await db.execute(
                select(UserPreferences).where(UserPreferences.user_id == user_id)
            )
            preferences = result.scalar_one_or_none()
            
            if preferences:
                return preferences.preferences
            else:
                return self._get_default_preferences()
                
        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
            return self._get_default_preferences()
    
    async def update_user_preferences(
        self, 
        user_id: Optional[str], 
        preferences: Dict[str, Any], 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Update user preferences"""
        try:
            if not user_id:
                return preferences
            
            result = await db.execute(
                select(UserPreferences).where(UserPreferences.user_id == user_id)
            )
            user_prefs = result.scalar_one_or_none()
            
            if user_prefs:
                user_prefs.preferences = preferences
                user_prefs.updated_at = datetime.utcnow()
            else:
                user_prefs = UserPreferences(
                    user_id=user_id,
                    preferences=preferences
                )
                db.add(user_prefs)
            
            await db.commit()
            await db.refresh(user_prefs)
            
            return user_prefs.preferences
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update user preferences: {e}")
            raise
    
    async def get_usage_analytics(self, days: int, db: AsyncSession) -> Dict[str, Any]:
        """Get usage analytics for the specified number of days"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Operations per day
            daily_ops_result = await db.execute(
                select(
                    func.date(AtomicOperation.timestamp).label('date'),
                    func.count(AtomicOperation.id).label('count')
                )
                .where(AtomicOperation.timestamp >= start_date)
                .group_by(func.date(AtomicOperation.timestamp))
                .order_by(func.date(AtomicOperation.timestamp))
            )
            daily_operations = [
                {'date': row.date.isoformat(), 'count': row.count}
                for row in daily_ops_result
            ]
            
            # Most used operations
            popular_ops_result = await db.execute(
                select(
                    AtomicOperation.operation,
                    func.count(AtomicOperation.id).label('count')
                )
                .where(AtomicOperation.timestamp >= start_date)
                .group_by(AtomicOperation.operation)
                .order_by(desc(func.count(AtomicOperation.id)))
                .limit(10)
            )
            popular_operations = [
                {'operation': row.operation, 'count': row.count}
                for row in popular_ops_result
            ]
            
            # User activity
            active_users_result = await db.execute(
                select(func.count(func.distinct(AtomicOperation.user_id)))
                .where(
                    and_(
                        AtomicOperation.timestamp >= start_date,
                        AtomicOperation.user_id.isnot(None)
                    )
                )
            )
            active_users = active_users_result.scalar() or 0
            
            return {
                'period_days': days,
                'daily_operations': daily_operations,
                'popular_operations': popular_operations,
                'active_users': active_users,
                'total_operations': sum(day['count'] for day in daily_operations)
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage analytics: {e}")
            return {}
    
    def get_total_operations(self) -> int:
        """Get total number of operations processed"""
        return self.performance_metrics['total_operations']
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.performance_metrics.copy()
    
    # Private methods
    
    async def _cache_operation(self, operation: AtomicOperation):
        """Cache operation for quick access"""
        try:
            cache_key = f"operation_{operation.id}"
            await self.cache.set(
                cache_key, 
                json.dumps(operation.to_dict()), 
                expire=3600
            )
        except Exception as e:
            logger.warning(f"Failed to cache operation: {e}")
    
    def _update_performance_metrics(self, processing_time: float):
        """Update performance metrics"""
        total_ops = self.performance_metrics['total_operations']
        current_avg = self.performance_metrics['average_processing_time']
        
        # Update average processing time
        new_avg = ((current_avg * (total_ops - 1)) + processing_time) / total_ops
        self.performance_metrics['average_processing_time'] = new_avg
        
        # Calculate operations per second (simplified)
        if processing_time > 0:
            ops_per_second = 1000 / processing_time  # Convert ms to seconds
            self.performance_metrics['operations_per_second'] = ops_per_second
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default user preferences"""
        return {
            'theme': 'light',
            'auto_save': True,
            'ai_suggestions': True,
            'grid_visible': False,
            'snap_to_grid': True,
            'default_font': 'Arial',
            'default_font_size': 16,
            'default_colors': {
                'text': '#333333',
                'background': '#FFFFFF',
                'accent': '#1976D2'
            },
            'shortcuts': {
                'save': 'Ctrl+S',
                'undo': 'Ctrl+Z',
                'redo': 'Ctrl+Y',
                'copy': 'Ctrl+C',
                'paste': 'Ctrl+V'
            }
        }