"""
Agent API Routes
Execute agent recipes via API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from agents.recipe_evaluator import RecipeEvaluator
from app.utils.security import get_current_user
from app.models.schemas import UserResponse

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
        evaluator = RecipeEvaluator(str(recipe_path), mock_mode=request.mock_mode)
        
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
        evaluator = RecipeEvaluator(str(recipe_path), mock_mode=True)
        
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
