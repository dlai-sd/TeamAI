"""
Task Queue API Routes
Manage asynchronous agent task execution
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.security import get_current_user
from app.utils.db import get_db
from app.utils.rls import set_rls_context, get_agency_id_from_user
from app.models.schemas import UserResponse
from app.services.task_service import TaskQueueService
from app.services.authorization_service import AuthorizationService

router = APIRouter(prefix="/tasks", tags=["tasks"])


class CreateTaskRequest(BaseModel):
    """Request to create task"""
    agent_instance_id: UUID = Field(..., description="Agent to execute task")
    recipe_id: UUID = Field(..., description="Recipe to execute")
    inputs: Dict[str, Any] = Field(..., description="Recipe input parameters")
    task_type: Optional[str] = Field(None, description="Optional task type label")


class TaskResponse(BaseModel):
    """Task details response"""
    id: str
    agent_instance_id: str
    agent_name: str
    task_type: str
    status: str
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    input_params: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]


class TaskListResponse(BaseModel):
    """Paginated task list"""
    tasks: List[TaskResponse]
    total: int
    limit: int
    offset: int


class TaskStatisticsResponse(BaseModel):
    """Task queue statistics"""
    total: int
    pending: int
    running: int
    completed: int
    failed: int


@router.post("/", response_model=TaskResponse)
async def create_task(
    request: CreateTaskRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new task in queue
    
    Task will be in 'pending' status until executed
    """
    try:
        # Set RLS context for multi-tenant isolation
        agency_id = get_agency_id_from_user(current_user)
        await set_rls_context(db, agency_id)
        
        service = TaskQueueService(db)
        task = await service.create_task(
            agent_instance_id=request.agent_instance_id,
            recipe_id=request.recipe_id,
            inputs=request.inputs,
            task_type=request.task_type
        )
        
        await db.commit()
        
        return TaskResponse(
            id=str(task.id),
            agent_instance_id=str(task.agent_instance_id),
            agent_name=task.agent_instance.custom_name if task.agent_instance else "Unknown",
            task_type=task.task_type,
            status=task.status,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            input_params=task.input_params,
            output_data=task.output_data
        )
        
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@router.post("/{task_id}/execute", response_model=Dict[str, Any])
async def execute_task(
    task_id: UUID,
    mock_mode: bool = False,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute task from queue (synchronous)
    
    Task status will change: pending → running → completed/failed
    """
    try:
        # Set RLS context
        agency_id = get_agency_id_from_user(current_user)
        await set_rls_context(db, agency_id)
        
        service = TaskQueueService(db)
        result = await service.execute_task(task_id, mock_mode)
        
        await db.commit()
        
        return result
        
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.post("/{task_id}/execute-async")
async def execute_task_async(
    task_id: UUID,
    mock_mode: bool = False,
    background_tasks: BackgroundTasks = None,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute task asynchronously (background job)
    
    Returns immediately while task executes in background
    Use GET /tasks/{task_id} to check status
    """
    try:
        # Set RLS context
        agency_id = get_agency_id_from_user(current_user)
        await set_rls_context(db, agency_id)
        
        service = TaskQueueService(db)
        task = await service.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        if task.status != 'pending':
            raise HTTPException(status_code=400, detail=f"Task {task_id} is not pending (status: {task.status})")
        
        # Add task execution to background
        if background_tasks:
            background_tasks.add_task(_execute_task_background, task_id, mock_mode, db)
        
        return {
            'task_id': str(task_id),
            'status': 'queued',
            'message': 'Task execution started in background'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue task: {str(e)}")


async def _execute_task_background(task_id: UUID, mock_mode: bool, db: AsyncSession):
    """Background task execution helper"""
    try:
        service = TaskQueueService(db)
        await service.execute_task(task_id, mock_mode)
        await db.commit()
    except Exception as e:
        print(f"[TaskQueue] Background execution failed for {task_id}: {e}")
        await db.rollback()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get task details by ID
    """
    try:
        # Set RLS context
        agency_id = get_agency_id_from_user(current_user)
        await set_rls_context(db, agency_id)
        
        service = TaskQueueService(db)
        task = await service.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return TaskResponse(
            id=str(task.id),
            agent_instance_id=str(task.agent_instance_id),
            agent_name=task.agent_instance.custom_name if task.agent_instance else "Unknown",
            task_type=task.task_type,
            status=task.status,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            input_params=task.input_params,
            output_data=task.output_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve task: {str(e)}")


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    agent_instance_id: Optional[UUID] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List tasks with optional filters
    
    Query parameters:
    - agent_instance_id: Filter by agent
    - status: Filter by status (pending, running, completed, failed)
    - limit: Results per page (max 100)
    - offset: Pagination offset
    """
    try:
        # Set RLS context
        agency_id = get_agency_id_from_user(current_user)
        await set_rls_context(db, agency_id)
        
        if limit > 100:
            limit = 100
        
        service = TaskQueueService(db)
        tasks = await service.list_tasks(
            agent_instance_id=agent_instance_id,
            status=status,
            limit=limit,
            offset=offset
        )
        
        task_responses = [
            TaskResponse(
                id=str(task.id),
                agent_instance_id=str(task.agent_instance_id),
                agent_name=task.agent_instance.custom_name if task.agent_instance else "Unknown",
                task_type=task.task_type,
                status=task.status,
                created_at=task.created_at.isoformat(),
                started_at=task.started_at.isoformat() if task.started_at else None,
                completed_at=task.completed_at.isoformat() if task.completed_at else None,
                input_params=task.input_params,
                output_data=task.output_data
            )
            for task in tasks
        ]
        
        return TaskListResponse(
            tasks=task_responses,
            total=len(task_responses),
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")


@router.delete("/{task_id}")
async def cancel_task(
    task_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel pending task
    
    Only tasks with status='pending' can be cancelled
    """
    try:
        # Set RLS context
        agency_id = get_agency_id_from_user(current_user)
        await set_rls_context(db, agency_id)
        
        service = TaskQueueService(db)
        success = await service.cancel_task(task_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Task cannot be cancelled (not pending or not found)")
        
        await db.commit()
        
        return {
            'success': True,
            'message': f"Task {task_id} cancelled",
            'task_id': str(task_id)
        }
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to cancel task: {str(e)}")


@router.get("/statistics", response_model=TaskStatisticsResponse)
async def get_task_statistics(
    agent_instance_id: Optional[UUID] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get task queue statistics
    
    Returns counts by status (pending, running, completed, failed)
    """
    try:
        # Set RLS context
        agency_id = get_agency_id_from_user(current_user)
        await set_rls_context(db, agency_id)
        
        service = TaskQueueService(db)
        stats = await service.get_task_statistics(agent_instance_id)
        
        return TaskStatisticsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")
