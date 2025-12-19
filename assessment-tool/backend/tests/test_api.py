"""
Unit tests for Assessment API (Chapter 1)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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


class TestAssessmentAPI:
    """Test suite for Chapter 1: Identity Resolution"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "assessment-backend"
    
    def test_initialize_assessment(self):
        """Test POST /api/v1/assessment/init"""
        response = client.post(
            "/api/v1/assessment/init",
            json={"industry": "restaurant"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "assessment_id" in data
        assert data["status"] == "initiated"
        return data["assessment_id"]
    
    def test_search_identity_noya_foods(self):
        """Test identity search with 'Noya Foods'"""
        # First initialize assessment
        init_response = client.post(
            "/api/v1/assessment/init",
            json={"industry": "restaurant"}
        )
        assessment_id = init_response.json()["assessment_id"]
        
        # Search for identity
        response = client.post(
            f"/api/v1/assessment/{assessment_id}/identify",
            json={
                "company_name": "Noya Foods",
                "location": "Mumbai"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_found"] == 3
        assert len(data["candidates"]) == 3
        
        # Verify confidence scores
        assert data["candidates"][0]["confidence"] == 0.87
        assert data["candidates"][0]["name"] == "Noya Foods & Beverages Pvt Ltd"
    
    def test_search_identity_unknown_company(self):
        """Test identity search with unknown company"""
        init_response = client.post(
            "/api/v1/assessment/init",
            json={"industry": "retail"}
        )
        assessment_id = init_response.json()["assessment_id"]
        
        response = client.post(
            f"/api/v1/assessment/{assessment_id}/identify",
            json={"company_name": "Unknown Company XYZ"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_found"] == 1
        assert data["candidates"][0]["confidence"] == 0.50
    
    def test_confirm_identity(self):
        """Test identity confirmation"""
        # Initialize and search
        init_response = client.post(
            "/api/v1/assessment/init",
            json={"industry": "restaurant"}
        )
        assessment_id = init_response.json()["assessment_id"]
        
        client.post(
            f"/api/v1/assessment/{assessment_id}/identify",
            json={"company_name": "Noya Foods"}
        )
        
        # Confirm identity
        response = client.post(
            f"/api/v1/assessment/{assessment_id}/confirm",
            json={"selected_id": "noya-123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "identity_resolved"
        assert data["next_chapter"] == 2
        assert data["confirmed_company"]["name"] == "Noya Foods & Beverages Pvt Ltd"
    
    def test_get_assessment(self):
        """Test GET assessment details"""
        # Create assessment
        init_response = client.post(
            "/api/v1/assessment/init",
            json={"industry": "technology"}
        )
        assessment_id = init_response.json()["assessment_id"]
        
        # Get details
        response = client.get(f"/api/v1/assessment/{assessment_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["assessment_id"] == assessment_id
        assert data["industry"] == "technology"
        assert data["status"] == "initiated"
    
    def test_assessment_not_found(self):
        """Test 404 for non-existent assessment"""
        response = client.get("/api/v1/assessment/fake-id-12345")
        assert response.status_code == 404
    
    def test_invalid_industry(self):
        """Test validation error for invalid industry"""
        response = client.post(
            "/api/v1/assessment/init",
            json={"industry": "invalid_industry"}
        )
        assert response.status_code == 422  # Validation error
    
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
        assert response.status_code == 422  # Validation error


class TestConfigEndpoints:
    """Test configuration endpoints"""
    
    def test_get_chapters_config(self):
        """Test /config/chapters endpoint"""
        response = client.get("/config/chapters")
        assert response.status_code == 200
        data = response.json()
        assert "chapters" in data
        assert len(data["chapters"]) == 8
    
    def test_get_ui_config(self):
        """Test /config/ui endpoint"""
        response = client.get("/config/ui")
        assert response.status_code == 200
        data = response.json()
        assert "themes" in data
        assert "default_theme" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
