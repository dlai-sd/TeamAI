/**
 * End-to-End Integration Test - Complete Agent Workflow
 */
import { describe, it, expect, beforeAll, afterAll } from 'vitest';

describe('Complete Agent Workflow E2E', () => {
  let authToken: string;
  let agencyId: string;
  let teamId: string;
  let agentInstanceId: string;
  let recipeId: string;
  let taskId: string;

  const API_BASE = process.env.VITE_API_URL || 'http://localhost:8000';

  beforeAll(async () => {
    // 1. Login (get auth token)
    const loginResponse = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'test@agency.com',
        password: 'testpass123',
      }),
    });

    const loginData = await loginResponse.json();
    authToken = loginData.access_token;
    agencyId = loginData.user.agency_id;
  });

  it('Step 1: Create a team', async () => {
    const response = await fetch(`${API_BASE}/api/v1/teams`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        name: 'Test SEO Team',
        description: 'Integration test team',
      }),
    });

    expect(response.ok).toBe(true);
    const data = await response.json();
    teamId = data.id;
    expect(data.name).toBe('Test SEO Team');
  });

  it('Step 2: Browse marketplace and get agent roles', async () => {
    const response = await fetch(`${API_BASE}/api/v1/marketplace/agent-roles`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    expect(response.ok).toBe(true);
    const roles = await response.json();
    expect(roles.length).toBeGreaterThan(0);
    expect(roles[0]).toHaveProperty('id');
    expect(roles[0]).toHaveProperty('name');
  });

  it('Step 3: Allocate agent to team', async () => {
    // Get SEO Specialist role ID
    const rolesResponse = await fetch(`${API_BASE}/api/v1/marketplace/agent-roles`, {
      headers: { Authorization: `Bearer ${authToken}` },
    });
    const roles = await rolesResponse.json();
    const seoRole = roles.find((r) => r.name === 'SEO Specialist');

    const response = await fetch(`${API_BASE}/api/v1/agents/allocate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        agent_role_id: seoRole.id,
        team_id: teamId,
        custom_name: 'RoverBot',
        avatar_icon: '🐕',
        configuration: {
          max_pages: 100,
        },
      }),
    });

    expect(response.ok).toBe(true);
    const agent = await response.json();
    agentInstanceId = agent.id;
    expect(agent.custom_name).toBe('RoverBot');
    expect(agent.is_active).toBe(true);
  });

  it('Step 4: Configure secrets in Secret Locker', async () => {
    const response = await fetch(`${API_BASE}/api/v1/secrets`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        team_id: teamId,
        key_name: 'semrush_api_key',
        value: 'test_api_key_12345',
      }),
    });

    expect(response.ok).toBe(true);
    const secret = await response.json();
    expect(secret.key_name).toBe('semrush_api_key');
  });

  it('Step 5: Get available recipes for agent', async () => {
    const response = await fetch(`${API_BASE}/api/v1/agents/${agentInstanceId}/recipes`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    expect(response.ok).toBe(true);
    const recipes = await response.json();
    expect(recipes.length).toBeGreaterThan(0);
    
    const siteAudit = recipes.find((r) => r.name === 'Site Audit');
    expect(siteAudit).toBeDefined();
    recipeId = siteAudit.id;
  });

  it('Step 6: Execute recipe (sync)', async () => {
    const response = await fetch(`${API_BASE}/api/v1/tasks/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        agent_instance_id: agentInstanceId,
        recipe_id: recipeId,
        inputs: {
          website_url: 'https://example.com',
          max_depth: 2,
        },
        async_execution: false,
      }),
    });

    expect(response.ok).toBe(true);
    const result = await response.json();
    
    expect(result.status).toBe('completed');
    expect(result.output_data).toBeDefined();
    expect(result.execution_time_ms).toBeGreaterThan(0);
  });

  it('Step 7: Execute recipe (async) and check queue', async () => {
    const response = await fetch(`${API_BASE}/api/v1/tasks/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        agent_instance_id: agentInstanceId,
        recipe_id: recipeId,
        inputs: {
          website_url: 'https://example.com',
          max_depth: 3,
        },
        async_execution: true,
      }),
    });

    expect(response.status).toBe(202); // Accepted
    const task = await response.json();
    taskId = task.id;
    expect(task.status).toBe('pending');
  });

  it('Step 8: Poll task status until completion', async () => {
    let attempts = 0;
    let completed = false;

    while (attempts < 10 && !completed) {
      const response = await fetch(`${API_BASE}/api/v1/tasks/${taskId}`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      const task = await response.json();
      
      if (task.status === 'completed') {
        completed = true;
        expect(task.output_data).toBeDefined();
      } else if (task.status === 'failed') {
        throw new Error(`Task failed: ${task.error_message}`);
      }

      // Wait 1 second before next poll
      await new Promise((resolve) => setTimeout(resolve, 1000));
      attempts++;
    }

    expect(completed).toBe(true);
  });

  it('Step 9: View execution history in audit log', async () => {
    const response = await fetch(`${API_BASE}/api/v1/audit/agent/${agentInstanceId}`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    expect(response.ok).toBe(true);
    const logs = await response.json();
    
    expect(logs.length).toBeGreaterThan(0);
    expect(logs[0]).toHaveProperty('execution_time_ms');
    expect(logs[0]).toHaveProperty('tokens_used');
    expect(logs[0]).toHaveProperty('cost_incurred');
  });

  it('Step 10: Check subscription usage', async () => {
    const response = await fetch(`${API_BASE}/api/v1/subscriptions/usage`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    expect(response.ok).toBe(true);
    const usage = await response.json();
    
    expect(usage.active_agents).toBeGreaterThan(0);
    expect(usage.executions_this_month).toBeGreaterThan(0);
    expect(usage.total_cost).toBeGreaterThan(0);
  });

  afterAll(async () => {
    // Cleanup: Deactivate agent and delete team
    if (agentInstanceId) {
      await fetch(`${API_BASE}/api/v1/agents/${agentInstanceId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });
    }

    if (teamId) {
      await fetch(`${API_BASE}/api/v1/teams/${teamId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });
    }
  });
});
