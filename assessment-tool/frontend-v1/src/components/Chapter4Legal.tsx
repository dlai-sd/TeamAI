import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface LegalData {
  registration: any;
  compliance: any;
  licenses: any;
  disputes: any;
  legal_score: any;
}

interface Chapter4Props {
  assessmentId: string;
  onComplete: () => void;
  onBack: () => void;
}

const Chapter4Legal: React.FC<Chapter4Props> = ({ assessmentId, onComplete, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [legalData, setLegalData] = useState<LegalData>({
    registration: null,
    compliance: null,
    licenses: null,
    disputes: null,
    legal_score: null,
  });

  const API_BASE = API_BASE_URL;

  const verifyRegistration = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/legal/${assessmentId}/verify-registration`);
      setLegalData(prev => ({ ...prev, registration: response.data.registration_details }));
      setStep(2);
    } catch (error) {
      console.error('Registration verification failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeCompliance = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/legal/${assessmentId}/analyze-compliance`);
      setLegalData(prev => ({ ...prev, compliance: response.data.compliance_analysis }));
      setStep(3);
    } catch (error) {
      console.error('Compliance analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkLicenses = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/legal/${assessmentId}/check-licenses`);
      setLegalData(prev => ({ ...prev, licenses: response.data.license_status }));
      setStep(4);
    } catch (error) {
      console.error('License check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkDisputes = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/legal/${assessmentId}/check-legal-disputes`);
      setLegalData(prev => ({ ...prev, disputes: response.data.legal_disputes }));
      setStep(5);
    } catch (error) {
      console.error('Disputes check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateScore = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/legal/${assessmentId}/legal-score`);
      setLegalData(prev => ({ ...prev, legal_score: response.data.legal_score }));
      setStep(6);
    } catch (error) {
      console.error('Score calculation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (step === 1) verifyRegistration();
    else if (step === 2) analyzeCompliance();
    else if (step === 3) checkLicenses();
    else if (step === 4) checkDisputes();
    else if (step === 5) calculateScore();
    else if (step === 6) onComplete();
  };

  return (
    <div className="chapter-container">
      <div className="chapter-header">
        <h1>⚖️ Chapter 4: Legal & Compliance</h1>
        <p className="persona-intro">
          <strong>The Lawyer</strong> conducts a comprehensive legal audit of your business
        </p>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${(step / 6) * 100}%` }}></div>
        </div>
      </div>

      <div className="chapter-content">
        {step === 1 && (
          <div className="step-content">
            <h2>🏢 Company Registration Verification</h2>
            <p>Let's verify your company's legal registration and structure.</p>
            <div className="info-box">
              <p>We'll check:</p>
              <ul>
                <li>CIN (Corporate Identification Number)</li>
                <li>Registration date and status</li>
                <li>Directors and authorized signatories</li>
                <li>Authorized capital structure</li>
              </ul>
            </div>
          </div>
        )}

        {step === 2 && legalData.registration && (
          <div className="step-content">
            <h2>✅ Registration Verified</h2>
            <div className="data-card">
              <div className="data-row">
                <span>CIN:</span>
                <strong>{legalData.registration.cin}</strong>
              </div>
              <div className="data-row">
                <span>Status:</span>
                <span className="badge badge-success">{legalData.registration.status}</span>
              </div>
              <div className="data-row">
                <span>Registration Date:</span>
                <strong>{legalData.registration.registration_date}</strong>
              </div>
              <div className="data-row">
                <span>Directors:</span>
                <strong>{legalData.registration.directors.length}</strong>
              </div>
            </div>
            <h3>📋 Compliance Areas</h3>
            <p>Now let's analyze your regulatory compliance across key areas.</p>
          </div>
        )}

        {step === 3 && legalData.compliance && (
          <div className="step-content">
            <h2>📊 Compliance Analysis</h2>
            <div className="score-grid">
              {Object.entries(legalData.compliance.compliance_areas).map(([key, area]: [string, any]) => (
                <div key={key} className="score-card">
                  <h4>{area.area}</h4>
                  <div className="score-circle">
                    <span className="score-value">{area.score}</span>
                    <span className="score-max">/100</span>
                  </div>
                  <span className={`badge badge-${area.status.toLowerCase()}`}>{area.status}</span>
                </div>
              ))}
            </div>
            <div className="data-card mt-3">
              <h4>Overall Compliance: {legalData.compliance.overall_compliance_score}%</h4>
              {legalData.compliance.red_flags.length > 0 && (
                <div className="alert alert-warning">
                  <strong>⚠️ Red Flags:</strong>
                  <ul>
                    {legalData.compliance.red_flags.map((flag: any, idx: number) => (
                      <li key={idx}>
                        <strong>{flag.category}:</strong> {flag.issue}
                        {flag.recommendation && <div className="text-muted">{flag.recommendation}</div>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            <h3>📜 License Status</h3>
            <p>Let's check all your business licenses and their validity.</p>
          </div>
        )}

        {step === 4 && legalData.licenses && (
          <div className="step-content">
            <h2>📜 License Management</h2>
            <div className="license-summary">
              <div className="summary-stat">
                <span className="stat-value">{legalData.licenses.licenses.filter((l: any) => l.status === 'active').length}</span>
                <span className="stat-label">Active Licenses</span>
              </div>
              <div className="summary-stat">
                <span className="stat-value text-warning">{legalData.licenses.licenses.filter((l: any) => l.status === 'expiring_soon').length}</span>
                <span className="stat-label">Expiring Soon</span>
              </div>
              <div className="summary-stat">
                <span className="stat-value text-danger">{legalData.licenses.licenses.filter((l: any) => l.status === 'expired').length}</span>
                <span className="stat-label">Expired</span>
              </div>
            </div>
            <div className="license-list">
              {legalData.licenses.licenses.map((license: any, idx: number) => (
                <div key={idx} className="license-card">
                  <div className="license-header">
                    <h4>{license.license_type}</h4>
                    <span className={`badge badge-${license.status === 'active' ? 'success' : 'warning'}`}>
                      {license.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  <div className="license-details">
                    <p><strong>Number:</strong> {license.license_number}</p>
                    <p><strong>Expires:</strong> {license.expiry_date} ({license.days_to_expiry} days)</p>
                  </div>
                </div>
              ))}
            </div>
            <h3>⚖️ Legal Disputes</h3>
            <p>Let's review any litigation or legal disputes.</p>
          </div>
        )}

        {step === 5 && legalData.disputes && (
          <div className="step-content">
            <h2>⚖️ Legal Disputes History</h2>
            <div className="disputes-summary">
              <div className="summary-card">
                <span className="summary-number">{legalData.disputes.total_cases}</span>
                <span className="summary-text">Total Cases</span>
              </div>
              <div className="summary-card">
                <span className="summary-number text-warning">{legalData.disputes.active_cases}</span>
                <span className="summary-text">Active Cases</span>
              </div>
              <div className="summary-card">
                <span className="summary-number">{legalData.disputes.financial_exposure}</span>
                <span className="summary-text">Financial Exposure</span>
              </div>
            </div>
            {legalData.disputes.cases.map((case_item: any, idx: number) => (
              <div key={idx} className="case-card">
                <div className="case-header">
                  <h4>{case_item.case_type}</h4>
                  <span className={`badge badge-${case_item.status === 'active' ? 'warning' : 'success'}`}>
                    {case_item.status.toUpperCase()}
                  </span>
                </div>
                <p><strong>Filed:</strong> {case_item.filed_date}</p>
                <p><strong>Amount:</strong> {case_item.amount_involved}</p>
                <p>{case_item.description}</p>
              </div>
            ))}
            <h3>🎯 Legal Health Score</h3>
            <p>Now let's calculate your overall legal health score.</p>
          </div>
        )}

        {step === 6 && legalData.legal_score && (
          <div className="step-content">
            <h2>🎯 Legal Health Score</h2>
            <div className="final-score">
              <div className="score-display">
                <div className="score-number">{legalData.legal_score.overall_score}</div>
                <div className="score-grade">Grade: {legalData.legal_score.grade}</div>
              </div>
              <div className="score-status">
                <span className="status-badge badge-success">{legalData.legal_score.legal_health}</span>
              </div>
            </div>
            
            <div className="score-breakdown">
              <h3>Component Scores</h3>
              {Object.entries(legalData.legal_score.component_scores).map(([key, value]: [string, any]) => (
                <div key={key} className="component-bar">
                  <span className="component-label">{key.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}</span>
                  <div className="bar-container">
                    <div className="bar-fill" style={{ width: `${value}%` }}></div>
                    <span className="bar-value">{value}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="verdict-box">
              <h3>⚖️ Lawyer's Verdict</h3>
              <p>{legalData.legal_score.lawyers_verdict}</p>
            </div>

            {legalData.legal_score.action_items && legalData.legal_score.action_items.length > 0 && (
              <div className="action-items">
                <h3>📋 Action Items</h3>
                {legalData.legal_score.action_items.map((item: any, idx: number) => (
                  <div key={idx} className={`action-card priority-${item.priority}`}>
                    <span className="priority-badge">{item.priority.toUpperCase()}</span>
                    <p>{item.action}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="button-group">
          <button onClick={onBack} className="btn btn-secondary" disabled={loading}>
            ← Back
          </button>
          <button 
            onClick={handleNext} 
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Processing...' : step === 6 ? 'Continue to Operations →' : 'Next →'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chapter4Legal;
