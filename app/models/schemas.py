from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone

# ========== ENUMS ==========
class TargetRole(str, Enum):
    SDE = "SDE"
    DATA_SCIENCE = "Data Science"
    AI_ML = "AI/ML Engineer"
    WEB_DEV = "Web Developer"
    OTHER = "Other"

class SkillLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

# ========== AUTH - Devang owns ==========

class UserSyncRequest(BaseModel):
    """Frontend sends this AFTER supabase login to create profile in your DB"""
    supabase_id: str = Field(description="Comes from supabase.auth.getUser().id")
    email: EmailStr
    full_name: Optional[str] = None # Will be auto-filled if Google login
    avatar_url: Optional[str] = None # For Google profile pic

class UserResponse(BaseModel):
    id: str # supabase_id
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

class MeResponse(BaseModel):
    """For GET /me"""
    user: UserResponse
    is_authenticated: bool = True

# ========== RESUME - Devang owns, Navneet uses ==========
class ParsedResume(BaseModel):
    """Output of parser.py - THE MAIN OBJECT for whole app"""
    student_id: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    skills: List[str] = Field(default_factory=list, description="e.g. ['Python', 'React', 'SQL']")
    education: List[Dict[str, Any]] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    raw_text: str
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ResumeUploadResponse(BaseModel):
    message: str
    student_id: str
    parsed_data: ParsedResume

# ========== ANALYZE - Navneet owns ==========
class AnalyzeRequest(BaseModel):
    target_role: TargetRole
    required_skills: Optional[List[str]] = None # If None, Navneet will infer from role

class SkillGap(BaseModel):
    skill: str
    status: str = Field(description="matched | missing | partial")
    level: Optional[SkillLevel] = None

class AnalysisResponse(BaseModel):
    student_id: str
    target_role: TargetRole
    match_score: int = Field(..., ge=0, le=100, description="0-100%")
    matched_skills: List[str]
    missing_skills: List[str]
    gaps: List[SkillGap]
    summary: str = Field(description="AI summary by Groq")
    analyzed_at: datetime=Field(default_factory=lambda: datetime.now(timezone.utc))

# ========== ROADMAP - Navneet owns ==========
class RoadmapStep(BaseModel):
    step_no: int
    skill: str
    title: str
    description: str
    resources: List[Dict[str, str]] = Field(default_factory=list, description="[{'type': 'youtube', 'title': '...', 'url': '...'}]")
    estimated_days: int
    is_completed: bool = False

class RoadmapRequest(BaseModel):
    target_role: TargetRole
    missing_skills: List[str]

class RoadmapResponse(BaseModel):
    student_id: str
    target_role: TargetRole
    roadmap: List[RoadmapStep]
    total_estimated_days: int
    generated_at: datetime=Field(default_factory=lambda: datetime.now(timezone.utc))

# ========== INTERNSHIPS - Navneet owns ==========
class Internship(BaseModel):
    id: str
    title: str
    company: str
    required_skills: List[str]
    location: str
    stipend: Optional[str] = None
    match_score: Optional[int] = None
    url: Optional[str] = None

class InternshipMatchResponse(BaseModel):
    student_id: str
    total_found: int
    matches: List[Internship]

# ========== GENERIC ==========
class MessageResponse(BaseModel):
    message: str