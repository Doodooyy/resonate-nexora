from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String) # 'employer' or 'employee'

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    company = Column(String)
    description = Column(Text)
    requirements_json = Column(Text) # Storing structured JD as JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    shortlist_size = Column(Integer, default=5)

    applications = relationship("Application", back_populates="job")
    employer = relationship("User")

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    resume_filename = Column(String)
    resume_text = Column(Text)
    structured_resume_json = Column(Text)
    
    applications = relationship("Application", back_populates="candidate")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    status = Column(String, default="pending") # pending, shortlisted, rejected
    
    # Scores
    semantic_score = Column(Float, default=0.0)
    keyword_score = Column(Float, default=0.0)
    required_skill_score = Column(Float, default=0.0)
    coherence_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)
    rank = Column(Integer, nullable=True)
    
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")
    skill_matches = relationship("SkillMatch", back_populates="application")

class SkillMatch(Base):
    __tablename__ = "skill_matches"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"))
    skill = Column(String)
    normalized_skill = Column(String)
    required = Column(Boolean)
    matched = Column(Boolean)
    match_type = Column(String) # 'explicit', 'alias', 'fuzzy'
    evidence = Column(Text) # JSON list of evidence snippets

    application = relationship("Application", back_populates="skill_matches")

class BiasFlag(Base):
    __tablename__ = "bias_flags"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    category = Column(String)
    severity = Column(String)
    phrase = Column(String)
    explanation = Column(Text)
    suggestion = Column(Text)
