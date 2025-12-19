import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface CustomerData {
  demographics: any;
  satisfaction: any;
  retention: any;
  positioning: any;
  customer_score: any;
}

interface Chapter6Props {
  assessmentId: string;
  onComplete: () => void;
  onBack: () => void;
}

const Chapter6Customers: React.FC<Chapter6Props> = ({ assessmentId, onComplete, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [customerData, setCustomerData] = useState<CustomerData>({
    demographics: null,
    satisfaction: null,
    retention: null,
    positioning: null,
    customer_score: null,
  });

  const API_BASE = API_BASE_URL;

  const analyzeDemographics = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/customers/${assessmentId}/analyze-demographics`);
      setCustomerData(prev => ({ ...prev, demographics: response.data.demographics }));
      setStep(2);
    } catch (error) {
      console.error('Demographics analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const assessSatisfaction = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/customers/${assessmentId}/assess-satisfaction`);
      setCustomerData(prev => ({ ...prev, satisfaction: response.data.satisfaction }));
      setStep(3);
    } catch (error) {
      console.error('Satisfaction assessment failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const evaluateRetention = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/customers/${assessmentId}/evaluate-retention`);
      setCustomerData(prev => ({ ...prev, retention: response.data.retention }));
      setStep(4);
    } catch (error) {
      console.error('Retention evaluation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzePositioning = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/customers/${assessmentId}/market-positioning`);
      setCustomerData(prev => ({ ...prev, positioning: response.data.positioning }));
      setStep(5);
    } catch (error) {
      console.error('Positioning analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateScore = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/customers/${assessmentId}/customer-score`);
      setCustomerData(prev => ({ ...prev, customer_score: response.data.customer_score }));
      setStep(6);
    } catch (error) {
      console.error('Score calculation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (step === 1) analyzeDemographics();
    else if (step === 2) assessSatisfaction();
    else if (step === 3) evaluateRetention();
    else if (step === 4) analyzePositioning();
    else if (step === 5) calculateScore();
    else if (step === 6) onComplete();
  };

  return (
    <div className="chapter-container">
      <div className="chapter-header">
        <h1>👥 Chapter 6: Customer Insights</h1>
        <p className="persona-intro">
          <strong>The Customer Strategist</strong> analyzes your customer base and market position
        </p>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${(step / 6) * 100}%` }}></div>
        </div>
      </div>

      <div className="chapter-content">
        {step === 1 && (
          <div className="step-content">
            <h2>📊 Customer Demographics</h2>
            <p>Let's understand who your customers are.</p>
          </div>
        )}

        {step === 2 && customerData.demographics && (
          <div className="step-content">
            <h2>📊 Customer Base Analysis</h2>
            <div className="customer-stats">
              <div className="stat-card">
                <span className="stat-value">{customerData.demographics.total_customers.toLocaleString()}</span>
                <span className="stat-label">Total Customers</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{customerData.demographics.active_customers.toLocaleString()}</span>
                <span className="stat-label">Active</span>
              </div>
            </div>
            <div className="segment-grid">
              {customerData.demographics.customer_segments.map((segment: any, idx: number) => (
                <div key={idx} className="segment-card">
                  <h3>{segment.segment}</h3>
                  <p><strong>{segment.count}</strong> customers ({segment.percentage}%)</p>
                  <p>Avg Order: {segment.avg_order_value}</p>
                  <p>LTV: {segment.lifetime_value}</p>
                </div>
              ))}
            </div>
            <h3>😊 Customer Satisfaction</h3>
            <p>Now let's assess customer satisfaction levels.</p>
          </div>
        )}

        {step === 3 && customerData.satisfaction && (
          <div className="step-content">
            <h2>😊 Satisfaction Metrics</h2>
            <div className="nps-display">
              <div className="nps-score">{customerData.satisfaction.nps_score}</div>
              <div className="nps-label">Net Promoter Score</div>
              <span className="badge badge-success">{customerData.satisfaction.nps_category}</span>
            </div>
            <div className="satisfaction-metrics">
              <div className="metric">
                <h4>CSAT Score</h4>
                <p className="metric-value">{customerData.satisfaction.csat_score}/5.0</p>
              </div>
              <div className="metric">
                <h4>Total Reviews</h4>
                <p className="metric-value">{customerData.satisfaction.feedback_analysis.total_reviews.toLocaleString()}</p>
              </div>
            </div>
            <div className="feedback-breakdown">
              <h4>Feedback Distribution</h4>
              <div className="feedback-bars">
                <div className="feedback-bar positive">
                  <span>Positive</span>
                  <div className="bar" style={{ width: `${(customerData.satisfaction.feedback_analysis.positive / customerData.satisfaction.feedback_analysis.total_reviews) * 100}%` }}></div>
                  <span>{customerData.satisfaction.feedback_analysis.positive}</span>
                </div>
                <div className="feedback-bar neutral">
                  <span>Neutral</span>
                  <div className="bar" style={{ width: `${(customerData.satisfaction.feedback_analysis.neutral / customerData.satisfaction.feedback_analysis.total_reviews) * 100}%` }}></div>
                  <span>{customerData.satisfaction.feedback_analysis.neutral}</span>
                </div>
                <div className="feedback-bar negative">
                  <span>Negative</span>
                  <div className="bar" style={{ width: `${(customerData.satisfaction.feedback_analysis.negative / customerData.satisfaction.feedback_analysis.total_reviews) * 100}%` }}></div>
                  <span>{customerData.satisfaction.feedback_analysis.negative}</span>
                </div>
              </div>
            </div>
            <h3>🔄 Retention Analysis</h3>
            <p>Let's evaluate customer retention and churn.</p>
          </div>
        )}

        {step === 4 && customerData.retention && (
          <div className="step-content">
            <h2>🔄 Retention Metrics</h2>
            <div className="retention-stats">
              <div className="retention-card success">
                <span className="value">{customerData.retention.retention_rate}%</span>
                <span className="label">Retention Rate</span>
              </div>
              <div className="retention-card warning">
                <span className="value">{customerData.retention.churn_rate}%</span>
                <span className="label">Churn Rate</span>
              </div>
              <div className="retention-card info">
                <span className="value">{customerData.retention.repeat_purchase_rate}%</span>
                <span className="label">Repeat Purchase</span>
              </div>
            </div>
            <div className="at-risk-section">
              <h4>⚠️ At-Risk Customers</h4>
              <p><strong>{customerData.retention.at_risk_customers.count}</strong> customers ({customerData.retention.at_risk_customers.percentage}%)</p>
              <ul>
                {customerData.retention.at_risk_customers.criteria.map((criterion: string, idx: number) => (
                  <li key={idx}>{criterion}</li>
                ))}
              </ul>
            </div>
            <h3>📍 Market Positioning</h3>
            <p>Let's analyze your competitive position.</p>
          </div>
        )}

        {step === 5 && customerData.positioning && (
          <div className="step-content">
            <h2>📍 Market Position</h2>
            <div className="market-stats">
              <div className="market-stat">
                <h4>Market Share</h4>
                <p className="stat-value">{customerData.positioning.market_share}%</p>
              </div>
              <div className="market-stat">
                <h4>Market Rank</h4>
                <p className="stat-value">#{customerData.positioning.market_rank}</p>
              </div>
              <div className="market-stat">
                <h4>Position</h4>
                <p className="stat-value">{customerData.positioning.competitive_position}</p>
              </div>
            </div>
            <div className="competitors-section">
              <h4>🏆 Key Competitors</h4>
              {customerData.positioning.key_competitors.map((competitor: any, idx: number) => (
                <div key={idx} className="competitor-card">
                  <h5>{competitor.name}</h5>
                  <p>Market Share: {competitor.market_share}%</p>
                  <p>Strength: {competitor.strength}</p>
                </div>
              ))}
            </div>
            <h3>🎯 Customer Score</h3>
            <p>Let's calculate your overall customer health score.</p>
          </div>
        )}

        {step === 6 && customerData.customer_score && (
          <div className="step-content">
            <h2>🎯 Customer Health Score</h2>
            <div className="final-score">
              <div className="score-display">
                <div className="score-number">{customerData.customer_score.overall_score}</div>
                <div className="score-grade">Grade: {customerData.customer_score.grade}</div>
              </div>
              <div className="score-status">
                <span className="status-badge badge-success">{customerData.customer_score.customer_health}</span>
              </div>
            </div>
            
            <div className="verdict-box">
              <h3>👥 Customer Strategist's Verdict</h3>
              <p>{customerData.customer_score.customer_strategist_verdict}</p>
            </div>

            <div className="opportunities-section">
              <h4>💡 Key Opportunities</h4>
              {customerData.customer_score.opportunities.map((opp: any, idx: number) => (
                <div key={idx} className="opportunity-card">
                  <h5>{opp.area}</h5>
                  <p><strong>Impact:</strong> <span className={`badge badge-${opp.impact.toLowerCase()}`}>{opp.impact}</span></p>
                  <p>{opp.description || opp.potential_revenue_saved}</p>
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
            {loading ? 'Processing...' : step === 6 ? 'Continue to AI Opportunity →' : 'Next →'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chapter6Customers;
