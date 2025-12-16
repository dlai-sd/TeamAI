import { useState, useEffect } from 'react';
import axios from 'axios';
import Header from '../../components/layout/Header';
import './InvitesPage.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Invite {
  id: string;
  email: string;
  role: string;
  status: string;
  created_at: string;
  expires_at: string;
  team_id: string | null;
}

export default function InvitesPage() {
  const [invites, setInvites] = useState<Invite[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newInvite, setNewInvite] = useState({
    email: '',
    role: 'TEAM_USER',
    team_id: ''
  });

  const fetchInvites = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/invites`);
      setInvites(response.data);
    } catch (error) {
      console.error('Failed to fetch invites:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvites();
  }, []);

  const handleCreateInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE_URL}/api/v1/invites`, newInvite);
      setShowCreateModal(false);
      setNewInvite({ email: '', role: 'TEAM_USER', team_id: '' });
      fetchInvites();
      alert('Invite created successfully!');
    } catch (error: any) {
      alert(`Failed to create invite: ${error.response?.data?.detail || 'Unknown error'}`);
    }
  };

  const handleRevokeInvite = async (inviteId: string) => {
    if (!confirm('Are you sure you want to revoke this invitation?')) return;
    
    try {
      await axios.delete(`${API_BASE_URL}/api/v1/invites/${inviteId}`);
      fetchInvites();
      alert('Invite revoked successfully');
    } catch (error: any) {
      alert(`Failed to revoke invite: ${error.response?.data?.detail || 'Unknown error'}`);
    }
  };

  if (loading) {
    return (
      <>
        <Header />
        <div className="loading-container">Loading invites...</div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="invites-page">
        <div className="page-header">
          <div>
            <h1>Team Invitations</h1>
            <p>Manage user access to your agency</p>
          </div>
          <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
            + Create Invite
          </button>
        </div>

        <div className="invites-table">
          <table>
            <thead>
              <tr>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Created</th>
                <th>Expires</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {invites.map((invite) => (
                <tr key={invite.id}>
                  <td>{invite.email}</td>
                  <td>
                    <span className="role-badge">{invite.role.replace('_', ' ')}</span>
                  </td>
                  <td>
                    <span className={`status-badge status-${invite.status.toLowerCase()}`}>
                      {invite.status}
                    </span>
                  </td>
                  <td>{new Date(invite.created_at).toLocaleDateString()}</td>
                  <td>{new Date(invite.expires_at).toLocaleDateString()}</td>
                  <td>
                    {invite.status === 'pending' && (
                      <button
                        className="btn-danger-small"
                        onClick={() => handleRevokeInvite(invite.id)}
                      >
                        Revoke
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {invites.length === 0 && (
            <div className="empty-state">
              <p>No invitations yet. Create one to invite team members!</p>
            </div>
          )}
        </div>

        {showCreateModal && (
          <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <h2>Create New Invitation</h2>
              <form onSubmit={handleCreateInvite}>
                <div className="form-group">
                  <label>Email Address</label>
                  <input
                    type="email"
                    value={newInvite.email}
                    onChange={(e) => setNewInvite({ ...newInvite, email: e.target.value })}
                    placeholder="user@company.com"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Role</label>
                  <select
                    value={newInvite.role}
                    onChange={(e) => setNewInvite({ ...newInvite, role: e.target.value })}
                  >
                    <option value="TEAM_USER">Team User</option>
                    <option value="TEAM_ADMIN">Team Admin</option>
                    <option value="AGENCY_ADMIN">Agency Admin</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Team ID (Optional)</label>
                  <input
                    type="text"
                    value={newInvite.team_id}
                    onChange={(e) => setNewInvite({ ...newInvite, team_id: e.target.value })}
                    placeholder="Leave blank for agency-level access"
                  />
                </div>

                <div className="modal-actions">
                  <button type="button" className="btn-secondary" onClick={() => setShowCreateModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary">
                    Send Invitation
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
