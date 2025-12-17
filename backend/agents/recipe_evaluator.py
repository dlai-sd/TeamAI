"""
Recipe Evaluator
Executes YAML-defined recipes using LangGraph with mandatory subscription tracking
"""
import yaml
import asyncio
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Import our components
from components.processors.web_crawler import WebCrawler
from components.processors.llm_processor import LLMProcessor
from components.processors.report_generator import ReportGenerator
from components.subscription_tracker import SubscriptionTracker


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
    
    def __init__(self, recipe_path: str, mock_mode: bool = False, tracking_config: Optional[Dict[str, Any]] = None):
        """
        Initialize recipe evaluator
        
        Args:
            recipe_path: Path to YAML recipe file
            mock_mode: If True, use mock data instead of real API calls
            tracking_config: Configuration for subscription tracking (agency_id, agent_instance_id)
        """
        self.recipe_path = Path(recipe_path)
        self.mock_mode = mock_mode
        self.tracking_config = tracking_config or {}
        self.recipe = self._load_recipe()
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
            'recipe_id': self.recipe.get('id') if hasattr(self, 'recipe') else None,
            'agency_id': self.tracking_config.get('agency_id')
        }
        
        return SubscriptionTracker(config=tracker_config, mock_mode=self.mock_mode)
    
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
        Execute recipe with given inputs
        
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
        
        # Execute workflow as DAG
        workflow = self.recipe['workflow']
        nodes = {node['id']: node for node in workflow['nodes']}
        
        # Build execution order from edges
        execution_order = self._build_execution_order(nodes, workflow['edges'])
        
        # Execute nodes in order
        for node_id in execution_order:
            await self._execute_node(nodes[node_id])
        
        # Calculate final metrics
        self.metrics['end_time'] = datetime.utcnow()
        self.metrics['execution_time_ms'] = int(
            (self.metrics['end_time'] - self.metrics['start_time']).total_seconds() * 1000
        )
        
        # MANDATORY: Track execution for billing (compliance layer)
        execution_status = 'success'
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
                print(f"✅ Subscription tracked: {tracking_result.get('billable_units', 0)} units")
            except Exception as e:
                print(f"⚠️  Subscription tracking failed: {e}")
                # Continue execution but log the failure
        
        # Get output from workflow
        output_node = workflow.get('output', {})
        output_source = output_node.get('source', 'final_node.output')
        final_output = self._resolve_output(output_source)
        
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
        """Execute a single workflow node"""
        node_id = node['id']
        component_name = node['component']
        config = node.get('config', {})
        
        print(f"📦 Executing Node: {node_id} ({component_name})")
        
        # Replace template variables in config
        resolved_config = self._resolve_config(config)
        
        # Instantiate component
        component_class = self.COMPONENTS[component_name]
        component = component_class(config=resolved_config, mock_mode=self.mock_mode)
        
        # Get inputs from depends_on nodes
        depends_on = node.get('depends_on', [])
        node_inputs = {}
        for dep in depends_on:
            if f"{dep}.output" in self.execution_state:
                node_inputs[dep] = self.execution_state[f"{dep}.output"]
        
        # Execute component
        try:
            # Determine what to pass to component
            if component_name == 'WebCrawler':
                # WebCrawler needs URL and max_depth
                url = self.execution_state['inputs'].get('website_url')
                max_depth = self.execution_state['inputs'].get('max_depth', 2)
                result = await component.execute(url, max_depth)
            
            elif component_name == 'LLMProcessor':
                # LLMProcessor needs prompt (may include data from previous nodes)
                prompt_template = node.get('config', {}).get('prompt_template', '')
                prompt = self._build_prompt(prompt_template, node_inputs)
                result = await component.execute(prompt)
                
                # Track LLM metrics
                self.metrics['total_cost'] += result.get('cost', 0)
                self.metrics['tokens_used'] += result.get('usage', {}).get('total_tokens', 0)
            
            elif component_name == 'ReportGenerator':
                # ReportGenerator needs data from analysis
                report_data = self._build_report_data(node_inputs)
                title = config.get('title', 'Agent Report')
                result = await component.execute(report_data, title)
            
            else:
                # Generic execution
                result = await component.execute(**node_inputs)
            
            # Store result in execution state
            self.execution_state[f"{node_id}.output"] = result
            self.metrics['nodes_executed'] += 1
            
            print(f"✅ Node {node_id} completed\n")
            
        except Exception as e:
            print(f"❌ Node {node_id} failed: {str(e)}\n")
            raise
    
    def _resolve_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve template variables in config"""
        resolved = {}
        for key, value in config.items():
            if isinstance(value, str) and '{{' in value:
                # Template variable like {{ inputs.website_url }}
                resolved[key] = self._resolve_template(value)
            else:
                resolved[key] = value
        return resolved
    
    def _resolve_template(self, template: str) -> Any:
        """Resolve template variable"""
        # Simple template resolution
        import re
        pattern = r'\{\{\s*([^}]+)\s*\}\}'
        matches = re.findall(pattern, template)
        
        result = template
        for match in matches:
            parts = match.strip().split('.')
            value = self.execution_state
            for part in parts:
                value = value.get(part, '')
            result = result.replace(f'{{{{ {match} }}}}', str(value))
        
        # Try to convert to appropriate type
        if result.isdigit():
            return int(result)
        try:
            return float(result)
        except ValueError:
            pass
        if result.lower() in ('true', 'false'):
            return result.lower() == 'true'
        
        return result
    
    def _build_prompt(self, template: str, node_inputs: Dict) -> str:
        """Build LLM prompt from template and inputs"""
        # Replace {node.output} placeholders
        prompt = template
        for node_id, data in node_inputs.items():
            placeholder = f'{{{node_id}.output}}'
            if placeholder in prompt:
                # Convert data to string representation
                if isinstance(data, dict):
                    import json
                    data_str = json.dumps(data, indent=2)
                else:
                    data_str = str(data)
                prompt = prompt.replace(placeholder, data_str)
        
        return prompt
    
    def _build_report_data(self, node_inputs: Dict) -> Dict[str, Any]:
        """Build report data from analysis results"""
        report_data = {}
        
        for node_id, data in node_inputs.items():
            if isinstance(data, dict):
                # Extract LLM analysis content
                if 'content' in data:
                    report_data['analysis'] = data['content']
                    report_data['model_used'] = data.get('model', 'unknown')
                
                # Extract crawler data
                if 'pages' in data:
                    report_data['pages_analyzed'] = data.get('total_pages', 0)
                    report_data['detailed_data'] = {
                        'pages': data['pages'][:3]  # Include first 3 pages
                    }
        
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
