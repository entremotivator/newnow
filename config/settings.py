"""
Enhanced Matrix VAPI Client Configuration
Advanced settings and environment management
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class MatrixLevel(Enum):
    ARCHITECT = "Architect"
    ORACLE = "Oracle" 
    OPERATOR = "Operator"
    SENTINEL = "Sentinel"
    AGENT = "Agent"

class SecurityClearance(Enum):
    ALPHA = "Alpha"
    BETA = "Beta"
    GAMMA = "Gamma"
    DELTA = "Delta"
    OMEGA = "Omega"

@dataclass
class VoiceConfig:
    model: str
    voice_id: str
    speed: float = 1.0
    pitch: float = 1.0
    stability: float = 0.75
    similarity_boost: float = 0.75

@dataclass
class AgentConfig:
    id: str
    name: str
    category: str
    description: str
    system_prompt: str
    first_message: str
    capabilities: List[str]
    voice_config: VoiceConfig
    cost_per_minute: float
    language: str
    matrix_level: MatrixLevel
    security_clearance: SecurityClearance
    status: str = "active"
    created_at: str = ""
    last_updated: str = ""
    usage_count: int = 0
    avg_call_duration: float = 0.0
    success_rate: float = 100.0
    personality_traits: List[str] = None
    specializations: List[str] = None
    max_call_duration: int = 3600  # seconds
    min_call_duration: int = 30    # seconds

# Enhanced Matrix Configuration
MATRIX_CONFIG = {
    "app_name": "AI CALL MATRIX",
    "version": "2.0.0",
    "subtitle": "Neural Network Command Center",
    "description": "Advanced AI Agent Communication System",
    "theme": {
        "primary_color": "#00ff41",
        "secondary_color": "#ff0040", 
        "accent_color": "#4080ff",
        "warning_color": "#ffff00",
        "background_gradient": "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%)"
    },
    "features": {
        "real_time_monitoring": True,
        "advanced_analytics": True,
        "call_recording": True,
        "transcript_analysis": True,
        "cost_tracking": True,
        "performance_metrics": True,
        "automated_reporting": True,
        "webhook_integration": True,
        "api_rate_limiting": True,
        "data_encryption": True
    }
}

# API Configuration
API_CONFIG = {
    "vapi_base_url": "https://api.vapi.ai",
    "timeout": 30,
    "max_retries": 3,
    "rate_limit": {
        "calls_per_minute": 60,
        "calls_per_hour": 1000
    },
    "webhook_endpoints": {
        "call_started": "/webhook/call-started",
        "call_ended": "/webhook/call-ended", 
        "transcript_ready": "/webhook/transcript-ready"
    }
}

# Database Configuration
DATABASE_CONFIG = {
    "url": "sqlite:///matrix_vapi.db",
    "echo": False,
    "pool_size": 10,
    "max_overflow": 20
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/matrix_vapi.log",
    "max_bytes": 10485760,  # 10MB
    "backup_count": 5
}
