#!/usr/bin/env python3
"""
Demo script for AI-PPT System
Shows the 7 atomic operations and AI learning in action
"""

import asyncio
import json
import time
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"

class PPTDemo:
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.presentation_id = None
        self.session_id = f"demo_session_{int(time.time())}"
        
    async def demo_atomic_operations(self):
        """Demonstrate all 7 atomic operations"""
        print("🎯 AI-PPT System Demo - 7 Atomic Operations")
        print("=" * 50)
        
        # 1. CREATE slide
        print("\n1. CREATE - Creating a new slide")
        create_op = {
            "operation": {
                "op": "CREATE",
                "type": "slide",
                "target": 0,
                "data": {"layout": "blank"},
                "timestamp": int(time.time() * 1000),
                "sessionId": self.session_id
            },
            "context": {"currentSlide": {"index": 0, "elements": []}}
        }
        await self.send_operation(create_op)
        
        # 2. ADD text element
        print("\n2. ADD - Adding a text element")
        add_text_op = {
            "operation": {
                "op": "ADD",
                "type": "text",
                "target": 0,
                "data": {
                    "content": "Welcome to AI-PPT System",
                    "x": 100,
                    "y": 100,
                    "width": 600,
                    "height": 80,
                    "fontSize": 32,
                    "color": "#1976D2"
                },
                "timestamp": int(time.time() * 1000),
                "sessionId": self.session_id
            },
            "context": {"currentSlide": {"index": 0, "elements": []}}
        }
        await self.send_operation(add_text_op)
        
        # 3. ADD image element
        print("\n3. ADD - Adding an image element")
        add_image_op = {
            "operation": {
                "op": "ADD",
                "type": "image",
                "target": 0,
                "data": {
                    "src": "https://via.placeholder.com/300x200/1976D2/FFFFFF?text=AI+PPT",
                    "x": 400,
                    "y": 200,
                    "width": 300,
                    "height": 200
                },
                "timestamp": int(time.time() * 1000),
                "sessionId": self.session_id
            },
            "context": {"currentSlide": {"index": 0, "elements": [{"type": "text"}]}}
        }
        await self.send_operation(add_image_op)
        
        # 4. MODIFY text element
        print("\n4. MODIFY - Modifying text styling")
        modify_op = {
            "operation": {
                "op": "MODIFY",
                "type": "text",
                "target": "text_element_1",
                "data": {
                    "fontSize": 36,
                    "color": "#FF5722",
                    "bold": True
                },
                "timestamp": int(time.time() * 1000),
                "sessionId": self.session_id
            },
            "context": {"currentSlide": {"index": 0, "elements": [{"type": "text"}, {"type": "image"}]}}
        }
        await self.send_operation(modify_op)
        
        # 5. ADD shape element
        print("\n5. ADD - Adding a shape element")
        add_shape_op = {
            "operation": {
                "op": "ADD",
                "type": "shape",
                "target": 0,
                "data": {
                    "shape": "rectangle",
                    "x": 100,
                    "y": 300,
                    "width": 200,
                    "height": 100,
                    "fill": "#4CAF50",
                    "stroke": "#2E7D32"
                },
                "timestamp": int(time.time() * 1000),
                "sessionId": self.session_id
            },
            "context": {"currentSlide": {"index": 0, "elements": [{"type": "text"}, {"type": "image"}]}}
        }
        await self.send_operation(add_shape_op)
        
        # 6. APPLY theme
        print("\n6. APPLY - Applying a theme")
        apply_theme_op = {
            "operation": {
                "op": "APPLY",
                "type": "theme",
                "target": "all",
                "data": {
                    "name": "corporate-blue",
                    "colorScheme": {
                        "primary": "#1976D2",
                        "secondary": "#424242",
                        "background": "#FFFFFF",
                        "text": "#333333"
                    }
                },
                "timestamp": int(time.time() * 1000),
                "sessionId": self.session_id
            },
            "context": {"presentation": {"totalSlides": 1}}
        }
        await self.send_operation(apply_theme_op)
        
        # 7. REMOVE element
        print("\n7. REMOVE - Removing an element")
        remove_op = {
            "operation": {
                "op": "REMOVE",
                "type": "shape",
                "target": "shape_element_1",
                "data": {},
                "timestamp": int(time.time() * 1000),
                "sessionId": self.session_id
            },
            "context": {"currentSlide": {"index": 0, "elements": [{"type": "text"}, {"type": "image"}, {"type": "shape"}]}}
        }
        await self.send_operation(remove_op)
        
        print("\n✅ All 7 atomic operations demonstrated!")
        
    async def demo_ai_learning(self):
        """Demonstrate AI learning and predictions"""
        print("\n🤖 AI Learning & Prediction Demo")
        print("=" * 40)
        
        # Check AI status
        response = await self.client.get(f"{BASE_URL}/api/ai/metrics")
        if response.status_code == 200:
            metrics = response.json()
            print(f"📊 AI Metrics:")
            print(f"   Training samples: {metrics.get('training_samples', 0)}")
            print(f"   Model ready: {metrics.get('model_ready', False)}")
            print(f"   Accuracy: {metrics.get('accuracy', 0):.2%}")
        
        # Generate AI suggestions
        print("\n💡 Generating AI suggestions...")
        context = {
            "currentSlide": {
                "index": 0,
                "elements": [
                    {"type": "text", "content": "Welcome to AI-PPT System"}
                ]
            },
            "presentation": {"totalSlides": 1}
        }
        
        response = await self.client.post(f"{BASE_URL}/api/ai/suggestions", json=context)
        if response.status_code == 200:
            suggestions = response.json()
            print(f"🎯 Generated {len(suggestions)} suggestions:")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"   {i}. {suggestion.get('op')} {suggestion.get('type')}")
        
        # Try AI prediction
        print("\n🔮 Getting AI prediction...")
        response = await self.client.post(f"{BASE_URL}/api/ai/predict", json=context)
        if response.status_code == 200:
            prediction = response.json()
            print(f"🎯 AI Prediction:")
            print(f"   Operation: {prediction.get('atom', {}).get('op')} {prediction.get('atom', {}).get('type')}")
            print(f"   Confidence: {prediction.get('confidence', 0):.2%}")
            print(f"   Reasoning: {prediction.get('reasoning', 'N/A')}")
        elif response.status_code == 503:
            print("⚠️  AI model needs more training data (minimum 10 operations)")
        
    async def demo_presentation_generation(self):
        """Demonstrate AI presentation generation"""
        print("\n✨ AI Presentation Generation Demo")
        print("=" * 45)
        
        # Check if AI is ready for generation
        response = await self.client.get(f"{BASE_URL}/api/ai/metrics")
        if response.status_code == 200:
            metrics = response.json()
            if not metrics.get('model_ready', False):
                print("⚠️  AI model not ready for presentation generation")
                print("   Need more training data first")
                return
        
        # Generate a presentation
        prompt_data = {
            "prompt": "A quarterly business review presentation with sales data, market analysis, and future projections",
            "type": "business",
            "slides": 5
        }
        
        print(f"🎯 Generating presentation: {prompt_data['prompt']}")
        response = await self.client.post(f"{BASE_URL}/api/ai/generate-presentation", json=prompt_data)
        
        if response.status_code == 200:
            sequence = response.json()
            print(f"✅ Generated presentation with {len(sequence.get('atoms', []))} operations")
            print(f"   Sequence ID: {sequence.get('id')}")
            print(f"   Name: {sequence.get('name')}")
        elif response.status_code == 503:
            print("⚠️  AI not ready for presentation generation")
        else:
            print(f"❌ Generation failed: {response.status_code}")
    
    async def demo_analytics(self):
        """Demonstrate analytics and insights"""
        print("\n📊 Analytics & Insights Demo")
        print("=" * 35)
        
        # Get operation statistics
        response = await self.client.get(f"{BASE_URL}/api/operations/stats")
        if response.status_code == 200:
            stats = response.json()
            print("📈 Operation Statistics:")
            print(f"   Total operations: {stats.get('total_operations', 0)}")
            print(f"   Recent (24h): {stats.get('recent_operations_24h', 0)}")
            print(f"   Avg execution time: {stats.get('average_execution_time_ms', 0):.2f}ms")
            
            ops_by_type = stats.get('operations_by_type', {})
            if ops_by_type:
                print("   Operations by type:")
                for op_type, count in ops_by_type.items():
                    print(f"     {op_type}: {count}")
        
        # Get recent operations
        response = await self.client.get(f"{BASE_URL}/api/operations/recent?limit=5")
        if response.status_code == 200:
            operations = response.json()
            print(f"\n📝 Recent Operations ({len(operations)}):")
            for op in operations:
                timestamp = op.get('timestamp', '')
                if timestamp:
                    # Parse and format timestamp
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M:%S')
                    except:
                        time_str = timestamp[:8]
                else:
                    time_str = 'N/A'
                print(f"   {time_str} - {op.get('operation')} {op.get('element_type')}")
    
    async def send_operation(self, operation_data):
        """Send an operation to the backend"""
        try:
            response = await self.client.post(f"{BASE_URL}/api/operations", json=operation_data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Operation processed in {result.get('processing_time', 0):.2f}ms")
                return result
            else:
                print(f"   ❌ Operation failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    async def run_demo(self):
        """Run the complete demo"""
        print("🚀 Starting AI-PPT System Demo")
        print("This demo showcases the 7 atomic operations and AI capabilities")
        print("Backend URL:", BASE_URL)
        print()
        
        try:
            # Check backend health
            response = await self.client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                health = response.json()
                print(f"✅ Backend is {health['status']}")
                print(f"   Version: {health['version']}")
                print(f"   AI Ready: {health['ai_ready']}")
            else:
                print("❌ Backend not responding")
                return
            
            # Run demo sections
            await self.demo_atomic_operations()
            await asyncio.sleep(1)
            
            await self.demo_ai_learning()
            await asyncio.sleep(1)
            
            await self.demo_presentation_generation()
            await asyncio.sleep(1)
            
            await self.demo_analytics()
            
            print("\n🎉 Demo completed successfully!")
            print("\nNext steps:")
            print("1. Open http://localhost:12001 to see the frontend")
            print("2. Try creating presentations manually")
            print("3. Watch AI learn from your operations")
            print("4. Use AI suggestions to improve your presentations")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        finally:
            await self.client.aclose()

async def main():
    demo = PPTDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())