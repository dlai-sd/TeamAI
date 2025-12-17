"""
Agent Runtime Class - Bridge between AgentInstance DB records and RecipeEvaluator execution
Provides vertical integration: Database → Agent → RecipeEvaluator → Components
"""
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
from uuid import UUID
from datetime import datetime, timezone

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.models.agent import AgentInstance, Recipe, Cookbook, AgentRole
from agents.recipe_evaluator import RecipeEvaluator
from components.subscription_tracker import SubscriptionTracker


class Agent:
    """
    Agent Runtime - Represents a deployed AgentInstance with execution capabilities
    
    Responsibilities:
    - Load AgentInstance from database with relationships
    - Validate recipe ownership (security)
    - Execute recipes with mandatory tracking
    - Update agent activity timestamps
    
    Usage:
        agent = Agent(agent_instance_id, db_session)
        await agent.initialize()
        recipes = await agent.get_available_recipes()
        result = await agent.execute_recipe(recipe_id, {"url": "https://example.com"})
    """
    
    def __init__(self, agent_instance_id: UUID, session: AsyncSession):
        """
        Initialize agent runtime
        
        Args:
            agent_instance_id: UUID of AgentInstance record in database
            session: Async SQLAlchemy session for database operations
        """
        self.agent_instance_id = agent_instance_id
        self.session = session
        
        # Loaded from database
        self.agent_instance: Optional[AgentInstance] = None
        self.agent_role: Optional[AgentRole] = None
        self.cookbooks: List[Cookbook] = []
        self.recipes: List[Recipe] = []
        
    async def initialize(self) -> bool:
        """
        Load AgentInstance from database with all relationships
        
        Returns:
            True if agent loaded successfully, False otherwise
        """
        # Query with eager loading of relationships
        stmt = (
            select(AgentInstance)
            .options(
                selectinload(AgentInstance.agent_role).selectinload(AgentRole.cookbooks).selectinload(Cookbook.recipes),
                selectinload(AgentInstance.team)
            )
            .where(AgentInstance.id == self.agent_instance_id)
        )
        
        result = await self.session.execute(stmt)
        self.agent_instance = result.scalar_one_or_none()
        
        if not self.agent_instance:
            print(f"[Agent] AgentInstance {self.agent_instance_id} not found in database")
            return False
        
        if not self.agent_instance.is_active:
            print(f"[Agent] AgentInstance {self.agent_instance_id} is inactive")
            return False
        
        # Extract relationships
        self.agent_role = self.agent_instance.agent_role
        self.cookbooks = self.agent_role.cookbooks if self.agent_role else []
        
        # Flatten recipes from all cookbooks
        self.recipes = []
        for cookbook in self.cookbooks:
            self.recipes.extend(cookbook.recipes)
        
        print(f"[Agent] Loaded '{self.agent_instance.custom_name}' (Role: {self.agent_role.name})")
        print(f"[Agent] Available cookbooks: {len(self.cookbooks)}")
        print(f"[Agent] Available recipes: {len(self.recipes)}")
        
        return True
    
    async def get_available_recipes(self) -> List[Dict[str, Any]]:
        """
        Get list of recipes this agent can execute
        
        Returns:
            List of recipe metadata dictionaries
        """
        if not self.agent_instance:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        recipe_list = []
        for recipe in self.recipes:
            recipe_list.append({
                'id': str(recipe.id),
                'name': recipe.name,
                'version': recipe.version,
                'description': recipe.description,
                'cost_per_execution': float(recipe.cost_per_execution) if recipe.cost_per_execution else 0.0,
                'ab_testing_enabled': recipe.ab_testing_enabled,
                'cookbook_name': recipe.cookbook.name if recipe.cookbook else None
            })
        
        return recipe_list
    
    async def validate_recipe_ownership(self, recipe_id: UUID) -> bool:
        """
        Validate that this agent has access to execute the given recipe
        Security check to prevent unauthorized recipe execution
        
        Args:
            recipe_id: UUID of recipe to validate
            
        Returns:
            True if agent owns recipe, False otherwise
        """
        if not self.agent_instance:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        # Check if recipe_id is in agent's available recipes
        recipe_ids = [recipe.id for recipe in self.recipes]
        
        if recipe_id not in recipe_ids:
            print(f"[Agent] Recipe {recipe_id} not owned by agent {self.agent_instance_id}")
            print(f"[Agent] Available recipes: {recipe_ids}")
            return False
        
        return True
    
    async def execute_recipe(
        self, 
        recipe_id: UUID, 
        inputs: Dict[str, Any],
        mock_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a recipe with mandatory subscription tracking
        
        Args:
            recipe_id: UUID of recipe to execute
            inputs: Input parameters for recipe execution
            mock_mode: If True, components run in mock mode (no external API calls)
            
        Returns:
            Execution result dictionary with output, metrics, tracking info
            
        Raises:
            ValueError: If recipe not owned by agent
            RuntimeError: If agent not initialized
        """
        if not self.agent_instance:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        # Validate recipe ownership (security)
        if not await self.validate_recipe_ownership(recipe_id):
            raise ValueError(f"Agent does not have permission to execute recipe {recipe_id}")
        
        # Find recipe object
        recipe = next((r for r in self.recipes if r.id == recipe_id), None)
        if not recipe:
            raise ValueError(f"Recipe {recipe_id} not found")
        
        print(f"\n[Agent] Executing recipe: {recipe.name} v{recipe.version}")
        print(f"[Agent] Agent: {self.agent_instance.custom_name}")
        print(f"[Agent] Team: {self.agent_instance.team.name if self.agent_instance.team else 'Unknown'}")
        
        # Extract yaml_definition from database (JSONB field)
        recipe_yaml = recipe.yaml_definition
        
        if not recipe_yaml:
            raise ValueError(f"Recipe {recipe_id} has no yaml_definition in database")
        
        # Initialize RecipeEvaluator with mandatory tracking
        tracking_config = {
            'agent_instance_id': str(self.agent_instance_id),
            'recipe_id': str(recipe_id),
            'agency_id': str(self.agent_instance.team.agency_id) if self.agent_instance.team else None
        }
        
        evaluator = RecipeEvaluator(
            recipe_definition=recipe_yaml,
            tracking_config=tracking_config,
            db_session=self.session,  # Pass DB session for audit log persistence
            mock_mode=mock_mode
        )
        
        # Execute recipe
        result = await evaluator.execute(inputs)
        
        # Update agent activity timestamp
        self.agent_instance.last_active_at = datetime.now(timezone.utc)
        await self.session.flush()
        
        print(f"[Agent] Execution complete: {result.get('success')}")
        print(f"[Agent] Tracked: {result.get('tracking', {}).get('tracked', False)}")
        
        return result
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent metadata (name, role, configuration, status)
        
        Returns:
            Agent information dictionary
        """
        if not self.agent_instance:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        return {
            'id': str(self.agent_instance.id),
            'custom_name': self.agent_instance.custom_name,
            'avatar_icon': self.agent_instance.avatar_icon,
            'is_active': self.agent_instance.is_active,
            'last_active_at': self.agent_instance.last_active_at.isoformat() if self.agent_instance.last_active_at else None,
            'created_at': self.agent_instance.created_at.isoformat() if self.agent_instance.created_at else None,
            'agent_role': {
                'id': str(self.agent_role.id) if self.agent_role else None,
                'name': self.agent_role.name if self.agent_role else None,
                'version': self.agent_role.version if self.agent_role else None
            },
            'team': {
                'id': str(self.agent_instance.team.id) if self.agent_instance.team else None,
                'name': self.agent_instance.team.name if self.agent_instance.team else None
            },
            'cookbooks': [
                {
                    'id': str(cb.id),
                    'name': cb.name,
                    'version': cb.version
                }
                for cb in self.cookbooks
            ],
            'configuration': self.agent_instance.configuration
        }


# Convenience function for quick agent usage
async def create_agent(agent_instance_id: UUID, session: AsyncSession) -> Agent:
    """
    Factory function to create and initialize an Agent
    
    Args:
        agent_instance_id: UUID of AgentInstance
        session: Database session
        
    Returns:
        Initialized Agent instance
        
    Raises:
        ValueError: If agent not found or inactive
    """
    agent = Agent(agent_instance_id, session)
    success = await agent.initialize()
    
    if not success:
        raise ValueError(f"Failed to initialize agent {agent_instance_id}")
    
    return agent
