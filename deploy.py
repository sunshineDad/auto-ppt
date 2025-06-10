#!/usr/bin/env python3
"""
Simple deployment script for AI-PPT System
Serves the built frontend and provides deployment utilities
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
import http.server
import socketserver
import threading
import webbrowser

class AIPPTDeployment:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.dist_dir = self.base_dir / "dist"
        self.backend_dir = self.base_dir / "backend"
        self.frontend_port = 3000
        self.backend_port = 8000
        self.processes = []
        
    def check_requirements(self):
        """Check if all requirements are met"""
        print("🔍 Checking requirements...")
        
        # Check if dist directory exists
        if not self.dist_dir.exists():
            print("❌ Frontend not built. Run 'npm run build' first.")
            return False
            
        # Check if backend requirements are installed
        try:
            import fastapi
            import uvicorn
            print("✅ Backend dependencies found")
        except ImportError:
            print("❌ Backend dependencies missing. Run 'pip install -r backend/requirements.txt'")
            return False
            
        print("✅ All requirements met")
        return True
    
    def start_backend(self):
        """Start the FastAPI backend server"""
        print(f"🚀 Starting backend server on port {self.backend_port}...")
        
        cmd = [
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", str(self.backend_port),
            "--reload"
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=self.backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes.append(process)
        print(f"✅ Backend started (PID: {process.pid})")
        return process
    
    def start_frontend(self):
        """Start the frontend static file server"""
        print(f"🌐 Starting frontend server on port {self.frontend_port}...")
        
        class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(self.dist_dir), **kwargs)
            
            def end_headers(self):
                # Add CORS headers
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                super().end_headers()
            
            def log_message(self, format, *args):
                # Suppress default logging
                pass
        
        handler = CustomHTTPRequestHandler
        
        with socketserver.TCPServer(("0.0.0.0", self.frontend_port), handler) as httpd:
            print(f"✅ Frontend server started on http://0.0.0.0:{self.frontend_port}")
            
            def serve_forever():
                httpd.serve_forever()
            
            thread = threading.Thread(target=serve_forever, daemon=True)
            thread.start()
            
            return httpd
    
    def wait_for_backend(self, timeout=30):
        """Wait for backend to be ready"""
        import requests
        
        print("⏳ Waiting for backend to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Backend is ready")
                    return True
            except:
                pass
            time.sleep(1)
        
        print("❌ Backend failed to start within timeout")
        return False
    
    def deploy_development(self):
        """Deploy for development (local access)"""
        print("🎯 Starting AI-PPT System - Development Mode")
        print("=" * 50)
        
        if not self.check_requirements():
            return False
        
        try:
            # Start backend
            backend_process = self.start_backend()
            
            # Wait for backend to be ready
            if not self.wait_for_backend():
                return False
            
            # Start frontend
            frontend_server = self.start_frontend()
            
            print("\n🎉 AI-PPT System is running!")
            print(f"📱 Frontend: http://localhost:{self.frontend_port}")
            print(f"🔧 Backend API: http://localhost:{self.backend_port}")
            print(f"📚 API Docs: http://localhost:{self.backend_port}/docs")
            print("\n💡 Press Ctrl+C to stop all services")
            
            # Open browser
            webbrowser.open(f"http://localhost:{self.frontend_port}")
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down...")
                self.cleanup()
                
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            self.cleanup()
            return False
    
    def deploy_production(self):
        """Deploy for production (public access)"""
        print("🎯 Starting AI-PPT System - Production Mode")
        print("=" * 50)
        
        if not self.check_requirements():
            return False
        
        try:
            # Start backend
            backend_process = self.start_backend()
            
            # Wait for backend to be ready
            if not self.wait_for_backend():
                return False
            
            # Start frontend
            frontend_server = self.start_frontend()
            
            # Get public IP
            public_ip = self.get_public_ip()
            
            print("\n🎉 AI-PPT System is running in production mode!")
            print(f"🌐 Public Frontend: http://{public_ip}:{self.frontend_port}")
            print(f"🔧 Backend API: http://{public_ip}:{self.backend_port}")
            print(f"📚 API Docs: http://{public_ip}:{self.backend_port}/docs")
            print(f"🏠 Local Frontend: http://localhost:{self.frontend_port}")
            print("\n⚠️  Make sure ports {self.frontend_port} and {self.backend_port} are open in your firewall")
            print("💡 Press Ctrl+C to stop all services")
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down...")
                self.cleanup()
                
        except Exception as e:
            print(f"❌ Production deployment failed: {e}")
            self.cleanup()
            return False
    
    def get_public_ip(self):
        """Get public IP address"""
        try:
            import requests
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text.strip()
        except:
            try:
                import socket
                # Connect to a remote server to get local IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
            except:
                return "localhost"
    
    def cleanup(self):
        """Clean up processes"""
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
    
    def build_and_deploy(self, mode="development"):
        """Build frontend and deploy"""
        print("🔨 Building frontend...")
        
        # Build frontend
        result = subprocess.run(["npm", "run", "build"], cwd=self.base_dir)
        if result.returncode != 0:
            print("❌ Frontend build failed")
            return False
        
        print("✅ Frontend built successfully")
        
        # Deploy
        if mode == "production":
            return self.deploy_production()
        else:
            return self.deploy_development()

def main():
    deployment = AIPPTDeployment()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode in ["production", "prod"]:
            deployment.build_and_deploy("production")
        elif mode in ["development", "dev"]:
            deployment.build_and_deploy("development")
        elif mode == "build":
            subprocess.run(["npm", "run", "build"], cwd=deployment.base_dir)
        else:
            print("Usage: python deploy.py [development|production|build]")
    else:
        # Default to development
        deployment.build_and_deploy("development")

if __name__ == "__main__":
    main()