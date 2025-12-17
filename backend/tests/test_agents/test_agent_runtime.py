"""
Test Agent Runtime - Integration between AgentInstance DB and RecipeEvaluator
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4
from agents.agent import Agent


@pytest.fixture
def mock_agent_instance():
    """Mock AgentInstance DB record"""
    instance = Mock()
    instance.id = uuid4()
    instance.team_id = uuid4()
    instance.agent_role_id = uuid4()
    instance.custom_name = "TestBot"
    instance.avatar_icon = "🤖"
    instance.configuration = {
        'max_executions_per_day': 100,
        'allowed_models': ['groq-llama-3.1-8b-instant']
    }
    instance.is_active = True
    return instance


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = Mock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


class TestAgentInitialization:
    """Test Agent runtime initialization"""
    
    @pytest.mark.asyncio
    async def test_initialize_agent_success(self, mock_agent_instance, mock_db_session):
        """Should initialize agent and load cookbooks/recipes"""
        with patch('agents.agent.select') as mock_select:
            # Mock cookbook and recipe queries
            mock_cookbook_result = Mock()
            mock_cookbook_result.scalars().all.return_value = [
                Mock(id=uuid4(), name='SEO Specialist', version='1.0.0')
            ]
            
            mock_recipe_result = Mock()
            mock_recipe_result.scalars().all.return_value = [
                Mock(id=uuid4(), name='Site Audit', version='1.0.0')
            ]
            
            mock_db_session.execute.side_effect = [
                mock_cookbook_result,
                mock_recipe_result
            ]
            
            agent = Agent(mock_agent_instance, mock_db_session)
            await agent.initialize()
            
            assert agent.is_initialized is True
            assert len(agent.cookbooks) > 0
            assert len(agent.recipes) > 0
    
    @pytest.mark.asyncio
    async def test_get_agent_info(self, mock_agent_instance, mock_db_session):
        """Should return agent metadata"""
        agent = Agent(mock_agent_instance, mock_db_session)
        
        info = agent.get_agent_info()
        
        assert info['id'] == str(mock_agent_instance.id)
        assert info['name'] == 'TestBot'
        assert info['avatar'] == '🤖'
        assert info['is_active'] is True


class TestRecipeValidation:
    """Test recipe ownership validation"""
    
    @pytest.mark.asyncio
    async def test_validate_recipe_ownership_success(self, mock_agent_instance, mock_db_session):
        """Should validate agent owns the recipe"""
        agent = Agent(mock_agent_instance, mock_db_session)
        
        recipe_id = uuid4()
        agent.recipes = [
            Mock(id=recipe_id, name='Site Audit')
        ]
        
        is_valid = await agent.validate_recipe_ownership(recipe_id)
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_recipe_ownership_failure(self, mock_agent_instance, mock_db_session):
        """Should reject recipe not owned by agent"""
        agent = Agent(mock_agent_instance, mock_db_session)
        agent.recipes = []
        
        unknown_recipe_id = uuid4()
        
        is_valid = await agent.validate_recipe_ownership(unknown_recipe_id)
        
        assert is_valid is False


class TestRecipeExecution:
    """Test agent recipe execution"""
    
    @pytest.mark.asyncio
    async def test_execute_recipe_success(self, mock_agent_instance, mock_db_session):
        """Should execute recipe and return results"""
        agent = Agent(mock_agent_instance, mock_db_session)
        
        recipe_id = uuid4()
        recipe_mock = Mock(
            id=recipe_id,
            name='Site Audit',
            yaml_definition={
                'id': 'site-audit',
                'name': 'Site Audit',
                'workflow': {
                    'nodes': [
                        {
                            'id': 'crawler',
                            'component': 'WebCrawler',
                            'config': {'max_pages': 10}
                        }
                    ],
                    'edges': []
                }
            }
        )
        agent.recipes = [recipe_mock]
        
        with patch('agents.agent.RecipeEvaluator') as mock_evaluator_class:
            mock_evaluator = Mock()
            mock_evaluator.execute = AsyncMock(return_value={
                'crawler.output': {'pages': ['page1', 'page2']},
                'execution_time_ms': 1500
            })
            mock_evaluator_class.return_value = mock_evaluator
            
            inputs = {'website_url': 'https://example.com', 'max_depth': 2}
            result = await agent.execute_recipe(recipe_id, inputs)
            
            assert 'crawler.output' in result
            assert result['crawler.output'] == {'pages': ['page1', 'page2']}
    
    @pytest.mark.asyncio
    async def test_execute_recipe_not_found(self, mock_agent_instance, mock_db_session):
        """Should raise error for unknown recipe"""
        agent = Agent(mock_agent_instance, mock_db_session)
        agent.recipes = []
        
        unknown_recipe_id = uuid4()
        
        with pytest.raises(ValueError, match="not found or not accessible"):
            await agent.execute_recipe(unknown_recipe_id, {})
    
    @pytest.mark.asyncio
    async def test_execute_recipe_with_tracking(self, mock_agent_instance, mock_db_session):
        """Should pass tracking config to RecipeEvaluator"""
        agent = Agent(mock_agent_instance, mock_db_session)
        
        recipe_id = uuid4()
        recipe_mock = Mock(
            id=recipe_id,
            name='Site Audit',
            yaml_definition={
                'id': 'site-audit',
                'name': 'Site Audit',
                'workflow': {'nodes': [], 'edges': []}
            }
        )
        agent.recipes = [recipe_mock]
        
        with patch('agents.agent.RecipeEvaluator') as mock_evaluator_class:
            mock_evaluator = Mock()
            mock_evaluator.execute = AsyncMock(return_value={})
            mock_evaluator_class.return_value = mock_evaluator
            
            await agent.execute_recipe(recipe_id, {})
            
            # Verify tracking_config was passed
            init_call_kwargs = mock_evaluator_class.call_args[1]
            assert 'tracking_config' in init_call_kwargs
            
            tracking_config = init_call_kwargs['tracking_config']
            assert tracking_config['agent_instance_id'] == str(mock_agent_instance.id)
            assert tracking_config['recipe_id'] == str(recipe_id)
    
    @pytest.mark.asyncio
    async def test_execute_recipe_passes_agency_team_ids(self, mock_agent_instance, mock_db_session):
        """Should pass agency_id and team_id for secret injection"""
        agent = Agent(mock_agent_instance, mock_db_session)
        
        # Mock team with agency_id
        mock_team = Mock(id=mock_agent_instance.team_id, agency_id=uuid4())
        
        with patch('agents.agent.select') as mock_select:
            team_result = Mock()
            team_result.scalar_one_or_none.return_value = mock_team
            mock_db_session.execute.return_value = team_result
            
            recipe_id = uuid4()
            recipe_mock = Mock(
                id=recipe_id,
                yaml_definition={
                    'id': 'test',
                    'name': 'Test',
                    'workflow': {'nodes': [], 'edges': []}
                }
            )
            agent.recipes = [recipe_mock]
            
            with patch('agents.agent.RecipeEvaluator') as mock_evaluator_class:
                mock_evaluator = Mock()
                mock_evaluator.execute = AsyncMock(return_value={})
                mock_evaluator_class.return_value = mock_evaluator
                
                await agent.execute_recipe(recipe_id, {})
                
                # Verify agency_id and team_id in tracking_config
                tracking_config = mock_evaluator_class.call_args[1]['tracking_config']
                assert tracking_config['agency_id'] == str(mock_team.agency_id)
                assert tracking_config['team_id'] == str(mock_agent_instance.team_id)


class TestAgentState:
    """Test agent state management"""
    
    @pytest.mark.asyncio
    async def test_active_agent_executes(self, mock_agent_instance, mock_db_session):
        """Should allow execution when agent is active"""
        mock_agent_instance.is_active = True
        agent = Agent(mock_agent_instance, mock_db_session)
        
        recipe_id = uuid4()
        recipe_mock = Mock(
            id=recipe_id,
            yaml_definition={
                'id': 'test',
                'name': 'Test',
                'workflow': {'nodes': [], 'edges': []}
            }
        )
        agent.recipes = [recipe_mock]
        
        with patch('agents.agent.RecipeEvaluator') as mock_evaluator_class:
            mock_evaluator = Mock()
            mock_evaluator.execute = AsyncMock(return_value={})
            mock_evaluator_class.return_value = mock_evaluator
            
            result = await agent.execute_recipe(recipe_id, {})
            
            # Should complete without error
            assert result is not None
    
    def test_get_configuration(self, mock_agent_instance, mock_db_session):
        """Should return agent configuration"""
        agent = Agent(mock_agent_instance, mock_db_session)
        
        config = agent.get_agent_info()['configuration']
        
        assert config['max_executions_per_day'] == 100
        assert 'groq-llama-3.1-8b-instant' in config['allowed_models']
# Agent runtime tests need refactoring - Agent class constructor changed
# Old: Agent(agent_instance, db_session)  
# New: Agent(agent_instance_id: UUID, session: AsyncSession)
# Marking as TODO for separate refactoring task
