"""
Chapter 5: Operations & Team Assessment API

Endpoints for analyzing business operations, team structure, efficiency,
and resource utilization.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List, Any
from database import get_db, Assessment

router = APIRouter()


@router.post("/{assessment_id}/analyze-team")
async def analyze_team(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Analyze team structure, roles, and composition.
    """
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Mock team analysis data
    team_data = {
        "total_employees": 47,
        "departments": [
            {
                "name": "Sales & Marketing",
                "headcount": 18,
                "roles": [
                    {"title": "Sales Manager", "count": 2},
                    {"title": "Sales Executive", "count": 12},
                    {"title": "Marketing Manager", "count": 1},
                    {"title": "Digital Marketing Executive", "count": 3}
                ],
                "avg_experience_years": 3.5,
                "turnover_rate": "12%"
            },
            {
                "name": "Operations",
                "headcount": 15,
                "roles": [
                    {"title": "Operations Manager", "count": 1},
                    {"title": "Supervisor", "count": 3},
                    {"title": "Operator", "count": 11}
                ],
                "avg_experience_years": 5.2,
                "turnover_rate": "8%"
            },
            {
                "name": "Administration",
                "headcount": 8,
                "roles": [
                    {"title": "HR Manager", "count": 1},
                    {"title": "Accountant", "count": 2},
                    {"title": "Admin Staff", "count": 5}
                ],
                "avg_experience_years": 6.1,
                "turnover_rate": "5%"
            },
            {
                "name": "Technology",
                "headcount": 6,
                "roles": [
                    {"title": "IT Manager", "count": 1},
                    {"title": "Developer", "count": 3},
                    {"title": "Support Staff", "count": 2}
                ],
                "avg_experience_years": 4.8,
                "turnover_rate": "15%"
            }
        ],
        "org_structure": {
            "hierarchy_levels": 4,
            "span_of_control": "1:6 average",
            "reporting_clarity": "Good",
            "structure_type": "Functional"
        },
        "team_composition": {
            "permanent": 42,
            "contract": 5,
            "full_time": 45,
            "part_time": 2
        },
        "key_insights": [
            "Healthy span of control with manageable team sizes",
            "High turnover in Tech (15%) - needs attention",
            "Operations team shows good stability (8% turnover)",
            "Sales team is largest department - growth focused"
        ],
        "red_flags": [
            {
                "severity": "medium",
                "issue": "Technology turnover above industry average",
                "impact": "May affect digital transformation initiatives"
            },
            {
                "severity": "low",
                "issue": "Limited mid-level management in Sales",
                "impact": "Could create bottlenecks as team scales"
            }
        ]
    }
    
    return {
        "assessment_id": assessment_id,
        "timestamp": datetime.utcnow().isoformat(),
        "team_analysis": team_data
    }


@router.post("/{assessment_id}/assess-efficiency")
async def assess_efficiency(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Assess operational efficiency metrics and KPIs.
    """
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Mock efficiency metrics
    efficiency_data = {
        "overall_efficiency_score": 72,
        "productivity_metrics": {
            "revenue_per_employee": {
                "value": "₹31.9 Lakhs",
                "benchmark": "₹25-35 Lakhs",
                "status": "Good",
                "percentile": 68
            },
            "order_fulfillment_time": {
                "value": "3.2 days",
                "benchmark": "2-4 days",
                "status": "Good",
                "improvement_potential": "18%"
            },
            "customer_response_time": {
                "value": "4.5 hours",
                "benchmark": "< 6 hours",
                "status": "Good",
                "percentile": 72
            },
            "task_completion_rate": {
                "value": "87%",
                "benchmark": "> 85%",
                "status": "Good"
            }
        },
        "process_efficiency": {
            "automation_level": "32%",
            "manual_processes": 68,
            "automated_processes": 32,
            "bottlenecks_identified": 5,
            "process_documentation": "Partial"
        },
        "resource_utilization": {
            "equipment_utilization": "78%",
            "space_utilization": "82%",
            "inventory_turnover": "6.2x per year",
            "capacity_utilization": "71%"
        },
        "time_management": {
            "on_time_delivery": "89%",
            "avg_project_delay": "2.3 days",
            "meeting_efficiency_score": 65,
            "admin_time_percentage": "18%"
        },
        "efficiency_trends": [
            {
                "metric": "Order Processing Time",
                "change_6m": "-12%",
                "trend": "improving"
            },
            {
                "metric": "Customer Response Time",
                "change_6m": "-8%",
                "trend": "improving"
            },
            {
                "metric": "Revenue per Employee",
                "change_6m": "+15%",
                "trend": "improving"
            }
        ],
        "improvement_opportunities": [
            {
                "area": "Process Automation",
                "potential_impact": "High",
                "estimated_savings": "₹15-20 Lakhs/year",
                "effort": "Medium"
            },
            {
                "area": "Inventory Management",
                "potential_impact": "Medium",
                "estimated_savings": "₹8-12 Lakhs/year",
                "effort": "Low"
            },
            {
                "area": "Meeting Optimization",
                "potential_impact": "Medium",
                "estimated_savings": "15-20 hours/week",
                "effort": "Low"
            }
        ]
    }
    
    return {
        "assessment_id": assessment_id,
        "timestamp": datetime.utcnow().isoformat(),
        "efficiency_assessment": efficiency_data
    }


@router.post("/{assessment_id}/evaluate-processes")
async def evaluate_processes(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Evaluate business processes and workflows.
    """
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Mock process evaluation
    process_data = {
        "core_processes": [
            {
                "name": "Order Management",
                "maturity_level": "Defined",
                "score": 75,
                "steps": 8,
                "avg_cycle_time": "3.2 days",
                "automation": "45%",
                "pain_points": [
                    "Manual data entry in multiple systems",
                    "No real-time inventory sync",
                    "Email-based approvals slow down flow"
                ],
                "recommendations": [
                    "Implement integrated order management system",
                    "Automate approval workflows",
                    "Real-time inventory integration"
                ]
            },
            {
                "name": "Customer Service",
                "maturity_level": "Managed",
                "score": 68,
                "steps": 6,
                "avg_response_time": "4.5 hours",
                "automation": "25%",
                "pain_points": [
                    "No unified customer view",
                    "Manual ticket routing",
                    "Limited self-service options"
                ],
                "recommendations": [
                    "Implement CRM with 360° customer view",
                    "Add chatbot for common queries",
                    "Create knowledge base for self-service"
                ]
            },
            {
                "name": "Financial Reconciliation",
                "maturity_level": "Optimizing",
                "score": 82,
                "steps": 5,
                "automation": "65%",
                "frequency": "Daily",
                "pain_points": [
                    "Some manual data entry still required"
                ],
                "recommendations": [
                    "Eliminate remaining manual steps",
                    "Add exception handling automation"
                ]
            },
            {
                "name": "Inventory Management",
                "maturity_level": "Defined",
                "score": 70,
                "automation": "40%",
                "pain_points": [
                    "Stock counts partially manual",
                    "Reorder points not automated",
                    "Multiple spreadsheets in use"
                ],
                "recommendations": [
                    "Implement automated reorder system",
                    "RFID/barcode scanning for stock counts",
                    "Centralized inventory management system"
                ]
            }
        ],
        "process_maturity": {
            "overall_level": "Defined",
            "description": "Processes are documented and standardized but not fully optimized",
            "maturity_distribution": {
                "ad_hoc": 0,
                "defined": 6,
                "managed": 3,
                "optimizing": 2,
                "continuous_improvement": 0
            }
        },
        "documentation_status": {
            "processes_documented": 11,
            "total_processes": 15,
            "documentation_quality": "Good",
            "last_updated": "6 months ago",
            "sop_availability": "73%"
        },
        "workflow_analysis": {
            "handoffs_per_process": 4.2,
            "avg_wait_time": "6.5 hours",
            "rework_rate": "8%",
            "process_exceptions": "12% of transactions"
        }
    }
    
    return {
        "assessment_id": assessment_id,
        "timestamp": datetime.utcnow().isoformat(),
        "process_evaluation": process_data
    }


@router.post("/{assessment_id}/check-resources")
async def check_resources(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Check resource allocation and utilization.
    """
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Mock resource data
    resource_data = {
        "human_resources": {
            "total_employees": 47,
            "utilization_rate": "76%",
            "skill_gaps": [
                {
                    "area": "Digital Marketing",
                    "current_capacity": "2 specialists",
                    "required_capacity": "4 specialists",
                    "gap": "50%",
                    "priority": "High"
                },
                {
                    "area": "Data Analytics",
                    "current_capacity": "1 analyst",
                    "required_capacity": "2 analysts",
                    "gap": "50%",
                    "priority": "Medium"
                },
                {
                    "area": "Automation/RPA",
                    "current_capacity": "None",
                    "required_capacity": "1 specialist",
                    "gap": "100%",
                    "priority": "Medium"
                }
            ],
            "training_budget": "₹3.5 Lakhs/year",
            "training_hours": "24 hours/employee/year"
        },
        "technology_resources": {
            "it_spend": "₹18 Lakhs/year",
            "it_spend_percentage": "1.2% of revenue",
            "benchmark": "2-3% for growth companies",
            "systems": [
                {
                    "category": "ERP/Accounting",
                    "solution": "Tally Prime",
                    "utilization": "High",
                    "age": "2 years",
                    "status": "Good"
                },
                {
                    "category": "CRM",
                    "solution": "Spreadsheets",
                    "utilization": "Medium",
                    "status": "Needs Upgrade",
                    "recommendation": "Implement proper CRM (Zoho/Salesforce)"
                },
                {
                    "category": "Collaboration",
                    "solution": "Google Workspace",
                    "utilization": "High",
                    "status": "Good"
                },
                {
                    "category": "Project Management",
                    "solution": "Trello",
                    "utilization": "Medium",
                    "status": "Fair"
                }
            ],
            "infrastructure": {
                "cloud_adoption": "45%",
                "legacy_systems": 3,
                "security_tools": "Basic",
                "backup_strategy": "Weekly"
            }
        },
        "physical_resources": {
            "office_space": "3,500 sq ft",
            "space_per_employee": "74 sq ft",
            "benchmark": "75-100 sq ft/employee",
            "utilization": "82%",
            "equipment": {
                "computers": 42,
                "condition": "Good (avg 2.5 years old)",
                "replacement_cycle": "4 years"
            },
            "facilities": [
                "Meeting rooms: 2",
                "Parking: 15 slots",
                "Cafeteria: Yes",
                "Storage: 500 sq ft"
            ]
        },
        "financial_resources": {
            "working_capital": "₹45 Lakhs",
            "working_capital_days": 42,
            "credit_lines": "₹25 Lakhs available",
            "cash_reserves": "₹18 Lakhs",
            "burn_rate": "Positive cash flow",
            "capex_budget": "₹12 Lakhs/year"
        },
        "resource_optimization": [
            {
                "resource": "IT Budget",
                "current_allocation": "1.2% of revenue",
                "recommended": "2-2.5% of revenue",
                "action": "Increase IT investments for automation"
            },
            {
                "resource": "Training Budget",
                "current_allocation": "₹3.5 Lakhs",
                "recommended": "₹5-6 Lakhs",
                "action": "Invest in upskilling digital capabilities"
            },
            {
                "resource": "Office Space",
                "status": "Near capacity",
                "action": "Plan for expansion or hybrid work model"
            }
        ]
    }
    
    return {
        "assessment_id": assessment_id,
        "timestamp": datetime.utcnow().isoformat(),
        "resource_analysis": resource_data
    }


@router.post("/{assessment_id}/operations-score")
async def operations_score(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """
    Calculate overall operations and team score.
    """
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    # Mock comprehensive operations score
    score_data = {
        "overall_score": 74,
        "grade": "B",
        "operations_health": "Good",
        "component_scores": {
            "team_structure": 78,
            "operational_efficiency": 72,
            "process_maturity": 70,
            "resource_utilization": 76,
            "leadership_effectiveness": 75
        },
        "strengths": [
            "Strong team stability in core operations (8% turnover)",
            "Good revenue per employee (₹31.9L vs ₹25-35L benchmark)",
            "Financial processes well-automated (65%)",
            "Adequate working capital and cash reserves"
        ],
        "weaknesses": [
            "High tech team turnover (15%) affecting digital initiatives",
            "Limited process automation (32% overall)",
            "IT spend below industry benchmark (1.2% vs 2-3%)",
            "Manual processes in customer service and inventory"
        ],
        "opportunities": [
            {
                "area": "Process Automation",
                "impact": "High",
                "potential_savings": "₹15-20 Lakhs/year",
                "timeline": "6-9 months"
            },
            {
                "area": "CRM Implementation",
                "impact": "High",
                "potential_improvement": "25% in customer satisfaction",
                "timeline": "3-4 months"
            },
            {
                "area": "Team Upskilling",
                "impact": "Medium",
                "focus": "Digital marketing and data analytics",
                "timeline": "Ongoing"
            }
        ],
        "action_items": [
            {
                "priority": "high",
                "action": "Implement CRM system with 360° customer view",
                "estimated_cost": "₹5-8 Lakhs",
                "timeline": "Q1 2025",
                "expected_benefit": "Improved customer retention and sales efficiency"
            },
            {
                "priority": "high",
                "action": "Automate order management and inventory processes",
                "estimated_cost": "₹8-12 Lakhs",
                "timeline": "Q1-Q2 2025",
                "expected_benefit": "₹15-20L/year savings + faster fulfillment"
            },
            {
                "priority": "medium",
                "action": "Address tech team turnover through retention initiatives",
                "estimated_cost": "₹3-5 Lakhs",
                "timeline": "Immediate",
                "expected_benefit": "Reduced hiring costs, improved continuity"
            },
            {
                "priority": "medium",
                "action": "Increase IT budget to 2% of revenue",
                "estimated_cost": "₹12 Lakhs additional",
                "timeline": "FY 2025-26",
                "expected_benefit": "Better tools and infrastructure"
            },
            {
                "priority": "low",
                "action": "Update process documentation and SOPs",
                "estimated_cost": "₹1-2 Lakhs",
                "timeline": "Q2 2025",
                "expected_benefit": "Improved onboarding and consistency"
            }
        ],
        "operations_manager_verdict": "The business demonstrates good operational fundamentals with stable teams and healthy efficiency metrics. Key focus areas should be increasing automation (currently only 32%) and modernizing technology infrastructure. The tech team turnover is a concern that needs immediate attention. With targeted investments in CRM, automation, and process optimization, operations could easily move from 'Good' (74/100) to 'Excellent' (85+) within 12-18 months.",
        "benchmark_comparison": {
            "revenue_per_employee": {
                "value": "₹31.9L",
                "industry_avg": "₹28L",
                "percentile": 68,
                "status": "Above Average"
            },
            "automation_level": {
                "value": "32%",
                "industry_avg": "45%",
                "percentile": 35,
                "status": "Below Average"
            },
            "employee_turnover": {
                "value": "10.5%",
                "industry_avg": "12%",
                "percentile": 62,
                "status": "Average"
            },
            "process_maturity": {
                "level": "Defined",
                "industry_benchmark": "Managed",
                "status": "Slightly Below"
            }
        }
    }
    
    # Update assessment progress
    assessment.current_chapter = 6
    db.commit()
    
    return {
        "assessment_id": assessment_id,
        "timestamp": datetime.utcnow().isoformat(),
        "operations_score": score_data,
        "next_chapter": 6
    }
