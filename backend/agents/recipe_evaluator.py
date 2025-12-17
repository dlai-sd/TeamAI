"""
Recipe Evaluator
Executes YAML-defined recipes using LangGraph with mandatory subscription tracking
"""
import yaml
import asyncio
import sys
import re
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from datetime import datetime
from jinja2 import Template, TemplateError

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Import our components
from components.processors.web_crawler import WebCrawler
from components.processors.llm_processor import LLMProcessor
from components.processors.report_generator import ReportGenerator
from components.subscription_tracker import SubscriptionTracker
from app.utils.secrets import SecretInjector


class RecipeEvaluator:
    """
    Executes agent recipes defined in YAML
    Core of the agent runtime engine
    """
    
    # Component registry
    COMPONENTS = {
        'WebCrawler': WebCrawler,
        'LLMProcessor': LLMProcessor,
        'ReportGenerator': ReportGenerator,
        'SubscriptionTracker': SubscriptionTracker
    }
    
    def __init__(
        self, 
        recipe_path: Optional[str] = None,
        recipe_definition: Optional[Dict[str, Any]] = None,
        mock_mode: bool = False, 
        tracking_config: Optional[Dict[str, Any]] = None,
        db_session: Optional[Any] = None
    ):
        """
        Initialize recipe evaluator
        
        Args:
            recipe_path: Path to YAML recipe file (deprecated - use recipe_definition)
            recipe_definition: Pre-loaded recipe dictionary (from database)
            mock_mode: If True, use mock data instead of real API calls
            tracking_config: Configuration for subscription tracking (agency_id, agent_instance_id, recipe_id)
            db_session: Optional AsyncSession for database persistence
        """
        if recipe_path:
            # Legacy mode - load from file
            self.recipe_path = Path(recipe_path)
            self.recipe = self._load_recipe()
        elif recipe_definition:
            # New mode - use pre-loaded definition (from database)
            self.recipe_path = None
            # Handle both {recipe: {...}} and {...} formats
            self.recipe = recipe_definition.get('recipe', recipe_definition)
        else:
            raise ValueError("Either recipe_path or recipe_definition must be provided")
        
        self.mock_mode = mock_mode
        self.tracking_config = tracking_config or {}
        self.db_session = db_session
        self.execution_state = {}
        self.metrics = {
            'start_time': None,
            'end_time': None,
            'execution_time_ms': 0,
            'total_cost': 0.0,
            'tokens_used': 0,
            'nodes_executed': 0
        }
        
        # Initialize subscription tracker (mandatory for billing)
        self.subscription_tracker = self._init_subscription_tracker()
    
    def _init_subscription_tracker(self) -> Optional[SubscriptionTracker]:
        """Initialize subscription tracker with tracking configuration"""
        if not self.tracking_config:
            print("[RecipeEvaluator] No tracking config provided - skipping subscription tracker")
            return None
        
        tracker_config = {
            'agent_instance_id': self.tracking_config.get('agent_instance_id'),
            'recipe_id': self.tracking_config.get('recipe_id') or (self.recipe.get('id') if hasattr(self, 'recipe') else None),
            'agency_id': self.tracking_config.get('agency_id')
        }
        
        return SubscriptionTracker(
            config=tracker_config, 
            mock_mode=self.mock_mode,
            db_session=self.db_session
        )
    
    def _load_recipe(self) -> Dict[str, Any]:
        """Load and parse YAML recipe"""
        if not self.recipe_path.exists():
            raise FileNotFoundError(f"Recipe not found: {self.recipe_path}")
        
        with open(self.recipe_path, 'r') as f:
            recipe = yaml.safe_load(f)
        
        if 'recipe' not in recipe:
            raise ValueError("Invalid recipe format - missing 'recipe' key")
        
        return recipe['recipe']
    
    def validate_recipe(self) -> bool:
        """Validate recipe structure"""
        required_keys = ['id', 'name', 'workflow']
        for key in required_keys:
            if key not in self.recipe:
                print(f"Missing required key: {key}")
                return False
        
        workflow = self.recipe['workflow']
        if 'nodes' not in workflow or 'edges' not in workflow:
            print("Invalid workflow structure")
            return False
        
        # Validate nodes
        for node in workflow['nodes']:
            if 'id' not in node or 'component' not in node:
                print(f"Invalid node structure: {node}")
                return False
            
            component_name = node['component']
            if component_name not in self.COMPONENTS:
                print(f"Unknown component: {component_name}")
                return False
        
        return True
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute recipe with given inputs (DAG workflow execution)
        
        Args:
            inputs: Input parameters defined in recipe
            
        Returns:
            Execution results with metrics
        """
        if not self.validate_recipe():
            raise ValueError("Invalid recipe")
        
        self.metrics['start_time'] = datetime.utcnow()
        self.execution_state = {'inputs': inputs}
        
        print(f"\n🚀 Executing Recipe: {self.recipe['name']}")
        print(f"Recipe ID: {self.recipe['id']}")
        print(f"Version: {self.recipe.get('version', '1.0.0')}")
        print(f"Mock Mode: {self.mock_mode}\n")
        
        try:
            # Execute workflow as DAG
            workflow = self.recipe['workflow']
            nodes = {node['id']: node for node in workflow['nodes']}
            
            # Build execution order from edges
            execution_order = self._build_execution_order(nodes, workflow['edges'])
            print(f"Execution order: {' → '.join(execution_order)}\n")
            
            # Execute nodes in order
            for node_id in execution_order:
                try:
                    await self._execute_node(nodes[node_id])
                except Exception as e:
                    # Check if node allows failure
                    allow_failure = nodes[node_id].get('allow_failure', False)
                    if allow_failure:
                        print(f"⚠️  Node {node_id} failed (allowed): {e}")
                        self.execution_state[f"{node_id}.error"] = str(e)
                        self.execution_state[f"{node_id}.status"] = 'failed'
                    else:
                        print(f"❌ Node {node_id} failed (critical): {e}")
                        raise
            
            execution_status = 'success'
            
        except Exception as e:
            execution_status = 'failed'
            print(f"\n❌ Recipe execution failed: {e}")
            
            # Calculate metrics even on failure
            self.metrics['end_time'] = datetime.utcnow()
            self.metrics['execution_time_ms'] = int(
                (self.metrics['end_time'] - self.metrics['start_time']).total_seconds() * 1000
            )
            
            # Track failure
            if self.subscription_tracker:
                try:
                    await self.subscription_tracker.execute({
                        'execution_time_ms': self.metrics['execution_time_ms'],
                        'tokens_used': self.metrics['tokens_used'],
                        'cost_incurred': self.metrics['total_cost'],
                        'status': execution_status,
                        'metadata': {'error': str(e)}
                    })
                except:
                    pass
            
            # Re-raise the exception
            raise
        
        # Calculate final metrics
        self.metrics['end_time'] = datetime.utcnow()
        self.metrics['execution_time_ms'] = int(
            (self.metrics['end_time'] - self.metrics['start_time']).total_seconds() * 1000
        )
        
        # MANDATORY: Track execution for billing (compliance layer)
        tracking_result = None
        if self.subscription_tracker:
            try:
                tracking_result = await self.subscription_tracker.execute({
                    'execution_time_ms': self.metrics['execution_time_ms'],
                    'tokens_used': self.metrics['tokens_used'],
                    'cost_incurred': self.metrics['total_cost'],
                    'status': execution_status,
                    'metadata': {
                        'nodes_executed': self.metrics['nodes_executed'],
                        'recipe_version': self.recipe.get('version', '1.0.0')
                    }
                })
                print(f"\n✅ Subscription tracked: {tracking_result.get('billable_units', 0)} units")
            except Exception as e:
                print(f"⚠️  Subscription tracking failed: {e}")
                # Continue execution but log the failure
        
        # Get output from workflow
        output_config = workflow.get('output', {})
        output_source = output_config.get('source', 'final_node.output')
        final_output = self._resolve_output(output_source)
        
        print(f"\n✅ Recipe execution complete in {self.metrics['execution_time_ms']}ms")
        
        return {
            'success': True,
            'recipe_id': self.recipe['id'],
            'output': final_output,
            'metrics': self.metrics,
            'tracking': tracking_result,
            'execution_state': self.execution_state
        }
    
    def _build_execution_order(self, nodes: Dict, edges: List[Dict]) -> List[str]:
        """
        Build execution order from DAG edges
        Simple topological sort
        """
        # Build adjacency list
        dependencies = {node_id: [] for node_id in nodes.keys()}
        for edge in edges:
            to_node = edge['to']
            from_node = edge['from']
            if to_node not in dependencies[from_node]:
                dependencies[to_node].append(from_node)
        
        # Topological sort
        visited = set()
        order = []
        
        def visit(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            for dep in dependencies.get(node_id, []):
                visit(dep)
            order.append(node_id)
        
        for node_id in nodes.keys():
            visit(node_id)
        
        return order
    
    async def _execute_node(self, node: Dict[str, Any]):
        """
        Execute a single workflow node with secret injection and parameter interpolation
        
        Args:
            node: Node configuration from workflow
        """
        node_id = node['id']
        component_name = node['component']
        config = node.get('config', {})
        secrets = node.get('secrets', {})
        
        print(f"📦 Executing Node: {node_id} ({component_name})")
        
        try:
            # Step 1: Inject secrets from Azure Key Vault
            if secrets and self.tracking_config:
                agency_id = self.tracking_config.get('agency_id')
                team_id = self.tracking_config.get('team_id')
                if agency_id:
                    secret_injector = SecretInjector(agency_id, team_id)
                    secrets = secret_injector.inject_secrets(secrets)
                    print(f"  🔐 Secrets injected: {list(secrets.keys())}")
            
            # Step 2: Interpolate config parameters with Jinja2
            resolved_config = self._interpolate_config(config)
            
            # Merge secrets into config
            resolved_config.update(secrets)
            
            # Step 3: Instantiate component
            component_class = self.COMPONENTS[component_name]
            component = component_class(config=resolved_config, mock_mode=self.mock_mode)
            
            # Step 4: Get inputs from depends_on nodes
            depends_on = node.get('depends_on', [])
            node_inputs = {}
            for dep in depends_on:
                if f"{dep}.output" in self.execution_state:
                    node_inputs[dep] = self.execution_state[f"{dep}.output"]
            
            # Step 5: Execute component based on type
            result = await self._execute_component(
                component, 
                component_name, 
                resolved_config, 
                node_inputs
            )
            
            # Step 6: Store result in execution state
            self.execution_state[f"{node_id}.output"] = result
            self.execution_state[f"{node_id}.status"] = 'success'
            self.metrics['nodes_executed'] += 1
            
            # Track LLM costs
            if isinstance(result, dict):
                if 'cost' in result:
                    self.metrics['total_cost'] += result.get('cost', 0)
                if 'usage' in result:
                    self.metrics['tokens_used'] += result.get('usage', {}).get('total_tokens', 0)
            
            print(f"  ✅ Node {node_id} completed\n")
            
        except Exception as e:
            print(f"  ❌ Node {node_id} failed: {str(e)}\n")
            self.execution_state[f"{node_id}.status"] = 'failed'
            self.execution_state[f"{node_id}.error"] = str(e)
            raise
    
    async def _execute_component(
        self, 
        component, 
        component_name: str, 
        config: Dict[str, Any],
        node_inputs: Dict[str, Any]
    ) -> Any:
        """
        Execute component based on its type
        
        Args:
            component: Component instance
            component_name: Component class name
            config: Resolved configuration
            node_inputs: Outputs from dependent nodes
            
        Returns:
            Component execution result
        """
        if component_name == 'WebCrawler':
            # WebCrawler needs URL and max_depth
            url = self.execution_state['inputs'].get('website_url')
            max_depth = config.get('max_depth') or self.execution_state['inputs'].get('max_depth', 2)
            max_pages = config.get('max_pages', 50)
            return await component.execute(url, max_depth, max_pages)
        
        elif component_name == 'LLMProcessor':
            # LLMProcessor needs prompt (may include data from previous nodes)
            prompt_template = config.get('prompt_template', '')
            prompt = self._build_prompt(prompt_template, node_inputs)
            
            model = config.get('model', 'groq-llama-3.1-8b-instant')
            temperature = config.get('temperature', 0.2)
            
            return await component.execute(
                prompt=prompt,
                model=model,
                temperature=temperature
            )
        
        elif component_name == 'ReportGenerator':
            # ReportGenerator needs data from analysis
            report_data = self._build_report_data(node_inputs)
            title = config.get('title', 'Agent Report')
            format_type = config.get('format', 'markdown')
            
            return await component.execute(
                data=report_data,
                title=title,
                format=format_type
            )
        
        elif component_name == 'SubscriptionTracker':
            # Subscription tracking (mandatory compliance)
            return await component.execute(node_inputs)
        
        else:
            # Generic execution - pass all node_inputs
            return await component.execute(**node_inputs)
    
    def _interpolate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpolate config parameters using Jinja2 templates
        
        Supports:
        - {{ inputs.website_url }}
        - {{ inputs.max_depth * 20 }}
        - {{ fetch_pages.output.total_pages }}
        
        Args:
            config: Configuration dict with template strings
            
        Returns:
            Resolved configuration
        """
        resolved = {}
        
        # Build template context
        context = {
            'inputs': self.execution_state.get('inputs', {}),
            'config': self.config if hasattr(self, 'config') else {}
        }
        
        # Add node outputs to context
        for key, value in self.execution_state.items():
            if '.output' in key:
                node_name = key.replace('.output', '')
                context[node_name] = {'output': value}
        
        for key, value in config.items():
            if isinstance(value, str) and '{{' in value and '}}' in value:
                try:
                    # Render with Jinja2
                    template = Template(value)
                    rendered = template.render(**context)
                    
                    # Try to convert to appropriate type
                    resolved[key] = self._cast_value(rendered)
                    
                except TemplateError as e:
                    print(f"  ⚠️  Template error in {key}: {e}")
                    resolved[key] = value
            elif isinstance(value, dict):
                # Recursively interpolate nested dicts
                resolved[key] = self._interpolate_config(value)
            else:
                resolved[key] = value
        
        return resolved
    
    def _cast_value(self, value: str) -> Any:
        """Cast string value to appropriate type"""
        # Try integer
        if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
            return int(value)
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Return as string
        return value
    
    def _build_prompt(self, template: str, node_inputs: Dict) -> str:
        """
        Build LLM prompt from template and node inputs
        
        Args:
            template: Prompt template with placeholders
            node_inputs: Outputs from dependent nodes
            
        Returns:
            Rendered prompt
        """
        # Build context
        context = {
            'inputs': self.execution_state.get('inputs', {})
        }
        context.update(node_inputs)
        
        try:
            # Render with Jinja2
            jinja_template = Template(template)
            return jinja_template.render(**context)
        except TemplateError as e:
            print(f"  ⚠️  Prompt template error: {e}")
            return template
    
    def _build_report_data(self, node_inputs: Dict) -> Dict[str, Any]:
        """Build report data from node outputs"""
        report_data = {}
        for node_id, output in node_inputs.items():
            if isinstance(output, dict):
                report_data.update(output)
            else:
                report_data[node_id] = output
        return report_data
    
    def _resolve_output(self, output_source: str) -> Any:
        """Resolve final output from execution state"""
        if output_source in self.execution_state:
            return self.execution_state[output_source]
        
        # Try to find last node output
        for key in reversed(list(self.execution_state.keys())):
            if key.endswith('.output'):
                return self.execution_state[key]
        
        return self.execution_state

