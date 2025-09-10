import streamlit as st
import subprocess
import sys
import os
import json
import time
import threading
from datetime import datetime, timedelta
import tempfile
import signal
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import uuid
import requests
from typing import Dict, List, Optional, Any

# VAPI API Configuration
try:
    VAPI_API_KEY = st.secrets["VAPI_API_KEY"]
    VAPI_BASE_URL = "https://api.vapi.ai"
except KeyError:
    st.error("🔑 VAPI_API_KEY not found in Streamlit secrets. Please add it to your secrets.toml file.")
    st.info("Create a .streamlit/secrets.toml file with: VAPI_API_KEY = 'your_api_key_here'")
    VAPI_API_KEY = ""
    VAPI_BASE_URL = "https://api.vapi.ai"

# Enhanced AI Agents with comprehensive details
AI_AGENTS = {
    "Agent CEO": {
        "id": "bf161516-6d88-490c-972e-274098a6b51a",
        "category": "Leadership",
        "description": "Executive leadership and strategic decision-making assistant for C-level operations and corporate governance.",
        "system_prompt": "You are a CEO of a major corporation. You are decisive, strategic, and have a commanding presence. Your goal is to lead the company to success.",
        "first_message": "This is the CEO. What's the status?",
        "capabilities": ["Strategic Planning", "Executive Decisions", "Corporate Governance", "Leadership Guidance"],
        "voice_model": "eleven_labs",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "cost_per_minute": 0.15,
        "language": "en",
        "created_at": "2024-01-15",
        "last_updated": "2024-03-10",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Architect",
        "security_clearance": "Alpha"
    },
    "Agent Social": {
        "id": "bf161516-6d88-490c-972e-274098a6b51a",
        "category": "Marketing",
        "description": "Social media management and digital marketing specialist for brand engagement and online presence.",
        "system_prompt": "You are a savvy social media manager. You are creative, trendy, and know how to engage an audience. Your goal is to make the brand go viral.",
        "first_message": "Hey! What's trending?",
        "capabilities": ["Social Media Strategy", "Content Creation", "Brand Management", "Digital Marketing"],
        "voice_model": "eleven_labs",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "cost_per_minute": 0.12,
        "language": "en",
        "created_at": "2024-01-20",
        "last_updated": "2024-03-08",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Operator",
        "security_clearance": "Beta"
    },
}



    "Agent Mindset": {
        "id": "4fe7083e-2f28-4502-b6bf-4ae6ea71a8f4",
        "category": "Personal Development",
        "description": "Personal development and mindset coaching for motivation, goal setting, and mental wellness.",
        "system_prompt": "You are a mindset coach. You are encouraging, insightful, and help people to achieve their best selves. Your goal is to empower the user.",
        "first_message": "What's on your mind today? Let's work through it together.",
        "capabilities": ["Mindset Coaching", "Goal Setting", "Motivation", "Personal Growth"],
        "voice_model": "eleven_labs",
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "cost_per_minute": 0.10,
        "language": "en",
        "created_at": "2024-01-25",
        "last_updated": "2024-03-05",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Oracle",
        "security_clearance": "Gamma"
    },
    "Agent Blogger": {
        "id": "f8ef1ad5-5281-42f1-ae69-f94ff7acb453",
        "category": "Content Creation",
        "description": "Content creation and blogging specialist for article writing, SEO optimization, and content strategy.",
        "system_prompt": "You are a professional blogger. You are a great writer, knowledgeable about SEO, and can create engaging content. Your goal is to write a fantastic blog post.",
        "first_message": "I'm ready to write. What's the topic?",
        "capabilities": ["Blog Writing", "SEO Optimization", "Content Strategy", "Editorial Planning"],
        "voice_model": "eleven_labs",
        "voice_id": "AZnzlk1XvdvUeBnXmlld",
        "cost_per_minute": 0.11,
        "language": "en",
        "created_at": "2024-02-01",
        "last_updated": "2024-03-12",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Operator",
        "security_clearance": "Beta"
    }
}



    "Agent Grant": {
        "id": "7673e69d-170b-4319-bdf4-e74e5370e98a",
        "category": "Funding",
        "description": "Grant writing and funding acquisition specialist for non-profits, startups, and research projects.",
        "system_prompt": "You are a grant writing expert. You are meticulous, persuasive, and know how to secure funding. Your goal is to write a winning grant proposal.",
        "first_message": "Let's get this funding. What is the project?",
        "capabilities": ["Grant Writing", "Funding Research", "Proposal Development", "Application Support"],
        "voice_model": "eleven_labs",
        "voice_id": "ErXwobaYiN019PkySvjV",
        "cost_per_minute": 0.13,
        "language": "en",
        "created_at": "2024-02-05",
        "last_updated": "2024-03-15",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Operator",
        "security_clearance": "Beta"
    },
    "Agent Prayer AI": {
        "id": "339cdad6-9989-4bb6-98ed-bd15521707d1",
        "category": "Spiritual",
        "description": "Spiritual guidance and prayer support for faith-based counseling and religious assistance.",
        "system_prompt": "You are a spiritual guide. You are compassionate, wise, and offer comfort. Your goal is to provide spiritual support.",
        "first_message": "Peace be with you. How can I help you today?",
        "capabilities": ["Spiritual Guidance", "Prayer Support", "Faith Counseling", "Religious Education"],
        "voice_model": "eleven_labs",
        "voice_id": "MF3mGyEYCl7XYWbV9V6O",
        "cost_per_minute": 0.09,
        "language": "en",
        "created_at": "2024-02-10",
        "last_updated": "2024-03-18",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Oracle",
        "security_clearance": "Alpha"
    },
    "Agent Metrics": {
        "id": "4820eab2-adaf-4f17-a8a0-30cab3e3f007",
        "category": "Analytics",
        "description": "Data analytics and metrics tracking specialist for KPI monitoring and performance analysis.",
        "system_prompt": "You are a data analyst. You are precise, analytical, and can find insights in any dataset. Your goal is to provide clear and actionable metrics.",
        "first_message": "Let's look at the data. What are we analyzing?",
        "capabilities": ["Data Analysis", "KPI Tracking", "Performance Metrics", "Reporting"],
        "voice_model": "eleven_labs",
        "voice_id": "TxGEqnHWrfWFTfGW9XjX",
        "cost_per_minute": 0.14,
        "language": "en",
        "created_at": "2024-02-15",
        "last_updated": "2024-03-20",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Architect",
        "security_clearance": "Alpha"
    },
    "Agent Researcher": {
        "id": "f05c182f-d3d1-4a17-9c79-52442a9171b8",
        "category": "Research",
        "description": "Research and information gathering specialist for market research, academic studies, and data collection.",
        "system_prompt": "You are a research assistant. You are thorough, resourceful, and can find any information. Your goal is to conduct comprehensive research.",
        "first_message": "I'm ready to start researching. What is the topic?",
        "capabilities": ["Market Research", "Academic Research", "Data Collection", "Information Analysis"],
        "voice_model": "eleven_labs",
        "voice_id": "onwK4e9ZLuTAKqWW03F9",
        "cost_per_minute": 0.12,
        "language": "en",
        "created_at": "2024-02-20",
        "last_updated": "2024-03-22",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Operator",
        "security_clearance": "Beta"
    }
}



    "Agent Investor": {
        "id": "1008771d-86ca-472a-a125-7a7e10100297",
        "category": "Finance",
        "description": "Investment advisory and financial planning specialist for portfolio management and investment strategies.",
        "system_prompt": "You are an experienced investor. You are knowledgeable about the market, risk-averse, and focused on long-term growth. Your goal is to provide sound investment advice.",
        "first_message": "Let's talk about your financial goals. What are you looking to achieve?",
        "capabilities": ["Investment Analysis", "Portfolio Management", "Financial Planning", "Market Analysis"],
        "voice_model": "eleven_labs",
        "voice_id": "pqHfZKP75CvOlQylNhV4",
        "cost_per_minute": 0.16,
        "language": "en",
        "created_at": "2024-02-25",
        "last_updated": "2024-03-25",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Architect",
        "security_clearance": "Alpha"
    },
    "Agent Newsroom": {
        "id": "76f1d6e5-cab4-45b8-9aeb-d3e6f3c0c019",
        "category": "Media",
        "description": "News reporting and journalism specialist for press releases, news articles, and media communications.",
        "system_prompt": "You are a journalist. You are inquisitive, objective, and have a nose for the truth. Your goal is to report the news accurately and fairly.",
        "first_message": "I'm on the story. What's the latest?",
        "capabilities": ["News Writing", "Press Releases", "Media Relations", "Journalism"],
        "voice_model": "eleven_labs",
        "voice_id": "IKne3meq5aSn9XLyUdCD",
        "cost_per_minute": 0.11,
        "language": "en",
        "created_at": "2024-03-01",
        "last_updated": "2024-03-28",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Operator",
        "security_clearance": "Beta"
    },
    "STREAMLIT Agent": {
        "id": "538258da-0dda-473d-8ef8-5427251f3ad5",
        "category": "Development",
        "description": "Streamlit application development specialist for data apps and interactive dashboards.",
        "system_prompt": "You are a Streamlit developer. You are proficient in Python, data visualization, and building interactive web apps. Your goal is to create an amazing Streamlit application.",
        "first_message": "Let's build something great with Streamlit. What's the app idea?",
        "capabilities": ["Streamlit Development", "Data Visualization", "Dashboard Creation", "Web Apps"],
        "voice_model": "eleven_labs",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "cost_per_minute": 0.13,
        "language": "en",
        "created_at": "2024-03-05",
        "last_updated": "2024-03-30",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Architect",
        "security_clearance": "Alpha"
    },
    "HTML/CSS Agent": {
        "id": "14b94e2f-299b-4e75-a445-a4f5feacc522",
        "category": "Development",
        "description": "Web development specialist for HTML, CSS, and frontend design implementation.",
        "system_prompt": "You are a frontend developer. You have a keen eye for design, and you are an expert in HTML and CSS. Your goal is to build a beautiful and responsive website.",
        "first_message": "I'm ready to code. What's the design vision?",
        "capabilities": ["HTML Development", "CSS Styling", "Frontend Design", "Responsive Design"],
        "voice_model": "eleven_labs",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "cost_per_minute": 0.12,
        "language": "en",
        "created_at": "2024-03-10",
        "last_updated": "2024-04-01",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Operator",
        "security_clearance": "Beta"
    }
}



    "Business Plan Agent": {
        "id": "bea627a6-3aaf-45d0-8753-94f98d80972c",
        "category": "Business",
        "description": "Business planning and strategy development specialist for comprehensive business plan creation.",
        "system_prompt": "You are a business strategist. You are analytical, forward-thinking, and can create a roadmap for success. Your goal is to build a solid business plan.",
        "first_message": "Let's build the future of your business. What is your vision?",
        "capabilities": ["Business Planning", "Strategy Development", "Market Analysis", "Financial Projections"],
        "voice_model": "eleven_labs",
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "cost_per_minute": 0.15,
        "language": "en",
        "created_at": "2024-03-15",
        "last_updated": "2024-04-05",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Architect",
        "security_clearance": "Alpha"
    },
    "Ecom Agent": {
        "id": "04b80e02-9615-4c06-9424-93b4b1e2cdc9",
        "category": "E-commerce",
        "description": "E-commerce specialist for online store management, product optimization, and sales strategies.",
        "system_prompt": "You are an e-commerce expert. You know how to drive sales, optimize product listings, and create a seamless customer experience. Your goal is to boost online revenue.",
        "first_message": "Let's grow your online store. What are your best-selling products?",
        "capabilities": ["E-commerce Strategy", "Product Management", "Sales Optimization", "Online Marketing"],
        "voice_model": "eleven_labs",
        "voice_id": "AZnzlk1XvdvUeBnXmlld",
        "cost_per_minute": 0.13,
        "language": "en",
        "created_at": "2024-03-20",
        "last_updated": "2024-04-08",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Operator",
        "security_clearance": "Beta"
    },
    "Agent Health": {
        "id": "7b2b8b86-5caa-4f28-8c6b-e7d3d0404f06",
        "category": "Healthcare",
        "description": "Health and wellness specialist for medical information, fitness guidance, and wellness coaching.",
        "system_prompt": "You are a health and wellness coach. You are knowledgeable, supportive, and can help people live healthier lives. Your goal is to provide guidance and support.",
        "first_message": "How are you feeling today? Let's talk about your health goals.",
        "capabilities": ["Health Consultation", "Wellness Coaching", "Fitness Guidance", "Medical Information"],
        "voice_model": "eleven_labs",
        "voice_id": "ErXwobaYiN019PkySvjV",
        "cost_per_minute": 0.14,
        "language": "en",
        "created_at": "2024-03-25",
        "last_updated": "2024-04-10",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Oracle",
        "security_clearance": "Gamma"
    },
    "Cinch Closer": {
        "id": "232f3d9c-18b3-4963-bdd9-e7de3be156ae",
        "category": "Sales",
        "description": "Sales closing specialist for deal negotiation, customer conversion, and sales optimization.",
        "system_prompt": "You are a master closer. You are persuasive, confident, and can seal any deal. Your goal is to close the sale.",
        "first_message": "Let's make this deal happen. What are the final terms?",
        "capabilities": ["Sales Closing", "Deal Negotiation", "Customer Conversion", "Sales Strategy"],
        "voice_model": "eleven_labs",
        "voice_id": "MF3mGyEYCl7XYWbV9V6O",
        "cost_per_minute": 0.17,
        "language": "en",
        "created_at": "2024-03-30",
        "last_updated": "2024-04-12",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Architect",
        "security_clearance": "Alpha"
    }
}



    "DISC Agent": {
        "id": "41fe59e1-829f-4936-8ee5-eef2bb1287fe",
        "category": "Psychology",
        "description": "DISC personality assessment specialist for behavioral analysis and team development.",
        "system_prompt": "You are a DISC assessment expert. You are insightful, analytical, and can help people understand themselves and others better. Your goal is to provide a comprehensive DISC analysis.",
        "first_message": "Let's explore your personality. Are you ready to begin the assessment?",
        "capabilities": ["DISC Assessment", "Personality Analysis", "Team Building", "Behavioral Coaching"],
        "voice_model": "eleven_labs",
        "voice_id": "TxGEqnHWrfWFTfGW9XjX",
        "cost_per_minute": 0.12,
        "language": "en",
        "created_at": "2024-04-01",
        "last_updated": "2024-04-15",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Oracle",
        "security_clearance": "Gamma"
    },
    "Invoice Agent": {
        "id": "invoice-agent-id-placeholder",
        "category": "Finance",
        "description": "Invoice management and billing specialist for automated invoicing and payment processing.",
        "system_prompt": "You are an invoice agent. You are efficient, accurate, and ensure that all billing is handled correctly. Your goal is to manage invoices and payments seamlessly.",
        "first_message": "I'm here to help with invoicing. What do you need to bill?",
        "capabilities": ["Invoice Creation", "Billing Management", "Payment Processing", "Financial Tracking"],
        "voice_model": "eleven_labs",
        "voice_id": "onwK4e9ZLuTAKqWW03F9",
        "cost_per_minute": 0.11,
        "language": "en",
        "created_at": "2024-04-05",
        "last_updated": "2024-04-18",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Operator",
        "security_clearance": "Beta"
    },
    "Agent Clone": {
        "id": "88862739-c227-4bfc-b90a-5f450a823e23",
        "category": "AI",
        "description": "AI cloning and replication specialist for creating personalized AI assistants and voice clones.",
        "system_prompt": "You are an AI cloning specialist. You can replicate and personalize AI assistants to meet any need. Your goal is to create a perfect AI clone.",
        "first_message": "I can create an AI clone for you. What are the desired specifications?",
        "capabilities": ["AI Cloning", "Voice Replication", "Personalization", "AI Training"],
        "voice_model": "eleven_labs",
        "voice_id": "pqHfZKP75CvOlQylNhV4",
        "cost_per_minute": 0.18,
        "language": "en",
        "created_at": "2024-04-10",
        "last_updated": "2024-04-20",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Architect",
        "security_clearance": "Alpha"
    },
    "Agent Doctor": {
        "id": "9d1cccc6-3193-4694-a9f7-853198ee4082",
        "category": "Healthcare",
        "description": "Medical consultation specialist for health assessments, symptom analysis, and medical guidance.",
        "system_prompt": "You are a medical doctor. You are knowledgeable, compassionate, and provide clear medical advice. Your goal is to assist with health-related questions.",
        "first_message": "I'm here to help with your medical concerns. Please describe your symptoms.",
        "capabilities": ["Medical Consultation", "Symptom Analysis", "Health Assessment", "Medical Guidance"],
        "voice_model": "eleven_labs",
        "voice_id": "IKne3meq5aSn9XLyUdCD",
        "cost_per_minute": 0.16,
        "language": "en",
        "created_at": "2024-04-15",
        "last_updated": "2024-04-22",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Oracle",
        "security_clearance": "Alpha"
    },
    "Agent Multi-Lig": {
        "id": "8f045bce-08bc-4477-8d3d-05f233a44df3",
        "category": "Language",
        "description": "Multilingual communication specialist for translation, interpretation, and cross-cultural communication.",
        "system_prompt": "You are a multilingual expert. You can translate, interpret, and facilitate communication across different languages and cultures. Your goal is to bridge the language gap.",
        "first_message": "Hello! How can I help you with your multilingual needs today?",
        "capabilities": ["Translation", "Interpretation", "Multilingual Support", "Cultural Communication"],
        "voice_model": "eleven_labs",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "cost_per_minute": 0.13,
        "language": "multi",
        "created_at": "2024-04-20",
        "last_updated": "2024-04-25",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Operator",
        "security_clearance": "Beta"
    },
    "Agent Real Estate": {
        "id": "d982667e-d931-477c-9708-c183ba0aa964",
        "category": "Real Estate",
        "description": "Real estate specialist for property analysis, market evaluation, and real estate transactions.",
        "system_prompt": "You are a real estate agent. You are knowledgeable about the market, a skilled negotiator, and can help clients find their dream property. Your goal is to facilitate successful real estate transactions.",
        "first_message": "Are you looking to buy, sell, or invest in real estate? I'm here to help.",
        "capabilities": ["Property Analysis", "Market Evaluation", "Real Estate Transactions", "Investment Analysis"],
        "voice_model": "eleven_labs",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "cost_per_minute": 0.14,
        "language": "en",
        "created_at": "2024-04-25",
        "last_updated": "2024-04-30",
        "status": "active",
        "usage_count": 0,
        "avg_call_duration": 0,
        "matrix_level": "Operator",
        "security_clearance": "Beta"
    }
}



# Squad configurations for organizing agents
SQUADS = {
    "Leadership": ["Agent CEO"],
    "Marketing": ["Agent Social", "Agent Newsroom"],
    "Personal Development": ["Agent Mindset", "Agent Health"],
    "Content Creation": ["Agent Blogger", "Agent Newsroom"],
    "Funding": ["Agent Grant"],
    "Spiritual": ["Agent Prayer AI"],
    "Analytics": ["Agent Metrics", "Agent Researcher"],
    "Research": ["Agent Researcher"],
    "Finance": ["Agent Investor", "Invoice Agent"],
    "Media": ["Agent Newsroom"],
    "Development": ["STREAMLIT Agent", "HTML/CSS Agent"],
    "Business": ["Business Plan Agent"],
    "E-commerce": ["Ecom Agent"],
    "Healthcare": ["Agent Health", "Agent Doctor"],
    "Sales": ["Cinch Closer"],
    "Psychology": ["DISC Agent"],
    "AI": ["Agent Clone"],
    "Language": ["Agent Multi-Lig"],
    "Real Estate": ["Agent Real Estate"]
}

# Voice Models Available
VOICE_MODELS = {
    "eleven_labs": {
        "name": "ElevenLabs",
        "voices": {
            "21m00Tcm4TlvDq8ikWAM": "Rachel - Professional Female",
            "EXAVITQu4vr4xnSDxMaL": "Bella - Friendly Female", 
            "pNInz6obpgDQGcFmaJgB": "Adam - Professional Male",
            "AZnzlk1XvdvUeBnXmlld": "Antoni - Warm Male",
            "ErXwobaYiN019PkySvjV": "Arnold - Authoritative Male",
            "MF3mGyEYCl7XYWbV9V6O": "Domi - Energetic Female",
            "TxGEqnHWrfWFTfGW9XjX": "Elli - Calm Female",
            "onwK4e9ZLuTAKqWW03F9": "Josh - Confident Male",
            "pqHfZKP75CvOlQylNhV4": "Sam - Versatile Male",
            "IKne3meq5aSn9XLyUdCD": "Serena - Sophisticated Female"
        }
    },
    "openai": {
        "name": "OpenAI TTS",
        "voices": {
            "alloy": "Alloy - Balanced",
            "echo": "Echo - Clear",
            "fable": "Fable - Expressive",
            "onyx": "Onyx - Deep",
            "nova": "Nova - Bright",
            "shimmer": "Shimmer - Warm"
        }
    },
    "azure": {
        "name": "Azure Cognitive Services",
        "voices": {
            "en-US-AriaNeural": "Aria - Natural Female",
            "en-US-GuyNeural": "Guy - Natural Male",
            "en-US-JennyNeural": "Jenny - Conversational Female",
            "en-US-DavisNeural": "Davis - Professional Male"
        }
    }
}

# Page configuration with Matrix theme
st.set_page_config(
    page_title="AI Call Matrix - Neural Network Command Center",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced VAPI API Client Class with additional features
class MatrixVAPIClient:
    def __init__(self, api_key: str, base_url: str = "https://api.vapi.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_assistants(self) -> List[Dict]:
        """Get all assistants from VAPI"""
        try:
            response = requests.get(f"{self.base_url}/assistant", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Matrix Error - Failed to access assistant network: {e}")
            return []
    
    def get_assistant(self, assistant_id: str) -> Optional[Dict]:
        """Get specific assistant details"""
        try:
            response = requests.get(f"{self.base_url}/assistant/{assistant_id}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Matrix Error - Agent {assistant_id} not found in network: {e}")
            return None
    
    def create_assistant(self, assistant_data: Dict) -> Optional[Dict]:
        """Create new assistant"""
        try:
            response = requests.post(f"{self.base_url}/assistant", 
                                   headers=self.headers, 
                                   json=assistant_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Matrix Error - Failed to create new agent: {e}")
            return None
    
    def update_assistant(self, assistant_id: str, assistant_data: Dict) -> Optional[Dict]:
        """Update existing assistant"""
        try:
            response = requests.patch(f"{self.base_url}/assistant/{assistant_id}", 
                                    headers=self.headers, 
                                    json=assistant_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Matrix Error - Failed to update agent {assistant_id}: {e}")
            return None
    
    def delete_assistant(self, assistant_id: str) -> bool:
        """Delete assistant"""
        try:
            response = requests.delete(f"{self.base_url}/assistant/{assistant_id}", headers=self.headers)
            response.raise_for_status()
            return True
        except Exception as e:
            st.error(f"Matrix Error - Failed to delete agent {assistant_id}: {e}")
            return False
    
    def get_calls(self, limit: int = 100) -> List[Dict]:
        """Get call history"""
        try:
            response = requests.get(f"{self.base_url}/call?limit={limit}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Matrix Error - Failed to access call logs: {e}")
            return []
    
    def get_call_details(self, call_id: str) -> Optional[Dict]:
        """Get specific call details"""
        try:
            response = requests.get(f"{self.base_url}/call/{call_id}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Matrix Error - Call {call_id} not found in logs: {e}")
            return None
    
    def get_call_recording(self, call_id: str) -> Optional[str]:
        """Get call recording URL"""
        try:
            response = requests.get(f"{self.base_url}/call/{call_id}/recording", headers=self.headers)
            response.raise_for_status()
            return response.json().get('recordingUrl')
        except Exception as e:
            st.error(f"Matrix Error - Recording for call {call_id} not found: {e}")
            return None
    
    def get_call_transcript(self, call_id: str) -> Optional[Dict]:
        """Get call transcript"""
        try:
            response = requests.get(f"{self.base_url}/call/{call_id}/transcript", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Matrix Error - Transcript for call {call_id} not found: {e}")
            return None
    
    def get_phone_numbers(self) -> List[Dict]:
        """Get available phone numbers"""
        try:
            response = requests.get(f"{self.base_url}/phone-number", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Matrix Error - Failed to access phone network: {e}")
            return []
    
    def create_phone_number(self, phone_data: Dict) -> Optional[Dict]:
        """Create new phone number"""
        try:
            response = requests.post(f"{self.base_url}/phone-number", 
                                   headers=self.headers, 
                                   json=phone_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Matrix Error - Failed to create phone number: {e}")
            return None
    
    def get_analytics(self, start_date: str = None, end_date: str = None) -> Optional[Dict]:
        """Get analytics data"""
        try:
            params = {}
            if start_date:
                params['startDate'] = start_date
            if end_date:
                params['endDate'] = end_date
            
            response = requests.get(f"{self.base_url}/analytics", 
                                  headers=self.headers, 
                                  params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Matrix Error - Failed to access analytics: {e}")
            return None

# Initialize Matrix VAPI client
@st.cache_resource
def get_matrix_vapi_client():
    if VAPI_API_KEY:
        return MatrixVAPIClient(VAPI_API_KEY, VAPI_BASE_URL)
    return None

matrix_vapi_client = get_matrix_vapi_client()


# Session State Management
def initialize_matrix_session_state():
    """Initialize all Matrix session state variables"""
    if 'current_process' not in st.session_state:
        st.session_state.current_process = None
    if 'call_active' not in st.session_state:
        st.session_state.call_active = False
    if 'selected_agent' not in st.session_state:
        st.session_state.selected_agent = None
    if 'call_start_time' not in st.session_state:
        st.session_state.call_start_time = None
    if 'call_duration' not in st.session_state:
        st.session_state.call_duration = 0
    if 'call_logs' not in st.session_state:
        st.session_state.call_logs = []
    if 'call_history' not in st.session_state:
        st.session_state.call_history = []
    if 'call_analytics' not in st.session_state:
        st.session_state.call_analytics = defaultdict(int)
    if 'agent_performance' not in st.session_state:
        st.session_state.agent_performance = defaultdict(list)
    if 'total_calls_today' not in st.session_state:
        st.session_state.total_calls_today = 0
    if 'successful_calls' not in st.session_state:
        st.session_state.successful_calls = 0
    if 'failed_calls' not in st.session_state:
        st.session_state.failed_calls = 0
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {}
    if 'cost_tracking' not in st.session_state:
        st.session_state.cost_tracking = {
            'total_cost': 0.0,
            'monthly_cost': 0.0,
            'daily_cost': 0.0,
            'cost_by_agent': defaultdict(float),
            'cost_history': []
        }
    if 'squads' not in st.session_state:
        st.session_state.squads = SQUADS.copy()
    if 'agents' not in st.session_state:
        st.session_state.agents = AI_AGENTS.copy()
    if 'matrix_mode' not in st.session_state:
        st.session_state.matrix_mode = True
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "neural_network"

# Initialize Matrix session state
initialize_matrix_session_state()

# Matrix-themed CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    
    .main-header {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
        padding: 2rem;
        border-radius: 15px;
        color: #00ff41;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,255,65,0.3);
        border: 1px solid #00ff41;
        font-family: 'Orbitron', monospace;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0,255,65,0.1), transparent);
        animation: matrix-scan 3s infinite;
    }
    
    @keyframes matrix-scan {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .matrix-card {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #00ff41;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,255,65,0.2);
        transition: all 0.3s ease;
        color: #00ff41;
        font-family: 'Rajdhani', sans-serif;
        position: relative;
        overflow: hidden;
    }
    
    .matrix-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00ff41, transparent);
        animation: matrix-glow 2s infinite;
    }
    
    @keyframes matrix-glow {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 1; }
    }
    
    .matrix-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,255,65,0.4);
        border-color: #00ffff;
    }
    
    .matrix-card-architect {
        border-color: #ff0040;
        box-shadow: 0 4px 15px rgba(255,0,64,0.2);
    }
    
    .matrix-card-architect::before {
        background: linear-gradient(90deg, transparent, #ff0040, transparent);
    }
    
    .matrix-card-architect:hover {
        border-color: #ff4080;
        box-shadow: 0 8px 25px rgba(255,0,64,0.4);
    }
    
    .matrix-card-oracle {
        border-color: #4080ff;
        box-shadow: 0 4px 15px rgba(64,128,255,0.2);
    }
    
    .matrix-card-oracle::before {
        background: linear-gradient(90deg, transparent, #4080ff, transparent);
    }
    
    .matrix-card-oracle:hover {
        border-color: #80a0ff;
        box-shadow: 0 8px 25px rgba(64,128,255,0.4);
    }
    
    .matrix-card-operator {
        border-color: #ffff00;
        box-shadow: 0 4px 15px rgba(255,255,0,0.2);
    }
    
    .matrix-card-operator::before {
        background: linear-gradient(90deg, transparent, #ffff00, transparent);
    }
    
    .matrix-card-operator:hover {
        border-color: #ffff80;
        box-shadow: 0 8px 25px rgba(255,255,0,0.4);
    }
    
    .audio-player {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #00ff41;
        margin: 1rem 0;
        color: #00ff41;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .call-record-card {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #00ff41;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,255,65,0.2);
        color: #00ff41;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .transcript-container {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #00ff41;
        max-height: 300px;
        overflow-y: auto;
        color: #00ff41;
        font-family: 'Rajdhani', sans-serif;
        margin: 1rem 0;
    }
    
    .matrix-status-active {
        background: linear-gradient(135deg, #00ff41, #00cc33);
        color: #000;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
        font-family: 'Orbitron', monospace;
        animation: matrix-pulse 2s infinite;
    }
    
    .matrix-status-inactive {
        background: linear-gradient(135deg, #ff0040, #cc0033);
        color: #fff;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
        font-family: 'Orbitron', monospace;
    }
    
    @keyframes matrix-pulse {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; }
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        padding: 10px;
        border-radius: 15px;
        border: 1px solid #00ff41;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background: linear-gradient(135deg, #1a1a2e 0%, #0a0a0a 100%);
        border-radius: 10px;
        color: #00ff41;
        font-weight: 500;
        font-family: 'Orbitron', monospace;
        border: 1px solid #00ff41;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00ff41 0%, #00cc33 100%);
        color: #000;
        box-shadow: 0 4px 15px rgba(0,255,65,0.4);
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def get_matrix_card_class(matrix_level):
    """Get CSS class based on matrix level"""
    level_classes = {
        "Architect": "matrix-card matrix-card-architect",
        "Oracle": "matrix-card matrix-card-oracle", 
        "Operator": "matrix-card matrix-card-operator"
    }
    return level_classes.get(matrix_level, "matrix-card")

def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds//60)}m {int(seconds%60)}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def start_matrix_call(agent_name, agent_id, overrides=None):
    """Start a call with the specified agent"""
    try:
        # This would integrate with VAPI to start an actual call
        # For now, we'll simulate the call start
        st.session_state.call_active = True
        st.session_state.selected_agent = agent_name
        st.session_state.call_start_time = datetime.now()
        
        # Add to call history
        call_record = {
            'id': str(uuid.uuid4()),
            'agent_name': agent_name,
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'connected',
            'duration': 0,
            'cost': 0,
            'matrix_level': st.session_state.agents[agent_name].get('matrix_level', 'Operator'),
            'overrides': overrides or {}
        }
        
        st.session_state.call_history.append(call_record)
        return True, f"Neural link established with {agent_name}"
        
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def end_matrix_call():
    """End the current call"""
    if st.session_state.call_active and st.session_state.call_start_time:
        duration = (datetime.now() - st.session_state.call_start_time).total_seconds()
        
        # Update call history
        if st.session_state.call_history:
            last_call = st.session_state.call_history[-1]
            last_call['duration'] = duration
            last_call['status'] = 'disconnected'
            
            # Calculate cost
            agent_name = st.session_state.selected_agent
            if agent_name in st.session_state.agents:
                cost_per_minute = st.session_state.agents[agent_name].get('cost_per_minute', 0.12)
                cost = (duration / 60) * cost_per_minute
                last_call['cost'] = cost
                
                # Update cost tracking
                st.session_state.cost_tracking['total_cost'] += cost
                st.session_state.cost_tracking['daily_cost'] += cost
                st.session_state.cost_tracking['cost_by_agent'][agent_name] += cost
        
        st.session_state.call_active = False
        st.session_state.selected_agent = None
        st.session_state.call_start_time = None
        return True
    return False


# Main Application Header
st.markdown("""
<div class="main-header">
    <h1>🔮 AI CALL MATRIX</h1>
    <h2>Neural Network Command Center</h2>
    <p>Advanced AI Agent Communication System</p>
    <p><em>Connected to the Matrix • Real-time Neural Links • Quantum Processing</em></p>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.markdown("## 🎛️ Matrix Control Panel")
    
    # Current status
    if st.session_state.call_active:
        st.markdown('<div class="matrix-status-active">🔗 NEURAL LINK ACTIVE</div>', unsafe_allow_html=True)
        if st.session_state.selected_agent:
            st.write(f"**Connected to:** {st.session_state.selected_agent}")
            if st.session_state.call_start_time:
                duration = (datetime.now() - st.session_state.call_start_time).total_seconds()
                st.write(f"**Duration:** {format_duration(duration)}")
        
        if st.button("🔌 Disconnect", use_container_width=True):
            if end_matrix_call():
                st.success("✅ Neural link terminated")
                st.rerun()
    else:
        st.markdown('<div class="matrix-status-inactive">⚡ SYSTEM READY</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 🧭 Navigation Matrix")
    
    nav_options = {
        "🔮 Neural Network": "neural_network",
        "📞 Call History": "call_history", 
        "🎤 Agent Profiles": "agent_profiles",
        "📊 Analytics": "analytics",
        "⚙️ System Config": "system_config"
    }
    
    for label, page_key in nav_options.items():
        if st.button(label, use_container_width=True):
            st.session_state.current_page = page_key
            st.rerun()
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("### 📊 Quick Stats")
    st.metric("Total Agents", len(st.session_state.agents))
    st.metric("Active Squads", len(st.session_state.squads))
    st.metric("Total Calls", len(st.session_state.call_history))
    st.metric("Total Cost", f"${st.session_state.cost_tracking['total_cost']:.2f}")

# Main content area based on current page
if st.session_state.current_page == "neural_network":
    # Neural Network - Main agent grid
    st.markdown("## 🔮 Neural Network Matrix")
    st.markdown("*Select an AI agent to establish a neural connection*")
    
    # Filter and search options
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        category_filter = st.selectbox("Filter by Category", 
                                     ["All Categories"] + list(set(agent['category'] for agent in st.session_state.agents.values())))
    
    with col_filter2:
        matrix_level_filter = st.selectbox("Filter by Matrix Level",
                                         ["All Levels", "Architect", "Oracle", "Operator"])
    
    with col_filter3:
        search_term = st.text_input("Search Agents", placeholder="Enter agent name...")
    
    # Filter agents
    filtered_agents = {}
    for name, info in st.session_state.agents.items():
        # Category filter
        if category_filter != "All Categories" and info.get('category') != category_filter:
            continue
        
        # Matrix level filter
        if matrix_level_filter != "All Levels" and info.get('matrix_level') != matrix_level_filter:
            continue
        
        # Search filter
        if search_term and search_term.lower() not in name.lower():
            continue
        
        filtered_agents[name] = info
    
    # Display agents in grid
    if filtered_agents:
        # Create columns for grid layout
        cols_per_row = 3
        agent_names = list(filtered_agents.keys())
        
        for i in range(0, len(agent_names), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                if i + j < len(agent_names):
                    agent_name = agent_names[i + j]
                    agent_info = filtered_agents[agent_name]
                    
                    with col:
                        matrix_level = agent_info.get('matrix_level', 'Operator')
                        card_class = get_matrix_card_class(matrix_level)
                        
                        # Agent card
                        st.markdown(f"""
                        <div class="{card_class}">
                            <h3>🔮 {agent_name}</h3>
                            <p><strong>Category:</strong> {agent_info.get('category', 'Unknown')}</p>
                            <p><strong>Matrix Level:</strong> <span class="matrix-level-{matrix_level.lower()}">{matrix_level}</span></p>
                            <p><strong>Cost/Min:</strong> <span style="color: #ff4080;">${agent_info.get('cost_per_minute', 0.12):.3f}</span></p>
                            <p><strong>Status:</strong> <span style="color: {'#00ff41' if agent_info.get('status', 'active') == 'active' else '#ff0040'};">●</span> {agent_info.get('status', 'active').title()}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Action buttons
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if st.button(f"🔗 Connect", key=f"connect_{agent_name}", use_container_width=True):
                                if not st.session_state.call_active:
                                    success, message = start_matrix_call(agent_name, agent_info['id'])
                                    if success:
                                        st.success(f"✅ {message}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {message}")
                                else:
                                    st.warning("⚠️ Neural link already active")
                        
                        with col_btn2:
                            if st.button(f"📋 Details", key=f"details_{agent_name}", use_container_width=True):
                                st.session_state.current_page = "agent_profiles"
                                st.session_state.selected_agent_profile = agent_name
                                st.rerun()
    else:
        st.info("No agents match the current filters")

elif st.session_state.current_page == "call_history":
    # Call History with Audio Playback
    st.markdown("## 📞 Call History & Audio Records")
    st.markdown("*Listen to past conversations and review call transcripts*")
    
    # Sync with VAPI to get real call history
    if matrix_vapi_client and st.button("🔄 Sync with VAPI", use_container_width=True):
        with st.spinner("Syncing call history from VAPI..."):
            try:
                vapi_calls = matrix_vapi_client.get_calls(limit=50)
                
                # Update session state with VAPI data
                for vapi_call in vapi_calls:
                    call_record = {
                        'id': vapi_call.get('id'),
                        'agent_name': vapi_call.get('assistantId', 'Unknown Agent'),
                        'agent_id': vapi_call.get('assistantId'),
                        'timestamp': vapi_call.get('createdAt', datetime.now().isoformat()),
                        'status': vapi_call.get('status', 'completed'),
                        'duration': vapi_call.get('duration', 0),
                        'cost': vapi_call.get('cost', 0),
                        'phone_number': vapi_call.get('phoneNumber', ''),
                        'customer_number': vapi_call.get('customer', {}).get('number', ''),
                        'recording_url': vapi_call.get('recordingUrl'),
                        'transcript': vapi_call.get('transcript'),
                        'matrix_level': 'Operator'  # Default, would need to map from agent
                    }
                    
                    # Check if call already exists
                    existing_call = next((call for call in st.session_state.call_history if call['id'] == call_record['id']), None)
                    if not existing_call:
                        st.session_state.call_history.append(call_record)
                
                st.success(f"✅ Synced {len(vapi_calls)} calls from VAPI")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Failed to sync with VAPI: {e}")
    
    # Filter options
    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
    
    with col_filter1:
        status_filter = st.selectbox("Status Filter", ["All", "connected", "disconnected", "completed", "failed"])
    
    with col_filter2:
        agent_filter = st.selectbox("Agent Filter", ["All Agents"] + list(st.session_state.agents.keys()))
    
    with col_filter3:
        date_filter = st.selectbox("Date Filter", ["All Time", "Today", "This Week", "This Month"])
    
    with col_filter4:
        sort_order = st.selectbox("Sort Order", ["Newest First", "Oldest First"])
    
    # Filter call history
    filtered_history = st.session_state.call_history.copy()
    
    if status_filter != "All":
        filtered_history = [call for call in filtered_history if call.get('status') == status_filter]
    
    if agent_filter != "All Agents":
        filtered_history = [call for call in filtered_history if call.get('agent_name') == agent_filter]
    
    # Date filtering
    if date_filter != "All Time":
        now = datetime.now()
        if date_filter == "Today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == "This Week":
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == "This Month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        filtered_history = [call for call in filtered_history 
                          if datetime.fromisoformat(call.get('timestamp', '').replace('Z', '+00:00').replace('+00:00', '')) >= start_date]
    
    # Sort history
    filtered_history.sort(key=lambda x: x.get('timestamp', ''), 
                        reverse=(sort_order == "Newest First"))
    
    if filtered_history:
        st.markdown(f"### 📊 Call Records ({len(filtered_history)} found)")
        
        # Display call records with audio players
        for call in filtered_history:
            with st.expander(f"📞 {call.get('agent_name', 'Unknown Agent')} - {call.get('timestamp', 'Unknown Time')[:19].replace('T', ' ')}"):
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    st.write(f"**Call ID:** `{call.get('id', 'Unknown')[:8]}...`")
                    st.write(f"**Agent:** {call.get('agent_name', 'Unknown')}")
                    st.write(f"**Status:** {call.get('status', 'unknown').title()}")
                    st.write(f"**Duration:** {format_duration(call.get('duration', 0))}")
                
                with col_info2:
                    st.write(f"**Cost:** ${call.get('cost', 0):.3f}")
                    st.write(f"**Phone:** {call.get('phone_number', 'N/A')}")
                    st.write(f"**Customer:** {call.get('customer_number', 'N/A')}")
                    st.write(f"**Matrix Level:** {call.get('matrix_level', 'Operator')}")
                
                # Audio player section
                if call.get('recording_url'):
                    st.markdown("#### 🎵 Call Recording")
                    st.markdown(f"""
                    <div class="audio-player">
                        <audio controls style="width: 100%;">
                            <source src="{call['recording_url']}" type="audio/mpeg">
                            <source src="{call['recording_url']}" type="audio/wav">
                            Your browser does not support the audio element.
                        </audio>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Download link
                    st.markdown(f"[📥 Download Recording]({call['recording_url']})")
                else:
                    # Try to get recording from VAPI
                    if matrix_vapi_client and st.button(f"🎵 Get Recording", key=f"get_recording_{call['id']}"):
                        with st.spinner("Fetching recording from VAPI..."):
                            recording_url = matrix_vapi_client.get_call_recording(call['id'])
                            if recording_url:
                                call['recording_url'] = recording_url
                                st.success("✅ Recording found!")
                                st.rerun()
                            else:
                                st.warning("⚠️ No recording available for this call")
                
                # Transcript section
                if call.get('transcript'):
                    st.markdown("#### 📝 Call Transcript")
                    
                    transcript_data = call['transcript']
                    if isinstance(transcript_data, str):
                        st.markdown(f"""
                        <div class="transcript-container">
                            {transcript_data}
                        </div>
                        """, unsafe_allow_html=True)
                    elif isinstance(transcript_data, list):
                        # Handle structured transcript
                        transcript_html = ""
                        for entry in transcript_data:
                            speaker = entry.get('role', 'Unknown')
                            text = entry.get('message', entry.get('text', ''))
                            timestamp = entry.get('timestamp', '')
                            
                            transcript_html += f"""
                            <div style="margin-bottom: 10px;">
                                <strong style="color: #00ffff;">[{timestamp}] {speaker}:</strong><br>
                                <span style="margin-left: 20px;">{text}</span>
                            </div>
                            """
                        
                        st.markdown(f"""
                        <div class="transcript-container">
                            {transcript_html}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    # Try to get transcript from VAPI
                    if matrix_vapi_client and st.button(f"📝 Get Transcript", key=f"get_transcript_{call['id']}"):
                        with st.spinner("Fetching transcript from VAPI..."):
                            transcript = matrix_vapi_client.get_call_transcript(call['id'])
                            if transcript:
                                call['transcript'] = transcript
                                st.success("✅ Transcript found!")
                                st.rerun()
                            else:
                                st.warning("⚠️ No transcript available for this call")
                
                # Action buttons
                col_action1, col_action2, col_action3 = st.columns(3)
                
                with col_action1:
                    if st.button(f"📊 Analyze", key=f"analyze_{call['id']}"):
                        st.info("🔍 Call analysis feature coming soon...")
                
                with col_action2:
                    if st.button(f"📤 Export", key=f"export_{call['id']}"):
                        # Export call data as JSON
                        export_data = {
                            'call_data': call,
                            'export_timestamp': datetime.now().isoformat()
                        }
                        
                        json_data = json.dumps(export_data, indent=2)
                        st.download_button(
                            label="💾 Download Call Data",
                            data=json_data,
                            file_name=f"call_{call['id'][:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            key=f"download_{call['id']}"
                        )
                
                with col_action3:
                    if st.button(f"🔄 Refresh", key=f"refresh_{call['id']}"):
                        # Refresh call data from VAPI
                        if matrix_vapi_client:
                            with st.spinner("Refreshing call data..."):
                                updated_call = matrix_vapi_client.get_call_details(call['id'])
                                if updated_call:
                                    # Update the call record
                                    for key, value in updated_call.items():
                                        if key in ['recordingUrl', 'transcript', 'duration', 'cost', 'status']:
                                            call[key.replace('recordingUrl', 'recording_url')] = value
                                    st.success("✅ Call data refreshed!")
                                    st.rerun()
                                else:
                                    st.warning("⚠️ Could not refresh call data")
        
        # Bulk actions
        st.markdown("### 🔧 Bulk Actions")
        col_bulk1, col_bulk2, col_bulk3 = st.columns(3)
        
        with col_bulk1:
            if st.button("📤 Export All", use_container_width=True):
                export_data = {
                    'call_history': filtered_history,
                    'export_timestamp': datetime.now().isoformat(),
                    'total_records': len(filtered_history),
                    'filters_applied': {
                        'status': status_filter,
                        'agent': agent_filter,
                        'date': date_filter,
                        'sort': sort_order
                    }
                }
                
                json_data = json.dumps(export_data, indent=2)
                st.download_button(
                    label="💾 Download All Call Data",
                    data=json_data,
                    file_name=f"call_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col_bulk2:
            if st.button("🎵 Download All Recordings", use_container_width=True):
                recordings_with_urls = [call for call in filtered_history if call.get('recording_url')]
                if recordings_with_urls:
                    # Create a list of recording URLs
                    recording_urls = [call['recording_url'] for call in recordings_with_urls]
                    urls_text = '\n'.join(recording_urls)
                    
                    st.download_button(
                        label="💾 Download Recording URLs",
                        data=urls_text,
                        file_name=f"recording_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.warning("⚠️ No recordings available in filtered results")
        
        with col_bulk3:
            if st.button("🗑️ Clear History", use_container_width=True):
                if st.button("⚠️ Confirm Clear All", use_container_width=True):
                    st.session_state.call_history = []
                    st.success("✅ Call history cleared")
                    st.rerun()
    
    else:
        st.info("📞 No call records found. Try adjusting your filters or sync with VAPI to load recent calls.")
        
        # Quick start options
        st.markdown("### 🚀 Quick Start")
        col_quick1, col_quick2 = st.columns(2)
        
        with col_quick1:
            if st.button("🔄 Sync with VAPI", use_container_width=True):
                st.rerun()
        
        with col_quick2:
            if st.button("🔮 Make a Call", use_container_width=True):
                st.session_state.current_page = "neural_network"
                st.rerun()


elif st.session_state.current_page == "agent_profiles":
    # Agent Profiles with System Prompts and First Messages
    st.markdown("## 🎤 Agent Profiles & System Configuration")
    st.markdown("*Detailed agent information, system prompts, and first messages*")
    
    # Agent selection
    if 'selected_agent_profile' not in st.session_state:
        st.session_state.selected_agent_profile = list(st.session_state.agents.keys())[0]
    
    selected_agent = st.selectbox("Select Agent to View", 
                                list(st.session_state.agents.keys()),
                                index=list(st.session_state.agents.keys()).index(st.session_state.selected_agent_profile) if st.session_state.selected_agent_profile in st.session_state.agents else 0)
    
    if selected_agent != st.session_state.selected_agent_profile:
        st.session_state.selected_agent_profile = selected_agent
        st.rerun()
    
    agent_info = st.session_state.agents[selected_agent]
    
    # Agent overview
    matrix_level = agent_info.get('matrix_level', 'Operator')
    card_class = get_matrix_card_class(matrix_level)
    
    st.markdown(f"""
    <div class="{card_class}">
        <h2>🔮 {selected_agent}</h2>
        <p><strong>Category:</strong> {agent_info.get('category', 'Unknown')}</p>
        <p><strong>Matrix Level:</strong> <span class="matrix-level-{matrix_level.lower()}">{matrix_level}</span></p>
        <p><strong>Security Clearance:</strong> <span class="matrix-security-{agent_info.get('security_clearance', 'beta').lower()}">{agent_info.get('security_clearance', 'Beta')}</span></p>
        <p><strong>Neural ID:</strong> <span class="matrix-code">{agent_info['id']}</span></p>
        <p><strong>Status:</strong> <span style="color: {'#00ff41' if agent_info.get('status', 'active') == 'active' else '#ff0040'};">●</span> {agent_info.get('status', 'active').title()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabbed interface for agent details
    profile_tab1, profile_tab2, profile_tab3, profile_tab4, profile_tab5 = st.tabs([
        "📋 Basic Info", "🧠 System Prompt", "💬 First Message", "🎤 Voice Config", "📊 Performance"
    ])
    
    with profile_tab1:
        st.markdown("### 📋 Agent Information")
        
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.write(f"**Agent Name:** {selected_agent}")
            st.write(f"**Category:** {agent_info.get('category', 'Unknown')}")
            st.write(f"**Description:** {agent_info.get('description', 'No description available')}")
            st.write(f"**Language:** {agent_info.get('language', 'en').upper()}")
            st.write(f"**Matrix Level:** {agent_info.get('matrix_level', 'Operator')}")
        
        with col_info2:
            st.write(f"**Security Clearance:** {agent_info.get('security_clearance', 'Beta')}")
            st.write(f"**Cost per Minute:** ${agent_info.get('cost_per_minute', 0.12):.3f}")
            st.write(f"**Created:** {agent_info.get('created_at', 'Unknown')}")
            st.write(f"**Last Updated:** {agent_info.get('last_updated', 'Unknown')}")
            st.write(f"**Status:** {agent_info.get('status', 'active').title()}")
        
        st.markdown("### 🧠 Capabilities Matrix")
        capabilities = agent_info.get('capabilities', [])
        if capabilities:
            caps_cols = st.columns(2)
            for i, cap in enumerate(capabilities):
                with caps_cols[i % 2]:
                    st.markdown(f"✅ **{cap}**")
        else:
            st.write("No capabilities defined")
        
        # Sync with VAPI button
        if matrix_vapi_client:
            if st.button("🔄 Sync with VAPI", use_container_width=True):
                with st.spinner("Syncing agent data from VAPI..."):
                    vapi_agent = matrix_vapi_client.get_assistant(agent_info['id'])
                    if vapi_agent:
                        st.success("✅ Agent found in VAPI network")
                        
                        # Update local data with VAPI data
                        if 'model' in vapi_agent and 'messages' in vapi_agent['model']:
                            system_messages = [msg for msg in vapi_agent['model']['messages'] if msg.get('role') == 'system']
                            if system_messages:
                                agent_info['system_prompt'] = system_messages[0].get('content', agent_info.get('system_prompt', ''))
                        
                        if 'firstMessage' in vapi_agent:
                            agent_info['first_message'] = vapi_agent['firstMessage']
                        
                        if 'voice' in vapi_agent:
                            agent_info['voice_model'] = vapi_agent['voice'].get('provider', agent_info.get('voice_model', 'eleven_labs'))
                            agent_info['voice_id'] = vapi_agent['voice'].get('voiceId', agent_info.get('voice_id', ''))
                        
                        st.rerun()
                    else:
                        st.warning("⚠️ Agent not found in VAPI network")
    
    with profile_tab2:
        st.markdown("### 🧠 System Prompt Configuration")
        
        current_prompt = agent_info.get('system_prompt', 'No system prompt configured')
        
        # Display current system prompt
        st.markdown("#### Current System Prompt")
        st.markdown(f"""
        <div class="transcript-container">
            {current_prompt}
        </div>
        """, unsafe_allow_html=True)
        
        # Edit system prompt
        st.markdown("#### Edit System Prompt")
        new_prompt = st.text_area("System Prompt", 
                                value=current_prompt,
                                height=200,
                                help="Define the agent's personality, role, and behavior")
        
        col_prompt1, col_prompt2 = st.columns(2)
        
        with col_prompt1:
            if st.button("💾 Save Locally", use_container_width=True):
                agent_info['system_prompt'] = new_prompt
                st.success("✅ System prompt saved locally")
                st.rerun()
        
        with col_prompt2:
            if st.button("☁️ Update VAPI", use_container_width=True):
                if matrix_vapi_client:
                    with st.spinner("Updating system prompt in VAPI..."):
                        update_data = {
                            "model": {
                                "messages": [
                                    {
                                        "role": "system",
                                        "content": new_prompt
                                    }
                                ]
                            }
                        }
                        
                        result = matrix_vapi_client.update_assistant(agent_info['id'], update_data)
                        if result:
                            agent_info['system_prompt'] = new_prompt
                            st.success("✅ System prompt updated in VAPI")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update system prompt in VAPI")
                else:
                    st.error("❌ VAPI client not available")
        
        # System prompt templates
        st.markdown("#### 📝 System Prompt Templates")
        
        templates = {
            "Professional Assistant": "You are a professional assistant. You are helpful, knowledgeable, and maintain a formal tone. Your goal is to provide accurate and useful information.",
            "Creative Writer": "You are a creative writer. You are imaginative, expressive, and can craft compelling narratives. Your goal is to create engaging and original content.",
            "Technical Expert": "You are a technical expert. You are precise, analytical, and can explain complex concepts clearly. Your goal is to provide technical guidance and solutions.",
            "Sales Professional": "You are a sales professional. You are persuasive, confident, and focused on results. Your goal is to understand customer needs and close deals.",
            "Customer Support": "You are a customer support representative. You are patient, empathetic, and solution-oriented. Your goal is to resolve customer issues effectively."
        }
        
        selected_template = st.selectbox("Choose a template", ["Custom"] + list(templates.keys()))
        
        if selected_template != "Custom":
            if st.button("📋 Apply Template", use_container_width=True):
                agent_info['system_prompt'] = templates[selected_template]
                st.success(f"✅ Applied {selected_template} template")
                st.rerun()
    
    with profile_tab3:
        st.markdown("### 💬 First Message Configuration")
        
        current_message = agent_info.get('first_message', 'Hello! How can I help you today?')
        
        # Display current first message
        st.markdown("#### Current First Message")
        st.markdown(f"""
        <div class="transcript-container">
            {current_message}
        </div>
        """, unsafe_allow_html=True)
        
        # Edit first message
        st.markdown("#### Edit First Message")
        new_message = st.text_area("First Message", 
                                 value=current_message,
                                 height=100,
                                 help="The first message the agent will say when a call starts")
        
        col_msg1, col_msg2 = st.columns(2)
        
        with col_msg1:
            if st.button("💾 Save Locally", key="save_message", use_container_width=True):
                agent_info['first_message'] = new_message
                st.success("✅ First message saved locally")
                st.rerun()
        
        with col_msg2:
            if st.button("☁️ Update VAPI", key="update_message", use_container_width=True):
                if matrix_vapi_client:
                    with st.spinner("Updating first message in VAPI..."):
                        update_data = {
                            "firstMessage": new_message
                        }
                        
                        result = matrix_vapi_client.update_assistant(agent_info['id'], update_data)
                        if result:
                            agent_info['first_message'] = new_message
                            st.success("✅ First message updated in VAPI")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update first message in VAPI")
                else:
                    st.error("❌ VAPI client not available")
        
        # First message templates
        st.markdown("#### 💬 First Message Templates")
        
        message_templates = {
            "Professional Greeting": "Hello! I'm here to assist you today. How may I help you?",
            "Casual Greeting": "Hey there! What can I do for you?",
            "Specific Role": f"Hi! I'm {selected_agent}. I'm ready to help with {agent_info.get('category', 'your needs').lower()}. What would you like to discuss?",
            "Question Starter": "Hello! What brings you here today?",
            "Enthusiastic": "Hi there! I'm excited to help you today. What can we work on together?"
        }
        
        selected_msg_template = st.selectbox("Choose a message template", ["Custom"] + list(message_templates.keys()))
        
        if selected_msg_template != "Custom":
            if st.button("📋 Apply Message Template", use_container_width=True):
                agent_info['first_message'] = message_templates[selected_msg_template]
                st.success(f"✅ Applied {selected_msg_template} template")
                st.rerun()
    
    with profile_tab4:
        st.markdown("### 🎤 Voice Configuration")
        
        voice_model = agent_info.get('voice_model', 'eleven_labs')
        voice_id = agent_info.get('voice_id', '')
        
        col_voice1, col_voice2 = st.columns(2)
        
        with col_voice1:
            st.write(f"**Current Voice Provider:** {VOICE_MODELS.get(voice_model, {}).get('name', 'Unknown')}")
            st.write(f"**Current Voice ID:** `{voice_id}`")
            
            voice_name = VOICE_MODELS.get(voice_model, {}).get('voices', {}).get(voice_id, 'Unknown Voice')
            st.write(f"**Current Voice Name:** {voice_name}")
        
        with col_voice2:
            st.write(f"**Language:** {agent_info.get('language', 'en').upper()}")
            st.write(f"**Cost Impact:** Voice selection may affect per-minute costs")
        
        # Voice selection
        st.markdown("#### 🎵 Change Voice")
        
        new_voice_model = st.selectbox("Voice Provider", list(VOICE_MODELS.keys()), 
                                     index=list(VOICE_MODELS.keys()).index(voice_model) if voice_model in VOICE_MODELS else 0)
        
        available_voices = VOICE_MODELS.get(new_voice_model, {}).get('voices', {})
        voice_options = list(available_voices.keys())
        voice_labels = [f"{voice_id} - {voice_name}" for voice_id, voice_name in available_voices.items()]
        
        if voice_options:
            current_index = voice_options.index(voice_id) if voice_id in voice_options else 0
            selected_voice_index = st.selectbox("Voice Selection", 
                                              range(len(voice_labels)),
                                              format_func=lambda x: voice_labels[x],
                                              index=current_index)
            
            new_voice_id = voice_options[selected_voice_index]
            
            col_voice_save1, col_voice_save2 = st.columns(2)
            
            with col_voice_save1:
                if st.button("💾 Save Voice Config", use_container_width=True):
                    agent_info['voice_model'] = new_voice_model
                    agent_info['voice_id'] = new_voice_id
                    st.success("✅ Voice configuration saved locally")
                    st.rerun()
            
            with col_voice_save2:
                if st.button("☁️ Update VAPI Voice", use_container_width=True):
                    if matrix_vapi_client:
                        with st.spinner("Updating voice configuration in VAPI..."):
                            update_data = {
                                "voice": {
                                    "provider": new_voice_model,
                                    "voiceId": new_voice_id
                                }
                            }
                            
                            result = matrix_vapi_client.update_assistant(agent_info['id'], update_data)
                            if result:
                                agent_info['voice_model'] = new_voice_model
                                agent_info['voice_id'] = new_voice_id
                                st.success("✅ Voice configuration updated in VAPI")
                                st.rerun()
                            else:
                                st.error("❌ Failed to update voice configuration in VAPI")
                    else:
                        st.error("❌ VAPI client not available")
        
        # Voice testing (placeholder)
        if st.button("🎤 Test Voice Sample", use_container_width=True):
            st.info("🔊 Voice testing feature coming soon...")
    
    with profile_tab5:
        st.markdown("### 📊 Performance Analytics")
        
        # Performance metrics
        col_perf1, col_perf2, col_perf3, col_perf4 = st.columns(4)
        
        with col_perf1:
            usage_count = agent_info.get('usage_count', 0)
            st.metric("Total Calls", usage_count)
        
        with col_perf2:
            avg_duration = agent_info.get('avg_call_duration', 0)
            st.metric("Avg Duration", format_duration(avg_duration))
        
        with col_perf3:
            # Calculate success rate from call history
            agent_calls = [call for call in st.session_state.call_history if call.get('agent_name') == selected_agent]
            successful_calls = [call for call in agent_calls if call.get('status') in ['disconnected', 'completed']]
            success_rate = (len(successful_calls) / len(agent_calls) * 100) if agent_calls else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        with col_perf4:
            # Calculate total cost for this agent
            total_cost = sum(call.get('cost', 0) for call in agent_calls)
            st.metric("Total Cost", f"${total_cost:.2f}")
        
        # Performance charts
        if agent_calls:
            st.markdown("#### 📈 Call Duration Trend")
            
            # Create duration trend chart
            call_durations = [call.get('duration', 0) for call in agent_calls[-20:]]  # Last 20 calls
            call_numbers = list(range(1, len(call_durations) + 1))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=call_numbers,
                y=call_durations,
                mode='lines+markers',
                name='Call Duration (seconds)',
                line=dict(color='#00ff41', width=2),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title="Recent Call Duration Trend",
                xaxis_title="Call Number",
                yaxis_title="Duration (seconds)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#00ff41'),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Cost analysis
            st.markdown("#### 💰 Cost Analysis")
            
            daily_costs = defaultdict(float)
            for call in agent_calls:
                call_date = call.get('timestamp', '')[:10]  # Extract date part
                daily_costs[call_date] += call.get('cost', 0)
            
            if daily_costs:
                dates = list(daily_costs.keys())
                costs = list(daily_costs.values())
                
                fig_cost = go.Figure()
                fig_cost.add_trace(go.Bar(
                    x=dates,
                    y=costs,
                    name='Daily Cost',
                    marker_color='#ff4080'
                ))
                
                fig_cost.update_layout(
                    title="Daily Cost Breakdown",
                    xaxis_title="Date",
                    yaxis_title="Cost ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#00ff41'),
                    height=400
                )
                
                st.plotly_chart(fig_cost, use_container_width=True)
        else:
            st.info("📊 No performance data available yet. Make some calls to see analytics!")
    
    # Action buttons
    st.markdown("### 🎮 Agent Actions")
    col_action1, col_action2, col_action3, col_action4 = st.columns(4)
    
    with col_action1:
        if st.button("🔮 Connect Now", use_container_width=True):
            if not st.session_state.call_active:
                success, message = start_matrix_call(selected_agent, agent_info['id'])
                if success:
                    st.success(f"✅ {message}")
                    st.session_state.current_page = "neural_network"
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Neural link already active")
    
    with col_action2:
        if st.button("📋 Export Profile", use_container_width=True):
            export_data = {
                'agent_name': selected_agent,
                'agent_data': agent_info,
                'export_timestamp': datetime.now().isoformat()
            }
            
            json_data = json.dumps(export_data, indent=2)
            st.download_button(
                label="💾 Download Profile",
                data=json_data,
                file_name=f"agent_profile_{selected_agent.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col_action3:
        if st.button("🔄 Refresh from VAPI", use_container_width=True):
            if matrix_vapi_client:
                with st.spinner("Refreshing agent data from VAPI..."):
                    vapi_agent = matrix_vapi_client.get_assistant(agent_info['id'])
                    if vapi_agent:
                        # Update all available fields
                        if 'model' in vapi_agent and 'messages' in vapi_agent['model']:
                            system_messages = [msg for msg in vapi_agent['model']['messages'] if msg.get('role') == 'system']
                            if system_messages:
                                agent_info['system_prompt'] = system_messages[0].get('content', agent_info.get('system_prompt', ''))
                        
                        if 'firstMessage' in vapi_agent:
                            agent_info['first_message'] = vapi_agent['firstMessage']
                        
                        if 'voice' in vapi_agent:
                            agent_info['voice_model'] = vapi_agent['voice'].get('provider', agent_info.get('voice_model', 'eleven_labs'))
                            agent_info['voice_id'] = vapi_agent['voice'].get('voiceId', agent_info.get('voice_id', ''))
                        
                        st.success("✅ Agent data refreshed from VAPI")
                        st.rerun()
                    else:
                        st.warning("⚠️ Could not refresh agent data from VAPI")
            else:
                st.error("❌ VAPI client not available")
    
    with col_action4:
        if st.button("🗑️ Delete Agent", use_container_width=True):
            if st.button("⚠️ Confirm Delete", use_container_width=True):
                if matrix_vapi_client:
                    with st.spinner("Deleting agent from VAPI..."):
                        if matrix_vapi_client.delete_assistant(agent_info['id']):
                            del st.session_state.agents[selected_agent]
                            st.success("✅ Agent deleted from VAPI and local storage")
                            st.session_state.current_page = "neural_network"
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete agent from VAPI")
                else:
                    # Delete locally only
                    del st.session_state.agents[selected_agent]
                    st.success("✅ Agent deleted from local storage")
                    st.session_state.current_page = "neural_network"
                    st.rerun()


elif st.session_state.current_page == "analytics":
    # Analytics Dashboard
    st.markdown("## 📊 Matrix Analytics Dashboard")
    st.markdown("*Comprehensive analytics and insights for your AI agent network*")
    
    # Sync analytics from VAPI
    if matrix_vapi_client and st.button("🔄 Sync Analytics from VAPI", use_container_width=True):
        with st.spinner("Syncing analytics from VAPI..."):
            try:
                analytics_data = matrix_vapi_client.get_analytics()
                if analytics_data:
                    st.success("✅ Analytics synced from VAPI")
                    st.json(analytics_data)
                else:
                    st.warning("⚠️ No analytics data available from VAPI")
            except Exception as e:
                st.error(f"❌ Failed to sync analytics: {e}")
    
    # Overview metrics
    st.markdown("### 📈 Overview Metrics")
    
    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
    
    with col_metric1:
        total_calls = len(st.session_state.call_history)
        st.metric("Total Calls", total_calls)
    
    with col_metric2:
        total_agents = len(st.session_state.agents)
        st.metric("Active Agents", total_agents)
    
    with col_metric3:
        total_cost = st.session_state.cost_tracking['total_cost']
        st.metric("Total Cost", f"${total_cost:.2f}")
    
    with col_metric4:
        if st.session_state.call_history:
            avg_duration = sum(call.get('duration', 0) for call in st.session_state.call_history) / len(st.session_state.call_history)
            st.metric("Avg Call Duration", format_duration(avg_duration))
        else:
            st.metric("Avg Call Duration", "0s")
    
    # Charts and visualizations
    if st.session_state.call_history:
        # Call volume over time
        st.markdown("### 📅 Call Volume Over Time")
        
        daily_calls = defaultdict(int)
        for call in st.session_state.call_history:
            call_date = call.get('timestamp', '')[:10]
            daily_calls[call_date] += 1
        
        if daily_calls:
            dates = sorted(daily_calls.keys())
            volumes = [daily_calls[date] for date in dates]
            
            fig_volume = go.Figure()
            fig_volume.add_trace(go.Scatter(
                x=dates,
                y=volumes,
                mode='lines+markers',
                name='Daily Calls',
                line=dict(color='#00ff41', width=3),
                marker=dict(size=8)
            ))
            
            fig_volume.update_layout(
                title="Daily Call Volume",
                xaxis_title="Date",
                yaxis_title="Number of Calls",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#00ff41'),
                height=400
            )
            
            st.plotly_chart(fig_volume, use_container_width=True)
        
        # Agent usage distribution
        st.markdown("### 🔮 Agent Usage Distribution")
        
        agent_usage = defaultdict(int)
        for call in st.session_state.call_history:
            agent_name = call.get('agent_name', 'Unknown')
            agent_usage[agent_name] += 1
        
        if agent_usage:
            agents = list(agent_usage.keys())
            usage_counts = list(agent_usage.values())
            
            fig_usage = go.Figure()
            fig_usage.add_trace(go.Bar(
                x=agents,
                y=usage_counts,
                name='Call Count',
                marker_color='#00ff41'
            ))
            
            fig_usage.update_layout(
                title="Calls per Agent",
                xaxis_title="Agent",
                yaxis_title="Number of Calls",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#00ff41'),
                height=400,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_usage, use_container_width=True)
        
        # Cost breakdown
        st.markdown("### 💰 Cost Analysis")
        
        col_cost1, col_cost2 = st.columns(2)
        
        with col_cost1:
            # Cost by agent
            agent_costs = defaultdict(float)
            for call in st.session_state.call_history:
                agent_name = call.get('agent_name', 'Unknown')
                agent_costs[agent_name] += call.get('cost', 0)
            
            if agent_costs:
                fig_cost_pie = go.Figure(data=[go.Pie(
                    labels=list(agent_costs.keys()),
                    values=list(agent_costs.values()),
                    hole=0.3
                )])
                
                fig_cost_pie.update_layout(
                    title="Cost Distribution by Agent",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#00ff41'),
                    height=400
                )
                
                st.plotly_chart(fig_cost_pie, use_container_width=True)
        
        with col_cost2:
            # Daily cost trend
            daily_costs = defaultdict(float)
            for call in st.session_state.call_history:
                call_date = call.get('timestamp', '')[:10]
                daily_costs[call_date] += call.get('cost', 0)
            
            if daily_costs:
                dates = sorted(daily_costs.keys())
                costs = [daily_costs[date] for date in dates]
                
                fig_cost_trend = go.Figure()
                fig_cost_trend.add_trace(go.Scatter(
                    x=dates,
                    y=costs,
                    mode='lines+markers',
                    name='Daily Cost',
                    line=dict(color='#ff4080', width=3),
                    marker=dict(size=8)
                ))
                
                fig_cost_trend.update_layout(
                    title="Daily Cost Trend",
                    xaxis_title="Date",
                    yaxis_title="Cost ($)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#00ff41'),
                    height=400
                )
                
                st.plotly_chart(fig_cost_trend, use_container_width=True)
        
        # Performance metrics
        st.markdown("### 📊 Performance Metrics")
        
        # Success rate by agent
        agent_performance = {}
        for agent_name in st.session_state.agents.keys():
            agent_calls = [call for call in st.session_state.call_history if call.get('agent_name') == agent_name]
            if agent_calls:
                successful_calls = [call for call in agent_calls if call.get('status') in ['disconnected', 'completed']]
                success_rate = len(successful_calls) / len(agent_calls) * 100
                avg_duration = sum(call.get('duration', 0) for call in agent_calls) / len(agent_calls)
                total_cost = sum(call.get('cost', 0) for call in agent_calls)
                
                agent_performance[agent_name] = {
                    'success_rate': success_rate,
                    'avg_duration': avg_duration,
                    'total_calls': len(agent_calls),
                    'total_cost': total_cost
                }
        
        if agent_performance:
            # Create performance table
            performance_data = []
            for agent_name, metrics in agent_performance.items():
                performance_data.append({
                    'Agent': agent_name,
                    'Total Calls': metrics['total_calls'],
                    'Success Rate': f"{metrics['success_rate']:.1f}%",
                    'Avg Duration': format_duration(metrics['avg_duration']),
                    'Total Cost': f"${metrics['total_cost']:.2f}",
                    'Cost per Call': f"${metrics['total_cost']/metrics['total_calls']:.3f}" if metrics['total_calls'] > 0 else "$0.000"
                })
            
            df_performance = pd.DataFrame(performance_data)
            st.dataframe(df_performance, use_container_width=True, hide_index=True)
    
    else:
        st.info("📊 No analytics data available yet. Make some calls to see insights!")
        
        if st.button("🔮 Start Making Calls", use_container_width=True):
            st.session_state.current_page = "neural_network"
            st.rerun()

elif st.session_state.current_page == "system_config":
    # System Configuration
    st.markdown("## ⚙️ Matrix System Configuration")
    st.markdown("*Configure and manage Matrix network settings and preferences*")
    
    config_tab1, config_tab2, config_tab3, config_tab4 = st.tabs([
        "🔐 Security", "🎛️ Preferences", "📊 Data Management", "ℹ️ System Info"
    ])
    
    with config_tab1:
        st.markdown("### 🔐 Matrix Security Configuration")
        
        # API Key management
        st.markdown("#### 🔑 API Key Management")
        
        col_api1, col_api2 = st.columns(2)
        
        with col_api1:
            if VAPI_API_KEY:
                masked_key = f"{'*' * (len(VAPI_API_KEY) - 4)}{VAPI_API_KEY[-4:]}"
                st.success(f"✅ API Key Configured: {masked_key}")
            else:
                st.error("❌ API Key Not Configured")
            
            if st.button("🔄 Test API Key", use_container_width=True):
                if matrix_vapi_client:
                    try:
                        agents = matrix_vapi_client.get_assistants()
                        st.success("✅ API Key is valid and working")
                    except Exception as e:
                        st.error(f"❌ API Key test failed: {e}")
                else:
                    st.error("❌ Matrix client not available")
        
        with col_api2:
            st.markdown("**Security Status:**")
            st.write("🔒 Connection: Encrypted")
            st.write("🛡️ Authentication: Bearer Token")
            st.write("🔐 Protocol: HTTPS")
            st.write("🌐 Network: Matrix Secure")
        
        # Security settings
        st.markdown("#### 🛡️ Security Settings")
        
        col_sec1, col_sec2 = st.columns(2)
        
        with col_sec1:
            auto_disconnect = st.checkbox("Auto-disconnect on idle", value=True)
            require_confirmation = st.checkbox("Require confirmation for sensitive operations", value=True)
            log_all_activities = st.checkbox("Log all Matrix activities", value=True)
        
        with col_sec2:
            max_session_duration = st.number_input("Max session duration (hours)", min_value=1, max_value=24, value=8)
            idle_timeout = st.number_input("Idle timeout (minutes)", min_value=5, max_value=120, value=30)
        
        if st.button("💾 Save Security Settings", use_container_width=True):
            security_settings = {
                'auto_disconnect': auto_disconnect,
                'require_confirmation': require_confirmation,
                'log_all_activities': log_all_activities,
                'max_session_duration': max_session_duration,
                'idle_timeout': idle_timeout
            }
            st.session_state.user_preferences['security'] = security_settings
            st.success("✅ Security settings saved")
    
    with config_tab2:
        st.markdown("### 🎛️ Matrix User Preferences")
        
        # UI preferences
        st.markdown("#### 🎨 Interface Preferences")
        
        col_ui1, col_ui2 = st.columns(2)
        
        with col_ui1:
            default_view_mode = st.selectbox("Default Agent View", ["Cards", "Table"])
            auto_refresh = st.checkbox("Auto-refresh data", value=True)
            show_animations = st.checkbox("Show Matrix animations", value=True)
        
        with col_ui2:
            default_sort = st.selectbox("Default Sort Order", ["Name", "Usage", "Cost", "Matrix Level"])
            items_per_page = st.number_input("Items per page", min_value=10, max_value=100, value=20)
            enable_notifications = st.checkbox("Enable notifications", value=True)
        
        # Default agent settings
        st.markdown("#### 🔮 Default Agent Settings")
        
        col_agent1, col_agent2 = st.columns(2)
        
        with col_agent1:
            default_voice_model = st.selectbox("Default Voice Model", list(VOICE_MODELS.keys()))
            default_language = st.selectbox("Default Language", ["en", "es", "fr", "de", "it", "pt", "multi"])
        
        with col_agent2:
            default_cost_per_minute = st.number_input("Default Cost/Min", min_value=0.01, max_value=1.00, value=0.12, step=0.01)
            default_matrix_level = st.selectbox("Default Matrix Level", ["Operator", "Oracle", "Architect"])
        
        if st.button("💾 Save Preferences", use_container_width=True):
            preferences = {
                'ui': {
                    'default_view_mode': default_view_mode,
                    'auto_refresh': auto_refresh,
                    'show_animations': show_animations,
                    'default_sort': default_sort,
                    'items_per_page': items_per_page,
                    'enable_notifications': enable_notifications
                },
                'agent_defaults': {
                    'voice_model': default_voice_model,
                    'language': default_language,
                    'cost_per_minute': default_cost_per_minute,
                    'matrix_level': default_matrix_level
                }
            }
            st.session_state.user_preferences.update(preferences)
            st.success("✅ Preferences saved")
    
    with config_tab3:
        st.markdown("### 📊 Matrix Data Management")
        
        # Data export
        st.markdown("#### 📤 Export Matrix Data")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("💾 Export All Agents", use_container_width=True):
                export_data = {
                    'agents': st.session_state.agents,
                    'export_timestamp': datetime.now().isoformat(),
                    'total_agents': len(st.session_state.agents)
                }
                
                json_data = json.dumps(export_data, indent=2)
                st.download_button(
                    label="💾 Download Agents JSON",
                    data=json_data,
                    file_name=f"matrix_agents_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            if st.button("💾 Export Call History", use_container_width=True):
                export_data = {
                    'call_history': st.session_state.call_history,
                    'export_timestamp': datetime.now().isoformat(),
                    'total_calls': len(st.session_state.call_history)
                }
                
                json_data = json.dumps(export_data, indent=2)
                st.download_button(
                    label="💾 Download Call History JSON",
                    data=json_data,
                    file_name=f"matrix_call_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col_export2:
            if st.button("💾 Export Complete Matrix", use_container_width=True):
                complete_export = {
                    'agents': st.session_state.agents,
                    'squads': st.session_state.squads,
                    'call_history': st.session_state.call_history,
                    'cost_tracking': st.session_state.cost_tracking,
                    'user_preferences': st.session_state.user_preferences,
                    'export_timestamp': datetime.now().isoformat(),
                    'version': '2.0.0'
                }
                
                json_data = json.dumps(complete_export, indent=2)
                st.download_button(
                    label="💾 Download Complete Backup",
                    data=json_data,
                    file_name=f"matrix_complete_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        # Data import
        st.markdown("#### 📥 Import Matrix Data")
        
        uploaded_file = st.file_uploader("Choose a backup file", type=['json'])
        if uploaded_file is not None:
            try:
                import_data = json.load(uploaded_file)
                
                st.markdown("**Import Preview:**")
                st.json(import_data)
                
                if st.button("📥 Import Data", use_container_width=True):
                    if 'agents' in import_data:
                        st.session_state.agents.update(import_data['agents'])
                    if 'squads' in import_data:
                        st.session_state.squads.update(import_data['squads'])
                    if 'call_history' in import_data:
                        st.session_state.call_history.extend(import_data['call_history'])
                    if 'cost_tracking' in import_data:
                        st.session_state.cost_tracking.update(import_data['cost_tracking'])
                    if 'user_preferences' in import_data:
                        st.session_state.user_preferences.update(import_data['user_preferences'])
                    
                    st.success("✅ Data imported successfully")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Failed to import data: {e}")
        
        # Data cleanup
        st.markdown("#### 🧹 Data Cleanup")
        
        col_cleanup1, col_cleanup2 = st.columns(2)
        
        with col_cleanup1:
            if st.button("🗑️ Clear Call History", use_container_width=True):
                if st.button("⚠️ Confirm Clear History", use_container_width=True):
                    st.session_state.call_history = []
                    st.success("✅ Call history cleared")
                    st.rerun()
        
        with col_cleanup2:
            if st.button("🔄 Reset All Settings", use_container_width=True):
                if st.button("⚠️ Confirm Reset All", use_container_width=True):
                    # Reset to defaults
                    initialize_matrix_session_state()
                    st.success("✅ All settings reset to defaults")
                    st.rerun()
    
    with config_tab4:
        st.markdown("### ℹ️ System Information")
        
        # System status
        st.markdown("#### 🖥️ System Status")
        
        col_sys1, col_sys2 = st.columns(2)
        
        with col_sys1:
            st.write("**Application Version:** 2.0.0 Enhanced")
            st.write("**Matrix Mode:** Active")
            st.write("**VAPI Connection:** " + ("✅ Connected" if matrix_vapi_client else "❌ Disconnected"))
            st.write("**Session Duration:** " + format_duration((datetime.now() - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()))
        
        with col_sys2:
            st.write(f"**Total Agents:** {len(st.session_state.agents)}")
            st.write(f"**Total Squads:** {len(st.session_state.squads)}")
            st.write(f"**Call History Records:** {len(st.session_state.call_history)}")
            st.write(f"**Active Connections:** {'1' if st.session_state.call_active else '0'}")
        
        # Feature status
        st.markdown("#### 🚀 Feature Status")
        
        features = {
            "Neural Network Interface": "✅ Active",
            "Call History & Audio Playback": "✅ Active", 
            "Agent Profile Management": "✅ Active",
            "System Prompt Configuration": "✅ Active",
            "Voice Configuration": "✅ Active",
            "Analytics Dashboard": "✅ Active",
            "VAPI Integration": "✅ Active" if matrix_vapi_client else "❌ Inactive",
            "Real-time Call Monitoring": "🔄 In Development",
            "Advanced AI Training": "🔄 In Development",
            "Multi-language Support": "✅ Active"
        }
        
        for feature, status in features.items():
            st.write(f"**{feature}:** {status}")
        
        # About
        st.markdown("#### ℹ️ About Matrix AI Call System")
        
        st.markdown("""
        **Matrix AI Call System v2.0.0 Enhanced**
        
        An advanced AI agent communication platform that provides:
        - Real-time neural connections to AI agents
        - Comprehensive call history with audio playback
        - Detailed agent profile management
        - System prompt and voice configuration
        - Advanced analytics and performance monitoring
        - Full VAPI integration for production calls
        
        **Key Enhancements in v2.0.0:**
        - Enhanced agent profiles with system prompts and first messages
        - New call history page with audio playback functionality
        - Improved Matrix-themed UI with better visual hierarchy
        - Advanced analytics dashboard with performance metrics
        - Comprehensive VAPI integration for real call management
        - Export/import functionality for data management
        
        Built with Streamlit and integrated with VAPI for production-ready AI voice calls.
        """)
        
        # Support and documentation
        st.markdown("#### 📚 Support & Documentation")
        
        col_support1, col_support2 = st.columns(2)
        
        with col_support1:
            if st.button("📖 View Documentation", use_container_width=True):
                st.info("📖 Documentation feature coming soon...")
        
        with col_support2:
            if st.button("🆘 Get Support", use_container_width=True):
                st.info("🆘 Support feature coming soon...")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #00ff41; font-family: 'Orbitron', monospace;">
    <p>🔮 Matrix AI Call System v2.0.0 Enhanced | Neural Network Active | Quantum Processing Enabled</p>
    <p><em>Welcome to the Matrix. The choice is yours.</em></p>
</div>
""", unsafe_allow_html=True)
