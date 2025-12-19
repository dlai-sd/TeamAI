import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface OpsData {
  team: any;
  efficiency: any;
  processes: any;
  resources: any;
  operations_score: any;
}

interface Chapter5Props {
  assessmentId: string;
  onComplete: () => void;
  onBack: () => void;
}

const Chapter5Operations: React.FC<Chapter5Props> = ({ assessmentId, onComplete, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [opsData, setOpsData] = useState<OpsData>({
    team: null,
    efficiency: null,
    processes: null,
    resources: null,
    operations_score: null,
  });

  const API_BASE = API_BASE_URL;

  const analyzeTeam = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/operations/${assessmentId}/analyze-team`);
      setOpsData(prev => ({ ...prev, team: response.data.team_analysis }));
      setStep(2);
    } catch (error) {
      console.error('Team analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const assessEfficiency = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/operations/${assessmentId}/assess-efficiency`);
      setOpsData(prev => ({ ...prev, efficiency: response.data.efficiency_assessment }));
      setStep(3);
    } catch (error) {
      console.error('Efficiency assessment failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const evaluateProcesses = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/operations/${assessmentId}/evaluate-processes`);
      setOpsData(prev => ({ ...prev, processes: response.data.process_evaluation }));
      setStep(4);
    } catch (error) {
      console.error('Process evaluation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkResources = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/operations/${assessmentId}/check-resources`);
      setOpsData(prev => ({ ...prev, resources: response.data.resource_analysis }));
      setStep(5);
    } catch (error) {
      console.error('Resource check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateScore = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/operations/${assessmentId}/operations-score`);
      setOpsData(prev => ({ ...prev, operations_score: response.data.operations_score }));
      setStep(6);
    } catch (error) {
      console.error('Score calculation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (step === 1) analyzeTeam();
    else if (step === 2) assessEfficiency();
    else if (step === 3) evaluateProcesses();
    else if (step === 4) checkResources();
    else if (step === 5) calculateScore();
    else if (step === 6) onComplete();
  };

  return (
    <div className="chapter-container">
      <div className="chapter-header">
        <h1>⚙️ Chapter 5: Operations & Team</h1>
        <p className="persona-intro">
          <strong>The Operations Manager</strong> evaluates your team structure and operational efficiency
        </p>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${(step / 6) * 100}%` }}></div>
        </div>
      </div>

      <div className="chapter-content">
        {step === 1 && (
          <div className="step-content">
            <h2>👥 Team Structure Analysis</h2>
            <p>Let's analyze your team composition and organizational structure.</p>
          </div>
        )}

        {step === 2 && opsData.team && (
          <div className="step-content">
            <h2>👥 Team Analysis Results</h2>
            <div className="data-card">
              <h3>{opsData.team.total_employees} Total Employees</h3>
              <div className="department-grid">
                {opsData.team.departments.map((dept: any, idx: number) => (
                  <div key={idx} className="department-card">
                    <h4>{dept.name}</h4>
                    <p><strong>{dept.headcount}</strong> employees</p>
                    <p>Avg Experience: {dept.avg_experience_years} years</p>
                    <p>Turnover: <span className={dept.turnover_rate.includes('15') ? 'text-warning' : 'text-success'}>{dept.turnover_rate}</span></p>
                  </div>
                ))}
              </div>
            </div>
            <h3>📊 Efficiency Metrics</h3>
            <p>Now let's assess your operational efficiency.</p>
          </div>
        )}

        {step === 3 && opsData.efficiency && (
          <div className="step-content">
            <h2>📊 Efficiency Assessment</h2>
            <div className="score-display">
              <span className="score-number">{opsData.efficiency.overall_efficiency_score}</span>
              <span className="score-label">Efficiency Score</span>
            </div>
            <div className="metrics-grid">
              {Object.entries(opsData.efficiency.productivity_metrics).map(([key, metric]: [string, any]) => (
                <div key={key} className="metric-card">
                  <h4>{key.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}</h4>
                  <p className="metric-value">{metric.value}</p>
                  <span className={`badge badge-${metric.status.toLowerCase()}`}>{metric.status}</span>
                </div>
              ))}
            </div>
            <h3>🔄 Process Evaluation</h3>
            <p>Let's evaluate your business processes.</p>
          </div>
        )}

        {step === 4 && opsData.processes && (
          <div className="step-content">
            <h2>🔄 Process Maturity</h2>
            <div className="maturity-card">
              <h3>Overall Level: {opsData.processes.process_maturity.overall_level}</h3>
              <p>{opsData.processes.process_maturity.description}</p>
            </div>
            <div className="process-list">
              {opsData.processes.core_processes.map((process: any, idx: number) => (
                <div key={idx} className="process-card">
                  <div className="process-header">
                    <h4>{process.name}</h4>
                    <div className="process-score">{process.score}/100</div>
                  </div>
                  <p><strong>Maturity:</strong> {process.maturity_level}</p>
                  <p><strong>Automation:</strong> {process.automation}</p>
                  {process.pain_points && process.pain_points.length > 0 && (
                    <div className="pain-points">
                      <strong>⚠️ Pain Points:</strong>
                      <ul>
                        {process.pain_points.map((point: string, pidx: number) => (
                          <li key={pidx}>{point}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
            <h3>💼 Resource Allocation</h3>
            <p>Let's check your resource utilization.</p>
          </div>
        )}

        {step === 5 && opsData.resources && (
          <div className="step-content">
            <h2>💼 Resource Analysis</h2>
            <div className="resource-sections">
              <div className="resource-section">
                <h3>👥 Human Resources</h3>
                <p>Utilization Rate: <strong>{opsData.resources.human_resources.utilization_rate}</strong></p>
                {opsData.resources.human_resources.skill_gaps.map((gap: any, idx: number) => (
                  <div key={idx} className="gap-card">
                    <h4>{gap.area}</h4>
                    <p>Gap: {gap.gap} | Priority: <span className={`badge badge-${gap.priority.toLowerCase()}`}>{gap.priority}</span></p>
                  </div>
                ))}
              </div>
              <div className="resource-section">
                <h3>💻 Technology Resources</h3>
                <p>IT Spend: {opsData.resources.technology_resources.it_spend}/year ({opsData.resources.technology_resources.it_spend_percentage})</p>
                <p className="text-warning">Benchmark: {opsData.resources.technology_resources.benchmark}</p>
              </div>
            </div>
            <h3>🎯 Operations Score</h3>
            <p>Let's calculate your overall operations score.</p>
          </div>
        )}

        {step === 6 && opsData.operations_score && (
          <div className="step-content">
            <h2>🎯 Operations Score</h2>
            <div className="final-score">
              <div className="score-display">
                <div className="score-number">{opsData.operations_score.overall_score}</div>
                <div className="score-grade">Grade: {opsData.operations_score.grade}</div>
              </div>
              <div className="score-status">
                <span className="status-badge badge-success">{opsData.operations_score.operations_health}</span>
              </div>
            </div>
            
            <div className="verdict-box">
              <h3>⚙️ Operations Manager's Verdict</h3>
              <p>{opsData.operations_score.operations_manager_verdict}</p>
            </div>

            <div className="strengths-weaknesses">
              <div className="strengths">
                <h4>✅ Strengths</h4>
                <ul>
                  {opsData.operations_score.strengths.map((item: string, idx: number) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
              <div className="weaknesses">
                <h4>⚠️ Weaknesses</h4>
                <ul>
                  {opsData.operations_score.weaknesses.map((item: string, idx: number) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
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
            {loading ? 'Processing...' : step === 6 ? 'Continue to Customer Insights →' : 'Next →'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chapter5Operations;
