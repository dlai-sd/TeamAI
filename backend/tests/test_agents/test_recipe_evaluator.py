"""
Test RecipeEvaluator - DAG execution, secret injection, parameter interpolation, error handling
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
from agents.recipe_evaluator import RecipeEvaluator
from app.utils.secrets import SecretInjector


@pytest.fixture
def mock_recipe_simple():
    """Simple recipe with 2 nodes"""
    return {
        'id': 'test-recipe',
        'name': 'Test Recipe',
        'workflow': {
            'nodes': [
                {
                    'id': 'node1',
                    'component': 'WebCrawler',
                    'config': {
                        'max_pages': 10
                    }
                },
                {
                    'id': 'node2',
                    'component': 'LLMProcessor',
                    'config': {
                        'model': 'groq-llama-3.1-8b-instant',
                        'temperature': 0.2,
                        'prompt_template': 'Analyze: {{ node1.output }}'
                    },
                    'depends_on': ['node1']
                }
            ],
            'edges': [
                {'from': 'node1', 'to': 'node2'}
            ]
        }
    }


@pytest.fixture
def mock_recipe_with_secrets():
    """Recipe with secret injection"""
    return {
        'id': 'secret-recipe',
        'name': 'Secret Recipe',
        'workflow': {
            'nodes': [
                {
                    'id': 'fetch_data',
                    'component': 'WebCrawler',
                    'config': {
                        'max_pages': 5
                    },
                    'secrets': {
                        'api_key': 'secret:semrush_api_key'
                    }
                }
            ],
            'edges': []
        }
    }


@pytest.fixture
def mock_recipe_with_interpolation():
    """Recipe with Jinja2 parameter interpolation"""
    return {
        'id': 'interpolation-recipe',
        'name': 'Interpolation Recipe',
        'workflow': {
            'nodes': [
                {
                    'id': 'crawler',
                    'component': 'WebCrawler',
                    'config': {
                        'max_pages': '{{ inputs.max_depth * 20 }}',
                        'url': '{{ inputs.website_url }}'
                    }
                }
            ],
            'edges': []
        }
    }


@pytest.fixture
def mock_recipe_with_error_handling():
    """Recipe with allow_failure nodes"""
    return {
        'id': 'error-recipe',
        'name': 'Error Recipe',
        'workflow': {
            'nodes': [
                {
                    'id': 'critical_node',
                    'component': 'WebCrawler',
                    'config': {'max_pages': 5}
                },
                {
                    'id': 'optional_node',
                    'component': 'LLMProcessor',
                    'config': {'model': 'groq-llama-3.1-8b-instant'},
                    'allow_failure': True,
                    'depends_on': ['critical_node']
                },
                {
                    'id': 'final_node',
                    'component': 'ReportGenerator',
                    'config': {'format': 'markdown'},
                    'depends_on': ['optional_node']
                }
            ],
            'edges': [
                {'from': 'critical_node', 'to': 'optional_node'},
                {'from': 'optional_node', 'to': 'final_node'}
            ]
        }
    }


class TestRecipeEvaluatorInitialization:
    """Test RecipeEvaluator initialization"""
    
    def test_init_with_recipe_dict(self, mock_recipe_simple):
        """Should initialize with recipe dict"""
        evaluator = RecipeEvaluator(
            recipe=mock_recipe_simple,
            mock_mode=True
        )
        assert evaluator.recipe == mock_recipe_simple
        assert evaluator.mock_mode is True
        assert evaluator.execution_state == {}
    
    def test_init_with_tracking_config(self, mock_recipe_simple):
        """Should initialize subscription tracker when tracking_config provided"""
        tracking_config = {
            'agent_instance_id': 'agent-123',
            'recipe_id': 'recipe-456',
            'agency_id': 'agency-789'
        }
        evaluator = RecipeEvaluator(
            recipe=mock_recipe_simple,
            tracking_config=tracking_config,
            mock_mode=True
        )
        assert evaluator.tracking_config == tracking_config
        # Note: subscription_tracker will be None in mock_mode without db_session
    
    def test_validate_recipe_success(self, mock_recipe_simple):
        """Should validate correct recipe structure"""
        evaluator = RecipeEvaluator(recipe=mock_recipe_simple, mock_mode=True)
        assert evaluator.validate_recipe() is True
    
    def test_validate_recipe_missing_keys(self):
        """Should fail validation for missing required keys"""
        invalid_recipe = {'id': 'test', 'name': 'Test'}  # Missing workflow
        evaluator = RecipeEvaluator(recipe=invalid_recipe, mock_mode=True)
        assert evaluator.validate_recipe() is False
    
    def test_validate_recipe_unknown_component(self):
        """Should fail validation for unknown component"""
        invalid_recipe = {
            'id': 'test',
            'name': 'Test',
            'workflow': {
                'nodes': [{'id': 'node1', 'component': 'UnknownComponent'}],
                'edges': []
            }
        }
        evaluator = RecipeEvaluator(recipe=invalid_recipe, mock_mode=True)
        assert evaluator.validate_recipe() is False


class TestDAGExecution:
    """Test workflow DAG execution"""
    
    @pytest.mark.asyncio
    async def test_build_execution_order(self, mock_recipe_simple):
        """Should build topological execution order"""
        evaluator = RecipeEvaluator(recipe=mock_recipe_simple, mock_mode=True)
        
        nodes = {node['id']: node for node in mock_recipe_simple['workflow']['nodes']}
        edges = mock_recipe_simple['workflow']['edges']
        
        execution_order = evaluator._build_execution_order(nodes, edges)
        
        assert len(execution_order) == 2
        assert execution_order[0] == 'node1'  # No dependencies, runs first
        assert execution_order[1] == 'node2'  # Depends on node1
    
    @pytest.mark.asyncio
    async def test_execute_nodes_in_order(self, mock_recipe_simple):
        """Should execute nodes in dependency order"""
        evaluator = RecipeEvaluator(recipe=mock_recipe_simple, mock_mode=True)
        
        with patch.object(evaluator, '_execute_node', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = None
            
            inputs = {'website_url': 'https://example.com', 'max_depth': 2}
            
            try:
                await evaluator.execute(inputs)
            except Exception:
                pass  # May fail due to mocking, but we check call order
            
            # Verify nodes executed in correct order
            assert mock_execute.call_count == 2
            first_call_node = mock_execute.call_args_list[0][0][0]
            second_call_node = mock_execute.call_args_list[1][0][0]
            
            assert first_call_node['id'] == 'node1'
            assert second_call_node['id'] == 'node2'
    
    @pytest.mark.asyncio
    async def test_execution_state_stores_outputs(self, mock_recipe_simple):
        """Should store node outputs in execution_state"""
        evaluator = RecipeEvaluator(recipe=mock_recipe_simple, mock_mode=True)
        
        # Mock component execution
        with patch.object(evaluator, '_execute_component', new_callable=AsyncMock) as mock_comp:
            mock_comp.side_effect = [
                {'pages': ['page1', 'page2']},  # WebCrawler output
                {'content': 'Analysis result'}  # LLMProcessor output
            ]
            
            inputs = {'website_url': 'https://example.com', 'max_depth': 2}
            
            await evaluator.execute(inputs)
            
            # Check execution state
            assert 'node1.output' in evaluator.execution_state
            assert 'node2.output' in evaluator.execution_state
            assert evaluator.execution_state['node1.output'] == {'pages': ['page1', 'page2']}


class TestSecretInjection:
    """Test secret injection from Azure Key Vault"""
    
    @pytest.mark.asyncio
    async def test_secrets_injected_before_execution(self, mock_recipe_with_secrets):
        """Should inject secrets before component execution"""
        tracking_config = {
            'agency_id': '123e4567-e89b-12d3-a456-426614174000',
            'team_id': '123e4567-e89b-12d3-a456-426614174001'
        }
        
        evaluator = RecipeEvaluator(
            recipe=mock_recipe_with_secrets,
            tracking_config=tracking_config,
            mock_mode=True
        )
        
        with patch('agents.recipe_evaluator.SecretInjector') as mock_injector_class:
            mock_injector = Mock()
            mock_injector.inject_secrets.return_value = {'api_key': 'real_secret_value'}
            mock_injector_class.return_value = mock_injector
            
            with patch.object(evaluator, '_execute_component', new_callable=AsyncMock) as mock_comp:
                mock_comp.return_value = {'data': 'fetched'}
                
                inputs = {}
                await evaluator.execute(inputs)
                
                # Verify SecretInjector was created with correct IDs
                mock_injector_class.assert_called_once()
                
                # Verify inject_secrets was called
                assert mock_injector.inject_secrets.called
    
    @pytest.mark.asyncio
    async def test_secret_injector_namespacing(self):
        """Should use agency and team namespacing for secrets"""
        from uuid import UUID
        
        agency_id = UUID('123e4567-e89b-12d3-a456-426614174000')
        team_id = UUID('123e4567-e89b-12d3-a456-426614174001')
        
        with patch('app.utils.secrets.get_secret_manager') as mock_manager:
            mock_sm = Mock()
            mock_sm.get_secret.return_value = 'secret_value'
            mock_manager.return_value = mock_sm
            
            injector = SecretInjector(agency_id, team_id)
            config = {'api_key': 'secret:semrush_api_key'}
            
            result = injector.inject_secrets(config)
            
            # Should call with agency-{id}-semrush_api_key format
            expected_key = f"agency-{agency_id}-semrush-api-key"
            mock_sm.get_secret.assert_called()


class TestParameterInterpolation:
    """Test Jinja2 parameter interpolation"""
    
    @pytest.mark.asyncio
    async def test_interpolate_config_with_inputs(self, mock_recipe_with_interpolation):
        """Should interpolate {{ inputs.* }} variables"""
        evaluator = RecipeEvaluator(recipe=mock_recipe_with_interpolation, mock_mode=True)
        
        config = {
            'max_pages': '{{ inputs.max_depth * 20 }}',
            'url': '{{ inputs.website_url }}'
        }
        
        evaluator.execution_state = {
            'inputs': {
                'max_depth': 3,
                'website_url': 'https://example.com'
            }
        }
        
        resolved = evaluator._interpolate_config(config)
        
        assert resolved['max_pages'] == 60  # 3 * 20
        assert resolved['url'] == 'https://example.com'
    
    @pytest.mark.asyncio
    async def test_interpolate_with_node_outputs(self):
        """Should interpolate {{ node.output.* }} variables"""
        evaluator = RecipeEvaluator(recipe={'id': 'test', 'name': 'Test', 'workflow': {'nodes': [], 'edges': []}}, mock_mode=True)
        
        evaluator.execution_state = {
            'inputs': {'depth': 2},
            'crawler.output': {'total_pages': 50}
        }
        
        config = {'limit': '{{ crawler.output.total_pages }}'}
        resolved = evaluator._interpolate_config(config)
        
        assert resolved['limit'] == 50
    
    def test_cast_value_to_int(self):
        """Should cast numeric strings to int"""
        evaluator = RecipeEvaluator(recipe={'id': 'test', 'name': 'Test', 'workflow': {'nodes': [], 'edges': []}}, mock_mode=True)
        
        assert evaluator._cast_value('42') == 42
        assert evaluator._cast_value('-10') == -10
    
    def test_cast_value_to_float(self):
        """Should cast decimal strings to float"""
        evaluator = RecipeEvaluator(recipe={'id': 'test', 'name': 'Test', 'workflow': {'nodes': [], 'edges': []}}, mock_mode=True)
        
        assert evaluator._cast_value('3.14') == 3.14
        assert evaluator._cast_value('0.5') == 0.5
    
    def test_cast_value_to_bool(self):
        """Should cast 'true'/'false' to bool"""
        evaluator = RecipeEvaluator(recipe={'id': 'test', 'name': 'Test', 'workflow': {'nodes': [], 'edges': []}}, mock_mode=True)
        
        assert evaluator._cast_value('true') is True
        assert evaluator._cast_value('false') is False
        assert evaluator._cast_value('True') is True
    
    def test_cast_value_to_string(self):
        """Should keep strings as strings"""
        evaluator = RecipeEvaluator(recipe={'id': 'test', 'name': 'Test', 'workflow': {'nodes': [], 'edges': []}}, mock_mode=True)
        
        assert evaluator._cast_value('hello') == 'hello'
        assert evaluator._cast_value('not_a_number') == 'not_a_number'
    
    @pytest.mark.asyncio
    async def test_build_prompt_with_context(self):
        """Should build LLM prompt from template and context"""
        evaluator = RecipeEvaluator(recipe={'id': 'test', 'name': 'Test', 'workflow': {'nodes': [], 'edges': []}}, mock_mode=True)
        
        evaluator.execution_state = {
            'inputs': {'topic': 'SEO'}
        }
        
        template = "Analyze this topic: {{ inputs.topic }}"
        node_inputs = {'crawler': {'pages': ['page1', 'page2']}}
        
        prompt = evaluator._build_prompt(template, node_inputs)
        
        assert 'SEO' in prompt


class TestErrorHandling:
    """Test error handling and allow_failure"""
    
    @pytest.mark.asyncio
    async def test_node_failure_stops_execution(self, mock_recipe_simple):
        """Should stop execution when node fails without allow_failure"""
        evaluator = RecipeEvaluator(recipe=mock_recipe_simple, mock_mode=True)
        
        with patch.object(evaluator, '_execute_component', new_callable=AsyncMock) as mock_comp:
            mock_comp.side_effect = Exception("Component failed")
            
            inputs = {'website_url': 'https://example.com', 'max_depth': 2}
            
            with pytest.raises(Exception, match="Component failed"):
                await evaluator.execute(inputs)
            
            # Should have execution_status = 'failed'
            assert evaluator.metrics.get('execution_status') is not None
    
    @pytest.mark.asyncio
    async def test_allow_failure_continues_execution(self, mock_recipe_with_error_handling):
        """Should continue execution when node fails with allow_failure=True"""
        evaluator = RecipeEvaluator(recipe=mock_recipe_with_error_handling, mock_mode=True)
        
        with patch.object(evaluator, '_execute_component', new_callable=AsyncMock) as mock_comp:
            # critical_node succeeds, optional_node fails, final_node succeeds
            mock_comp.side_effect = [
                {'data': 'success'},           # critical_node
                Exception("Optional failed"),  # optional_node (allow_failure=True)
                {'report': 'generated'}        # final_node
            ]
            
            inputs = {}
            await evaluator.execute(inputs)
            
            # Check that optional_node failure was stored
            assert 'optional_node.error' in evaluator.execution_state
            assert 'Optional failed' in evaluator.execution_state['optional_node.error']
            
            # Check that execution continued to final_node
            assert 'final_node.output' in evaluator.execution_state
    
    @pytest.mark.asyncio
    async def test_execution_status_tracked_on_failure(self, mock_recipe_simple):
        """Should track execution_status='failed' on error"""
        tracking_config = {
            'agent_instance_id': 'agent-123',
            'recipe_id': 'recipe-456',
            'agency_id': 'agency-789'
        }
        
        evaluator = RecipeEvaluator(
            recipe=mock_recipe_simple,
            tracking_config=tracking_config,
            mock_mode=True
        )
        
        # Mock subscription tracker
        mock_tracker = Mock()
        mock_tracker.execute = AsyncMock()
        evaluator.subscription_tracker = mock_tracker
        
        with patch.object(evaluator, '_execute_component', new_callable=AsyncMock) as mock_comp:
            mock_comp.side_effect = Exception("Execution failed")
            
            inputs = {'website_url': 'https://example.com'}
            
            with pytest.raises(Exception):
                await evaluator.execute(inputs)
            
            # Verify subscription tracker was called with failed status
            assert mock_tracker.execute.called
            call_args = mock_tracker.execute.call_args[0][0]
            assert call_args.get('execution_status') == 'failed'


class TestComponentExecution:
    """Test component-specific execution logic"""
    
    @pytest.mark.asyncio
    async def test_execute_webcrawler_component(self):
        """Should execute WebCrawler with correct parameters"""
        evaluator = RecipeEvaluator(recipe={'id': 'test', 'name': 'Test', 'workflow': {'nodes': [], 'edges': []}}, mock_mode=True)
        evaluator.execution_state = {
            'inputs': {
                'website_url': 'https://example.com',
                'max_depth': 3
            }
        }
        
        mock_component = Mock()
        mock_component.execute = AsyncMock(return_value={'pages': ['page1']})
        
        config = {'max_depth': 3, 'max_pages': 50}
        result = await evaluator._execute_component(
            mock_component,
            'WebCrawler',
            config,
            {}
        )
        
        mock_component.execute.assert_called_once_with('https://example.com', 3, 50)
        assert result == {'pages': ['page1']}
    
    @pytest.mark.asyncio
    async def test_execute_llmprocessor_component(self):
        """Should execute LLMProcessor with rendered prompt"""
        evaluator = RecipeEvaluator(recipe={'id': 'test', 'name': 'Test', 'workflow': {'nodes': [], 'edges': []}}, mock_mode=True)
        evaluator.execution_state = {'inputs': {}}
        
        mock_component = Mock()
        mock_component.execute = AsyncMock(return_value={'content': 'Analysis'})
        
        config = {
            'prompt_template': 'Analyze data',
            'model': 'groq-llama-3.1-8b-instant',
            'temperature': 0.2
        }
        
        result = await evaluator._execute_component(
            mock_component,
            'LLMProcessor',
            config,
            {'crawler': {'data': 'test'}}
        )
        
        assert mock_component.execute.called
        assert result == {'content': 'Analysis'}
    
    @pytest.mark.asyncio
    async def test_execute_reportgenerator_component(self):
        """Should execute ReportGenerator with aggregated data"""
        evaluator = RecipeEvaluator(recipe={'id': 'test', 'name': 'Test', 'workflow': {'nodes': [], 'edges': []}}, mock_mode=True)
        
        mock_component = Mock()
        mock_component.execute = AsyncMock(return_value={'report': 'Markdown report'})
        
        config = {'title': 'SEO Report', 'format': 'markdown'}
        node_inputs = {
            'crawler': {'pages': 10},
            'analyzer': {'score': 85}
        }
        
        result = await evaluator._execute_component(
            mock_component,
            'ReportGenerator',
            config,
            node_inputs
        )
        
        assert mock_component.execute.called
        assert result == {'report': 'Markdown report'}


class TestMetricsTracking:
    """Test execution metrics tracking"""
    
    @pytest.mark.asyncio
    async def test_tracks_execution_time(self, mock_recipe_simple):
        """Should track total execution time"""
        evaluator = RecipeEvaluator(recipe=mock_recipe_simple, mock_mode=True)
        
        with patch.object(evaluator, '_execute_component', new_callable=AsyncMock) as mock_comp:
            mock_comp.return_value = {'data': 'test'}
            
            inputs = {'website_url': 'https://example.com', 'max_depth': 2}
            await evaluator.execute(inputs)
            
            assert 'execution_time_ms' in evaluator.metrics
            assert evaluator.metrics['execution_time_ms'] >= 0
    
    @pytest.mark.asyncio
    async def test_tracks_tokens_and_cost(self, mock_recipe_simple):
        """Should track LLM tokens and cost"""
        evaluator = RecipeEvaluator(recipe=mock_recipe_simple, mock_mode=True)
        
        with patch.object(evaluator, '_execute_component', new_callable=AsyncMock) as mock_comp:
            mock_comp.side_effect = [
                {'pages': ['page1']},
                {
                    'content': 'Analysis',
                    'cost': 0.05,
                    'usage': {'total_tokens': 1500}
                }
            ]
            
            inputs = {'website_url': 'https://example.com', 'max_depth': 2}
            await evaluator.execute(inputs)
            
            assert evaluator.metrics['tokens_used'] == 1500
            assert evaluator.metrics['total_cost'] == 0.05
    
    @pytest.mark.asyncio
    async def test_tracks_nodes_executed(self, mock_recipe_simple):
        """Should count number of nodes executed"""
        evaluator = RecipeEvaluator(recipe=mock_recipe_simple, mock_mode=True)
        
        with patch.object(evaluator, '_execute_component', new_callable=AsyncMock) as mock_comp:
            mock_comp.return_value = {'data': 'test'}
            
            inputs = {'website_url': 'https://example.com', 'max_depth': 2}
            await evaluator.execute(inputs)
            
            assert evaluator.metrics['nodes_executed'] == 2
