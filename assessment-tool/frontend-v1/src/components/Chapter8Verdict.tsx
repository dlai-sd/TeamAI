import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface VerdictData {
  aggregate: any;
  summary: any;
  recommendations: any;
  final_verdict: any;
}

interface Chapter8Props {
  assessmentId: string;
  onBack: () => void;
}

const Chapter8Verdict: React.FC<Chapter8Props> = ({ assessmentId, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [verdictData, setVerdictData] = useState<VerdictData>({
    aggregate: null,
    summary: null,
    recommendations: null,
    final_verdict: null,
  });

  const API_BASE = API_BASE_URL;

  const aggregateScores = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/verdict/${assessmentId}/aggregate-scores`);
      setVerdictData(prev => ({ ...prev, aggregate: response.data.aggregate_scores }));
      setStep(2);
    } catch (error) {
      console.error('Score aggregation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateSummary = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/verdict/${assessmentId}/executive-summary`);
      setVerdictData(prev => ({ ...prev, summary: response.data.executive_summary }));
      setStep(3);
    } catch (error) {
      console.error('Summary generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateRecommendations = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/verdict/${assessmentId}/strategic-recommendations`);
      setVerdictData(prev => ({ ...prev, recommendations: response.data.recommendations }));
      setStep(4);
    } catch (error) {
      console.error('Recommendations generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateFinalVerdict = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/verdict/${assessmentId}/final-verdict`);
      setVerdictData(prev => ({ ...prev, final_verdict: response.data.final_verdict }));
      setStep(5);
    } catch (error) {
      console.error('Final verdict generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (step === 1) aggregateScores();
    else if (step === 2) generateSummary();
    else if (step === 3) generateRecommendations();
    else if (step === 4) generateFinalVerdict();
  };

  return (
    <div className="chapter-container">
      <div className="chapter-header">
        <h1>🎯 Chapter 8: The Final Verdict</h1>
        <p className="persona-intro">
          <strong>The CEO Advisor</strong> synthesizes all insights into actionable strategy
        </p>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${(step / 5) * 100}%` }}></div>
        </div>
      </div>

      <div className="chapter-content">
        {step === 1 && (
          <div className="step-content">
            <h2>📊 Aggregate Assessment Scores</h2>
            <p>Let's compile all chapter scores into your overall business health score.</p>
            <button onClick={aggregateScores} className="btn btn-primary" disabled={loading}>
              {loading ? 'Calculating...' : 'Calculate Overall Score'}
            </button>
          </div>
        )}

        {step === 2 && verdictData.aggregate && (
          <div className="step-content">
            <h2>📊 Overall Assessment Score</h2>
            <div className="overall-score-display">
              <div className="main-score">
                <span className="score-number">{verdictData.aggregate.weighted_overall_score}</span>
                <span className="score-grade">{verdictData.aggregate.overall_grade}</span>
              </div>
              <p className="health-status">{verdictData.aggregate.business_health}</p>
              <p className="percentile">Better than {verdictData.aggregate.percentile_rank}% of similar businesses</p>
            </div>
            
            <div className="chapter-scores-grid">
              {Object.entries(verdictData.aggregate.chapter_scores).map(([key, score]: [string, any]) => (
                <div key={key} className="chapter-score-card">
                  <h4>{key.replace(/_/g, ' ').replace(/ch\d+/g, '').trim()}</h4>
                  <div className="score-badge">{score.score}/100</div>
                  <span className={`grade-badge grade-${score.grade.replace('+', 'plus').replace('-', 'minus')}`}>{score.grade}</span>
                </div>
              ))}
            </div>

            <h3>📝 Executive Summary</h3>
            <p>Now let's create an executive summary of your assessment.</p>
          </div>
        )}

        {step === 3 && verdictData.summary && (
          <div className="step-content">
            <h2>📝 Executive Summary</h2>
            <div className="exec-summary-header">
              <h3>{verdictData.summary.business_snapshot.company_name}</h3>
              <p>{verdictData.summary.business_snapshot.industry} | {verdictData.summary.business_snapshot.size} | {verdictData.summary.business_snapshot.revenue}</p>
              <p className="assessment-date">Assessed: {verdictData.summary.business_snapshot.assessment_date}</p>
            </div>

            <div className="exec-verdict">
              <h3>{verdictData.summary.executive_verdict.headline}</h3>
              <p className="verdict-summary">{verdictData.summary.executive_verdict.summary}</p>
              <p><strong>Confidence Level:</strong> {verdictData.summary.executive_verdict.confidence_level} | <strong>Data Quality:</strong> {verdictData.summary.executive_verdict.data_quality_score}/100</p>
            </div>

            <div className="strengths-weaknesses-grid">
              <div className="strengths-section">
                <h4>💪 Top Strengths</h4>
                {verdictData.summary.top_strengths.map((strength: any, idx: number) => (
                  <div key={idx} className="strength-card">
                    <div className="strength-header">
                      <h5>{strength.area}</h5>
                      <span className="score-badge">{strength.score}</span>
                    </div>
                    <p>{strength.highlight}</p>
                  </div>
                ))}
              </div>
              <div className="weaknesses-section">
                <h4>⚠️ Critical Areas</h4>
                {verdictData.summary.critical_weaknesses.map((weakness: any, idx: number) => (
                  <div key={idx} className="weakness-card">
                    <div className="weakness-header">
                      <h5>{weakness.area}</h5>
                      <span className={`severity-badge severity-${weakness.severity}`}>{weakness.severity}</span>
                    </div>
                    <p><strong>Issue:</strong> {weakness.issue}</p>
                    <p><strong>Impact:</strong> {weakness.impact}</p>
                  </div>
                ))}
              </div>
            </div>

            <h3>🎯 Strategic Recommendations</h3>
            <p>Now let's outline your strategic action plan.</p>
          </div>
        )}

        {step === 4 && verdictData.recommendations && (
          <div className="step-content">
            <h2>🎯 Strategic Recommendations</h2>
            
            <div className="immediate-actions">
              <h3>🚨 Immediate Actions (Top Priority)</h3>
              {verdictData.recommendations.immediate_actions.map((action: any, idx: number) => (
                <div key={idx} className="action-card immediate">
                  <div className="action-header">
                    <span className="priority-number">#{action.priority}</span>
                    <h4>{action.action}</h4>
                  </div>
                  <p className="rationale">{action.rationale}</p>
                  <div className="action-details">
                    <div className="detail-item">
                      <strong>Investment:</strong> {action.investment}
                    </div>
                    <div className="detail-item">
                      <strong>Timeline:</strong> {action.timeline}
                    </div>
                    <div className="detail-item">
                      <strong>Expected Benefit:</strong> {action.expected_benefit}
                    </div>
                    <div className="detail-item">
                      <strong>Owner:</strong> {action.owner}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="investment-summary">
              <h3>💰 Investment Summary</h3>
              <div className="investment-grid">
                <div className="investment-card">
                  <span className="inv-label">Year 1 Investment</span>
                  <span className="inv-value">{verdictData.recommendations.investment_summary.total_required_year_1}</span>
                </div>
                <div className="investment-card positive">
                  <span className="inv-label">Year 1 Return</span>
                  <span className="inv-value">{verdictData.recommendations.investment_summary.expected_return_year_1}</span>
                </div>
                <div className="investment-card highlight">
                  <span className="inv-label">3-Year ROI</span>
                  <span className="inv-value">{verdictData.recommendations.investment_summary['3_year_roi']}</span>
                </div>
                <div className="investment-card">
                  <span className="inv-label">Payback Period</span>
                  <span className="inv-value">{verdictData.recommendations.investment_summary.payback_period}</span>
                </div>
              </div>
            </div>

            <h3>✅ Final Verdict</h3>
            <p>Let's compile the final verdict for your business.</p>
          </div>
        )}

        {step === 5 && verdictData.final_verdict && (
          <div className="step-content final-verdict-page">
            <h2>✅ Assessment Complete!</h2>
            
            <div className="final-score-display">
              <div className="score-main">
                <span className="score-number">{verdictData.final_verdict.overall_verdict.score}</span>
                <span className="score-grade">{verdictData.final_verdict.overall_verdict.grade}</span>
              </div>
              <p className="score-rating">{verdictData.final_verdict.overall_verdict.rating}</p>
              <p className="score-confidence">Confidence: {verdictData.final_verdict.overall_verdict.confidence}</p>
            </div>

            <div className="ceo-message">
              <h3>📋 {verdictData.final_verdict.ceo_summary.headline}</h3>
              <div className="message-content">
                {verdictData.final_verdict.ceo_summary.message.split('\n\n').map((para: string, idx: number) => (
                  <p key={idx}>{para}</p>
                ))}
              </div>
              <div className="message-signature">
                <p><strong>{verdictData.final_verdict.ceo_summary.signed}</strong></p>
                <p>{verdictData.final_verdict.ceo_summary.date}</p>
              </div>
            </div>

            <div className="next-steps">
              <h3>🚀 Next Steps</h3>
              <div className="timeline-steps">
                <div className="timeline-section">
                  <h4>Week 1</h4>
                  <ul>
                    {verdictData.final_verdict.next_steps.week_1.map((step: string, idx: number) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ul>
                </div>
                <div className="timeline-section">
                  <h4>Weeks 2-4</h4>
                  <ul>
                    {verdictData.final_verdict.next_steps.week_2_4.map((step: string, idx: number) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ul>
                </div>
                <div className="timeline-section">
                  <h4>Months 2-3</h4>
                  <ul>
                    {verdictData.final_verdict.next_steps.month_2_3.map((step: string, idx: number) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            <div className="assessment-metadata">
              <h4>📊 Assessment Details</h4>
              <p><strong>Chapters Completed:</strong> {verdictData.final_verdict.assessment_metadata.chapters_completed}</p>
              <p><strong>Data Points Analyzed:</strong> {verdictData.final_verdict.assessment_metadata.total_data_points}</p>
              <p><strong>Personas Consulted:</strong> {verdictData.final_verdict.assessment_metadata.personas_consulted}</p>
              <p><strong>Assessment Duration:</strong> {verdictData.final_verdict.assessment_metadata.assessment_duration}</p>
            </div>

            <div className="certification-box">
              <h4>🏆 Certification</h4>
              <p><strong>Assessment ID:</strong> {verdictData.final_verdict.certification.assessment_id}</p>
              <p><strong>Completed:</strong> {new Date(verdictData.final_verdict.certification.completed_date).toLocaleString()}</p>
              <p><strong>Valid Until:</strong> {verdictData.final_verdict.certification.valid_until}</p>
              <p><strong>Recommended Reassessment:</strong> {verdictData.final_verdict.certification.recommended_reassessment}</p>
              <p className="signature">{verdictData.final_verdict.certification.signature}</p>
            </div>

            <div className="final-actions">
              <button className="btn btn-primary btn-large" onClick={() => window.print()}>
                📄 Download Report
              </button>
              <button className="btn btn-secondary" onClick={() => window.location.reload()}>
                🔄 Start New Assessment
              </button>
            </div>
          </div>
        )}

        <div className="button-group">
          <button onClick={onBack} className="btn btn-secondary" disabled={loading || step === 5}>
            ← Back
          </button>
          {step < 5 && (
            <button 
              onClick={handleNext} 
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Processing...' : 'Next →'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Chapter8Verdict;
