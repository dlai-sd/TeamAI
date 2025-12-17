"""
CookbookLoader - Imports YAML cookbooks and recipes into PostgreSQL
Bridges the gap between YAML configuration files and database models
"""
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from uuid import UUID
import uuid

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import ValidationError
from app.models.agent import AgentRole, Cookbook, Recipe
from agents.recipe_schema import validate_cookbook_yaml, validate_recipe_yaml


class CookbookLoader:
    """
    Loads cookbooks and recipes from YAML files into PostgreSQL
    Handles AgentRole creation, Cookbook parsing, and Recipe registration
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize loader with database session
        
        Args:
            session: Async SQLAlchemy session
        """
        self.session = session
    
    async def load_cookbook(self, cookbook_path: str, agent_role_name: str) -> Cookbook:
        """
        Load a cookbook from YAML file into database
        
        Args:
            cookbook_path: Path to cookbook YAML file
            agent_role_name: Name of agent role this cookbook belongs to
            
        Returns:
            Created Cookbook instance
        """
        cookbook_yaml = self._load_yaml(cookbook_path)
        
        # Validate structure
        if 'cookbook' not in cookbook_yaml:
            raise ValueError(f"Invalid cookbook file: missing 'cookbook' key")
        
        cookbook_data = cookbook_yaml['cookbook']
        
        # Find or create AgentRole
        agent_role = await self._get_or_create_agent_role(
            agent_role_name,
            cookbook_data.get('description', ''),
            cookbook_data.get('version', '1.0.0')
        )
        
        # Check if cookbook already exists
        result = await self.session.execute(
            select(Cookbook).where(
                Cookbook.agent_role_id == agent_role.id,
                Cookbook.name == cookbook_data['name'],
                Cookbook.version == cookbook_data['version']
            )
        )
        existing_cookbook = result.scalar_one_or_none()
        
        if existing_cookbook:
            print(f"Cookbook '{cookbook_data['name']}' v{cookbook_data['version']} already exists")
            return existing_cookbook
        
        # Create Cookbook record
        cookbook = Cookbook(
            agent_role_id=agent_role.id,
            name=cookbook_data['name'],
            version=cookbook_data['version'],
            description=cookbook_data.get('description', ''),
            yaml_definition=cookbook_data,  # Store full YAML as JSONB
            required_secrets=cookbook_data.get('required_secrets', []),
            allowed_data_sources=cookbook_data.get('allowed_data_sources', []),
            subscription_limits=cookbook_data.get('subscription_limits', {})
        )
        
        self.session.add(cookbook)
        await self.session.flush()  # Get cookbook.id
        
        print(f"Created cookbook: {cookbook.name} (ID: {cookbook.id})")
        
        # Load recipes referenced in cookbook
        recipe_ids = cookbook_data.get('recipes', [])
        for recipe_id in recipe_ids:
            await self._load_recipe(recipe_id, cookbook)
        
        await self.session.commit()
        
        return cookbook
    
    async def _load_recipe(self, recipe_id: str, cookbook: Cookbook):
        """
        Load a recipe from YAML file into database
        
        Args:
            recipe_id: Recipe identifier (e.g., 'site-audit')
            cookbook: Parent cookbook instance
        """
        # Construct recipe file path
        # Assumes recipes are in recipes/{category}/{recipe_id}.yaml
        recipe_paths = [
            Path(backend_path.parent) / 'recipes' / 'seo' / f'{recipe_id}.yaml',
            Path(backend_path.parent) / 'recipes' / 'social' / f'{recipe_id}.yaml',
            Path(backend_path.parent) / 'recipes' / 'leads' / f'{recipe_id}.yaml',
        ]
        
        recipe_path = None
        for path in recipe_paths:
            if path.exists():
                recipe_path = path
                break
        
        if not recipe_path:
            print(f"Warning: Recipe file not found for '{recipe_id}'")
            return
        
        recipe_yaml = self._load_yaml(str(recipe_path))
        
        if 'recipe' not in recipe_yaml:
            print(f"Warning: Invalid recipe file for '{recipe_id}'")
            return
        
        recipe_data = recipe_yaml['recipe']
        
        # Check if recipe already exists
        result = await self.session.execute(
            select(Recipe).where(
                Recipe.cookbook_id == cookbook.id,
                Recipe.name == recipe_data['name'],
                Recipe.version == recipe_data['version']
            )
        )
        existing_recipe = result.scalar_one_or_none()
        
        if existing_recipe:
            print(f"  Recipe '{recipe_data['name']}' already exists")
            return
        
        # Create Recipe record
        recipe = Recipe(
            cookbook_id=cookbook.id,
            name=recipe_data['name'],
            version=recipe_data['version'],
            description=recipe_data.get('description', ''),
            yaml_definition=recipe_data,  # Store full YAML as JSONB
            ab_testing_enabled=recipe_data.get('ab_testing', {}).get('enabled', False),
            cost_per_execution=float(recipe_data.get('compliance', {}).get('cost_per_unit', 0.50))
        )
        
        self.session.add(recipe)
        print(f"  Created recipe: {recipe.name} (ID: {recipe.id})")
    
    async def _get_or_create_agent_role(
        self, 
        name: str, 
        description: str, 
        version: str
    ) -> AgentRole:
        """
        Get existing AgentRole or create new one
        
        Args:
            name: Agent role name (e.g., 'SEO Specialist')
            description: Role description
            version: Version string
            
        Returns:
            AgentRole instance
        """
        # Check if exists
        result = await self.session.execute(
            select(AgentRole).where(
                AgentRole.name == name,
                AgentRole.version == version
            )
        )
        agent_role = result.scalar_one_or_none()
        
        if agent_role:
            print(f"Found existing AgentRole: {name} v{version}")
            return agent_role
        
        # Create new
        agent_role = AgentRole(
            name=name,
            description=description,
            version=version,
            status='available',
            capabilities=[],  # Will be populated from cookbook data
            base_price=50.00  # Default, can be overridden
        )
        
        self.session.add(agent_role)
        await self.session.flush()  # Get agent_role.id
        
        print(f"Created AgentRole: {name} v{version} (ID: {agent_role.id})")
        
        return agent_role
    
    def _load_yaml(self, file_path: str) -> Dict[str, Any]:
        """Load and parse YAML file"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {file_path}")
        
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    async def load_all_cookbooks(self, cookbooks_dir: str = None) -> List[Cookbook]:
        """
        Load all cookbooks from a directory
        
        Args:
            cookbooks_dir: Path to cookbooks directory (default: ../cookbooks)
            
        Returns:
            List of created Cookbook instances
        """
        if cookbooks_dir is None:
            cookbooks_dir = Path(backend_path.parent) / 'cookbooks'
        else:
            cookbooks_dir = Path(cookbooks_dir)
        
        if not cookbooks_dir.exists():
            raise FileNotFoundError(f"Cookbooks directory not found: {cookbooks_dir}")
        
        cookbooks = []
        
        # Find all YAML files in cookbooks directory
        for yaml_file in cookbooks_dir.glob('*.yaml'):
            try:
                # Extract agent role name from filename (e.g., 'seo-specialist-v1.yaml' -> 'SEO Specialist')
                agent_role_name = yaml_file.stem.split('-v')[0].replace('-', ' ').title()
                
                print(f"\nLoading cookbook: {yaml_file.name}")
                cookbook = await self.load_cookbook(str(yaml_file), agent_role_name)
                cookbooks.append(cookbook)
                
            except Exception as e:
                print(f"Error loading cookbook {yaml_file.name}: {e}")
                continue
        
        return cookbooks


# Standalone seed script
async def seed_database(session: AsyncSession):
    """
    Seed database with default cookbooks
    Run this to populate AgentRole, Cookbook, and Recipe tables
    """
    loader = CookbookLoader(session)
    
    print("=" * 70)
    print("SEEDING DATABASE WITH COOKBOOKS")
    print("=" * 70)
    
    try:
        cookbooks = await loader.load_all_cookbooks()
        
        print("\n" + "=" * 70)
        print(f"SEEDING COMPLETE: {len(cookbooks)} cookbook(s) loaded")
        print("=" * 70)
        
        return cookbooks
        
    except Exception as e:
        print(f"\nSEEDING FAILED: {e}")
        await session.rollback()
        raise
