from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime

class UserBase(BaseModel):
    email: str
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class JobBase(BaseModel):
    title: str
    company: str
    description: str
    shortlist_size: int = 5

class JobCreate(JobBase):
    location: str
    years_of_experience: int
    qualification: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    responsibilities: List[str] = []

class Job(JobBase):
    id: int
    employer_id: int
    requirements_json: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CandidateBase(BaseModel):
    name: str
    email: str
    resume_filename: str

class CandidateCreate(CandidateBase):
    resume_text: str
    structured_resume_json: str

class Candidate(CandidateBase):
    id: int
    structured_resume_json: str
    model_config = ConfigDict(from_attributes=True)

class SkillMatch(BaseModel):
    skill: str
    required: bool
    matched: bool
    match_type: Optional[str] = None
    evidence: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ApplicationBase(BaseModel):
    job_id: int
    candidate_id: int

class ApplicationCreate(ApplicationBase):
    pass

class Application(ApplicationBase):
    id: int
    status: str
    semantic_score: float
    keyword_score: float
    required_skill_score: float
    coherence_score: float
    final_score: float
    rank: Optional[int] = None
    explanation: Optional[str] = None
    created_at: datetime
    
    candidate: Candidate
    skill_matches: List[SkillMatch] = []
    
    model_config = ConfigDict(from_attributes=True)

class RankResponse(BaseModel):
    applications: List[Application]
