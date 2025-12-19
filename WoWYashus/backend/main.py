from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Any
import os
from datetime import datetime

app = FastAPI(title="WoWYashus API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class MilestoneData(BaseModel):
    milestone_number: int
    data: Dict[str, Any]

class AnalysisRequest(BaseModel):
    milestones: Dict[int, Dict[str, Any]]

class EmailRequest(BaseModel):
    email: EmailStr
    milestones: Dict[int, Dict[str, Any]]
    analysis: Any

# In-memory storage (replace with database in production)
submissions = {}

@app.get("/")
async def root():
    return {
        "message": "WoWYashus API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/milestones/{milestone_number}")
async def submit_milestone(milestone_number: int, data: Dict[str, Any]):
    """Submit milestone data"""
    if milestone_number < 1 or milestone_number > 9:
        raise HTTPException(status_code=400, detail="Invalid milestone number")
    
    session_id = "default_session"  # In production, use proper session management
    
    if session_id not in submissions:
        submissions[session_id] = {}
    
    submissions[session_id][milestone_number] = {
        "data": data,
        "submitted_at": datetime.now().isoformat()
    }
    
    return {
        "success": True,
        "milestone_number": milestone_number,
        "message": "Milestone data saved successfully"
    }

@app.post("/api/analyze")
async def analyze_data(request: AnalysisRequest):
    """Generate AI analysis and recommendations"""
    
    milestones = request.milestones
    completed_count = len(milestones)
    
    # Mock Groq API call (replace with actual Groq integration)
    insights = generate_insights(milestones)
    statistics = calculate_statistics(milestones)
    roadmap = generate_roadmap(milestones)
    
    return {
        "insights": insights,
        "statistics": statistics,
        "roadmap": roadmap,
        "completed_milestones": completed_count
    }

@app.post("/api/send-report")
async def send_report(request: EmailRequest):
    """Send analysis report via email"""
    
    # Mock email sending (replace with actual SMTP/SendGrid)
    print(f"📧 Sending report to: {request.email}")
    print(f"Milestones completed: {len(request.milestones)}")
    
    return {
        "success": True,
        "message": f"Report sent to {request.email}",
        "email": request.email
    }

# Helper Functions
def generate_insights(milestones: Dict) -> List[Dict]:
    """Generate AI-powered insights (mock implementation)"""
    
    insights = [
        {
            "title": "Market Positioning Strength",
            "content": "Your product positioning shows strong differentiation in a competitive market. Consider emphasizing unique value propositions in early marketing materials."
        },
        {
            "title": "Target Audience Clarity",
            "content": "Well-defined target audience with specific pain points. Recommend persona-based content strategy for maximum engagement."
        },
        {
            "title": "Growth Potential",
            "content": "High growth potential identified based on market trends and competitive analysis. Focus on scalable acquisition channels."
        }
    ]
    
    # Add more insights based on completed milestones
    if len(milestones) >= 5:
        insights.append({
            "title": "Campaign Readiness",
            "content": "Strong foundation established. Ready to launch initial marketing campaigns with clear measurement framework."
        })
    
    if len(milestones) >= 8:
        insights.append({
            "title": "Scaling Opportunities",
            "content": "Multiple proven channels identified. Recommend 3-month scaling plan with phased budget increases."
        })
    
    return insights

def calculate_statistics(milestones: Dict) -> Dict[str, int]:
    """Calculate benchmark statistics (mock implementation)"""
    
    base_scores = {
        "Market Fit Score": 65,
        "Competitive Advantage": 58,
        "Scalability Index": 70,
        "Brand Readiness": 62
    }
    
    # Increase scores based on completed milestones
    boost = len(milestones) * 3
    
    return {
        key: min(value + boost, 95) 
        for key, value in base_scores.items()
    }

def generate_roadmap(milestones: Dict) -> List[Dict]:
    """Generate prioritized action roadmap (mock implementation)"""
    
    roadmap = [
        {
            "priority": 1,
            "title": "Define Core Brand Identity",
            "description": "Establish brand voice, visual identity, and messaging framework within 2 weeks."
        },
        {
            "priority": 2,
            "title": "Build Minimum Viable Audience",
            "description": "Launch targeted content marketing to acquire first 1000 engaged followers."
        },
        {
            "priority": 3,
            "title": "Implement Analytics Stack",
            "description": "Set up tracking and measurement infrastructure for data-driven decisions."
        },
        {
            "priority": 4,
            "title": "Launch Paid Acquisition Test",
            "description": "Run controlled experiments across 3 channels with $5k budget."
        },
        {
            "priority": 5,
            "title": "Optimize Conversion Funnel",
            "description": "Analyze user journey and improve key conversion points for 2x improvement."
        }
    ]
    
    # Customize based on completed milestones
    if len(milestones) >= 6:
        roadmap.append({
            "priority": 6,
            "title": "Scale Top Performing Channels",
            "description": "Double down on channels with best ROI and CAC metrics."
        })
    
    return roadmap

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
