"""
SubscriptionTracker Component
Mandatory compliance layer for usage tracking and billing
Every agent execution MUST include this component
"""
import sys
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from components.base import BaseComponent


class SubscriptionTracker(BaseComponent):
    """
    Tracks agent execution metrics for billing accuracy
    This is a mandatory component - all recipes must include it
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, mock_mode: bool = False):
        super().__init__(config, mock_mode)
        self.agent_instance_id = self.config.get('agent_instance_id')
        self.recipe_id = self.config.get('recipe_id')
        self.agency_id = self.config.get('agency_id')
    
    def validate_config(self) -> bool:
        """Validate required tracking parameters"""
        if not self.agent_instance_id:
            return False
        if not self.recipe_id:
            return False
        if not self.agency_id:
            return False
        return True
    
    async def execute(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track execution metrics
        
        Args:
            execution_data: Dict containing:
                - execution_time_ms: Total execution time
                - tokens_used: LLM tokens consumed
                - cost_incurred: Dollar cost of execution
                - status: success|failed|timeout
                - metadata: Additional tracking data
                
        Returns:
            Dict with tracking confirmation
        """
        if self.mock_mode:
            return self._mock_track(execution_data)
        
        if not self.validate_config():
            raise ValueError("Invalid subscription tracker configuration - missing required IDs")
        
        # Calculate billable metrics
        execution_time_ms = execution_data.get('execution_time_ms', 0)
        tokens_used = execution_data.get('tokens_used', 0)
        cost_incurred = execution_data.get('cost_incurred', 0.0)
        status = execution_data.get('status', 'unknown')
        metadata = execution_data.get('metadata', {})
        
        # Prepare audit log entry
        audit_entry = {
            'agency_id': self.agency_id,
            'agent_instance_id': self.agent_instance_id,
            'recipe_id': self.recipe_id,
            'execution_time_ms': execution_time_ms,
            'tokens_used': tokens_used,
            'cost_incurred': cost_incurred,
            'status': status,
            'metadata': metadata,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # TODO: Write to PostgreSQL audit_logs table
        # For now, store in-memory (will be integrated with database in next step)
        print(f"[SubscriptionTracker] Logged execution: {audit_entry}")
        
        return {
            'tracked': True,
            'audit_entry': audit_entry,
            'billable_units': self._calculate_billable_units(execution_data)
        }
    
    def _calculate_billable_units(self, execution_data: Dict[str, Any]) -> float:
        """
        Calculate billable units based on execution metrics
        Current model: Per-execution billing (1 unit = 1 execution)
        Future: Can be extended for usage-based pricing
        """
        # MVP: Simple per-execution billing
        if execution_data.get('status') == 'success':
            return 1.0
        elif execution_data.get('status') == 'failed':
            return 0.0  # Don't charge for failed executions
        else:
            return 0.5  # Partial charge for timeouts
    
    def _mock_track(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return mock tracking data for testing"""
        return {
            'tracked': True,
            'audit_entry': {
                'agency_id': 'mock-agency-123',
                'agent_instance_id': 'mock-agent-456',
                'recipe_id': 'mock-recipe-789',
                'execution_time_ms': execution_data.get('execution_time_ms', 5000),
                'tokens_used': execution_data.get('tokens_used', 1000),
                'cost_incurred': execution_data.get('cost_incurred', 0.001),
                'status': execution_data.get('status', 'success'),
                'metadata': execution_data.get('metadata', {}),
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            'billable_units': 1.0
        }
    
    def get_summary(self, execution_results: list) -> Dict[str, Any]:
        """
        Generate billing summary from multiple executions
        Used for monthly subscription reports
        """
        total_executions = len(execution_results)
        successful_executions = sum(1 for r in execution_results if r.get('status') == 'success')
        failed_executions = sum(1 for r in execution_results if r.get('status') == 'failed')
        total_tokens = sum(r.get('tokens_used', 0) for r in execution_results)
        total_cost = sum(r.get('cost_incurred', 0.0) for r in execution_results)
        total_time_ms = sum(r.get('execution_time_ms', 0) for r in execution_results)
        
        return {
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': failed_executions,
            'success_rate': successful_executions / total_executions if total_executions > 0 else 0.0,
            'total_tokens': total_tokens,
            'total_cost_usd': round(total_cost, 6),
            'avg_execution_time_ms': total_time_ms // total_executions if total_executions > 0 else 0,
            'avg_tokens_per_execution': total_tokens // total_executions if total_executions > 0 else 0
        }
