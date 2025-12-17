"""
Test CookbookLoader - YAML cookbook and recipe import functionality
"""
import pytest
from pathlib import Path
from uuid import uuid4
from unittest.mock import patch, MagicMock
import yaml
import tempfile

from agents.cookbook_loader import CookbookLoader, seed_database
from app.models.agent import AgentRole, Cookbook, Recipe


@pytest.fixture
def sample_cookbook_yaml():
    """Sample cookbook YAML data"""
    return {
        'cookbook': {
            'id': 'test-cookbook-v1',
            'name': 'Test Cookbook',
            'version': '1.0.0',
            'description': 'Test cookbook for unit tests',
            'required_secrets': ['api_key'],
            'allowed_data_sources': [
                {'type': 'web_crawler', 'max_pages': 100}
            ],
            'recipes': ['test-recipe'],
            'subscription_limits': {
                'max_executions_per_month': 500
            }
        }
    }


@pytest.fixture
def sample_recipe_yaml():
    """Sample recipe YAML data"""
    return {
        'recipe': {
            'id': 'test-recipe',
            'name': 'Test Recipe',
            'version': '1.0.0',
            'description': 'Test recipe for unit tests',
            'cookbook': 'test-cookbook-v1',
            'inputs': [
                {'name': 'test_input', 'type': 'string', 'required': True}
            ],
            'workflow': {
                'nodes': [
                    {'id': 'step1', 'component': 'TestComponent'}
                ],
                'edges': [
                    {'from': 'step1', 'to': 'step2'}
                ]
            },
            'compliance': {
                'track_usage': True,
                'cost_per_unit': 0.75
            },
            'ab_testing': {
                'enabled': True
            }
        }
    }


@pytest.fixture
def temp_yaml_file(sample_cookbook_yaml):
    """Create temporary YAML file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_cookbook_yaml, f)
        return f.name


class TestCookbookLoaderInitialization:
    """Test CookbookLoader initialization"""
    
    @pytest.mark.asyncio
    async def test_init_with_session(self, db_session):
        """Should initialize loader with database session"""
        loader = CookbookLoader(db_session)
        
        assert loader.session == db_session
        assert loader.session is not None


class TestLoadYaml:
    """Test YAML file loading"""
    
    @pytest.mark.asyncio
    async def test_load_yaml_success(self, db_session, temp_yaml_file, sample_cookbook_yaml):
        """Should load and parse YAML file"""
        loader = CookbookLoader(db_session)
        
        data = loader._load_yaml(temp_yaml_file)
        
        assert 'cookbook' in data
        assert data['cookbook']['name'] == 'Test Cookbook'
        assert data['cookbook']['version'] == '1.0.0'
    
    @pytest.mark.asyncio
    async def test_load_yaml_file_not_found(self, db_session):
        """Should raise FileNotFoundError for missing file"""
        loader = CookbookLoader(db_session)
        
        with pytest.raises(FileNotFoundError):
            loader._load_yaml('/nonexistent/file.yaml')


class TestGetOrCreateAgentRole:
    """Test AgentRole creation and retrieval"""
    
    @pytest.mark.asyncio
    async def test_create_new_agent_role(self, db_session):
        """Should create new AgentRole if not exists"""
        loader = CookbookLoader(db_session)
        
        agent_role = await loader._get_or_create_agent_role(
            name="Test Agent",
            description="Test agent role",
            version="1.0.0"
        )
        
        assert agent_role.id is not None
        assert agent_role.name == "Test Agent"
        assert agent_role.description == "Test agent role"
        assert agent_role.version == "1.0.0"
        assert agent_role.status == 'available'
        assert agent_role.base_price == 50.00
    
    @pytest.mark.asyncio
    async def test_get_existing_agent_role(self, db_session):
        """Should return existing AgentRole instead of creating duplicate"""
        loader = CookbookLoader(db_session)
        
        # Create first time
        first = await loader._get_or_create_agent_role(
            name="Test Agent",
            description="Description 1",
            version="1.0.0"
        )
        await db_session.commit()
        
        # Get second time
        second = await loader._get_or_create_agent_role(
            name="Test Agent",
            description="Description 2",  # Different description
            version="1.0.0"
        )
        
        # Should be same instance
        assert first.id == second.id
        assert first.description == second.description  # Original description preserved


class TestLoadCookbook:
    """Test cookbook loading from YAML"""
    
    @pytest.mark.asyncio
    async def test_load_cookbook_success(self, db_session, temp_yaml_file):
        """Should load cookbook and create database records"""
        loader = CookbookLoader(db_session)
        
        cookbook = await loader.load_cookbook(temp_yaml_file, "Test Agent")
        
        assert cookbook.id is not None
        assert cookbook.name == "Test Cookbook"
        assert cookbook.version == "1.0.0"
        assert cookbook.description == "Test cookbook for unit tests"
        assert cookbook.agent_role_id is not None
        assert 'api_key' in cookbook.required_secrets
        assert len(cookbook.allowed_data_sources) == 1
        assert cookbook.subscription_limits['max_executions_per_month'] == 500
    
    @pytest.mark.asyncio
    async def test_load_cookbook_invalid_yaml(self, db_session):
        """Should raise ValueError for invalid cookbook YAML"""
        loader = CookbookLoader(db_session)
        
        # Create temp file with invalid structure
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'invalid': 'structure'}, f)
            invalid_file = f.name
        
        with pytest.raises(ValueError, match="missing 'cookbook' key"):
            await loader.load_cookbook(invalid_file, "Test Agent")
    
    @pytest.mark.asyncio
    async def test_load_cookbook_duplicate_prevented(self, db_session, temp_yaml_file):
        """Should not create duplicate cookbook with same name and version"""
        loader = CookbookLoader(db_session)
        
        # Load first time
        first = await loader.load_cookbook(temp_yaml_file, "Test Agent")
        await db_session.commit()
        
        # Load second time
        second = await loader.load_cookbook(temp_yaml_file, "Test Agent")
        
        # Should be same cookbook
        assert first.id == second.id


class TestLoadRecipe:
    """Test recipe loading"""
    
    @pytest.mark.asyncio
    async def test_load_recipe_success(self, db_session, sample_recipe_yaml):
        """Should load recipe and create database record"""
        loader = CookbookLoader(db_session)
        
        # Create parent cookbook first
        agent_role = AgentRole(
            id=uuid4(),
            name="Test Agent",
            description="Test",
            version="1.0.0",
            status="available",
            capabilities={},
            base_price=50.0
        )
        db_session.add(agent_role)
        await db_session.flush()
        
        cookbook = Cookbook(
            id=uuid4(),
            agent_role_id=agent_role.id,
            name="Test Cookbook",
            version="1.0.0",
            description="Test",
            yaml_definition={'cookbook': {'name': 'Test'}},
            required_secrets=[],
            allowed_data_sources=[]
        )
        db_session.add(cookbook)
        await db_session.flush()
        
        # Create temp recipe file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(sample_recipe_yaml, f)
            recipe_file = f.name
        
        # Mock the recipe path resolution
        recipe_path = Path(recipe_file)
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(loader, '_load_yaml', return_value=sample_recipe_yaml):
                await loader._load_recipe('test-recipe', cookbook)
        
        await db_session.commit()
        
        # Verify recipe was created
        from sqlalchemy import select
        result = await db_session.execute(
            select(Recipe).where(Recipe.cookbook_id == cookbook.id)
        )
        recipe = result.scalar_one_or_none()
        
        assert recipe is not None
        assert recipe.name == "Test Recipe"
        assert recipe.version == "1.0.0"
        assert recipe.cost_per_execution == 0.75
        assert recipe.ab_testing_enabled is True
    
    @pytest.mark.asyncio
    async def test_load_recipe_file_not_found(self, db_session, capsys):
        """Should handle missing recipe file gracefully"""
        loader = CookbookLoader(db_session)
        
        cookbook = Cookbook(
            id=uuid4(),
            agent_role_id=uuid4(),
            name="Test",
            version="1.0.0",
            description="Test",
            yaml_definition={},
            required_secrets=[],
            allowed_data_sources=[]
        )
        db_session.add(cookbook)
        
        # Try to load non-existent recipe
        await loader._load_recipe('nonexistent-recipe', cookbook)
        
        # Should print warning, not raise exception
        captured = capsys.readouterr()
        assert "Recipe file not found" in captured.out


class TestLoadAllCookbooks:
    """Test batch cookbook loading"""
    
    @pytest.mark.asyncio
    async def test_load_all_cookbooks_success(self, db_session):
        """Should load all cookbooks from directory"""
        loader = CookbookLoader(db_session)
        
        # Create temp directory with cookbook files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test cookbook file
            cookbook_yaml = {
                'cookbook': {
                    'id': 'test-v1',
                    'name': 'Test Cookbook',
                    'version': '1.0.0',
                    'description': 'Test',
                    'recipes': []
                }
            }
            
            cookbook_file = Path(temp_dir) / 'test-cookbook-v1.yaml'
            with open(cookbook_file, 'w') as f:
                yaml.dump(cookbook_yaml, f)
            
            cookbooks = await loader.load_all_cookbooks(temp_dir)
            
            assert len(cookbooks) == 1
            assert cookbooks[0].name == 'Test Cookbook'
    
    @pytest.mark.asyncio
    async def test_load_all_cookbooks_directory_not_found(self, db_session):
        """Should raise FileNotFoundError for missing directory"""
        loader = CookbookLoader(db_session)
        
        with pytest.raises(FileNotFoundError):
            await loader.load_all_cookbooks('/nonexistent/directory')


class TestSeedDatabase:
    """Test database seeding functionality"""
    
    @pytest.mark.asyncio
    async def test_seed_database_success(self, db_session):
        """Should seed database with cookbooks"""
        # Mock the load_all_cookbooks to avoid filesystem dependencies
        mock_cookbook = Cookbook(
            id=uuid4(),
            agent_role_id=uuid4(),
            name="Seeded Cookbook",
            version="1.0.0",
            description="Test",
            yaml_definition={},
            required_secrets=[],
            allowed_data_sources=[]
        )
        
        with patch.object(CookbookLoader, 'load_all_cookbooks', return_value=[mock_cookbook]):
            cookbooks = await seed_database(db_session)
            
            assert len(cookbooks) == 1
            assert cookbooks[0].name == "Seeded Cookbook"
    
    @pytest.mark.asyncio
    async def test_seed_database_handles_errors(self, db_session):
        """Should rollback on error and re-raise exception"""
        with patch.object(CookbookLoader, 'load_all_cookbooks', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Test error"):
                await seed_database(db_session)
