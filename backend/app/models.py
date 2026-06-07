# app/models.py
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.database import Base

# Update Skill
class Skill(Base):
    __tablename__ = "skills"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    depth_score = Column(Integer, default=3)
    recency_score = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="skills")
    outgoing_edges = relationship("Edge", foreign_keys="Edge.from_skill_id", back_populates="from_skill")
    incoming_edges = relationship("Edge", foreign_keys="Edge.to_skill_id", back_populates="to_skill")
    artifacts = relationship("Artifact", back_populates="skill")

# Update Edge
class Edge(Base):
    __tablename__ = "edges"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    from_skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"))
    to_skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"))
    project_name = Column(String, nullable=False)
    outcome = Column(Text, nullable=False)
    artifact_links = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resume = relationship("Resume", back_populates="edges")
    from_skill = relationship("Skill", foreign_keys=[from_skill_id], back_populates="outgoing_edges")
    to_skill = relationship("Skill", foreign_keys=[to_skill_id], back_populates="incoming_edges")

# Update Artifact
class Artifact(Base):
    __tablename__ = "artifacts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"))
    title = Column(String)
    url = Column(String)
    description = Column(Text)
    metric_impact = Column(String, nullable=True)
    
    resume = relationship("Resume", back_populates="artifacts")
    skill = relationship("Skill", back_populates="artifacts")

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)   # optional title, e.g., "John's Resume"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    skills = relationship("Skill", back_populates="resume", cascade="all, delete-orphan")
    edges = relationship("Edge", back_populates="resume", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="resume", cascade="all, delete-orphan") 
