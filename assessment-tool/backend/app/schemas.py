"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class IndustryType(str, Enum):
    RESTAURANT = "restaurant"
    RETAIL = "retail"
    SERVICES = "services"
    MANUFACTURING = "manufacturing"
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    OTHER = "other"


class AssessmentStatus(str, Enum):
    INITIATED = "initiated"
    IDENTITY_RESOLVED = "identity_resolved"
    DISCOVERY_COMPLETE = "discovery_complete"
    ANALYSIS_COMPLETE = "analysis_complete"
    COMPLETED = "completed"


# Chapter 1: Identity Resolution

class AssessmentInitRequest(BaseModel):
    industry: IndustryType = Field(..., description="Business industry type")
    
    class Config:
        use_enum_values = True


class AssessmentInitResponse(BaseModel):
    assessment_id: str
    status: AssessmentStatus
    created_at: datetime
    message: str = "Assessment initialized successfully"


class IdentitySearchRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=200, description="Company name to search")
    location: Optional[str] = Field(None, max_length=100, description="City or state")
    
    @validator('company_name')
    def validate_company_name(cls, v):
        if not v.strip():
            raise ValueError('Company name cannot be empty')
        return v.strip()


class CandidateCompany(BaseModel):
    id: str
    name: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    cin: Optional[str] = Field(None, description="Corporate Identification Number")
    registered_address: Optional[str] = None
    founded_year: Optional[int] = Field(None, ge=1800, le=2030)
    industry: Optional[str] = None
    website: Optional[str] = None
    

class IdentitySearchResponse(BaseModel):
    assessment_id: str
    candidates: List[CandidateCompany]
    search_query: str
    total_found: int
    message: str = "Identity candidates retrieved"


class IdentityConfirmRequest(BaseModel):
    selected_id: str = Field(..., description="ID of the selected candidate")


class IdentityConfirmResponse(BaseModel):
    assessment_id: str
    confirmed_company: CandidateCompany
    status: AssessmentStatus
    next_chapter: int = 2
    message: str = "Identity confirmed successfully"


# Error Response

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    type: str


class ErrorResponse(BaseModel):
    error: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = None


# Health Check

class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    service: str = "assessment-backend"
    timestamp: str
    version: str = "1.0.0"
