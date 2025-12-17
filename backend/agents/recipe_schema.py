"""
Recipe YAML Schema Validation (Pydantic)
Ensures recipes conform to expected structure before execution
"""
from pydantic import BaseModel, Field, validator, root_validator
from typing import Dict, Any, List, Optional, Union
from enum import Enum


class InputType(str, Enum):
    """Allowed input types for recipe parameters"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class InputValidation(str, Enum):
    """Input validation rules"""
    URL = "url"
    EMAIL = "email"
    UUID = "uuid"
    NONE = "none"


class RecipeInputSchema(BaseModel):
    """Schema for recipe input parameter"""
    name: str = Field(..., description="Parameter name")
    type: InputType = Field(..., description="Data type")
    required: bool = Field(True, description="Whether parameter is required")
    default: Optional[Any] = Field(None, description="Default value if not provided")
    validation: Optional[InputValidation] = Field(None, description="Validation rule")
    range: Optional[List[Union[int, float]]] = Field(None, description="Min/max range for numeric types")
    description: Optional[str] = Field(None, description="Human-readable description")
    
    @validator('range')
    def validate_range(cls, v, values):
        """Ensure range has exactly 2 elements [min, max]"""
        if v is not None and len(v) != 2:
            raise ValueError("Range must have exactly 2 elements [min, max]")
        if v is not None and v[0] >= v[1]:
            raise ValueError("Range min must be less than max")
        return v
    
    @validator('default')
    def validate_default_type(cls, v, values):
        """Ensure default value matches declared type"""
        if v is None:
            return v
        
        input_type = values.get('type')
        if input_type == InputType.STRING and not isinstance(v, str):
            raise ValueError(f"Default value must be string, got {type(v)}")
        elif input_type == InputType.INTEGER and not isinstance(v, int):
            raise ValueError(f"Default value must be integer, got {type(v)}")
        elif input_type == InputType.FLOAT and not isinstance(v, (int, float)):
            raise ValueError(f"Default value must be float, got {type(v)}")
        elif input_type == InputType.BOOLEAN and not isinstance(v, bool):
            raise ValueError(f"Default value must be boolean, got {type(v)}")
        
        return v


class WorkflowNodeSchema(BaseModel):
    """Schema for recipe workflow node"""
    id: str = Field(..., description="Unique node identifier")
    component: str = Field(..., description="Component class name (WebCrawler, LLMProcessor, etc.)")
    config: Dict[str, Any] = Field(default_factory=dict, description="Component configuration")
    secrets: Optional[Dict[str, str]] = Field(None, description="Secret references (secret:key_name)")
    depends_on: Optional[List[str]] = Field(None, description="Node IDs this node depends on")
    
    @validator('component')
    def validate_component(cls, v):
        """Ensure component is registered"""
        valid_components = [
            'WebCrawler', 'LLMProcessor', 'ReportGenerator',
            'SubscriptionTracker', 'DataFetcher', 'WebsiteConnector'
        ]
        if v not in valid_components:
            raise ValueError(f"Unknown component: {v}. Valid: {valid_components}")
        return v


class WorkflowEdgeSchema(BaseModel):
    """Schema for recipe workflow edge (defines execution order)"""
    from_node: str = Field(..., alias="from", description="Source node ID")
    to_node: str = Field(..., alias="to", description="Target node ID")
    
    class Config:
        allow_population_by_field_name = True


class WorkflowOutputSchema(BaseModel):
    """Schema for recipe output definition"""
    type: str = Field(..., description="Output type (report, data, file)")
    format: Optional[str] = Field(None, description="Output format (markdown, json, pdf)")
    source: str = Field(..., description="Node output to use (e.g., 'generate_report.output')")


class WorkflowSchema(BaseModel):
    """Schema for recipe workflow (LangGraph DAG)"""
    nodes: List[WorkflowNodeSchema] = Field(..., description="Workflow nodes")
    edges: List[WorkflowEdgeSchema] = Field(..., description="Workflow edges (execution order)")
    output: WorkflowOutputSchema = Field(..., description="Final output definition")
    
    @root_validator(skip_on_failure=True)
    def validate_workflow_graph(cls, values):
        """Validate workflow is a valid DAG"""
        nodes = values.get('nodes', [])
        edges = values.get('edges', [])
        
        # Build node ID set
        node_ids = {node.id for node in nodes}
        
        # Validate edges reference existing nodes
        for edge in edges:
            if edge.from_node not in node_ids:
                raise ValueError(f"Edge references unknown source node: {edge.from_node}")
            if edge.to_node not in node_ids:
                raise ValueError(f"Edge references unknown target node: {edge.to_node}")
        
        # Validate depends_on references
        for node in nodes:
            if node.depends_on:
                for dep in node.depends_on:
                    if dep not in node_ids:
                        raise ValueError(f"Node {node.id} depends on unknown node: {dep}")
        
        # Validate output source references existing node
        output = values.get('output')
        if output:
            output_node_id = output.source.split('.')[0]
            if output_node_id not in node_ids:
                raise ValueError(f"Output references unknown node: {output_node_id}")
        
        return values


class ComplianceSchema(BaseModel):
    """Schema for recipe compliance/tracking configuration"""
    track_usage: bool = Field(True, description="Enable subscription tracking")
    billable_units: str = Field("per_execution", description="Billing model (per_execution, per_token, per_minute)")
    cost_per_unit: float = Field(..., description="Cost per billable unit in USD")


class ABTestingSchema(BaseModel):
    """Schema for A/B testing configuration"""
    enabled: bool = Field(False, description="Enable A/B testing")
    variants: Optional[List[str]] = Field(None, description="Recipe versions to test (e.g., ['v1.2.0', 'v1.3.0-beta'])")
    success_metric: Optional[str] = Field(None, description="Metric to optimize (quality_score, execution_time, token_cost)")


class RecipeSchema(BaseModel):
    """Complete recipe YAML schema validation"""
    id: str = Field(..., description="Unique recipe identifier")
    name: str = Field(..., description="Human-readable recipe name")
    description: str = Field(..., description="Recipe description")
    cookbook: str = Field(..., description="Parent cookbook ID")
    version: str = Field(..., description="Semantic version (e.g., '1.0.0')")
    inputs: List[RecipeInputSchema] = Field(..., description="Input parameter definitions")
    workflow: WorkflowSchema = Field(..., description="Execution workflow (DAG)")
    compliance: ComplianceSchema = Field(..., description="Tracking/billing configuration")
    ab_testing: Optional[ABTestingSchema] = Field(None, description="A/B testing configuration")
    
    @validator('version')
    def validate_semver(cls, v):
        """Validate semantic versioning format"""
        parts = v.split('.')
        if len(parts) < 2 or len(parts) > 3:
            raise ValueError(f"Version must be semver format (e.g., '1.0.0'), got: {v}")
        return v


class CookbookSchema(BaseModel):
    """Complete cookbook YAML schema validation"""
    id: str = Field(..., description="Unique cookbook identifier")
    name: str = Field(..., description="Human-readable cookbook name")
    description: str = Field(..., description="Cookbook description")
    version: str = Field(..., description="Semantic version")
    author: str = Field(..., description="Cookbook author/organization")
    required_secrets: List[str] = Field(default_factory=list, description="Required secret keys")
    allowed_data_sources: List[Dict[str, Any]] = Field(default_factory=list, description="Allowed data source configurations")
    recipes: List[str] = Field(..., description="Recipe IDs included in cookbook")
    subscription_limits: Dict[str, Any] = Field(default_factory=dict, description="Subscription tier limits")
    pricing: Optional[Dict[str, Any]] = Field(None, description="Pricing information")
    
    @validator('version')
    def validate_semver(cls, v):
        """Validate semantic versioning format"""
        parts = v.split('.')
        if len(parts) < 2 or len(parts) > 3:
            raise ValueError(f"Version must be semver format (e.g., '1.0.0'), got: {v}")
        return v


def validate_recipe_yaml(recipe_data: Dict[str, Any]) -> RecipeSchema:
    """
    Validate recipe YAML structure
    
    Args:
        recipe_data: Parsed YAML dictionary (should have 'recipe' key)
        
    Returns:
        Validated RecipeSchema instance
        
    Raises:
        ValidationError: If recipe structure is invalid
    """
    # Handle both {recipe: {...}} and {...} formats
    if 'recipe' in recipe_data:
        recipe_data = recipe_data['recipe']
    
    return RecipeSchema(**recipe_data)


def validate_cookbook_yaml(cookbook_data: Dict[str, Any]) -> CookbookSchema:
    """
    Validate cookbook YAML structure
    
    Args:
        cookbook_data: Parsed YAML dictionary (should have 'cookbook' key)
        
    Returns:
        Validated CookbookSchema instance
        
    Raises:
        ValidationError: If cookbook structure is invalid
    """
    # Handle both {cookbook: {...}} and {...} formats
    if 'cookbook' in cookbook_data:
        cookbook_data = cookbook_data['cookbook']
    
    return CookbookSchema(**cookbook_data)


def validate_recipe_inputs(recipe: RecipeSchema, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user-provided inputs against recipe schema
    
    Args:
        recipe: Validated recipe schema
        inputs: User-provided input dictionary
        
    Returns:
        Validated inputs with defaults applied
        
    Raises:
        ValueError: If inputs are invalid
    """
    validated = {}
    
    for input_schema in recipe.inputs:
        value = inputs.get(input_schema.name)
        
        # Check required
        if input_schema.required and value is None:
            if input_schema.default is not None:
                value = input_schema.default
            else:
                raise ValueError(f"Required input missing: {input_schema.name}")
        
        # Apply default if not provided
        if value is None and input_schema.default is not None:
            value = input_schema.default
        
        # Type validation
        if value is not None:
            if input_schema.type == InputType.STRING and not isinstance(value, str):
                raise ValueError(f"Input {input_schema.name} must be string, got {type(value)}")
            elif input_schema.type == InputType.INTEGER and not isinstance(value, int):
                raise ValueError(f"Input {input_schema.name} must be integer, got {type(value)}")
            elif input_schema.type == InputType.FLOAT and not isinstance(value, (int, float)):
                raise ValueError(f"Input {input_schema.name} must be float, got {type(value)}")
            elif input_schema.type == InputType.BOOLEAN and not isinstance(value, bool):
                raise ValueError(f"Input {input_schema.name} must be boolean, got {type(value)}")
            
            # Range validation
            if input_schema.range and isinstance(value, (int, float)):
                min_val, max_val = input_schema.range
                if not (min_val <= value <= max_val):
                    raise ValueError(f"Input {input_schema.name} must be between {min_val} and {max_val}, got {value}")
        
        validated[input_schema.name] = value
    
    return validated
