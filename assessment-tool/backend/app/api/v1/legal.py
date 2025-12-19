"""
Chapter 4: Legal & Compliance APIs
The Lawyer persona verifies legal standing and compliance
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from database import get_db, Assessment

router = APIRouter()


@router.post("/{assessment_id}/verify-registration")
async def verify_registration(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Verify company registration and legal entity status
    TODO: Integrate with MCA API for real verification
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )
    
    # Mock registration data
    mock_registration = {
        "company_name": assessment.company_name or "Example Corp Pvt Ltd",
        "cin": assessment.cin or "U74999MH2015PTC268901",
        "registration_date": "2015-03-15",
        "company_type": "Private Limited Company",
        "registered_office": "Mumbai, Maharashtra, India",
        "authorized_capital": 10000000,  # ₹1 Cr
        "paid_up_capital": 5000000,  # ₹50 Lakhs
        "registration_status": "Active",
        "roc": "RoC-Mumbai",
        "directors": [
            {
                "name": "Rajesh Kumar",
                "din": "08123456",
                "appointment_date": "2015-03-15",
                "designation": "Managing Director"
            },
            {
                "name": "Priya Sharma",
                "din": "08234567",
                "appointment_date": "2015-03-15",
                "designation": "Director"
            }
        ],
        "verification_status": "verified",
        "verification_date": "2024-12-19"
    }
    
    return {
        "assessment_id": assessment_id,
        "registration_data": mock_registration,
        "message": "Company registration verified (mock data)"
    }


@router.post("/{assessment_id}/analyze-compliance")
async def analyze_compliance(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Analyze regulatory compliance across various domains
    TODO: Integrate with compliance databases
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )
    
    # Mock compliance analysis
    mock_compliance = {
        "overall_compliance": 82,  # out of 100
        "compliance_areas": {
            "corporate_governance": {
                "score": 85,
                "status": "compliant",
                "items_checked": 12,
                "items_passed": 10,
                "last_audit": "2024-09-15"
            },
            "tax_compliance": {
                "score": 88,
                "status": "compliant",
                "items_checked": 15,
                "items_passed": 13,
                "filings_status": {
                    "gst_returns": "up_to_date",
                    "income_tax": "filed",
                    "tds_returns": "up_to_date"
                }
            },
            "labor_laws": {
                "score": 75,
                "status": "partially_compliant",
                "items_checked": 10,
                "items_passed": 7,
                "issues": [
                    "PF registration needs update",
                    "ESI coverage incomplete",
                    "Minimum wages compliance under review"
                ]
            },
            "data_privacy": {
                "score": 70,
                "status": "needs_improvement",
                "items_checked": 8,
                "items_passed": 5,
                "requirements": [
                    "GDPR compliance not applicable",
                    "DPDPA compliance in progress",
                    "Privacy policy needs update"
                ]
            },
            "industry_specific": {
                "score": 90,
                "status": "compliant",
                "items_checked": 6,
                "items_passed": 5,
                "licenses_valid": True
            }
        },
        "red_flags": [
            {
                "severity": "medium",
                "category": "labor_laws",
                "issue": "PF registration address mismatch",
                "recommendation": "Update registered address with EPFO"
            },
            {
                "severity": "low",
                "category": "data_privacy",
                "issue": "Privacy policy last updated 2 years ago",
                "recommendation": "Review and update privacy policy to align with DPDPA"
            }
        ],
        "recent_changes": [
            "Updated GST registration (Oct 2024)",
            "Renewed FSSAI license (Sep 2024)"
        ]
    }
    
    return {
        "assessment_id": assessment_id,
        "compliance_analysis": mock_compliance,
        "message": "Compliance analysis complete (mock data)"
    }


@router.post("/{assessment_id}/check-licenses")
async def check_licenses(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Check status of business licenses and permits
    TODO: Integrate with license verification APIs
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )
    
    # Mock license data
    mock_licenses = {
        "total_licenses": 8,
        "active_licenses": 7,
        "expired_licenses": 0,
        "expiring_soon": 1,
        "licenses": [
            {
                "name": "GST Registration",
                "number": "27AABCU9603R1ZM",
                "type": "tax",
                "status": "active",
                "issue_date": "2015-07-01",
                "expiry_date": "permanent",
                "issuing_authority": "GSTN"
            },
            {
                "name": "FSSAI License",
                "number": "12345678901234",
                "type": "food_safety",
                "status": "active",
                "issue_date": "2023-09-15",
                "expiry_date": "2025-09-14",
                "days_until_expiry": 269,
                "issuing_authority": "FSSAI"
            },
            {
                "name": "Trade License",
                "number": "TL/2015/12345",
                "type": "municipal",
                "status": "active",
                "issue_date": "2015-04-01",
                "expiry_date": "2025-03-31",
                "days_until_expiry": 102,
                "issuing_authority": "Municipal Corporation"
            },
            {
                "name": "Shops & Establishment Act",
                "number": "SE/2015/98765",
                "type": "labor",
                "status": "active",
                "issue_date": "2015-05-01",
                "expiry_date": "permanent",
                "issuing_authority": "Labor Department"
            },
            {
                "name": "Fire Safety Certificate",
                "number": "FSC/2024/456",
                "type": "safety",
                "status": "active",
                "issue_date": "2024-01-15",
                "expiry_date": "2025-01-14",
                "days_until_expiry": 26,
                "issuing_authority": "Fire Department"
            },
            {
                "name": "Pollution Control Certificate",
                "number": "PCC/2023/789",
                "type": "environmental",
                "status": "active",
                "issue_date": "2023-06-01",
                "expiry_date": "2025-05-31",
                "days_until_expiry": 163,
                "issuing_authority": "Pollution Control Board"
            },
            {
                "name": "Import Export Code (IEC)",
                "number": "0515987654",
                "type": "trade",
                "status": "active",
                "issue_date": "2016-08-20",
                "expiry_date": "permanent",
                "issuing_authority": "DGFT"
            },
            {
                "name": "Professional Tax Registration",
                "number": "PT/MH/2015/12345",
                "type": "tax",
                "status": "active",
                "issue_date": "2015-04-01",
                "expiry_date": "2025-03-31",
                "days_until_expiry": 102,
                "issuing_authority": "State Tax Department"
            }
        ],
        "renewal_alerts": [
            {
                "license": "Fire Safety Certificate",
                "days_remaining": 26,
                "urgency": "high",
                "action_required": "Start renewal process immediately"
            },
            {
                "license": "Trade License",
                "days_remaining": 102,
                "urgency": "medium",
                "action_required": "Plan renewal in next 60 days"
            }
        ]
    }
    
    return {
        "assessment_id": assessment_id,
        "license_data": mock_licenses,
        "message": "License verification complete (mock data)"
    }


@router.post("/{assessment_id}/check-legal-disputes")
async def check_legal_disputes(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Check for pending legal disputes and litigation
    TODO: Integrate with court databases
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )
    
    # Mock legal disputes data
    mock_disputes = {
        "total_cases": 2,
        "active_cases": 1,
        "closed_cases": 1,
        "cases": [
            {
                "case_number": "CS/2023/12345",
                "case_type": "commercial_dispute",
                "status": "active",
                "court": "Bombay High Court",
                "filed_date": "2023-05-15",
                "parties": {
                    "plaintiff": "ABC Suppliers Pvt Ltd",
                    "defendant": assessment.company_name or "Example Corp"
                },
                "claim_amount": 2500000,  # ₹25 Lakhs
                "description": "Payment dispute for supplies delivered",
                "next_hearing": "2025-01-20",
                "severity": "medium"
            },
            {
                "case_number": "LC/2022/67890",
                "case_type": "labor_dispute",
                "status": "closed",
                "court": "Labor Court, Mumbai",
                "filed_date": "2022-08-10",
                "closed_date": "2024-03-15",
                "parties": {
                    "plaintiff": "Former Employee",
                    "defendant": assessment.company_name or "Example Corp"
                },
                "claim_amount": 450000,  # ₹4.5 Lakhs
                "description": "Wrongful termination claim",
                "resolution": "Settled out of court",
                "severity": "low"
            }
        ],
        "risk_assessment": {
            "overall_risk": "low",
            "financial_exposure": 2500000,
            "litigation_history": "minimal",
            "resolution_rate": "100%"  # 1 out of 1 closed cases resolved
        }
    }
    
    return {
        "assessment_id": assessment_id,
        "legal_disputes": mock_disputes,
        "message": "Legal dispute check complete (mock data)"
    }


@router.post("/{assessment_id}/legal-score")
async def calculate_legal_score(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Calculate overall legal health score
    The Lawyer's final verdict
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )
    
    # Mock comprehensive legal score
    mock_score = {
        "overall_score": 78,
        "grade": "B",
        "legal_health": "Good",
        "percentile": 72,
        "component_scores": {
            "registration_validity": 95,
            "compliance_status": 82,
            "license_management": 85,
            "dispute_history": 70,
            "documentation": 75
        },
        "strengths": [
            "Strong corporate governance framework",
            "Excellent tax compliance record",
            "All critical licenses active and up-to-date",
            "Minimal litigation history"
        ],
        "weaknesses": [
            "Some labor law compliance gaps",
            "Data privacy policy needs update",
            "One active commercial dispute pending",
            "Fire safety certificate expiring soon"
        ],
        "lawyer_verdict": {
            "summary": "Legally sound entity with minor compliance gaps",
            "investment_risk": "Low",
            "due_diligence_rating": "Pass",
            "key_recommendation": "Address labor law compliance issues and renew expiring licenses"
        },
        "action_items": [
            {
                "priority": "high",
                "item": "Renew fire safety certificate (26 days remaining)",
                "timeline": "Immediate"
            },
            {
                "priority": "medium",
                "item": "Update PF registration address",
                "timeline": "30 days"
            },
            {
                "priority": "medium",
                "item": "Resolve pending commercial dispute",
                "timeline": "60 days"
            },
            {
                "priority": "low",
                "item": "Update privacy policy for DPDPA compliance",
                "timeline": "90 days"
            }
        ],
        "benchmarks": {
            "industry_average_score": 70,
            "top_quartile_score": 88,
            "your_position": "Above Average"
        }
    }
    
    # Update assessment in database
    assessment.current_chapter = 5
    db.commit()
    
    return {
        "assessment_id": assessment_id,
        "legal_score": mock_score,
        "next_chapter": 5,
        "message": "Legal score calculated (mock data)"
    }
