/**
 * Test Task Execution UI Component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TaskExecutionPanel from '../../../src/components/TaskExecutionPanel';

describe('TaskExecutionPanel', () => {
  const mockAgent = {
    id: 'agent-123',
    custom_name: 'RoverBot',
    avatar_icon: '🐕',
    is_active: true,
  };

  const mockRecipes = [
    { id: 'recipe-1', name: 'Site Audit', description: 'Comprehensive SEO audit' },
    { id: 'recipe-2', name: 'Keyword Research', description: 'Find target keywords' },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders agent info and recipe selector', () => {
    render(<TaskExecutionPanel agent={mockAgent} recipes={mockRecipes} />);

    expect(screen.getByText('RoverBot')).toBeInTheDocument();
    expect(screen.getByText('🐕')).toBeInTheDocument();
    expect(screen.getByLabelText(/select recipe/i)).toBeInTheDocument();
  });

  it('shows input fields when recipe selected', async () => {
    render(<TaskExecutionPanel agent={mockAgent} recipes={mockRecipes} />);

    // Select recipe
    const recipeSelect = screen.getByLabelText(/select recipe/i);
    fireEvent.change(recipeSelect, { target: { value: 'recipe-1' } });

    await waitFor(() => {
      expect(screen.getByLabelText(/website url/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/max depth/i)).toBeInTheDocument();
    });
  });

  it('executes task with provided inputs', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            id: 'task-123',
            status: 'pending',
          }),
      })
    );

    render(<TaskExecutionPanel agent={mockAgent} recipes={mockRecipes} />);

    // Select recipe
    fireEvent.change(screen.getByLabelText(/select recipe/i), {
      target: { value: 'recipe-1' },
    });

    // Fill inputs
    await waitFor(() => {
      fireEvent.change(screen.getByLabelText(/website url/i), {
        target: { value: 'https://example.com' },
      });
      fireEvent.change(screen.getByLabelText(/max depth/i), {
        target: { value: '3' },
      });
    });

    // Execute
    const executeButton = screen.getByRole('button', { name: /execute/i });
    fireEvent.click(executeButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/tasks/execute'),
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
  });

  it('shows loading state during execution', async () => {
    global.fetch = vi.fn(
      () =>
        new Promise((resolve) =>
          setTimeout(
            () =>
              resolve({
                ok: true,
                json: () => Promise.resolve({ id: 'task-123' }),
              }),
            100
          )
        )
    );

    render(<TaskExecutionPanel agent={mockAgent} recipes={mockRecipes} />);

    // Select recipe and fill inputs
    fireEvent.change(screen.getByLabelText(/select recipe/i), {
      target: { value: 'recipe-1' },
    });

    await waitFor(() => {
      fireEvent.change(screen.getByLabelText(/website url/i), {
        target: { value: 'https://example.com' },
      });
    });

    // Execute
    const executeButton = screen.getByRole('button', { name: /execute/i });
    fireEvent.click(executeButton);

    // Check loading state
    expect(screen.getByText(/executing/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText(/executing/i)).not.toBeInTheDocument();
    });
  });

  it('displays execution results', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            id: 'task-123',
            status: 'completed',
            output_data: {
              'crawler.output': {
                pages: 25,
                issues: ['Missing meta description on /about'],
              },
              execution_time_ms: 5400,
            },
          }),
      })
    );

    render(<TaskExecutionPanel agent={mockAgent} recipes={mockRecipes} />);

    // Execute task
    fireEvent.change(screen.getByLabelText(/select recipe/i), {
      target: { value: 'recipe-1' },
    });

    await waitFor(() => {
      fireEvent.change(screen.getByLabelText(/website url/i), {
        target: { value: 'https://example.com' },
      });
    });

    fireEvent.click(screen.getByRole('button', { name: /execute/i }));

    // Check results displayed
    await waitFor(() => {
      expect(screen.getByText(/completed/i)).toBeInTheDocument();
      expect(screen.getByText(/25 pages/i)).toBeInTheDocument();
      expect(screen.getByText(/5400ms/i)).toBeInTheDocument();
    });
  });

  it('shows error message on execution failure', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ detail: 'Agent not active' }),
      })
    );

    render(<TaskExecutionPanel agent={mockAgent} recipes={mockRecipes} />);

    // Execute task
    fireEvent.change(screen.getByLabelText(/select recipe/i), {
      target: { value: 'recipe-1' },
    });

    await waitFor(() => {
      fireEvent.change(screen.getByLabelText(/website url/i), {
        target: { value: 'https://example.com' },
      });
    });

    fireEvent.click(screen.getByRole('button', { name: /execute/i }));

    await waitFor(() => {
      expect(screen.getByText(/agent not active/i)).toBeInTheDocument();
    });
  });

  it('disables execute button when agent inactive', () => {
    const inactiveAgent = { ...mockAgent, is_active: false };
    render(<TaskExecutionPanel agent={inactiveAgent} recipes={mockRecipes} />);

    const executeButton = screen.getByRole('button', { name: /execute/i });
    expect(executeButton).toBeDisabled();
  });
});
