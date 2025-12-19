"""
Chapter 3: The Money Story (Financial Analysis)
CFO Persona - Analyzes financial health and generates scores
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
import sys
sys.path.append('..')

from database import get_db, Assessment

router = APIRouter(tags=["Chapter 3: Money Story"])


@router.post("/{assessment_id}/analyze-revenue")
async def analyze_revenue(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Analyze revenue patterns and trends
    CFO persona analyzes the money story
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )
    
    # TODO: Integrate with real financial APIs (MCA, GST)
    # For now, generate realistic mock data
    
    # Simulate revenue analysis
    mock_revenue = {
        "avg_monthly": 1250000,  # 12.5 lakhs
        "annual_revenue": {
            "current_year": 15000000,  # 1.5 Cr
            "previous_year": 12000000,  # 1.2 Cr
            "growth_rate": 25.0,
            "currency": "INR"
        },
        "growth_trend": "increasing",
        "revenue_breakdown": {
            "product_sales": 60,
            "service_revenue": 30,
            "other_income": 10
        },
        "monthly_trends": [
            {"month": "Jan", "revenue": 1100000},
            {"month": "Feb", "revenue": 1200000},
            {"month": "Mar", "revenue": 1300000},
            {"month": "Apr", "revenue": 1250000},
            {"month": "May", "revenue": 1400000},
            {"month": "Jun", "revenue": 1350000},
            {"month": "Jul", "revenue": 1450000},
            {"month": "Aug", "revenue": 1500000},
            {"month": "Sep", "revenue": 1550000},
            {"month": "Oct", "revenue": 1600000},
            {"month": "Nov", "revenue": 1650000},
            {"month": "Dec", "revenue": 1700000}
        ],
        "seasonality": {
            "peak_months": ["Nov", "Dec", "Jan"],
            "low_months": ["May", "Jun", "Jul"],
            "seasonal_factor": 1.35
        }
    }
    
    return {
        "assessment_id": assessment_id,
        "revenue_analysis": mock_revenue,
        "message": "Revenue analysis complete (mock data)"
    }


@router.post("/{assessment_id}/analyze-expenses")
async def analyze_expenses(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Analyze expense patterns and cost structure
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )
    
    # Mock expense data
    mock_expenses = {
        "avg_monthly": 916667,  # ~9.17 lakhs
        "total_annual_expenses": 11000000,  # 1.1 Cr
        "expense_breakdown": {
            "staff_costs": 45,
            "marketing": 15,
            "operations": 20,
            "technology": 8,
            "rent": 7,
            "other": 5
        },
        "monthly_burn_rate": 916667,
        "cost_per_sale": 733,
        "efficiency_metrics": {
            "gross_margin": 40,
            "operating_margin": 27,
            "net_margin": 22
        },
        "areas_of_concern": [
            "Marketing ROI below industry average",
            "Technology spending could be optimized"
        ]
    }
    
    return {
        "assessment_id": assessment_id,
        "expense_analysis": mock_expenses,
        "message": "Expense analysis complete (mock data)"
    }


@router.post("/{assessment_id}/analyze-cash-flow")
async def analyze_cash_flow(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Analyze cash flow and liquidity
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )
    
    # Mock cash flow data
    mock_cashflow = {
        "current_cash_balance": 3500000,
        "runway_months": 3.8,
        "operating_cash_flow": {
            "inflows": 15000000,
            "outflows": 11000000,
            "net_operating_cashflow": 4000000
        },
        "working_capital": {
            "current_assets": 5000000,
            "current_liabilities": 2000000,
            "working_capital": 3000000,
            "current_ratio": 2.5
        },
        "cash_conversion_cycle": {
            "days_sales_outstanding": 45,
            "days_inventory_outstanding": 30,
            "days_payables_outstanding": 35,
            "ccc_days": 40
        },
        "liquidity_score": 78,
        "health_status": "healthy"
    }
    
    return {
        "assessment_id": assessment_id,
        "cash_flow_analysis": mock_cashflow,
        "message": "Cash flow analysis complete (mock data)"
    }


@router.post("/{assessment_id}/analyze-debt")
async def analyze_debt(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Analyze debt structure and obligations
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )
    
    # Mock debt data
    mock_debt = {
        "total_debt": 2500000,
        "debt_breakdown": [
            {
                "type": "Term Loan",
                "amount": 1500000,
                "interest_rate": 12.5,
                "monthly_emi": 45000,
                "remaining_tenure_months": 36
            },
            {
                "type": "Working Capital",
                "amount": 1000000,
                "interest_rate": 14.0,
                "monthly_interest": 11667,
                "credit_limit": 1500000
            }
        ],
        "debt_ratios": {
            "debt_to_equity": 0.35,
            "debt_to_revenue": 0.17,
            "interest_coverage_ratio": 7.2
        },
        "credit_score": 720,
        "debt_health": "good",
        "recommendations": [
            "Consider refinancing term loan at lower rate",
            "Maintain current debt-to-equity ratio"
        ]
    }
    
    return {
        "assessment_id": assessment_id,
        "debt_analysis": mock_debt,
        "message": "Debt analysis complete (mock data)"
    }


@router.post("/{assessment_id}/financial-score")
async def calculate_financial_score(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Calculate overall financial health score
    CFO's final verdict
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )
    
    # Mock comprehensive financial score
    mock_score = {
        "overall_score": 73,
        "health_level": "Good",
        "grade": "B",
        "percentile": 68,
        "component_scores": {
            "revenue_growth": 85,
            "profitability": 72,
            "cash_flow": 78,
            "debt_management": 65,
            "financial_stability": 70
        },
        "strengths": [
            "Strong revenue growth (25% YoY)",
            "Healthy cash flow and liquidity",
            "Good profit margins",
            "Low debt-to-equity ratio"
        ],
        "weaknesses": [
            "Limited runway (3.8 months)",
            "High customer acquisition cost",
            "Seasonal revenue fluctuations"
        ],
        "cfo_verdict": {
            "summary": "Financially healthy with strong growth trajectory",
            "investment_readiness": "Ready for Series A",
            "risk_level": "Medium",
            "key_recommendation": "Extend runway to 12 months before major expansion"
        },
        "benchmarks": {
            "industry_average_score": 65,
            "top_quartile_score": 85,
            "your_position": "Above Average"
        }
    }
    
    # Update assessment in database
    assessment.financial_health_score = mock_score["overall_score"]
    assessment.current_chapter = 4
    db.commit()
    
    return {
        "assessment_id": assessment_id,
        "financial_score": mock_score,
        "next_chapter": 4,
        "message": "Financial analysis complete. Ready for Chapter 4: The Mirror"
    }


@router.get("/{assessment_id}/investment-readiness")
async def check_investment_readiness(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Assess readiness for external investment
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )
    
    # Mock investment readiness analysis
    mock_readiness = {
        "readiness_score": 76,
        "stage": "Series A Ready",
        "estimated_valuation_range": {
            "min": 50000000,
            "max": 80000000,
            "currency": "INR"
        },
        "recommended_raise_amount": {
            "amount": 15000000,
            "currency": "INR",
            "reasoning": "18-month runway + expansion capital"
        },
        "investor_appeal": {
            "growth_story": "strong",
            "unit_economics": "good",
            "market_size": "large",
            "team_strength": "strong",
            "traction": "proven"
        },
        "preparation_needed": [
            "Update financial projections for 3 years",
            "Prepare detailed use of funds",
            "Strengthen governance and board",
            "Document key processes and SOPs"
        ],
        "timeline_to_raise": "3-6 months"
    }
    
    return {
        "assessment_id": assessment_id,
        "investment_readiness": mock_readiness,
        "message": "Investment readiness assessment complete"
    }
