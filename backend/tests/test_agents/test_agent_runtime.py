"""
Test Agent Runtime - Integration tests with real database
"""
import pytest
from uuid import uuid4
from agents.agent import Agent
from app.models.agency import Agency, Team
from app.models.agent import AgentInstance, AgentRole, Cookbook, Recipe


@pytest.fixture
async def test_agency(db_session, db_engine):
    """Create test agency"""
    agency = Agency(
        id=uuid4(),
        name="Test Agency",
        billing_email="test@example.com",
        subscription_plan="professional",
        is_active=True
    )
    db_session.add(agency)
    await db_session.commit()
    await db_session.refresh(agency)
    return agency


@pytest.fixture
async def test_team(db_session, test_agency):
    """Create test team"""
    team = Team(
        id=uuid4(),
        agency_id=test_agency.id,
        name="Test Team"
    )
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)
    return team


@pytest.fixture
async def test_agent_role(db_session):
    """Create test agent role with cookbook and recipe"""
    role = AgentRole(
        id=uuid4(),
        name="Test Agent",
        description="Test agent for runtime tests",
        status="available",
        version="1.0.0",
        capabilities={"test": "capability"},
        base_price=10.0
    )
    db_session.add(role)
    await db_session.flush()
    
    cookbook = Cookbook(
        id=uuid4(),
        agent_role_id=role.id,
        name="Test Cookbook",
        version="1.0.0",
        description="Test cookbook",
        yaml_definition={
            "cookbook": {
                "id": "test-cookbook",
                "name": "Test Cookbook",
                "version": "1.0.0",
                "recipes": ["test-recipe"]
            }
        },
        required_secrets=[],
        allowed_data_sources=[]
    )
    db_session.add(cookbook)
    await db_session.flush()
    
    recipe = Recipe(
        id=uuid4(),
        cookbook_id=cookbook.id,
        name="Test Recipe",
        version="1.0.0",
        description="Test recipe",
        yaml_definition={"recipe": {"id": "test", "name": "Test"}},
        cost_per_execution=0.1
    )
    db_session.add(recipe)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest.fixture
async def test_agent_instance(db_session, test_team, test_agent_role):
    """Create test agent instance"""
    instance = AgentInstance(
        id=uuid4(),
        team_id=test_team.id,
        agent_role_id=test_agent_role.id,
        custom_name="TestBot",
        avatar_icon="🤖",
        configuration={"mock_mode": True},
        is_active=True
    )
    db_session.add(instance)
    await db_session.commit()
    await db_session.refresh(instance)
    return instance


class TestAgentInitialization:
    """Test Agent runtime initialization"""
    
    @pytest.mark.asyncio
    async def test_initialize_agent_success(self, db_session, test_agent_instance):
        """Should initialize agent and load cookbooks/recipes"""
        agent = Agent(test_agent_instance.id, db_session)
        result = await agent.initialize()
        
        assert result is True
        assert agent.agent_instance is not None
        assert agent.agent_instance.custom_name == "TestBot"
        assert agent.agent_role is not None
        assert len(agent.cookbooks) > 0
        assert len(agent.recipes) > 0
    
    @pytest.mark.asyncio
    async def test_get_agent_info(self, db_session, test_agent_instance):
        """Should return agent metadata"""
        agent = Agent(test_agent_instance.id, db_session)
        await agent.initialize()
        
        info = agent.get_agent_info()
        
        assert 'id' in info
        assert info['custom_name'] == 'TestBot'
        assert info['avatar_icon'] == '🤖'
        assert info['is_active'] is True


class TestRecipeValidation:
    """Test recipe ownership validation"""
    
    @pytest.mark.asyncio
    async def test_validate_recipe_ownership_success(self, db_session, test_agent_instance):
        """Should validate agent owns the recipe"""
        agent = Agent(test_agent_instance.id, db_session)
        await agent.initialize()
        
        # Get first recipe from loaded recipes
        assert len(agent.recipes) > 0
        recipe_id = agent.recipes[0].id
        
        is_valid = await agent.validate_recipe_ownership(recipe_id)
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_recipe_ownership_failure(self, db_session, test_agent_instance):
        """Should reject recipe not owned by agent"""
        agent = Agent(test_agent_instance.id, db_session)
        await agent.initialize()
        
        # Use random UUID that agent doesn't own
        fake_recipe_id = uuid4()
        
        is_valid = await agent.validate_recipe_ownership(fake_recipe_id)
        
        assert is_valid is False
        agent.recipes = []
