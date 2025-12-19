import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface AIData {
  readiness: any;
  opportunities: any;
  roi: any;
  plan: any;
  ai_score: any;
}

interface Chapter7Props {
  assessmentId: string;
  onComplete: () => void;
  onBack: () => void;
}

const Chapter7AI: React.FC<Chapter7Props> = ({ assessmentId, onComplete, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [aiData, setAIData] = useState<AIData>({
    readiness: null,
    opportunities: null,
    roi: null,
    plan: null,
    ai_score: null,
  });

  const API_BASE = API_BASE_URL;

  const assessReadiness = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/ai-opportunity/${assessmentId}/assess-readiness`);
      setAIData(prev => ({ ...prev, readiness: response.data.readiness }));
      setStep(2);
    } catch (error) {
      console.error('Readiness assessment failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const identifyOpportunities = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/ai-opportunity/${assessmentId}/identify-opportunities`);
      setAIData(prev => ({ ...prev, opportunities: response.data.opportunities }));
      setStep(3);
    } catch (error) {
      console.error('Opportunity identification failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateROI = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/ai-opportunity/${assessmentId}/calculate-roi`);
      setAIData(prev => ({ ...prev, roi: response.data.roi_analysis }));
      setStep(4);
    } catch (error) {
      console.error('ROI calculation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const generatePlan = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/ai-opportunity/${assessmentId}/implementation-plan`);
      setAIData(prev => ({ ...prev, plan: response.data.implementation_plan }));
      setStep(5);
    } catch (error) {
      console.error('Plan generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateScore = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/ai-opportunity/${assessmentId}/ai-score`);
      setAIData(prev => ({ ...prev, ai_score: response.data.ai_score }));
      setStep(6);
    } catch (error) {
      console.error('Score calculation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (step === 1) assessReadiness();
    else if (step === 2) identifyOpportunities();
    else if (step === 3) calculateROI();
    else if (step === 4) generatePlan();
    else if (step === 5) calculateScore();
    else if (step === 6) onComplete();
  };

  return (
    <div className="chapter-container">
      <div className="chapter-header">
        <h1>🤖 Chapter 7: AI Opportunity Scan</h1>
        <p className="persona-intro">
          <strong>The AI Strategist</strong> identifies automation opportunities and ROI potential
        </p>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${(step / 6) * 100}%` }}></div>
        </div>
      </div>

      <div className="chapter-content">
        {step === 1 && (
          <div className="step-content">
            <h2>🔍 AI Readiness Assessment</h2>
            <p>Let's evaluate your business readiness for AI and automation.</p>
          </div>
        )}

        {step === 2 && aiData.readiness && (
          <div className="step-content">
            <h2>🔍 AI Readiness Results</h2>
            <div className="readiness-score">
              <div className="score-circle">
                <span className="score-number">{aiData.readiness.overall_readiness}</span>
                <span className="score-label">/100</span>
              </div>
              <p className="readiness-level">{aiData.readiness.readiness_level}</p>
            </div>
            <div className="readiness-factors">
              {Object.entries(aiData.readiness.readiness_factors).map(([key, factor]: [string, any]) => (
                <div key={key} className="factor-card">
                  <h4>{key.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}</h4>
                  <div className="factor-score">
                    <div className="score-bar">
                      <div className="bar-fill" style={{ width: `${factor.score}%` }}></div>
                    </div>
                    <span className="score-value">{factor.score}/100</span>
                  </div>
                  <span className={`badge badge-${factor.status.toLowerCase().replace(' ', '-')}`}>{factor.status}</span>
                </div>
              ))}
            </div>
            <h3>💡 AI Opportunities</h3>
            <p>Now let's identify specific AI/automation opportunities.</p>
          </div>
        )}

        {step === 3 && aiData.opportunities && (
          <div className="step-content">
            <h2>💡 AI Opportunities Identified</h2>
            <div className="opportunity-summary">
              <h3>{aiData.opportunities.total_opportunities_identified} opportunities worth {aiData.opportunities.potential_annual_savings}</h3>
            </div>
            <div className="opportunities-list">
              <h4>🎯 High Impact Opportunities</h4>
              {aiData.opportunities.high_impact_opportunities.map((opp: any, idx: number) => (
                <div key={idx} className="opportunity-card high-impact">
                  <div className="opp-header">
                    <h5>#{opp.priority}: {opp.title}</h5>
                    <span className="roi-badge">ROI: {opp.roi}%</span>
                  </div>
                  <p className="opp-category">{opp.category}</p>
                  <p>{opp.description}</p>
                  <div className="opp-details">
                    <div className="opp-stat">
                      <strong>Impact:</strong>
                      <p>{opp.impact.time_saved || opp.impact.efficiency_gain}</p>
                    </div>
                    <div className="opp-stat">
                      <strong>Cost:</strong>
                      <p>{opp.implementation.cost}</p>
                    </div>
                    <div className="opp-stat">
                      <strong>Timeline:</strong>
                      <p>{opp.implementation.timeline}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <h3>💰 ROI Analysis</h3>
            <p>Let's calculate the financial return on AI investment.</p>
          </div>
        )}

        {step === 4 && aiData.roi && (
          <div className="step-content">
            <h2>💰 ROI Analysis</h2>
            <div className="roi-summary">
              <div className="roi-card">
                <h4>Total Investment</h4>
                <p className="roi-value">{aiData.roi.summary.total_investment}</p>
              </div>
              <div className="roi-card">
                <h4>Annual Benefit</h4>
                <p className="roi-value positive">{aiData.roi.summary.total_annual_benefit}</p>
              </div>
              <div className="roi-card">
                <h4>Payback Period</h4>
                <p className="roi-value">{aiData.roi.summary.payback_period}</p>
              </div>
              <div className="roi-card highlight">
                <h4>3-Year ROI</h4>
                <p className="roi-value highlight">{aiData.roi.summary['3_year_roi']}</p>
              </div>
            </div>
            <div className="scenario-analysis">
              <h4>📊 Scenario Analysis</h4>
              {Object.entries(aiData.roi.scenario_analysis).map(([scenario, data]: [string, any]) => (
                <div key={scenario} className="scenario-card">
                  <h5>{scenario.charAt(0).toUpperCase() + scenario.slice(1)} Scenario</h5>
                  <p>Investment: {data.investment} | ROI: {data.roi_3_year}</p>
                  <p>Annual Benefit: {data.annual_benefit} | Payback: {data.payback}</p>
                </div>
              ))}
            </div>
            <h3>📅 Implementation Roadmap</h3>
            <p>Let's create an implementation plan.</p>
          </div>
        )}

        {step === 5 && aiData.plan && (
          <div className="step-content">
            <h2>📅 Implementation Roadmap</h2>
            <div className="roadmap">
              {Object.entries(aiData.plan.roadmap).map(([phase, data]: [string, any]) => (
                <div key={phase} className="phase-card">
                  <h3>{phase.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}</h3>
                  <p className="phase-timeline"><strong>Timeline:</strong> {data.timeline}</p>
                  <p className="phase-focus"><strong>Focus:</strong> {data.focus}</p>
                  <div className="initiatives-list">
                    {data.initiatives.map((init: any, idx: number) => (
                      <div key={idx} className="initiative-item">
                        <h5>{init.initiative}</h5>
                        <p>Duration: {init.duration} | Cost: {init.cost}</p>
                        <p className="benefit">✅ {init.benefit}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            <h3>🎯 AI Opportunity Score</h3>
            <p>Let's calculate your overall AI opportunity score.</p>
          </div>
        )}

        {step === 6 && aiData.ai_score && (
          <div className="step-content">
            <h2>🎯 AI Opportunity Score</h2>
            <div className="final-score ai-score">
              <div className="score-display">
                <div className="score-number">{aiData.ai_score.overall_score}</div>
                <div className="score-grade">Grade: {aiData.ai_score.grade}</div>
              </div>
              <div className="score-status">
                <span className="status-badge badge-success">{aiData.ai_score.ai_potential}</span>
              </div>
            </div>

            <div className="recommendation-box">
              <h3>{aiData.ai_score.recommendation.verdict}</h3>
              <p><strong>Confidence:</strong> {aiData.ai_score.recommendation.confidence}</p>
              <p><strong>Priority:</strong> {aiData.ai_score.recommendation.priority}</p>
              <p><strong>Approach:</strong> {aiData.ai_score.recommendation.approach}</p>
              <p><strong>Timeline:</strong> {aiData.ai_score.recommendation.expected_timeline}</p>
              <p><strong>Investment:</strong> {aiData.ai_score.recommendation.investment_required}</p>
            </div>
            
            <div className="verdict-box">
              <h3>🤖 AI Strategist's Verdict</h3>
              <p>{aiData.ai_score.ai_strategist_verdict}</p>
            </div>

            <div className="action-items">
              <h4>📋 Immediate Action Items</h4>
              {aiData.ai_score.action_items.map((item: any, idx: number) => (
                <div key={idx} className={`action-card priority-${item.priority}`}>
                  <span className="priority-badge">{item.priority.toUpperCase()}</span>
                  <h5>{item.action}</h5>
                  <p>Cost: {item.cost} | Timeline: {item.timeline}</p>
                  <p className="benefit">✅ {item.benefit}</p>
                </div>
              ))}
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
            {loading ? 'Processing...' : step === 6 ? 'Continue to Final Verdict →' : 'Next →'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chapter7AI;
