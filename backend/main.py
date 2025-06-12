"""
AI-Powered PPT Generation System Backend
FastAPI server with atomic operations tracking and AI learning
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import asyncio
import logging

from database import get_db, init_db
from models import *
from ai_engine import AIEngine
from enhanced_ai_engine import EnhancedAIEngine
from atomic_processor import AtomicProcessor
from websocket_manager import WebSocketManager, start_cleanup_task
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
ai_engine = EnhancedAIEngine()
atomic_processor = AtomicProcessor()
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🎯 Starting AI-PPT System Backend...")
    
    # Validate configuration
    if not config.validate_config():
        raise RuntimeError("Configuration validation failed")
    
    await init_db()
    
    # Initialize enhanced AI engine with DeepSeek provider
    ai_config = config.get_ai_providers_config()
    await ai_engine.initialize_enhanced(ai_config)
    
    start_cleanup_task()  # Start WebSocket cleanup task
    logger.info("✅ Backend initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down AI-PPT System Backend...")
    await ai_engine.cleanup()
    logger.info("✅ Backend shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="AI-PPT System API",
    description="Backend for AI-Powered PPT Generation with 7 Atomic Operations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "ai_ready": ai_engine.is_ready(),
        "operations_processed": atomic_processor.get_total_operations()
    }

# Atomic Operations Endpoints
@app.post("/api/operations")
async def record_operation(
    operation_data: Dict[str, Any],
    db = Depends(get_db)
):
    """Record an atomic operation for AI learning"""
    try:
        # Process the operation
        result = await atomic_processor.process_operation(operation_data, db)
        
        # Learn from the operation
        await ai_engine.learn_from_operation(operation_data, result)
        
        # Broadcast to connected clients
        await websocket_manager.broadcast({
            "type": "operation_recorded",
            "data": operation_data,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "operation_id": result.get("operation_id"),
            "processing_time": result.get("processing_time", 0)
        }
        
    except Exception as e:
        logger.error(f"Failed to record operation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/operations/recent")
async def get_recent_operations(
    limit: int = 10,
    user_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Get recent atomic operations"""
    try:
        operations = await atomic_processor.get_recent_operations(
            limit=limit, 
            user_id=user_id, 
            db=db
        )
        return operations
    except Exception as e:
        logger.error(f"Failed to get recent operations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/operations/stats")
async def get_operation_stats(db = Depends(get_db)):
    """Get operation statistics"""
    try:
        stats = await atomic_processor.get_operation_stats(db)
        return stats
    except Exception as e:
        logger.error(f"Failed to get operation stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Endpoints
@app.post("/api/ai/predict")
async def predict_next_atom(context: Dict[str, Any]):
    """Predict the next atomic operation based on context"""
    try:
        if not ai_engine.is_ready():
            raise HTTPException(
                status_code=503, 
                detail="AI engine is not ready. Need more training data."
            )
        
        prediction = await ai_engine.predict_next_atom(context)
        return prediction
        
    except Exception as e:
        logger.error(f"AI prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/suggestions")
async def generate_suggestions(context: Dict[str, Any]):
    """Generate AI suggestions for the current context"""
    try:
        suggestions = await ai_engine.generate_suggestions(context)
        return suggestions
        
    except Exception as e:
        logger.error(f"Failed to generate suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/learn")
async def learn_from_operation(
    operation_data: Dict[str, Any],
    db = Depends(get_db)
):
    """Explicitly train AI from an operation"""
    try:
        result = await ai_engine.learn_from_operation(
            operation_data.get("operation"),
            operation_data.get("result")
        )
        
        # Store learning data
        await atomic_processor.store_learning_data(operation_data, db)
        
        return {
            "success": True,
            "learning_result": result
        }
        
    except Exception as e:
        logger.error(f"AI learning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/generate-presentation")
async def generate_presentation(prompt_data: Dict[str, Any]):
    """Generate a complete presentation from a prompt"""
    try:
        if not ai_engine.is_ready():
            raise HTTPException(
                status_code=503,
                detail="AI engine is not ready for presentation generation"
            )
        
        sequence = await ai_engine.generate_presentation_sequence(
            prompt_data.get("prompt", ""),
            prompt_data.get("type", "business"),
            prompt_data.get("slides", 10)
        )
        
        return sequence
        
    except Exception as e:
        logger.error(f"Presentation generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/patterns")
async def get_operation_patterns(db = Depends(get_db)):
    """Get discovered operation patterns"""
    try:
        patterns = await ai_engine.get_operation_patterns(db)
        return patterns
    except Exception as e:
        logger.error(f"Failed to get patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/sequences")
async def get_operation_sequences(db = Depends(get_db)):
    """Get saved operation sequences"""
    try:
        sequences = await atomic_processor.get_operation_sequences(db)
        return sequences
    except Exception as e:
        logger.error(f"Failed to get sequences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/metrics")
async def get_ai_metrics():
    """Get AI model performance metrics"""
    try:
        metrics = await ai_engine.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get AI metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/generate-ppt")
async def generate_ppt(request: Dict[str, Any]):
    """Generate a complete PowerPoint presentation using DeepSeek AI"""
    try:
        prompt = request.get("prompt", "")
        slides = request.get("slides", 5)
        theme = request.get("theme", "professional")
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # Use the enhanced AI engine to generate PPT with DeepSeek
        result = await ai_engine.generate_presentation(prompt, slides, theme)
        
        return {
            "success": True,
            "presentation": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"PPT generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Presentation Management Endpoints
@app.post("/api/presentations")
async def create_presentation(
    presentation_data: Dict[str, Any],
    db = Depends(get_db)
):
    """Create a new presentation"""
    try:
        presentation = await atomic_processor.create_presentation(presentation_data, db)
        return presentation
    except Exception as e:
        logger.error(f"Failed to create presentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/presentations/{presentation_id}")
async def get_presentation(presentation_id: str, db = Depends(get_db)):
    """Get a presentation by ID"""
    try:
        presentation = await atomic_processor.get_presentation(presentation_id, db)
        if not presentation:
            raise HTTPException(status_code=404, detail="Presentation not found")
        return presentation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get presentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/presentations/{presentation_id}")
async def update_presentation(
    presentation_id: str,
    presentation_data: Dict[str, Any],
    db = Depends(get_db)
):
    """Update a presentation"""
    try:
        presentation = await atomic_processor.update_presentation(
            presentation_id, 
            presentation_data, 
            db
        )
        return presentation
    except Exception as e:
        logger.error(f"Failed to update presentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/presentations/{presentation_id}")
async def delete_presentation(presentation_id: str, db = Depends(get_db)):
    """Delete a presentation"""
    try:
        result = await atomic_processor.delete_presentation(presentation_id, db)
        return {"success": True, "deleted": result}
    except Exception as e:
        logger.error(f"Failed to delete presentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/presentations")
async def list_presentations(
    limit: int = 20,
    offset: int = 0,
    user_id: Optional[str] = None,
    db = Depends(get_db)
):
    """List presentations"""
    try:
        presentations = await atomic_processor.list_presentations(
            limit=limit,
            offset=offset,
            user_id=user_id,
            db=db
        )
        return presentations
    except Exception as e:
        logger.error(f"Failed to list presentations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# User Management Endpoints
@app.get("/api/user/preferences")
async def get_user_preferences(user_id: Optional[str] = None, db = Depends(get_db)):
    """Get user preferences"""
    try:
        preferences = await atomic_processor.get_user_preferences(user_id, db)
        return preferences
    except Exception as e:
        logger.error(f"Failed to get user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/user/preferences")
async def update_user_preferences(
    preferences: Dict[str, Any],
    user_id: Optional[str] = None,
    db = Depends(get_db)
):
    """Update user preferences"""
    try:
        result = await atomic_processor.update_user_preferences(
            user_id, 
            preferences, 
            db
        )
        return result
    except Exception as e:
        logger.error(f"Failed to update user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }))
            elif message.get("type") == "subscribe":
                # Handle subscription to specific events
                pass
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)

# Template and Asset Endpoints
@app.post("/api/ai/suggest-template")
async def suggest_template(content_data: Dict[str, Any]):
    """Suggest a template based on content analysis"""
    try:
        template = await ai_engine.suggest_template(content_data.get("content", ""))
        return {"template": template}
    except Exception as e:
        logger.error(f"Template suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/enhance-content")
async def enhance_content(content_data: Dict[str, Any]):
    """Enhance content using AI"""
    try:
        enhanced = await ai_engine.enhance_content(
            content_data.get("elementId"),
            content_data.get("content", "")
        )
        return {"enhancedContent": enhanced}
    except Exception as e:
        logger.error(f"Content enhancement failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints
@app.get("/api/analytics/usage")
async def get_usage_analytics(
    days: int = 7,
    db = Depends(get_db)
):
    """Get usage analytics"""
    try:
        analytics = await atomic_processor.get_usage_analytics(days, db)
        return analytics
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/performance")
async def get_performance_metrics():
    """Get system performance metrics"""
    try:
        metrics = {
            "ai_engine": await ai_engine.get_performance_metrics(),
            "atomic_processor": atomic_processor.get_performance_metrics(),
            "websocket_connections": websocket_manager.get_connection_count(),
            "system_health": {
                "cpu_usage": "N/A",  # Would implement actual monitoring
                "memory_usage": "N/A",
                "disk_usage": "N/A"
            }
        }
        return metrics
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export/Import Endpoints
@app.post("/api/export/pptx/{presentation_id}")
async def export_to_pptx(presentation_id: str, db = Depends(get_db)):
    """Export presentation to PPTX format"""
    try:
        # This would implement actual PPTX export
        # For now, return a placeholder
        return {
            "success": True,
            "download_url": f"/api/download/pptx/{presentation_id}",
            "message": "PPTX export functionality would be implemented here"
        }
    except Exception as e:
        logger.error(f"PPTX export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/import/pptx")
async def import_from_pptx(file_data: Dict[str, Any], db = Depends(get_db)):
    """Import presentation from PPTX format"""
    try:
        # This would implement actual PPTX import
        # For now, return a placeholder
        return {
            "success": True,
            "presentation_id": "imported_presentation_id",
            "message": "PPTX import functionality would be implemented here"
        }
    except Exception as e:
        logger.error(f"PPTX import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files (frontend) - Mount last to avoid conflicts with API routes
import os
dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")
if os.path.exists(dist_path):
    # Mount static files with lower priority than API routes
    from fastapi.responses import FileResponse
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(dist_path, "index.html"))
    
    # Serve static assets
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")
    
    # Serve specific static files
    @app.get("/vite.svg")
    async def serve_vite_svg():
        svg_path = os.path.join(dist_path, "vite.svg")
        if os.path.exists(svg_path):
            return FileResponse(svg_path)
        # Return a simple SVG if file doesn't exist
        from fastapi.responses import Response
        return Response(
            content='<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><circle cx="16" cy="16" r="14" fill="#646cff"/></svg>',
            media_type="image/svg+xml"
        )
    
    @app.get("/favicon.ico")
    async def serve_favicon():
        favicon_path = os.path.join(dist_path, "favicon.ico")
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path)
        # Fallback to vite.svg
        svg_path = os.path.join(dist_path, "vite.svg")
        if os.path.exists(svg_path):
            return FileResponse(svg_path)
        # Return simple SVG
        from fastapi.responses import Response
        return Response(
            content='<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><circle cx="16" cy="16" r="14" fill="#646cff"/></svg>',
            media_type="image/svg+xml"
        )
    logger.info(f"✅ Serving frontend from {dist_path}")
else:
    logger.warning(f"⚠️ Frontend dist directory not found at {dist_path}")

if __name__ == "__main__":
    # Development server
    import os
    port = int(os.getenv("API_PORT", 12001))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )