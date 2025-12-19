"""
Admin API endpoints for managing the assessment system
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List
import sys
sys.path.append('..')

from database import get_db, Assessment
from app.utils.database_utils import DatabaseUtils
from app.utils.performance import monitor

router = APIRouter(prefix="/admin", tags=["Admin"])

# Simple API key auth (enhance with proper auth in production)
async def verify_admin_key(api_key: str = None):
    """Verify admin API key"""
    # TODO: Replace with proper authentication
    if api_key != "admin-secret-key-change-me":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key"
        )


@router.get("/stats/overview")
async def get_system_stats(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_admin_key)
):
    """Get system-wide statistics"""
    
    # Database stats
    total = db.query(func.count(Assessment.id)).scalar()
    
    by_status = db.query(
        Assessment.status,
        func.count(Assessment.id)
    ).group_by(Assessment.status).all()
    
    by_industry = db.query(
        Assessment.industry,
        func.count(Assessment.id)
    ).group_by(Assessment.industry).all()
    
    recent = db.query(func.count(Assessment.id)).filter(
        Assessment.created_at >= func.datetime('now', '-7 days')
    ).scalar()
    
    return {
        "total_assessments": total,
        "by_status": {status: count for status, count in by_status},
        "by_industry": {industry: count for industry, count in by_industry},
        "last_7_days": recent,
        "performance": monitor.get_stats()
    }


@router.get("/assessments/list")
async def list_assessments(
    skip: int = 0,
    limit: int = 50,
    status: str = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_admin_key)
):
    """List all assessments with pagination"""
    query = db.query(Assessment)
    
    if status:
        query = query.filter(Assessment.status == status)
    
    total = query.count()
    assessments = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "assessments": [
            {
                "id": a.id,
                "company_name": a.company_name,
                "industry": a.industry,
                "status": a.status,
                "current_chapter": a.current_chapter,
                "created_at": a.created_at.isoformat(),
                "digital_health_score": a.digital_health_score
            }
            for a in assessments
        ]
    }


@router.post("/database/backup")
async def create_backup(api_key: str = Depends(verify_admin_key)):
    """Create a database backup"""
    utils = DatabaseUtils()
    backup_file = utils.backup_database()
    
    return {
        "message": "Backup created successfully",
        "file": backup_file
    }


@router.post("/database/export")
async def export_data(
    format: str = "json",
    api_key: str = Depends(verify_admin_key)
):
    """Export assessment data"""
    utils = DatabaseUtils()
    
    if format == "json":
        file = utils.export_to_json()
    elif format == "csv":
        file = utils.export_to_csv()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'json' or 'csv'"
        )
    
    return {
        "message": f"Data exported successfully as {format}",
        "file": file
    }


@router.get("/performance/metrics")
async def get_performance_metrics(api_key: str = Depends(verify_admin_key)):
    """Get detailed performance metrics"""
    return monitor.get_stats()


@router.post("/performance/reset")
async def reset_performance_metrics(api_key: str = Depends(verify_admin_key)):
    """Reset performance metrics"""
    monitor.reset()
    return {"message": "Performance metrics reset"}


@router.delete("/assessments/{assessment_id}")
async def delete_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_admin_key)
):
    """Delete an assessment"""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )
    
    db.delete(assessment)
    db.commit()
    
    return {"message": f"Assessment {assessment_id} deleted"}


@router.post("/database/cleanup")
async def cleanup_old_data(
    days: int = 90,
    api_key: str = Depends(verify_admin_key)
):
    """Delete assessments older than specified days"""
    utils = DatabaseUtils()
    deleted = utils.cleanup_old_assessments(days)
    
    return {
        "message": f"Cleaned up old assessments",
        "deleted": deleted,
        "older_than_days": days
    }
