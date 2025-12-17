"""
TaskQueue Service - Manage agent task lifecycle
"""
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
from uuid import UUID
from datetime import datetime, timezone

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.audit import TaskQueue
from app.models.agent import AgentInstance
from agents.agent import create_agent


class TaskQueueService:
    """
    Service layer for managing agent task queue
    
    Responsibilities:
    - Create tasks (queued recipe executions)
    - Execute tasks asynchronously
    - Track task status (pending → running → completed/failed)
    - Retrieve task history
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize task queue service
        
        Args:
            db_session: Async SQLAlchemy session
        """
        self.session = db_session
    
    async def create_task(
        self,
        agent_instance_id: UUID,
        recipe_id: UUID,
        inputs: Dict[str, Any],
        task_type: Optional[str] = None
    ) -> TaskQueue:
        """
        Create new task in queue
        
        Args:
            agent_instance_id: UUID of agent to execute task
            recipe_id: UUID of recipe to execute
            inputs: Input parameters for recipe
            task_type: Optional task type label (defaults to recipe name)
            
        Returns:
            Created TaskQueue record
            
        Raises:
            ValueError: If agent not found or inactive
        """
        # Verify agent exists and is active
        stmt = select(AgentInstance).where(AgentInstance.id == agent_instance_id)
        result = await self.session.execute(stmt)
        agent_instance = result.scalar_one_or_none()
        
        if not agent_instance:
            raise ValueError(f"AgentInstance {agent_instance_id} not found")
        
        if not agent_instance.is_active:
            raise ValueError(f"AgentInstance {agent_instance_id} is inactive")
        
        # Use recipe_id as task_type if not provided
        if task_type is None:
            task_type = str(recipe_id)
        
        # Create task record
        task = TaskQueue(
            agent_instance_id=agent_instance_id,
            task_type=task_type,
            input_params={
                'recipe_id': str(recipe_id),
                'inputs': inputs
            },
            status='pending',
            created_at=datetime.now(timezone.utc)
        )
        
        self.session.add(task)
        await self.session.flush()
        
        return task
    
    async def execute_task(
        self,
        task_id: UUID,
        mock_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Execute task from queue
        
        Args:
            task_id: UUID of task to execute
            mock_mode: If True, run components in mock mode
            
        Returns:
            Execution result dictionary
            
        Raises:
            ValueError: If task not found or already completed
        """
        # Load task with agent relationship
        stmt = (
            select(TaskQueue)
            .options(selectinload(TaskQueue.agent_instance))
            .where(TaskQueue.id == task_id)
        )
        result = await self.session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        if task.status in ['completed', 'failed']:
            raise ValueError(f"Task {task_id} already {task.status}")
        
        # Update status to running
        task.status = 'running'
        task.started_at = datetime.now(timezone.utc)
        await self.session.flush()
        
        try:
            # Initialize agent
            agent = await create_agent(task.agent_instance_id, self.session)
            
            # Extract recipe_id and inputs from task params
            recipe_id = UUID(task.input_params['recipe_id'])
            inputs = task.input_params['inputs']
            
            # Execute recipe
            result = await agent.execute_recipe(recipe_id, inputs, mock_mode)
            
            # Update task with results
            task.status = 'completed'
            task.completed_at = datetime.now(timezone.utc)
            task.output_data = {
                'success': result['success'],
                'output': result['output'],
                'metrics': result['metrics']
            }
            
            await self.session.flush()
            
            return {
                'task_id': str(task.id),
                'status': 'completed',
                'result': result
            }
            
        except Exception as e:
            # Mark task as failed
            task.status = 'failed'
            task.completed_at = datetime.now(timezone.utc)
            task.output_data = {
                'error': str(e),
                'success': False
            }
            
            await self.session.flush()
            
            return {
                'task_id': str(task.id),
                'status': 'failed',
                'error': str(e)
            }
    
    async def get_task(self, task_id: UUID) -> Optional[TaskQueue]:
        """
        Retrieve task by ID
        
        Args:
            task_id: UUID of task
            
        Returns:
            TaskQueue record or None if not found
        """
        stmt = (
            select(TaskQueue)
            .options(selectinload(TaskQueue.agent_instance))
            .where(TaskQueue.id == task_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_tasks(
        self,
        agent_instance_id: Optional[UUID] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[TaskQueue]:
        """
        List tasks with optional filters
        
        Args:
            agent_instance_id: Filter by agent (optional)
            status: Filter by status (pending, running, completed, failed)
            limit: Max results to return
            offset: Pagination offset
            
        Returns:
            List of TaskQueue records
        """
        stmt = select(TaskQueue).options(selectinload(TaskQueue.agent_instance))
        
        # Apply filters
        filters = []
        if agent_instance_id:
            filters.append(TaskQueue.agent_instance_id == agent_instance_id)
        if status:
            filters.append(TaskQueue.status == status)
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        # Order by creation time (newest first)
        stmt = stmt.order_by(TaskQueue.created_at.desc())
        
        # Pagination
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def cancel_task(self, task_id: UUID) -> bool:
        """
        Cancel pending task
        
        Args:
            task_id: UUID of task to cancel
            
        Returns:
            True if task cancelled, False otherwise
        """
        task = await self.get_task(task_id)
        
        if not task:
            return False
        
        # Can only cancel pending tasks
        if task.status != 'pending':
            return False
        
        task.status = 'failed'
        task.completed_at = datetime.now(timezone.utc)
        task.output_data = {'error': 'Task cancelled by user', 'success': False}
        
        await self.session.flush()
        
        return True
    
    async def get_task_statistics(
        self,
        agent_instance_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get task queue statistics
        
        Args:
            agent_instance_id: Filter by agent (optional)
            
        Returns:
            Statistics dictionary with counts by status
        """
        from sqlalchemy import func
        
        # Build query
        stmt = select(
            TaskQueue.status,
            func.count(TaskQueue.id).label('count')
        ).group_by(TaskQueue.status)
        
        if agent_instance_id:
            stmt = stmt.where(TaskQueue.agent_instance_id == agent_instance_id)
        
        result = await self.session.execute(stmt)
        status_counts = {row.status: row.count for row in result}
        
        return {
            'total': sum(status_counts.values()),
            'pending': status_counts.get('pending', 0),
            'running': status_counts.get('running', 0),
            'completed': status_counts.get('completed', 0),
            'failed': status_counts.get('failed', 0)
        }
