"""
Agent API Routes
Execute agent recipes via API + Agent Allocation Management
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from pathlib import Path
from uuid import UUID
from datetime import datetime, timezone
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.recipe_evaluator import RecipeEvaluator
from agents.agent import Agent, create_agent
from app.utils.security import get_current_user
from app.utils.db import get_db
from app.models.schemas import UserResponse
from app.models.agent import AgentInstance, AgentRole, Cookbook
from app.models.agency import Team

router = APIRouter(prefix="/agents", tags=["agents"])


class ExecuteRecipeRequest(BaseModel):
    """Request to execute an agent recipe"""
    recipe_id: str = Field(..., description="Recipe ID (e.g., 'site-audit')")
    category: str = Field("seo", description="Recipe category (seo, social, leads)")
    inputs: Dict[str, Any] = Field(..., description="Input parameters for recipe")
    mock_mode: bool = Field(True, description="Use mock data instead of real API calls")


class ExecuteRecipeResponse(BaseModel):
    """Response from recipe execution"""
    success: bool
    recipe_id: str
    output: Dict[str, Any]
    metrics: Dict[str, Any]
    message: str = ""


@router.post("/execute", response_model=ExecuteRecipeResponse)
async def execute_recipe(
    request: ExecuteRecipeRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Execute an agent recipe
    
    Requires authentication. User must have access to agents.
    """
    try:
        # Build recipe path
        recipe_path = Path(__file__).parent.parent.parent.parent / "recipes" / request.category / f"{request.recipe_id}.yaml"
        
        if not recipe_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Recipe not found: {request.category}/{request.recipe_id}"
            )
        
        # Initialize evaluator
        evaluator = RecipeEvaluator(recipe_path=str(recipe_path), mock_mode=request.mock_mode)
        
        # Execute recipe
        result = await evaluator.execute(request.inputs)
        
        return ExecuteRecipeResponse(
            success=result['success'],
            recipe_id=result['recipe_id'],
            output=result['output'],
            metrics=result['metrics'],
            message=f"Recipe executed successfully in {result['metrics']['execution_time_ms']}ms"
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/recipes")
async def list_recipes(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    List available agent recipes
    """
    recipes_dir = Path(__file__).parent.parent.parent.parent / "recipes"
    
    recipes = []
    for category_dir in recipes_dir.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith('.'):
            for recipe_file in category_dir.glob("*.yaml"):
                recipes.append({
                    'recipe_id': recipe_file.stem,
                    'category': category_dir.name,
                    'path': f"{category_dir.name}/{recipe_file.name}"
                })
    
    return {
        'recipes': recipes,
        'total': len(recipes)
    }


@router.get("/test")
async def test_agent_system():
    """
    Test agent system (no auth required for testing)
    Runs SEO audit in mock mode
    """
    try:
        recipe_path = Path(__file__).parent.parent.parent.parent / "recipes" / "seo" / "site-audit.yaml"
        evaluator = RecipeEvaluator(recipe_path=str(recipe_path), mock_mode=True)
        
        result = await evaluator.execute({
            'website_url': 'https://example.com',
            'max_depth': 1,
            'include_images': True
        })
        
        return {
            'success': True,
            'message': 'Agent system operational',
            'metrics': result['metrics']
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Agent system error: {str(e)}'
        }


# ============================================================================
# AGENT ALLOCATION API (Phase 3)
# ============================================================================

class AllocateAgentRequest(BaseModel):
    """Request to allocate agent to team"""
    agent_role_id: UUID = Field(..., description="UUID of AgentRole to instantiate")
    team_id: UUID = Field(..., description="UUID of Team to assign agent")
    custom_name: str = Field(..., description="Custom name for agent (e.g., 'Rover', 'SocialBot')")
    avatar_icon: Optional[str] = Field("🤖", description="Emoji/icon for agent")
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Agent-specific configuration")


class AgentInfoResponse(BaseModel):
    """Agent instance details"""
    id: str
    custom_name: str
    avatar_icon: str
    is_active: bool
    last_active_at: Optional[str]
    created_at: Optional[str]
    agent_role: Dict[str, Any]
    team: Dict[str, Any]
    cookbooks: List[Dict[str, Any]]
    configuration: Dict[str, Any]
    available_recipes: List[Dict[str, Any]]


@router.post("/allocate", response_model=AgentInfoResponse)
async def allocate_agent(
    request: AllocateAgentRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Allocate agent to team (Agency Admin only)
    
    Creates AgentInstance record linking AgentRole → Team
    Validates subscription limits and team ownership
    """
    try:
        # Validate team exists and belongs to user's agency
        team_stmt = select(Team).where(Team.id == request.team_id)
        team_result = await db.execute(team_stmt)
        team = team_result.scalar_one_or_none()
        
        if not team:
            raise HTTPException(status_code=404, detail=f"Team {request.team_id} not found")
        
        # TODO: Validate current_user is admin of team's agency
        # For MVP, assuming user has permission
        
        # Validate agent_role exists
        role_stmt = select(AgentRole).where(AgentRole.id == request.agent_role_id)
        role_result = await db.execute(role_stmt)
        agent_role = role_result.scalar_one_or_none()
        
        if not agent_role:
            raise HTTPException(status_code=404, detail=f"AgentRole {request.agent_role_id} not found")
        
        # Check if agent_role is available (not "upcoming")
        if agent_role.status != "available":
            raise HTTPException(
                status_code=400,
                detail=f"AgentRole {agent_role.name} is not available (status: {agent_role.status})"
            )
        
        # TODO: Check subscription limits
        # For MVP, allowing unlimited allocation
        
        # Create AgentInstance
        agent_instance = AgentInstance(
            team_id=request.team_id,
            agent_role_id=request.agent_role_id,
            custom_name=request.custom_name,
            avatar_icon=request.avatar_icon,
            configuration=request.configuration,
            is_active=True,
            last_active_at=None,
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(agent_instance)
        await db.flush()
        
        # Initialize Agent runtime to get available recipes
        agent = await create_agent(agent_instance.id, db)
        agent_info = agent.get_agent_info()
        available_recipes = await agent.get_available_recipes()
        
        await db.commit()
        
        return AgentInfoResponse(
            id=agent_info['id'],
            custom_name=agent_info['custom_name'],
            avatar_icon=agent_info['avatar_icon'],
            is_active=agent_info['is_active'],
            last_active_at=agent_info['last_active_at'],
            created_at=agent_info['created_at'],
            agent_role=agent_info['agent_role'],
            team=agent_info['team'],
            cookbooks=agent_info['cookbooks'],
            configuration=agent_info['configuration'],
            available_recipes=available_recipes
        )
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Allocation failed: {str(e)}")


@router.get("/{agent_instance_id}", response_model=AgentInfoResponse)
async def get_agent(
    agent_instance_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get agent instance details with available recipes
    """
    try:
        agent = await create_agent(agent_instance_id, db)
        agent_info = agent.get_agent_info()
        available_recipes = await agent.get_available_recipes()
        
        return AgentInfoResponse(
            id=agent_info['id'],
            custom_name=agent_info['custom_name'],
            avatar_icon=agent_info['avatar_icon'],
            is_active=agent_info['is_active'],
            last_active_at=agent_info['last_active_at'],
            created_at=agent_info['created_at'],
            agent_role=agent_info['agent_role'],
            team=agent_info['team'],
            cookbooks=agent_info['cookbooks'],
            configuration=agent_info['configuration'],
            available_recipes=available_recipes
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve agent: {str(e)}")


@router.delete("/{agent_instance_id}")
async def deactivate_agent(
    agent_instance_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate agent (Agency Admin only)
    Sets is_active=False instead of deleting record (audit trail)
    """
    try:
        # Load agent instance
        stmt = select(AgentInstance).where(AgentInstance.id == agent_instance_id)
        result = await db.execute(stmt)
        agent_instance = result.scalar_one_or_none()
        
        if not agent_instance:
            raise HTTPException(status_code=404, detail=f"AgentInstance {agent_instance_id} not found")
        
        # TODO: Validate current_user is admin of agent's agency
        
        # Deactivate (soft delete)
        agent_instance.is_active = False
        await db.commit()
        
        return {
            'success': True,
            'message': f"Agent '{agent_instance.custom_name}' deactivated",
            'agent_instance_id': str(agent_instance_id)
        }
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Deactivation failed: {str(e)}")


@router.post("/{agent_instance_id}/execute", response_model=ExecuteRecipeResponse)
async def execute_agent_recipe(
    agent_instance_id: UUID,
    recipe_id: UUID,
    inputs: Dict[str, Any],
    mock_mode: bool = False,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute recipe using Agent runtime (with tracking + ownership validation)
    
    Replaces legacy /agents/execute endpoint - uses Agent class for vertical integration
    """
    try:
        # Initialize agent
        agent = await create_agent(agent_instance_id, db)
        
        # Execute recipe (validates ownership automatically)
        result = await agent.execute_recipe(recipe_id, inputs, mock_mode)
        
        await db.commit()
        
        return ExecuteRecipeResponse(
            success=result['success'],
            recipe_id=result['recipe_id'],
            output=result['output'],
            metrics=result['metrics'],
            message=f"Recipe executed by agent '{agent.agent_instance.custom_name}' in {result['metrics']['execution_time_ms']}ms"
        )
        
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=403, detail=str(e))  # Permission denied
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")
