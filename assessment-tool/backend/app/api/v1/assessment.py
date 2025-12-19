"""
Assessment API Endpoints - Chapter 1 (Identity Resolution)
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from database import get_db, Assessment

router = APIRouter()

# Pydantic models for request/response
class AssessmentInit(BaseModel):
    industry: str = "restaurant"
    language: str = "en"
    theme: Optional[str] = "tech_blue"

class AssessmentResponse(BaseModel):
    assessment_id: str
    status: str
    current_chapter: int
    created_at: str

class IdentitySearch(BaseModel):
    company_name: str
    location: Optional[str] = None
    website: Optional[str] = None

class Candidate(BaseModel):
    id: str
    name: str
    confidence: float
    cin: Optional[str] = None
    registered_address: Optional[str] = None
    founded_year: Optional[int] = None

class CandidatesResponse(BaseModel):
    candidates: List[Candidate]
    recommended_index: int

class ConfirmIdentity(BaseModel):
    company_name: str
    contact_email: Optional[str] = None
    website: Optional[str] = None
    cin: Optional[str] = None
    industry: Optional[str] = None

# MOCK DATA for rapid prototyping
MOCK_CANDIDATES = {
    "noya foods": [
        {
            "id": "U15400MH2015PTC268901",
            "name": "Noya Foods Pvt Ltd",
            "confidence": 0.87,
            "cin": "U15400MH2015PTC268901",
            "registered_address": "Mumbai, Maharashtra",
            "founded_year": 2015
        },
        {
            "id": "U15400MH2018PTC312456",
            "name": "Noya Traders",
            "confidence": 0.43,
            "cin": "U15400MH2018PTC312456",
            "registered_address": "Mumbai, Maharashtra",
            "founded_year": 2018
        },
        {
            "id": "ZOMATO_NOYA",
            "name": "Noya Restaurant (Zomato)",
            "confidence": 0.61,
            "cin": None,
            "registered_address": "Bandra West, Mumbai",
            "founded_year": 2019
        }
    ],
    "default": [
        {
            "id": "DEMO_001",
            "name": "Demo Company Pvt Ltd",
            "confidence": 0.75,
            "cin": "U74999MH2020PTC345678",
            "registered_address": "Pune, Maharashtra",
            "founded_year": 2020
        }
    ]
}

@router.post("/init", response_model=AssessmentResponse)
async def init_assessment(data: AssessmentInit, db: Session = Depends(get_db)):
    """
    Initialize a new assessment
    """
    assessment_id = str(uuid.uuid4())
    
    # Create assessment in database
    assessment = Assessment(
        id=assessment_id,
        company_name="Unknown",  # Will be set in identify step
        status="in_progress",
        current_chapter=1,
        created_at=datetime.utcnow()
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    return AssessmentResponse(
        assessment_id=assessment_id,
        status="in_progress",
        current_chapter=1,
        created_at=assessment.created_at.isoformat()
    )

@router.post("/{assessment_id}/identify", response_model=CandidatesResponse)
async def identify_company(assessment_id: str, data: IdentitySearch):
    """
    Search for company identity - returns candidate matches
    """
    # Simple mock search logic
    search_key = data.company_name.lower()
    
    if "noya" in search_key:
        candidates = MOCK_CANDIDATES["noya foods"]
    else:
        candidates = MOCK_CANDIDATES["default"]
    
    return CandidatesResponse(
        candidates=[Candidate(**c) for c in candidates],
        recommended_index=0
    )

@router.post("/{assessment_id}/confirm")
async def confirm_identity(assessment_id: str, data: ConfirmIdentity, db: Session = Depends(get_db)):
    """
    Confirm selected company identity
    """
    # Get assessment from database
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail=f"Assessment {assessment_id} not found")
    
    # Update with confirmed identity
    assessment.company_name = data.company_name
    assessment.cin = data.cin
    assessment.industry = data.industry or assessment.industry
    assessment.website = data.website
    assessment.current_chapter = 2
    assessment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(assessment)
    
    return {
        "success": True,
        "message": "Identity confirmed",
        "assessment_id": assessment_id,
        "next_chapter": 2,
        "company_name": assessment.company_name
    }

@router.get("/{assessment_id}")
async def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    """
    Get assessment status
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail=f"Assessment {assessment_id} not found")
    
    return {
        "assessment_id": assessment.id,
        "status": assessment.status,
        "current_chapter": assessment.current_chapter,
        "company_name": assessment.company_name or "Unknown",
        "digital_health_score": assessment.digital_health_score,
        "financial_health_score": assessment.financial_health_score,
        "created_at": assessment.created_at.isoformat() if assessment.created_at else None
    }

