"""Add row level security policies for multi-tenant isolation

Revision ID: 20251217_rls
Revises: 20251216_1222_seed_test_data
Create Date: 2025-12-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251217_rls'
down_revision = '20251216_1222_seed_test_data'
branch_labels = None
depends_on = None


def upgrade():
    """
    Enable Row-Level Security (RLS) for multi-tenant isolation
    Ensures users can only access data from their own agency
    """
    
    # Enable RLS on core tables
    op.execute("ALTER TABLE agencies ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE teams ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE agent_instances ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE task_queue ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY")
    
    # Create policies for agencies table
    # Users can only see their own agency
    op.execute("""
        CREATE POLICY agency_isolation ON agencies
        FOR ALL
        USING (id = current_setting('app.current_agency_id', true)::uuid)
    """)
    
    # Create policies for teams table
    # Users can only see teams in their agency
    op.execute("""
        CREATE POLICY team_isolation ON teams
        FOR ALL
        USING (agency_id = current_setting('app.current_agency_id', true)::uuid)
    """)
    
    # Create policies for agent_instances table
    # Users can only see agents belonging to their agency's teams
    op.execute("""
        CREATE POLICY agent_instance_isolation ON agent_instances
        FOR ALL
        USING (
            team_id IN (
                SELECT id FROM teams 
                WHERE agency_id = current_setting('app.current_agency_id', true)::uuid
            )
        )
    """)
    
    # Create policies for audit_logs table
    # Users can only see audit logs from their agency
    op.execute("""
        CREATE POLICY audit_log_isolation ON audit_logs
        FOR ALL
        USING (agency_id = current_setting('app.current_agency_id', true)::uuid)
    """)
    
    # Create policies for task_queue table
    # Users can only see tasks for agents in their agency
    op.execute("""
        CREATE POLICY task_queue_isolation ON task_queue
        FOR ALL
        USING (
            agent_instance_id IN (
                SELECT ai.id FROM agent_instances ai
                JOIN teams t ON ai.team_id = t.id
                WHERE t.agency_id = current_setting('app.current_agency_id', true)::uuid
            )
        )
    """)
    
    # Create policies for subscriptions table
    # Users can only see subscriptions for their agency
    op.execute("""
        CREATE POLICY subscription_isolation ON subscriptions
        FOR ALL
        USING (agency_id = current_setting('app.current_agency_id', true)::uuid)
    """)
    
    # Add indexes to improve RLS query performance
    op.create_index('idx_teams_agency_id', 'teams', ['agency_id'])
    op.create_index('idx_agent_instances_team_id', 'agent_instances', ['team_id'])
    op.create_index('idx_audit_logs_agency_id', 'audit_logs', ['agency_id'])
    op.create_index('idx_task_queue_agent_instance_id', 'task_queue', ['agent_instance_id'])
    op.create_index('idx_subscriptions_agency_id', 'subscriptions', ['agency_id'])


def downgrade():
    """Remove RLS policies and indexes"""
    
    # Drop indexes
    op.drop_index('idx_subscriptions_agency_id')
    op.drop_index('idx_task_queue_agent_instance_id')
    op.drop_index('idx_audit_logs_agency_id')
    op.drop_index('idx_agent_instances_team_id')
    op.drop_index('idx_teams_agency_id')
    
    # Drop policies
    op.execute("DROP POLICY IF EXISTS subscription_isolation ON subscriptions")
    op.execute("DROP POLICY IF EXISTS task_queue_isolation ON task_queue")
    op.execute("DROP POLICY IF EXISTS audit_log_isolation ON audit_logs")
    op.execute("DROP POLICY IF EXISTS agent_instance_isolation ON agent_instances")
    op.execute("DROP POLICY IF EXISTS team_isolation ON teams")
    op.execute("DROP POLICY IF EXISTS agency_isolation ON agencies")
    
    # Disable RLS
    op.execute("ALTER TABLE subscriptions DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE task_queue DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE agent_instances DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE teams DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE agencies DISABLE ROW LEVEL SECURITY")
