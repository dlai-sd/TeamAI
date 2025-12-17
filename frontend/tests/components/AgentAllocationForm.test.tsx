/**
 * Test Agent Allocation UI Component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AgentAllocationForm from '../../../src/components/AgentAllocationForm';

describe('AgentAllocationForm', () => {
  const mockOnSuccess = vi.fn();
  const mockOnCancel = vi.fn();

  const mockTeams = [
    { id: '123', name: 'SEO Team' },
    { id: '456', name: 'Social Media Team' },
  ];

  const mockAgentRoles = [
    { id: 'role-1', name: 'SEO Specialist', price: 250 },
    { id: 'role-2', name: 'Social Media Scheduler', price: 200 },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders form with all fields', () => {
    render(
      <AgentAllocationForm
        teams={mockTeams}
        agentRoles={mockAgentRoles}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByLabelText(/agent role/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/team/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/custom name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/avatar/i)).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    render(
      <AgentAllocationForm
        teams={mockTeams}
        agentRoles={mockAgentRoles}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    const submitButton = screen.getByRole('button', { name: /allocate/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/agent role is required/i)).toBeInTheDocument();
      expect(screen.getByText(/team is required/i)).toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ id: 'agent-123', name: 'RoverBot' }),
      })
    );

    render(
      <AgentAllocationForm
        teams={mockTeams}
        agentRoles={mockAgentRoles}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    // Fill form
    fireEvent.change(screen.getByLabelText(/agent role/i), {
      target: { value: 'role-1' },
    });
    fireEvent.change(screen.getByLabelText(/team/i), {
      target: { value: '123' },
    });
    fireEvent.change(screen.getByLabelText(/custom name/i), {
      target: { value: 'RoverBot' },
    });
    fireEvent.change(screen.getByLabelText(/avatar/i), {
      target: { value: '🐕' },
    });

    // Submit
    const submitButton = screen.getByRole('button', { name: /allocate/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it('shows error on API failure', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ detail: 'Subscription limit exceeded' }),
      })
    );

    render(
      <AgentAllocationForm
        teams={mockTeams}
        agentRoles={mockAgentRoles}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    // Fill and submit form
    fireEvent.change(screen.getByLabelText(/agent role/i), {
      target: { value: 'role-1' },
    });
    fireEvent.change(screen.getByLabelText(/team/i), {
      target: { value: '123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /allocate/i }));

    await waitFor(() => {
      expect(screen.getByText(/subscription limit exceeded/i)).toBeInTheDocument();
    });
  });

  it('calls onCancel when cancel button clicked', () => {
    render(
      <AgentAllocationForm
        teams={mockTeams}
        agentRoles={mockAgentRoles}
        onSuccess={mockOnSuccess}
        onCancel={mockOnCancel}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
  });
});
