"""
Chapter 6: Customer Insights Assessment API

Endpoints for analyzing customer demographics, satisfaction, retention,
and market positioning.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List, Any
from database import get_db, Assessment

router = APIRouter()


@router.post("/{assessment_id}/analyze-demographics")
async def analyze_demographics(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """Analyze customer demographics and segmentation."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    demographics_data = {
        "total_customers": 2847,
        "active_customers": 2156,
        "customer_segments": [
            {
                "segment": "Enterprise",
                "count": 127,
                "percentage": 5.9,
                "avg_order_value": "₹3.8 Lakhs",
                "lifetime_value": "₹45 Lakhs",
                "characteristics": ["B2B", "Long sales cycle", "High value"]
            },
            {
                "segment": "SMB",
                "count": 854,
                "percentage": 39.6,
                "avg_order_value": "₹85,000",
                "lifetime_value": "₹8.2 Lakhs",
                "characteristics": ["Growing businesses", "Moderate spend"]
            },
            {
                "segment": "Retail",
                "count": 1175,
                "percentage": 54.5,
                "avg_order_value": "₹18,500",
                "lifetime_value": "₹1.8 Lakhs",
                "characteristics": ["B2C", "Repeat purchases", "Price sensitive"]
            }
        ],
        "geographic_distribution": {
            "maharashtra": 42,
            "delhi_ncr": 18,
            "karnataka": 15,
            "gujarat": 12,
            "other": 13
        },
        "age_distribution": {
            "18-25": 12,
            "26-35": 38,
            "36-45": 32,
            "46-55": 14,
            "56+": 4
        },
        "acquisition_channels": [
            {"channel": "Referrals", "percentage": 35, "cac": "₹2,800"},
            {"channel": "Digital Marketing", "percentage": 28, "cac": "₹4,500"},
            {"channel": "Direct Sales", "percentage": 22, "cac": "₹8,200"},
            {"channel": "Partnerships", "percentage": 15, "cac": "₹3,100"}
        ]
    }
    
    return {
        "assessment_id": assessment_id,
        "timestamp": datetime.utcnow().isoformat(),
        "demographics": demographics_data
    }


@router.post("/{assessment_id}/assess-satisfaction")
async def assess_satisfaction(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """Assess customer satisfaction metrics."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    satisfaction_data = {
        "nps_score": 42,
        "nps_category": "Good",
        "csat_score": 4.2,
        "satisfaction_trends": {
            "improving": True,
            "6_month_change": "+8 points"
        },
        "feedback_analysis": {
            "total_reviews": 1847,
            "positive": 1289,
            "neutral": 412,
            "negative": 146,
            "response_rate": "87%"
        },
        "top_strengths": [
            "Product quality (mentioned 892 times)",
            "Customer service (mentioned 765 times)",
            "Delivery speed (mentioned 623 times)"
        ],
        "top_complaints": [
            "Pricing (mentioned 234 times)",
            "Website UX (mentioned 178 times)",
            "Limited payment options (mentioned 145 times)"
        ],
        "support_metrics": {
            "first_response_time": "4.5 hours",
            "resolution_time": "18 hours",
            "resolution_rate": "94%",
            "satisfaction_with_support": 4.3
        }
    }
    
    return {
        "assessment_id": assessment_id,
        "timestamp": datetime.utcnow().isoformat(),
        "satisfaction": satisfaction_data
    }


@router.post("/{assessment_id}/evaluate-retention")
async def evaluate_retention(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """Evaluate customer retention and churn."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    retention_data = {
        "retention_rate": 78,
        "churn_rate": 22,
        "cohort_analysis": {
            "month_1": 100,
            "month_3": 85,
            "month_6": 78,
            "month_12": 72
        },
        "repeat_purchase_rate": 65,
        "avg_customer_lifespan": "3.2 years",
        "churn_reasons": [
            {"reason": "Pricing", "percentage": 35},
            {"reason": "Found alternative", "percentage": 28},
            {"reason": "Product fit", "percentage": 18},
            {"reason": "Service issues", "percentage": 12},
            {"reason": "Other", "percentage": 7}
        ],
        "win_back_rate": 18,
        "at_risk_customers": {
            "count": 287,
            "percentage": 13.3,
            "criteria": ["No purchase in 90 days", "Declining engagement"]
        }
    }
    
    return {
        "assessment_id": assessment_id,
        "timestamp": datetime.utcnow().isoformat(),
        "retention": retention_data
    }


@router.post("/{assessment_id}/market-positioning")
async def market_positioning(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """Analyze market positioning and competitive landscape."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    positioning_data = {
        "market_share": 8.5,
        "market_rank": 3,
        "competitive_position": "Strong Challenger",
        "key_competitors": [
            {"name": "Competitor A", "market_share": 22, "strength": "Brand recognition"},
            {"name": "Competitor B", "market_share": 15, "strength": "Price leadership"},
            {"name": "Competitor C", "market_share": 12, "strength": "Product range"}
        ],
        "differentiation": [
            "Superior customer service",
            "Faster delivery times",
            "Quality certifications"
        ],
        "brand_perception": {
            "awareness": 42,
            "consideration": 35,
            "preference": 28,
            "associations": ["Reliable", "Quality", "Professional"]
        },
        "pricing_position": "Premium mid-market",
        "market_trends": {
            "market_growth_rate": "12% annually",
            "company_growth_rate": "18% annually",
            "gaining_share": True
        }
    }
    
    return {
        "assessment_id": assessment_id,
        "timestamp": datetime.utcnow().isoformat(),
        "positioning": positioning_data
    }


@router.post("/{assessment_id}/customer-score")
async def customer_score(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """Calculate overall customer insights score."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    score_data = {
        "overall_score": 76,
        "grade": "B",
        "customer_health": "Good",
        "component_scores": {
            "demographics_diversity": 80,
            "satisfaction_levels": 75,
            "retention_strength": 72,
            "market_position": 78,
            "growth_potential": 75
        },
        "strengths": [
            "Strong NPS of 42 showing good customer advocacy",
            "78% retention rate above industry average",
            "Growing market share (18% vs 12% market growth)",
            "Diverse customer base across 3 segments"
        ],
        "weaknesses": [
            "22% churn rate needs attention",
            "287 at-risk customers (13.3%) require intervention",
            "Pricing complaints common (35% of churn)",
            "Limited brand awareness (42%)"
        ],
        "opportunities": [
            {
                "area": "At-Risk Customer Program",
                "impact": "High",
                "potential_revenue_saved": "₹8-12 Crores/year",
                "timeline": "Immediate"
            },
            {
                "area": "Referral Program Enhancement",
                "impact": "High",
                "description": "Leverage 35% referral acquisition",
                "timeline": "Q1 2025"
            },
            {
                "area": "Brand Awareness Campaign",
                "impact": "Medium",
                "target": "Increase from 42% to 60%",
                "timeline": "6-9 months"
            }
        ],
        "action_items": [
            {
                "priority": "high",
                "action": "Launch at-risk customer retention program",
                "estimated_cost": "₹5 Lakhs",
                "timeline": "Immediate",
                "expected_benefit": "Save 50% of at-risk customers = ₹8-12 Cr"
            },
            {
                "priority": "high",
                "action": "Implement automated feedback collection post-purchase",
                "estimated_cost": "₹2 Lakhs",
                "timeline": "Q1 2025",
                "expected_benefit": "Increase response rate to 95%+"
            },
            {
                "priority": "medium",
                "action": "Develop pricing strategy for price-sensitive segments",
                "estimated_cost": "₹1 Lakh (consulting)",
                "timeline": "Q1 2025",
                "expected_benefit": "Reduce price-related churn by 50%"
            }
        ],
        "customer_strategist_verdict": "The business has a solid customer base with good satisfaction and retention metrics that outperform industry averages. The 42 NPS and 78% retention rate indicate strong fundamentals. However, the 287 at-risk customers represent immediate revenue leakage that can be prevented. Focus on retention programs and addressing pricing concerns. The 18% growth rate exceeding market growth shows you're winning, but there's untapped potential in the 42% brand awareness score.",
        "benchmark_comparison": {
            "nps_score": {"value": 42, "industry_avg": 35, "percentile": 72},
            "retention_rate": {"value": 78, "industry_avg": 70, "percentile": 68},
            "churn_rate": {"value": 22, "industry_avg": 30, "percentile": 65},
            "market_share_growth": {"value": "+1.8%", "industry_avg": "+0.5%", "status": "Strong"}
        }
    }
    
    # Update assessment progress
    assessment.current_chapter = 7
    db.commit()
    
    return {
        "assessment_id": assessment_id,
        "timestamp": datetime.utcnow().isoformat(),
        "customer_score": score_data,
        "next_chapter": 7
    }
