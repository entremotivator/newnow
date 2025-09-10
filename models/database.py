"""
Enhanced Database Models for Matrix VAPI Client
SQLAlchemy models for persistent data storage
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text)
    system_prompt = Column(Text, nullable=False)
    first_message = Column(Text)
    capabilities = Column(JSON)
    voice_config = Column(JSON)
    cost_per_minute = Column(Float, default=0.12)
    language = Column(String, default="en")
    matrix_level = Column(String, default="Operator")
    security_clearance = Column(String, default="Beta")
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usage_count = Column(Integer, default=0)
    avg_call_duration = Column(Float, default=0.0)
    success_rate = Column(Float, default=100.0)
    personality_traits = Column(JSON)
    specializations = Column(JSON)
    max_call_duration = Column(Integer, default=3600)
    min_call_duration = Column(Integer, default=30)

class CallRecord(Base):
    __tablename__ = "call_records"
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, nullable=False)
    agent_name = Column(String, nullable=False)
    phone_number = Column(String)
    customer_number = Column(String)
    status = Column(String, nullable=False)
    duration = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    recording_url = Column(String)
    transcript = Column(Text)
    summary = Column(Text)
    sentiment_score = Column(Float)
    quality_score = Column(Float)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class Squad(Base):
    __tablename__ = "squads"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    agent_ids = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    squad_type = Column(String, default="standard")
    max_concurrent_calls = Column(Integer, default=5)

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    agent_id = Column(String)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    module = Column(String)
    function = Column(String)
    line_number = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

# Database Manager
class DatabaseManager:
    def __init__(self, database_url: str = "sqlite:///matrix_vapi.db"):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Close database session"""
        session.close()
    
    # Agent operations
    def create_agent(self, agent_data: Dict[str, Any]) -> Optional[Agent]:
        """Create new agent record"""
        session = self.get_session()
        try:
            agent = Agent(**agent_data)
            session.add(agent)
            session.commit()
            session.refresh(agent)
            return agent
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        session = self.get_session()
        try:
            return session.query(Agent).filter(Agent.id == agent_id).first()
        finally:
            self.close_session(session)
    
    def get_all_agents(self) -> List[Agent]:
        """Get all agents"""
        session = self.get_session()
        try:
            return session.query(Agent).all()
        finally:
            self.close_session(session)
    
    def update_agent(self, agent_id: str, update_data: Dict[str, Any]) -> Optional[Agent]:
        """Update agent record"""
        session = self.get_session()
        try:
            agent = session.query(Agent).filter(Agent.id == agent_id).first()
            if agent:
                for key, value in update_data.items():
                    setattr(agent, key, value)
                agent.last_updated = datetime.utcnow()
                session.commit()
                session.refresh(agent)
            return agent
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete agent record"""
        session = self.get_session()
        try:
            agent = session.query(Agent).filter(Agent.id == agent_id).first()
            if agent:
                session.delete(agent)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    # Call record operations
    def create_call_record(self, call_data: Dict[str, Any]) -> Optional[CallRecord]:
        """Create new call record"""
        session = self.get_session()
        try:
            call_record = CallRecord(**call_data)
            session.add(call_record)
            session.commit()
            session.refresh(call_record)
            return call_record
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    def get_call_records(self, limit: int = 100, agent_id: str = None) -> List[CallRecord]:
        """Get call records with optional filtering"""
        session = self.get_session()
        try:
            query = session.query(CallRecord)
            if agent_id:
                query = query.filter(CallRecord.agent_id == agent_id)
            return query.order_by(CallRecord.created_at.desc()).limit(limit).all()
        finally:
            self.close_session(session)
    
    # Analytics operations
    def record_metric(self, date: datetime, agent_id: str, metric_name: str, 
                     metric_value: float, metadata: Dict = None):
        """Record analytics metric"""
        session = self.get_session()
        try:
            analytics = Analytics(
                date=date,
                agent_id=agent_id,
                metric_name=metric_name,
                metric_value=metric_value,
                metadata=metadata
            )
            session.add(analytics)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.close_session(session)
    
    def get_metrics(self, start_date: datetime, end_date: datetime, 
                   agent_id: str = None, metric_name: str = None) -> List[Analytics]:
        """Get analytics metrics with filtering"""
        session = self.get_session()
        try:
            query = session.query(Analytics).filter(
                Analytics.date >= start_date,
                Analytics.date <= end_date
            )
            if agent_id:
                query = query.filter(Analytics.agent_id == agent_id)
            if metric_name:
                query = query.filter(Analytics.metric_name == metric_name)
            return query.order_by(Analytics.date.desc()).all()
        finally:
            self.close_session(session)
