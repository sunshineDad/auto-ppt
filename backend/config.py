"""
Configuration management for AI-PPT System
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from ai_providers.base import ProviderConfig

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 12001))
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./ai_ppt_system.db")
    
    # AI Configuration
    AI_MIN_TRAINING_SAMPLES = int(os.getenv("AI_MIN_TRAINING_SAMPLES", 10))
    AI_LEARNING_RATE = float(os.getenv("AI_LEARNING_RATE", 0.001))
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # Frontend URL
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:12000")
    
    @staticmethod
    def get_deepseek_config() -> ProviderConfig:
        """Get DeepSeek provider configuration"""
        return ProviderConfig(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            max_retries=3,
            timeout=30.0,
            custom_headers={
                "User-Agent": "AI-PPT-System/1.0.0"
            }
        )
    
    @staticmethod
    def get_ai_providers_config() -> Dict[str, Any]:
        """Get AI providers configuration"""
        return {
            "deepseek": {
                "enabled": bool(os.getenv("DEEPSEEK_API_KEY")),
                "config": Config.get_deepseek_config(),
                "priority": 1,
                "weight": 1.0
            }
        }
    
    @staticmethod
    def validate_config() -> bool:
        """Validate configuration"""
        required_vars = ["DEEPSEEK_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {missing_vars}")
            return False
        
        print("✅ Configuration validation passed")
        return True

# Global config instance
config = Config()