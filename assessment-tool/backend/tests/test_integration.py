"""
Integration tests for full assessment flow
Tests end-to-end workflows across multiple chapters
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestChapter1Flow:
    """Test complete Chapter 1 workflow"""
    
    def test_complete_chapter_1_flow(self):
        """Test full Chapter 1: Identity Resolution"""
        
        # Step 1: Initialize assessment
        init_response = client.post(
            "/api/v1/assessment/init",
            json={"industry": "restaurant"}
        )
        assert init_response.status_code == 201
        data = init_response.json()
        assessment_id = data["assessment_id"]
        assert data["status"] == "initiated"
        
        # Step 2: Search for company identity
        search_response = client.post(
            f"/api/v1/assessment/{assessment_id}/identify",
            json={
                "company_name": "Noya Foods",
                "location": "Mumbai"
            }
        )
        assert search_response.status_code == 200
        search_data = search_response.json()
        assert search_data["total_found"] == 3
        assert len(search_data["candidates"]) == 3
        
        # Verify first candidate has highest confidence
        candidates = search_data["candidates"]
        assert candidates[0]["confidence"] > candidates[1]["confidence"]
        assert candidates[1]["confidence"] > candidates[2]["confidence"]
        
        # Step 3: Confirm identity
        selected_id = candidates[0]["id"]
        confirm_response = client.post(
            f"/api/v1/assessment/{assessment_id}/confirm",
            json={"selected_id": selected_id}
        )
        assert confirm_response.status_code == 200
        confirm_data = confirm_response.json()
        assert confirm_data["status"] == "identity_resolved"
        assert confirm_data["next_chapter"] == 2
        
        # Step 4: Verify assessment updated
        get_response = client.get(f"/api/v1/assessment/{assessment_id}")
        assert get_response.status_code == 200
        assessment_data = get_response.json()
        assert assessment_data["status"] == "identity_resolved"
        assert assessment_data["current_chapter"] == 2
        assert assessment_data["company_name"] == candidates[0]["name"]


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_enforcement(self):
        """Test that rate limits are enforced"""
        # Initialize assessment to get an ID
        init_response = client.post(
            "/api/v1/assessment/init",
            json={"industry": "restaurant"}
        )
        assessment_id = init_response.json()["assessment_id"]
        
        # Make multiple requests rapidly
        responses = []
        for i in range(70):  # Exceed per-minute limit (60)
            response = client.post(
                f"/api/v1/assessment/{assessment_id}/identify",
                json={"company_name": f"Test Company {i}"}
            )
            responses.append(response.status_code)
        
        # Should have some 429 responses
        rate_limited = [r for r in responses if r == 429]
        assert len(rate_limited) > 0, "Rate limiting not working"


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_assessment_not_found(self):
        """Test 404 for non-existent assessment"""
        response = client.get("/api/v1/assessment/fake-id-12345")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_invalid_industry(self):
        """Test validation error for invalid industry"""
        response = client.post(
            "/api/v1/assessment/init",
            json={"industry": "invalid_industry_type"}
        )
        assert response.status_code == 422
    
    def test_empty_company_name(self):
        """Test validation error for empty company name"""
        init_response = client.post(
            "/api/v1/assessment/init",
            json={"industry": "restaurant"}
        )
        assessment_id = init_response.json()["assessment_id"]
        
        response = client.post(
            f"/api/v1/assessment/{assessment_id}/identify",
            json={"company_name": ""}
        )
        assert response.status_code == 422


class TestPerformance:
    """Test performance and response times"""
    
    def test_health_check_performance(self):
        """Health check should be fast"""
        import time
        
        start = time.time()
        response = client.get("/health")
        duration = (time.time() - start) * 1000  # ms
        
        assert response.status_code == 200
        assert duration < 100, f"Health check too slow: {duration}ms"
    
    def test_config_endpoints_cached(self):
        """Config endpoints should return quickly"""
        import time
        
        # First call
        start = time.time()
        client.get("/config/chapters")
        first_duration = (time.time() - start) * 1000
        
        # Second call (should be faster if cached)
        start = time.time()
        client.get("/config/chapters")
        second_duration = (time.time() - start) * 1000
        
        assert second_duration <= first_duration


class TestChapter2Foundation:
    """Test Chapter 2 foundation (with mock data)"""
    
    def test_website_scan(self):
        """Test website scanning endpoint"""
        # Create assessment with website
        init_response = client.post(
            "/api/v1/assessment/init",
            json={"industry": "restaurant"}
        )
        assessment_id = init_response.json()["assessment_id"]
        
        # Confirm identity to set website
        client.post(
            f"/api/v1/assessment/{assessment_id}/identify",
            json={"company_name": "Noya Foods"}
        )
        client.post(
            f"/api/v1/assessment/{assessment_id}/confirm",
            json={"selected_id": "noya-123"}
        )
        
        # Scan website
        response = client.post(
            f"/api/v1/discovery/{assessment_id}/scan-website"
        )
        assert response.status_code == 200
        data = response.json()
        assert "website_data" in data
        assert data["website_data"]["status"] == "accessible"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
