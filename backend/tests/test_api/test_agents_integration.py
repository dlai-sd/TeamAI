"""
Integration tests for Agent API endpoints
Tests complete workflows with database interactions
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.main import app
from app.models.agency import Agency, Team
from app.models.agent import AgentInstance, AgentRole
from app.utils.security import hash_password


@pytest.fixture
async def test_agency(db_session: AsyncSession, db_engine):
    """Create test agency (depends on db_engine to ensure tables exist)"""
    unique_id = uuid4()
    agency = Agency(
        id=unique_id,
        name=f"Test Agency {unique_id}",
        billing_email=f"billing-{unique_id}@test.com",
        subscription_plan="professional",
        is_active=True
    )
    db_session.add(agency)
    await db_session.commit()
    await db_session.refresh(agency)
    return agency


@pytest.fixture
async def test_team(db_session: AsyncSession, test_agency):
    """Create test team"""
    team = Team(
        id=uuid4(),
        agency_id=test_agency.id,
        name="Test Team",
        description="Test team for integration tests"
    )
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def test_agent_role(db_session: AsyncSession):
    """Create test agent role"""
    role = AgentRole(
        id=uuid4(),
        name="SEO Specialist",
        description="SEO testing agent",
        status="available",
        version="1.0.0",
        capabilities={"keywords": "research", "audits": "technical"},
        base_price=50.00
    )
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest.fixture
async def test_agent_instance(db_session: AsyncSession, test_team, test_agent_role):
    """Create test agent instance"""
    agent = AgentInstance(
        id=uuid4(),
        team_id=test_team.id,
        agent_role_id=test_agent_role.id,
        custom_name="TestBot",
        avatar_icon="🤖",
        configuration={"mock_mode": True},
        is_active=True
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


class TestAgentAllocation:
    """Test agent allocation API"""
    
    @pytest.mark.asyncio
    async def test_allocate_agent_to_team(self, client: AsyncClient, test_agency, test_team, test_agent_role):
        """Should allocate agent to team with valid data"""
        payload = {
            "team_id": str(test_team.id),
            "agent_role_id": str(test_agent_role.id),
            "custom_name": "NewBot",
            "avatar_icon": "🚀",
            "configuration": {"max_depth": 3}
        }
        
        response = await client.post(
            f"/api/v1/agencies/{test_agency.id}/agents/allocate",
            json=payload,
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["custom_name"] == "NewBot"
        assert data["avatar_icon"] == "🚀"
        assert data["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_allocate_agent_invalid_team(self, client: AsyncClient, test_agency, test_agent_role):
        """Should reject allocation to non-existent team"""
        payload = {
            "team_id": str(uuid4()),  # Non-existent team
            "agent_role_id": str(test_agent_role.id),
            "custom_name": "InvalidBot",
            "avatar_icon": "❌"
        }
        
        response = await client.post(
            f"/api/v1/agencies/{test_agency.id}/agents/allocate",
            json=payload,
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code in (404, 422)
    
    @pytest.mark.asyncio
    async def test_list_team_agents(self, client: AsyncClient, test_team, test_agent_instance):
        """Should list all agents in team"""
        response = await client.get(
            f"/api/v1/teams/{test_team.id}/agents",
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["custom_name"] == "TestBot"


class TestAgentExecution:
    """Test agent execution API"""
    
    @pytest.mark.asyncio
    async def test_execute_agent_simple_recipe(self, client: AsyncClient, test_agent_instance):
        """Should execute agent with simple recipe"""
        payload = {
            "recipe_id": "site-audit",
            "inputs": {
                "website_url": "https://example.com",
                "max_depth": 2
            }
        }
        
        response = await client.post(
            f"/api/v1/agents/{test_agent_instance.id}/execute",
            json=payload,
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        # May be 200 (sync) or 202 (async)
        assert response.status_code in (200, 202)
        data = response.json()
        assert "task_id" in data or "result" in data
    
    @pytest.mark.asyncio
    async def test_execute_agent_missing_inputs(self, client: AsyncClient, test_agent_instance):
        """Should reject execution with missing required inputs"""
        payload = {
            "recipe_id": "site-audit",
            "inputs": {}  # Missing website_url
        }
        
        response = await client.post(
            f"/api/v1/agents/{test_agent_instance.id}/execute",
            json=payload,
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_agent_execution_history(self, client: AsyncClient, test_agent_instance):
        """Should retrieve agent execution history"""
        response = await client.get(
            f"/api/v1/agents/{test_agent_instance.id}/executions",
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAgentConfiguration:
    """Test agent configuration API"""
    
    @pytest.mark.asyncio
    async def test_update_agent_config(self, client: AsyncClient, test_agent_instance):
        """Should update agent configuration"""
        payload = {
            "custom_name": "UpdatedBot",
            "avatar_icon": "🔧",
            "configuration": {"max_depth": 5}
        }
        
        response = await client.patch(
            f"/api/v1/agents/{test_agent_instance.id}",
            json=payload,
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["custom_name"] == "UpdatedBot"
        assert data["configuration"]["max_depth"] == 5
    
    @pytest.mark.asyncio
    async def test_deactivate_agent(self, client: AsyncClient, test_agent_instance):
        """Should deactivate agent"""
        response = await client.post(
            f"/api/v1/agents/{test_agent_instance.id}/deactivate",
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
    
    @pytest.mark.asyncio
    async def test_reactivate_agent(self, client: AsyncClient, test_agent_instance):
        """Should reactivate agent"""
        # First deactivate
        await client.post(
            f"/api/v1/agents/{test_agent_instance.id}/deactivate",
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        # Then reactivate
        response = await client.post(
            f"/api/v1/agents/{test_agent_instance.id}/activate",
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True


class TestMarketplace:
    """Test marketplace API"""
    
    @pytest.mark.asyncio
    async def test_list_available_agents(self, client: AsyncClient, test_agent_role):
        """Should list available agent roles"""
        response = await client.get(
            "/api/v1/marketplace/agents",
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["status"] == "available"
    
    @pytest.mark.asyncio
    async def test_get_agent_role_details(self, client: AsyncClient, test_agent_role):
        """Should get agent role details"""
        response = await client.get(
            f"/api/v1/marketplace/agents/{test_agent_role.id}",
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "SEO Specialist"
        assert "capabilities" in data
        assert "base_price" in data
    
    @pytest.mark.asyncio
    async def test_filter_agents_by_capability(self, client: AsyncClient):
        """Should filter agents by capability"""
        response = await client.get(
            "/api/v1/marketplace/agents?capability=seo",
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAgentMetrics:
    """Test agent metrics and audit logs"""
    
    @pytest.mark.asyncio
    async def test_get_agent_metrics(self, client: AsyncClient, test_agent_instance):
        """Should get agent performance metrics"""
        response = await client.get(
            f"/api/v1/agents/{test_agent_instance.id}/metrics",
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_executions" in data
        assert "success_rate" in data
        assert "avg_execution_time_ms" in data
    
    @pytest.mark.asyncio
    async def test_get_agent_audit_logs(self, client: AsyncClient, test_agent_instance):
        """Should get agent audit logs"""
        response = await client.get(
            f"/api/v1/agents/{test_agent_instance.id}/audit",
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_agency_audit_logs(self, client: AsyncClient, test_agency):
        """Should get agency-wide audit logs"""
        response = await client.get(
            f"/api/v1/agencies/{test_agency.id}/audit",
            headers={"Authorization": f"Bearer mock_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
