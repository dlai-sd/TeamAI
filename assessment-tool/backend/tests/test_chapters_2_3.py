"""
Integration tests for Chapters 2 & 3
"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main_enhanced import app

# Test database
TEST_DATABASE_URL = "sqlite:///./test_chapters.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestChapter2Discovery:
    """Test Chapter 2: Digital Universe Discovery"""
    
    def test_complete_chapter2_flow(self):
        """Test full Chapter 2 workflow"""
        # Step 1: Initialize assessment (from Chapter 1)
        response = client.post(
            "/api/v1/init",
            json={"initial_data": "test"}
        )
        assert response.status_code == 200
        assessment_id = response.json()["assessment_id"]
        
        # Step 2: Scan website
        response = client.post(f"/api/v1/discovery/{assessment_id}/scan-website")
        assert response.status_code == 200
        data = response.json()
        assert "website_data" in data
        assert data["website_data"]["pages_found"] > 0
        
        # Step 3: Find social profiles
        response = client.post(f"/api/v1/discovery/{assessment_id}/find-social-profiles")
        assert response.status_code == 200
        data = response.json()
        assert "social_profiles" in data
        assert len(data["social_profiles"]["platforms"]) > 0
        
        # Step 4: Analyze reviews
        response = client.post(f"/api/v1/discovery/{assessment_id}/analyze-reviews")
        assert response.status_code == 200
        data = response.json()
        assert "review_analysis" in data
        assert data["review_analysis"]["average_rating"] > 0
        
        # Step 5: Calculate digital score
        response = client.post(f"/api/v1/discovery/{assessment_id}/digital-score")
        assert response.status_code == 200
        data = response.json()
        assert "digital_score" in data
        assert 0 <= data["digital_score"]["overall_score"] <= 100
    
    def test_website_scan_returns_valid_data(self):
        """Test website scan data structure"""
        response = client.post("/api/v1/init", json={})
        assessment_id = response.json()["assessment_id"]
        
        response = client.post(f"/api/v1/discovery/{assessment_id}/scan-website")
        data = response.json()["website_data"]
        
        # Verify data structure
        assert "pages_found" in data
        assert "performance" in data
        assert "seo" in data
        assert "mobile_friendly" in data
        assert data["seo"]["score"] <= 100
    
    def test_social_profiles_discovery(self):
        """Test social media profile discovery"""
        response = client.post("/api/v1/init", json={})
        assessment_id = response.json()["assessment_id"]
        
        response = client.post(f"/api/v1/discovery/{assessment_id}/find-social-profiles")
        data = response.json()["social_profiles"]
        
        # Verify platforms are discovered
        assert "platforms" in data
        platforms = data["platforms"]
        assert isinstance(platforms, list)
        assert any(p["name"] == "Facebook" for p in platforms)
        assert any(p["name"] == "Instagram" for p in platforms)
    
    def test_review_analysis_sentiment(self):
        """Test review sentiment analysis"""
        response = client.post("/api/v1/init", json={})
        assessment_id = response.json()["assessment_id"]
        
        response = client.post(f"/api/v1/discovery/{assessment_id}/analyze-reviews")
        data = response.json()["review_analysis"]
        
        # Verify review data structure
        assert "average_rating" in data
        assert "total_reviews" in data
        assert "sentiment_score" in data
        assert data["average_rating"] > 0
        assert data["total_reviews"] > 0
        assert 0 <= data["sentiment_score"] <= 100
    
    def test_digital_score_calculation(self):
        """Test digital health score calculation"""
        response = client.post("/api/v1/init", json={})
        assessment_id = response.json()["assessment_id"]
        
        response = client.post(f"/api/v1/discovery/{assessment_id}/digital-score")
        data = response.json()["digital_score"]
        
        # Verify score components
        assert "overall_score" in data
        assert "grade" in data
        assert "breakdown" in data
        assert "recommendations" in data
        
        # Check breakdown scores exist
        breakdown = data["breakdown"]
        assert "website" in breakdown
        assert "social_media" in breakdown
        assert "online_reputation" in breakdown


class TestChapter3Financial:
    """Test Chapter 3: The Money Story"""
    
    def test_complete_chapter3_flow(self):
        """Test full Chapter 3 workflow"""
        # Initialize assessment
        response = client.post("/api/v1/init", json={})
        assessment_id = response.json()["assessment_id"]
        
        # Step 1: Analyze revenue
        response = client.post(f"/api/v1/financial/{assessment_id}/analyze-revenue")
        assert response.status_code == 200
        assert "revenue_analysis" in response.json()
        
        # Step 2: Analyze expenses
        response = client.post(f"/api/v1/financial/{assessment_id}/analyze-expenses")
        assert response.status_code == 200
        assert "expense_analysis" in response.json()
        
        # Step 3: Analyze cash flow
        response = client.post(f"/api/v1/financial/{assessment_id}/analyze-cash-flow")
        assert response.status_code == 200
        assert "cash_flow_analysis" in response.json()
        
        # Step 4: Analyze debt
        response = client.post(f"/api/v1/financial/{assessment_id}/analyze-debt")
        assert response.status_code == 200
        assert "debt_analysis" in response.json()
        
        # Step 5: Calculate financial score
        response = client.post(f"/api/v1/financial/{assessment_id}/financial-score")
        assert response.status_code == 200
        data = response.json()
        assert "financial_score" in data
        assert 0 <= data["financial_score"]["overall_score"] <= 100
    
    def test_revenue_analysis_structure(self):
        """Test revenue analysis data structure"""
        response = client.post("/api/v1/init", json={})
        assessment_id = response.json()["assessment_id"]
        
        response = client.post(f"/api/v1/financial/{assessment_id}/analyze-revenue")
        data = response.json()["revenue_analysis"]
        
        # Verify revenue data structure
        assert "annual_revenue" in data
        assert "revenue_breakdown" in data
        assert "monthly_trends" in data
        assert data["annual_revenue"]["current_year"] > 0
        assert data["annual_revenue"]["growth_rate"] is not None
    
    def test_expense_analysis_breakdown(self):
        """Test expense analysis breakdown"""
        response = client.post("/api/v1/init", json={})
        assessment_id = response.json()["assessment_id"]
        
        response = client.post(f"/api/v1/financial/{assessment_id}/analyze-expenses")
        data = response.json()["expense_analysis"]
        
        # Verify expense breakdown
        assert "expense_breakdown" in data
        assert "efficiency_metrics" in data
        breakdown = data["expense_breakdown"]
        assert "staff_costs" in breakdown
        assert "marketing" in breakdown
        assert sum(breakdown.values()) == 100  # Percentages sum to 100
    
    def test_cash_flow_liquidity(self):
        """Test cash flow and liquidity analysis"""
        response = client.post("/api/v1/init", json={})
        assessment_id = response.json()["assessment_id"]
        
        response = client.post(f"/api/v1/financial/{assessment_id}/analyze-cash-flow")
        data = response.json()["cash_flow_analysis"]
        
        # Verify cash flow metrics
        assert "current_cash_balance" in data
        assert "runway_months" in data
        assert "liquidity_score" in data
        assert data["liquidity_score"] <= 100
        assert data["runway_months"] >= 0
    
    def test_debt_analysis_ratios(self):
        """Test debt analysis and ratios"""
        response = client.post("/api/v1/init", json={})
        assessment_id = response.json()["assessment_id"]
        
        response = client.post(f"/api/v1/financial/{assessment_id}/analyze-debt")
        data = response.json()["debt_analysis"]
        
        # Verify debt ratios
        assert "debt_ratios" in data
        ratios = data["debt_ratios"]
        assert "debt_to_equity" in ratios
        assert "debt_to_revenue" in ratios
        assert "interest_coverage_ratio" in ratios
        assert ratios["debt_to_equity"] >= 0
    
    def test_financial_score_components(self):
        """Test financial health score components"""
        response = client.post("/api/v1/init", json={})
        assessment_id = response.json()["assessment_id"]
        
        response = client.post(f"/api/v1/financial/{assessment_id}/financial-score")
        data = response.json()["financial_score"]
        
        # Verify score components
        assert "overall_score" in data
        assert "component_scores" in data
        assert "cfo_verdict" in data
        
        components = data["component_scores"]
        assert "revenue_growth" in components
        assert "profitability" in components
        assert "cash_flow" in components
        assert "debt_management" in components
    
    def test_investment_readiness_assessment(self):
        """Test investment readiness endpoint"""
        response = client.post("/api/v1/init", json={})
        assessment_id = response.json()["assessment_id"]
        
        response = client.get(f"/api/v1/financial/{assessment_id}/investment-readiness")
        assert response.status_code == 200
        data = response.json()["investment_readiness"]
        
        # Verify investment readiness data
        assert "readiness_score" in data
        assert "stage" in data
        assert "estimated_valuation_range" in data
        assert 0 <= data["readiness_score"] <= 100


class TestChapterIntegration:
    """Test integration between chapters"""
    
    def test_chapter_progression(self):
        """Test progression from Chapter 1 → 2 → 3"""
        # Initialize
        response = client.post("/api/v1/init", json={})
        assessment_id = response.json()["assessment_id"]
        
        # Complete Chapter 2
        response = client.post(f"/api/v1/discovery/{assessment_id}/digital-score")
        assert response.status_code == 200
        
        # Complete Chapter 3
        response = client.post(f"/api/v1/financial/{assessment_id}/financial-score")
        assert response.status_code == 200
        
        # Verify data exists
        assert "financial_score" in response.json()
    
    def test_404_for_nonexistent_assessment(self):
        """Test 404 error for nonexistent assessment"""
        fake_id = "nonexistent-id"
        
        response = client.post(f"/api/v1/discovery/{fake_id}/scan-website")
        assert response.status_code == 404
        
        response = client.post(f"/api/v1/financial/{fake_id}/analyze-revenue")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
