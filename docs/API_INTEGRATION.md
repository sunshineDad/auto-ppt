# AI-PPT System API Integration Guide

## Overview

This guide provides comprehensive documentation for integrating with the AI-PPT System's APIs, including DeepSeek AI integration, atomic operations, and real-time collaboration features.

## Authentication

### API Key Authentication

```bash
# Set environment variable
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# Or include in request headers
curl -H "Authorization: Bearer your-api-key" \
     -H "Content-Type: application/json" \
     https://api.your-domain.com/api/endpoint
```

### JWT Token Authentication

```javascript
// Frontend authentication
const token = localStorage.getItem('auth_token');
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

## Core API Endpoints

### Health Check Endpoints

#### System Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "uptime": 3600,
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "ai_providers": "healthy"
  }
}
```

#### AI Health Check
```http
GET /health/ai
```

**Response:**
```json
{
  "ai_ready": true,
  "model_status": "operational",
  "providers": {
    "deepseek": {
      "status": "healthy",
      "response_time_ms": 250,
      "success_rate": 99.5
    },
    "local": {
      "status": "healthy",
      "model_ready": true,
      "training_samples": 1500
    }
  }
}
```

### Atomic Operations API

#### Process Operation
```http
POST /api/operations/process
```

**Request Body:**
```json
{
  "operation": {
    "op": "ADD",
    "type": "text",
    "target": "slide-1",
    "data": {
      "content": "Hello World",
      "position": {"x": 100, "y": 100},
      "style": {"fontSize": 24, "color": "#000000"}
    },
    "timestamp": 1640995200000,
    "userId": "user-123",
    "sessionId": "session-456"
  },
  "presentationId": "presentation-789",
  "slideIndex": 0,
  "context": {
    "currentSlide": {"id": "slide-1", "elements": []},
    "presentation": {"title": "My Presentation"},
    "userBehavior": {"lastAction": "click", "frequency": 1}
  },
  "result": {
    "success": true,
    "elementId": "element-new",
    "processingTime": 50
  }
}
```

**Response:**
```json
{
  "success": true,
  "operation_id": "op-12345",
  "processing_time": 45.2,
  "element_id": "element-new"
}
```

#### Get Recent Operations
```http
GET /api/operations/recent?limit=10&user_id=user-123
```

**Response:**
```json
[
  {
    "id": "op-12345",
    "operation": "ADD",
    "element_type": "text",
    "target": "slide-1",
    "timestamp": "2024-01-01T00:00:00Z",
    "user_id": "user-123",
    "success": true,
    "execution_time_ms": 45.2
  }
]
```

#### Get Operation Statistics
```http
GET /api/operations/stats
```

**Response:**
```json
{
  "total_operations": 1500,
  "operations_by_type": {
    "ADD": 800,
    "MODIFY": 500,
    "DELETE": 200
  },
  "operations_by_element": {
    "text": 900,
    "image": 400,
    "shape": 200
  },
  "recent_operations_24h": 150,
  "average_execution_time_ms": 42.5,
  "performance_metrics": {
    "total_operations": 1500,
    "average_processing_time": 42.5,
    "operations_per_second": 2.5,
    "cache_hit_rate": 0.85
  }
}
```

### Presentation Management API

#### Create Presentation
```http
POST /api/presentations
```

**Request Body:**
```json
{
  "title": "My New Presentation",
  "slides": [
    {
      "id": "slide-1",
      "elements": [
        {
          "id": "element-1",
          "type": "text",
          "content": "Title Slide",
          "position": {"x": 100, "y": 100},
          "style": {"fontSize": 32, "color": "#000000"}
        }
      ]
    }
  ],
  "theme": {
    "name": "professional",
    "colors": {
      "primary": "#007bff",
      "secondary": "#6c757d"
    }
  },
  "metadata": {
    "author": "user-123",
    "version": "1.0.0",
    "tags": ["business", "quarterly"]
  }
}
```

**Response:**
```json
{
  "id": "presentation-789",
  "title": "My New Presentation",
  "slide_count": 1,
  "element_count": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Get Presentation
```http
GET /api/presentations/{presentation_id}
```

**Response:**
```json
{
  "id": "presentation-789",
  "title": "My New Presentation",
  "slide_count": 1,
  "element_count": 1,
  "data": {
    "slides": [...],
    "theme": {...},
    "metadata": {...}
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Update Presentation
```http
PUT /api/presentations/{presentation_id}
```

#### Delete Presentation
```http
DELETE /api/presentations/{presentation_id}
```

#### List Presentations
```http
GET /api/presentations?limit=20&offset=0&user_id=user-123
```

### AI Integration API

#### AI Prediction
```http
POST /api/ai/predict
```

**Request Body:**
```json
{
  "context": {
    "currentSlide": {
      "id": "slide-1",
      "elements": []
    },
    "presentation": {
      "title": "Business Report",
      "theme": "professional"
    },
    "userBehavior": {
      "lastAction": "click",
      "frequency": 5,
      "sessionDuration": 300
    }
  },
  "operation_type": "content_generation",
  "preferred_provider": "deepseek",
  "use_ai_provider": true
}
```

**Response:**
```json
{
  "atom": {
    "op": "ADD",
    "type": "text",
    "target": "slide-1",
    "data": {
      "content": "Quarterly Revenue Analysis",
      "position": {"x": 200, "y": 150},
      "style": {"fontSize": 28, "color": "#333333"}
    },
    "timestamp": 1640995200000,
    "userId": "ai-system",
    "sessionId": "ai-session"
  },
  "confidence": 0.89,
  "reasoning": "Based on business context and slide position, a title would be appropriate",
  "alternatives": [
    {
      "op": "ADD",
      "type": "chart",
      "data": {"type": "bar", "title": "Revenue Chart"}
    }
  ],
  "provider_used": "deepseek",
  "model_used": "deepseek-chat",
  "cost_estimate": {
    "estimated_cost_usd": 0.0042,
    "tokens_used": 300
  },
  "response_time": 1.25
}
```

#### AI Suggestions
```http
POST /api/ai/suggestions
```

**Request Body:**
```json
{
  "context": {
    "currentSlide": {"id": "slide-1", "elements": []},
    "presentation": {"title": "Business Report"},
    "userBehavior": {"lastAction": "create_slide"}
  },
  "max_suggestions": 5
}
```

**Response:**
```json
[
  {
    "op": "ADD",
    "type": "text",
    "data": {"content": "Title Slide"},
    "confidence": 0.9
  },
  {
    "op": "ADD",
    "type": "image",
    "data": {"placeholder": "Company Logo"},
    "confidence": 0.8
  },
  {
    "op": "ADD",
    "type": "chart",
    "data": {"type": "bar", "title": "Revenue Data"},
    "confidence": 0.75
  }
]
```

#### Generate Presentation
```http
POST /api/ai/generate-presentation
```

**Request Body:**
```json
{
  "prompt": "Create a quarterly business results presentation",
  "presentation_type": "business",
  "slide_count": 8,
  "style_preferences": {
    "theme": "professional",
    "color_scheme": "blue",
    "layout": "minimal"
  },
  "content_requirements": {
    "include_charts": true,
    "include_images": false,
    "data_heavy": true
  }
}
```

**Response:**
```json
{
  "id": "ai_generated_20240101_120000",
  "name": "AI Generated: Create a quarterly business results...",
  "description": "Generated presentation based on: Create a quarterly business results presentation",
  "atoms": [
    {
      "step": 1,
      "operation": "CREATE",
      "type": "slide",
      "data": {"title": "Q4 2024 Business Results"}
    },
    {
      "step": 2,
      "operation": "ADD",
      "type": "text",
      "data": {"content": "Executive Summary", "style": "heading"}
    }
  ],
  "createdAt": 1640995200000,
  "tags": ["ai-generated", "business", "enhanced"],
  "metadata": {
    "generation_method": "enhanced_ai",
    "provider_used": "deepseek",
    "confidence": 0.85,
    "cost_estimate": {"total_cost_usd": 0.025},
    "generation_time": 3.2
  }
}
```

#### Template Suggestion
```http
POST /api/ai/suggest-template
```

**Request Body:**
```json
{
  "content": "sales revenue profit business quarterly results"
}
```

**Response:**
```json
{
  "template": "business-report",
  "confidence": 0.92,
  "reasoning": "Content contains business and financial keywords"
}
```

#### Content Enhancement
```http
POST /api/ai/enhance-content
```

**Request Body:**
```json
{
  "element_id": "element-123",
  "content": "hello world this is a test"
}
```

**Response:**
```json
{
  "enhanced_content": "Hello world, this is a test.",
  "changes_made": [
    "Capitalized first letter",
    "Added proper punctuation",
    "Improved grammar"
  ],
  "confidence": 0.95
}
```

#### AI Metrics
```http
GET /api/ai/metrics
```

**Response:**
```json
{
  "model_ready": true,
  "training_samples": 1500,
  "total_predictions": 2500,
  "successful_predictions": 2375,
  "accuracy": 0.95,
  "enhanced_metrics": {
    "provider_usage": {
      "deepseek": 1800,
      "local": 700
    },
    "total_cost": 12.45,
    "average_confidence": 0.87,
    "cost_per_operation": 0.005
  },
  "provider_status": {
    "deepseek": {
      "status": "healthy",
      "is_healthy": true,
      "success_rate": 98.5
    }
  },
  "available_providers": ["deepseek", "local"],
  "healthy_providers": 2
}
```

#### Cost Estimation
```http
POST /api/ai/estimate-cost
```

**Request Body:**
```json
{
  "operation_type": "content_generation",
  "context": {
    "currentSlide": {"elements": []},
    "presentation": {"title": "Business Report"}
  },
  "provider": "deepseek",
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "estimates_by_provider": {
    "deepseek": {
      "estimated_prompt_tokens": 150,
      "estimated_completion_tokens": 1000,
      "estimated_total_tokens": 1150,
      "estimated_cost_usd": 0.00161,
      "model": "deepseek-chat",
      "currency": "USD"
    }
  },
  "recommended_provider": "deepseek",
  "total_estimated_cost": 0.00161
}
```

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
  console.log('Connected to WebSocket');
};

ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  handleMessage(message);
};
```

### Message Types

#### Operation Broadcast
```json
{
  "type": "operation",
  "data": {
    "operation": {
      "op": "ADD",
      "type": "text",
      "target": "slide-1",
      "data": {"content": "New text"}
    },
    "userId": "user-123",
    "timestamp": 1640995200000
  }
}
```

#### Cursor Position
```json
{
  "type": "cursor",
  "data": {
    "userId": "user-123",
    "position": {"x": 250, "y": 300},
    "slideId": "slide-1"
  }
}
```

#### User Presence
```json
{
  "type": "presence",
  "data": {
    "userId": "user-123",
    "status": "online",
    "lastSeen": 1640995200000
  }
}
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid operation data",
    "details": {
      "field": "operation.type",
      "reason": "Must be one of: text, image, shape, chart, table"
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req-12345"
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Request validation failed | 400 |
| `AUTHENTICATION_ERROR` | Invalid or missing authentication | 401 |
| `AUTHORIZATION_ERROR` | Insufficient permissions | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `AI_PROVIDER_ERROR` | AI service unavailable | 503 |
| `INTERNAL_ERROR` | Internal server error | 500 |

## Rate Limiting

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
X-RateLimit-Window: 3600
```

### Rate Limits by Endpoint

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/operations/process` | 100 req/min | 60s |
| `/api/ai/predict` | 20 req/min | 60s |
| `/api/presentations` | 50 req/min | 60s |
| `/health` | 1000 req/min | 60s |

## SDK Examples

### JavaScript/TypeScript SDK

```typescript
import { AIPPTClient } from '@ai-ppt/sdk';

const client = new AIPPTClient({
  baseURL: 'https://api.your-domain.com',
  apiKey: 'your-api-key'
});

// Process operation
const result = await client.operations.process({
  operation: {
    op: 'ADD',
    type: 'text',
    target: 'slide-1',
    data: { content: 'Hello World' }
  },
  presentationId: 'presentation-123',
  slideIndex: 0
});

// Get AI prediction
const prediction = await client.ai.predict({
  context: {
    currentSlide: { id: 'slide-1', elements: [] },
    presentation: { title: 'My Presentation' }
  }
});

// Create presentation
const presentation = await client.presentations.create({
  title: 'New Presentation',
  slides: [{ id: 'slide-1', elements: [] }]
});
```

### Python SDK

```python
from ai_ppt_sdk import AIPPTClient

client = AIPPTClient(
    base_url='https://api.your-domain.com',
    api_key='your-api-key'
)

# Process operation
result = await client.operations.process({
    'operation': {
        'op': 'ADD',
        'type': 'text',
        'target': 'slide-1',
        'data': {'content': 'Hello World'}
    },
    'presentationId': 'presentation-123',
    'slideIndex': 0
})

# Get AI prediction
prediction = await client.ai.predict({
    'context': {
        'currentSlide': {'id': 'slide-1', 'elements': []},
        'presentation': {'title': 'My Presentation'}
    }
})
```

## Integration Examples

### React Integration

```jsx
import React, { useState, useEffect } from 'react';
import { AIPPTClient } from '@ai-ppt/sdk';

const PresentationEditor = () => {
  const [client] = useState(() => new AIPPTClient({
    baseURL: process.env.REACT_APP_API_URL,
    apiKey: process.env.REACT_APP_API_KEY
  }));
  
  const [presentation, setPresentation] = useState(null);
  const [aiSuggestions, setAiSuggestions] = useState([]);

  useEffect(() => {
    loadPresentation();
    getAISuggestions();
  }, []);

  const loadPresentation = async () => {
    const data = await client.presentations.get('presentation-123');
    setPresentation(data);
  };

  const getAISuggestions = async () => {
    const suggestions = await client.ai.suggestions({
      context: {
        currentSlide: { id: 'slide-1', elements: [] },
        presentation: { title: 'My Presentation' }
      }
    });
    setAiSuggestions(suggestions);
  };

  const applyOperation = async (operation) => {
    await client.operations.process({
      operation,
      presentationId: presentation.id,
      slideIndex: 0
    });
    
    // Reload presentation
    await loadPresentation();
  };

  return (
    <div>
      <h1>{presentation?.title}</h1>
      
      <div className="ai-suggestions">
        <h3>AI Suggestions</h3>
        {aiSuggestions.map((suggestion, index) => (
          <button
            key={index}
            onClick={() => applyOperation(suggestion)}
          >
            {suggestion.op} {suggestion.type}
          </button>
        ))}
      </div>
    </div>
  );
};
```

### Vue.js Integration

```vue
<template>
  <div class="presentation-editor">
    <h1>{{ presentation?.title }}</h1>
    
    <div class="ai-panel">
      <h3>AI Suggestions</h3>
      <button
        v-for="(suggestion, index) in aiSuggestions"
        :key="index"
        @click="applyOperation(suggestion)"
        class="suggestion-btn"
      >
        {{ suggestion.op }} {{ suggestion.type }}
      </button>
    </div>
  </div>
</template>

<script>
import { AIPPTClient } from '@ai-ppt/sdk';

export default {
  name: 'PresentationEditor',
  data() {
    return {
      client: new AIPPTClient({
        baseURL: process.env.VUE_APP_API_URL,
        apiKey: process.env.VUE_APP_API_KEY
      }),
      presentation: null,
      aiSuggestions: []
    };
  },
  
  async mounted() {
    await this.loadPresentation();
    await this.getAISuggestions();
  },
  
  methods: {
    async loadPresentation() {
      this.presentation = await this.client.presentations.get('presentation-123');
    },
    
    async getAISuggestions() {
      this.aiSuggestions = await this.client.ai.suggestions({
        context: {
          currentSlide: { id: 'slide-1', elements: [] },
          presentation: { title: 'My Presentation' }
        }
      });
    },
    
    async applyOperation(operation) {
      await this.client.operations.process({
        operation,
        presentationId: this.presentation.id,
        slideIndex: 0
      });
      
      await this.loadPresentation();
    }
  }
};
</script>
```

## Best Practices

### 1. Error Handling
```javascript
try {
  const result = await client.ai.predict(context);
  // Handle success
} catch (error) {
  if (error.code === 'RATE_LIMIT_EXCEEDED') {
    // Wait and retry
    await new Promise(resolve => setTimeout(resolve, 60000));
    return client.ai.predict(context);
  } else if (error.code === 'AI_PROVIDER_ERROR') {
    // Fallback to local AI
    return client.ai.predict({ ...context, use_ai_provider: false });
  }
  // Handle other errors
}
```

### 2. Caching
```javascript
const cache = new Map();

const getCachedPrediction = async (context) => {
  const key = JSON.stringify(context);
  
  if (cache.has(key)) {
    return cache.get(key);
  }
  
  const prediction = await client.ai.predict(context);
  cache.set(key, prediction);
  
  // Cache for 5 minutes
  setTimeout(() => cache.delete(key), 5 * 60 * 1000);
  
  return prediction;
};
```

### 3. Real-time Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'operation':
      // Update presentation state
      updatePresentation(message.data);
      break;
    case 'cursor':
      // Update cursor positions
      updateCursors(message.data);
      break;
    case 'presence':
      // Update user presence
      updatePresence(message.data);
      break;
  }
};
```

This comprehensive API documentation provides all the necessary information for integrating with the AI-PPT System, including authentication, endpoints, error handling, and practical examples.