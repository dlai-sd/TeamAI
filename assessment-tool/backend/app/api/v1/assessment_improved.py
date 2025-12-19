"""
Improved Assessment API with proper validation and error handling
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
import logging

# Import schemas
import sys
sys.path.append('..')
from app.schemas import (
    AssessmentInitRequest,
    AssessmentInitResponse,
    IdentitySearchRequest,
    IdentitySearchResponse,
    IdentityConfirmRequest,
    IdentityConfirmResponse,
    CandidateCompany,
    AssessmentStatus,
    ErrorResponse
)

# Import database
from database import get_db, Assessment

router = APIRouter(prefix="/assessment", tags=["Chapter 1: Identity Resolution"])
logger = logging.getLogger(__name__)

# Mock data for development
MOCK_CANDIDATES = {
    "noya foods": [
        {
            "id": "noya-123",
            "name": "Noya Foods & Beverages Pvt Ltd",
            "confidence": 0.87,
            "cin": "U15400MH2018PTC308234",
            "registered_address": "Andheri East, Mumbai, Maharashtra",
            "founded_year": 2018,
            "industry": "Food & Beverages",
            "website": "https://noyafoods.com"
        },
        {
            "id": "noya-456",
            "name": "Noya Restaurant Services",
            "confidence": 0.61,
            "cin": "U55101MH2020PTC341567",
            "registered_address": "Bandra West, Mumbai, Maharashtra",
            "founded_year": 2020,
            "industry": "Restaurant Services"
        },
        {
            "id": "noya-789",
            "name": "Noya Hospitality Group",
            "confidence": 0.43,
            "registered_address": "Powai, Mumbai, Maharashtra",
            "founded_year": 2019,
            "industry": "Hospitality"
        }
    ],
    "default": [
        {
            "id": "unknown-001",
            "name": "Unknown Company Ltd",
            "confidence": 0.50,
            "registered_address": "Location not specified",
            "industry": "General"
        }
    ]
}


@router.post("/init", response_model=AssessmentInitResponse, status_code=status.HTTP_201_CREATED)
async def initialize_assessment(
    request: AssessmentInitRequest,
    db: Session = Depends(get_db)
):
    """
    Initialize a new assessment.
    Creates a new assessment record and returns assessment_id.
    """
    try:
        assessment_id = str(uuid.uuid4())
        
        # Create assessment in database
        assessment = Assessment(
            id=assessment_id,
            industry=request.industry,
            status="initiated",
            current_chapter=1
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        
        logger.info(f"Assessment initialized: {assessment_id}")
        
        return AssessmentInitResponse(
            assessment_id=assessment_id,
            status=AssessmentStatus.INITIATED,
            created_at=assessment.created_at,
            message="Assessment initialized successfully. Ready for Chapter 1."
        )
    
    except Exception as e:
        logger.error(f"Failed to initialize assessment: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize assessment: {str(e)}"
        )


@router.post("/{assessment_id}/identify", response_model=IdentitySearchResponse)
async def search_identity(
    assessment_id: str,
    request: IdentitySearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search for company identity candidates.
    Returns list of potential matches with confidence scores.
    """
    try:
        # Verify assessment exists
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment {assessment_id} not found"
            )
        
        # Search for candidates (mock implementation)
        search_key = request.company_name.lower().strip()
        candidates_data = MOCK_CANDIDATES.get(search_key, MOCK_CANDIDATES["default"])
        
        # Convert to Pydantic models
        candidates = [CandidateCompany(**c) for c in candidates_data]
        
        # Update assessment
        assessment.company_name = request.company_name
        assessment.location = request.location
        db.commit()
        
        logger.info(f"Identity search for '{request.company_name}': {len(candidates)} candidates found")
        
        return IdentitySearchResponse(
            assessment_id=assessment_id,
            candidates=candidates,
            search_query=request.company_name,
            total_found=len(candidates),
            message=f"Found {len(candidates)} potential matches for '{request.company_name}'"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Identity search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Identity search failed: {str(e)}"
        )


@router.post("/{assessment_id}/confirm", response_model=IdentityConfirmResponse)
async def confirm_identity(
    assessment_id: str,
    request: IdentityConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    Confirm selected company identity.
    Updates assessment with confirmed details and advances to Chapter 2.
    """
    try:
        # Verify assessment exists
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment {assessment_id} not found"
            )
        
        # Find confirmed candidate in mock data
        confirmed_company = None
        for candidates_list in MOCK_CANDIDATES.values():
            for candidate in candidates_list:
                if candidate["id"] == request.selected_id:
                    confirmed_company = CandidateCompany(**candidate)
                    break
            if confirmed_company:
                break
        
        if not confirmed_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate {request.selected_id} not found"
            )
        
        # Update assessment with confirmed details
        assessment.company_name = confirmed_company.name
        assessment.cin = confirmed_company.cin
        assessment.industry = confirmed_company.industry or assessment.industry
        assessment.location = confirmed_company.registered_address
        assessment.website = confirmed_company.website
        assessment.status = "identity_resolved"
        assessment.current_chapter = 2
        db.commit()
        db.refresh(assessment)
        
        logger.info(f"Identity confirmed for {assessment_id}: {confirmed_company.name}")
        
        return IdentityConfirmResponse(
            assessment_id=assessment_id,
            confirmed_company=confirmed_company,
            status=AssessmentStatus.IDENTITY_RESOLVED,
            next_chapter=2,
            message=f"Identity confirmed: {confirmed_company.name}. Ready for Chapter 2: Discovery."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Identity confirmation failed: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Identity confirmation failed: {str(e)}"
        )


@router.get("/{assessment_id}", response_model=dict)
async def get_assessment(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Get assessment details.
    """
    try:
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assessment {assessment_id} not found"
            )
        
        return {
            "assessment_id": assessment.id,
            "company_name": assessment.company_name,
            "cin": assessment.cin,
            "industry": assessment.industry,
            "location": assessment.location,
            "status": assessment.status,
            "current_chapter": assessment.current_chapter,
            "digital_health_score": assessment.digital_health_score,
            "created_at": assessment.created_at.isoformat(),
            "updated_at": assessment.updated_at.isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch assessment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch assessment: {str(e)}"
        )
