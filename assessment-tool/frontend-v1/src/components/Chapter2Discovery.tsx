/**
 * Frontend Component: Chapter 2 - Digital Universe Discovery
 */
import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface DiscoveryData {
  website_data: any;
  social_profiles: any;
  reviews: any;
  digital_score: any;
}

interface Chapter2Props {
  assessmentId: string;
  onComplete: () => void;
  onBack: () => void;
}

const Chapter2Discovery: React.FC<Chapter2Props> = ({ assessmentId, onComplete, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [discoveryData, setDiscoveryData] = useState<DiscoveryData>({
    website_data: null,
    social_profiles: null,
    reviews: null,
    digital_score: null,
  });

  const API_BASE = API_BASE_URL;

  const scanWebsite = async () => {
    setLoading(true);
    try {
      console.log('Assessment ID:', assessmentId);
      console.log('API URL:', `${API_BASE}/v1/discovery/${assessmentId}/scan-website`);
      const response = await axios.post(`${API_BASE}/v1/discovery/${assessmentId}/scan-website`);
      console.log('Scan response:', response.data);
      setDiscoveryData(prev => ({ ...prev, website_data: response.data.website_data }));
      setStep(2);
    } catch (error: any) {
      console.error('Website scan failed:', error);
      console.error('Error details:', error.response?.data || error.message);
      alert(`Failed to scan website: ${error.response?.data?.detail || error.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const findSocialProfiles = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/discovery/${assessmentId}/find-social-profiles`);
      setDiscoveryData(prev => ({ ...prev, social_profiles: response.data.social_profiles }));
      setStep(3);
    } catch (error) {
      console.error('Social profile search failed:', error);
      alert('Failed to find social profiles. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const analyzeReviews = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/discovery/${assessmentId}/analyze-reviews`);
      setDiscoveryData(prev => ({ ...prev, reviews: response.data.review_analysis }));
      setStep(4);
    } catch (error) {
      console.error('Review analysis failed:', error);
      alert('Failed to analyze reviews. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const calculateScore = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/discovery/${assessmentId}/digital-score`);
      setDiscoveryData(prev => ({ ...prev, digital_score: response.data.digital_health_score }));
      setStep(5);
    } catch (error) {
      console.error('Score calculation failed:', error);
      alert('Failed to calculate digital score. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (step === 1) scanWebsite();
    else if (step === 2) findSocialProfiles();
    else if (step === 3) analyzeReviews();
    else if (step === 4) calculateScore();
    else if (step === 5) onComplete();
  };

  return (
    <div className="chapter-container">
      <div className="chapter-header">
        <h1>🔍 Chapter 2: Your Digital Universe</h1>
        <p className="persona-intro">
          I'm the Investigator. Let me explore your digital footprint...
        </p>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${(step / 5) * 100}%` }}></div>
      </div>

      <div className="discovery-content">
        {step === 1 && (
          <div className="step-card">
            <h2>🌐 Scanning Your Website</h2>
            <p>I'll analyze your website's technical health, content quality, and SEO performance.</p>
            <div className="scan-animation">
              <div className="radar-pulse"></div>
            </div>
          </div>
        )}

        {step === 2 && discoveryData.website_data && (
          <div className="step-card">
            <h2>✅ Website Scan Complete</h2>
            <div className="results-grid">
              <div className="metric-card">
                <span className="metric-label">Pages Found</span>
                <span className="metric-value">{discoveryData.website_data.pages_found}</span>
              </div>
              <div className="metric-card">
                <span className="metric-label">Load Speed</span>
                <span className="metric-value">{discoveryData.website_data.performance.load_time}s</span>
              </div>
              <div className="metric-card">
                <span className="metric-label">SEO Score</span>
                <span className="metric-value">{discoveryData.website_data.seo.score}/100</span>
              </div>
              <div className="metric-card">
                <span className="metric-label">Mobile Friendly</span>
                <span className="metric-value">{discoveryData.website_data.mobile_friendly ? '✓' : '✗'}</span>
              </div>
            </div>
            <p className="next-prompt">Now let's find your social media presence...</p>
          </div>
        )}

        {step === 3 && discoveryData.social_profiles && (
          <div className="step-card">
            <h2>📱 Social Media Discovery</h2>
            <div className="social-profiles-list">
              {discoveryData.social_profiles.platforms.map((platform: any) => (
                <div key={platform.name} className="social-card">
                  <div className="social-header">
                    <span className="platform-icon">{platform.name}</span>
                    <span className={`status-badge ${platform.found ? 'found' : 'not-found'}`}>
                      {platform.found ? '✓ Found' : '✗ Not Found'}
                    </span>
                  </div>
                  {platform.found && (
                    <div className="social-stats">
                      <span>👥 {platform.followers.toLocaleString()} followers</span>
                      <span>📝 {platform.posts} posts</span>
                      <span>💬 {platform.engagement_rate}% engagement</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
            <p className="next-prompt">Let's check what people are saying about you...</p>
          </div>
        )}

        {step === 4 && discoveryData.reviews && (
          <div className="step-card">
            <h2>⭐ Online Reputation Analysis</h2>
            <div className="review-summary">
              <div className="rating-display">
                <span className="rating-number">{discoveryData.reviews.overall_rating}</span>
                <span className="rating-stars">★★★★☆</span>
                <span className="rating-count">{discoveryData.reviews.total_reviews} reviews</span>
              </div>
              <div className="sentiment-breakdown">
                <div className="sentiment-bar">
                  <span className="sentiment-label">Positive</span>
                  <div className="bar-container">
                    <div className="bar positive" style={{ width: `${discoveryData.reviews.sentiment_distribution.positive}%` }}></div>
                  </div>
                  <span className="sentiment-value">{discoveryData.reviews.sentiment_distribution.positive}%</span>
                </div>
                <div className="sentiment-bar">
                  <span className="sentiment-label">Neutral</span>
                  <div className="bar-container">
                    <div className="bar neutral" style={{ width: `${discoveryData.reviews.sentiment_distribution.neutral}%` }}></div>
                  </div>
                  <span className="sentiment-value">{discoveryData.reviews.sentiment_distribution.neutral}%</span>
                </div>
                <div className="sentiment-bar">
                  <span className="sentiment-label">Negative</span>
                  <div className="bar-container">
                    <div className="bar negative" style={{ width: `${discoveryData.reviews.sentiment_distribution.negative}%` }}></div>
                  </div>
                  <span className="sentiment-value">{discoveryData.reviews.sentiment_distribution.negative}%</span>
                </div>
              </div>
            </div>
            <p className="next-prompt">Time to calculate your Digital Health Score...</p>
          </div>
        )}

        {step === 5 && discoveryData.digital_score && (
          <div className="step-card final-score">
            <h2>🎯 Your Digital Health Score</h2>
            <div className="score-circle">
              <svg viewBox="0 0 200 200" className="score-svg">
                <circle cx="100" cy="100" r="80" fill="none" stroke="#e0e0e0" strokeWidth="20" />
                <circle 
                  cx="100" 
                  cy="100" 
                  r="80" 
                  fill="none" 
                  stroke="#8b5cf6" 
                  strokeWidth="20"
                  strokeDasharray={`${discoveryData.digital_score.overall_score * 5.03} 503`}
                  transform="rotate(-90 100 100)"
                />
                <text x="100" y="110" textAnchor="middle" fontSize="48" fill="#8b5cf6" fontWeight="bold">
                  {discoveryData.digital_score.overall_score}
                </text>
              </svg>
              <span className="grade-badge">{discoveryData.digital_score.grade}</span>
            </div>
            <div className="score-breakdown">
              {Object.entries(discoveryData.digital_score.component_scores).map(([key, value]) => (
                <div key={key} className="component-score">
                  <span className="component-name">{key.replace(/_/g, ' ')}</span>
                  <div className="component-bar">
                    <div className="component-fill" style={{ width: `${value}%` }}></div>
                  </div>
                  <span className="component-value">{value}</span>
                </div>
              ))}
            </div>
            <div className="investigator-verdict">
              <p className="verdict-text">{discoveryData.digital_score.investigator_verdict.summary}</p>
              <ul className="recommendations">
                {discoveryData.digital_score.investigator_verdict.top_priorities.map((priority: string, idx: number) => (
                  <li key={idx}>{priority}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      <div className="chapter-actions">
        <button onClick={onBack} className="btn-secondary" disabled={loading}>
          ← Back
        </button>
        <button onClick={handleNext} className="btn-primary" disabled={loading}>
          {loading ? 'Processing...' : step === 5 ? 'Continue to Chapter 3 →' : 'Continue →'}
        </button>
      </div>

      <style>{`
        .chapter-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
        }

        .chapter-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .chapter-header h1 {
          font-size: 2.5rem;
          margin-bottom: 0.5rem;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .persona-intro {
          font-size: 1.2rem;
          color: #666;
        }

        .progress-bar {
          height: 8px;
          background: #e0e0e0;
          border-radius: 4px;
          margin-bottom: 2rem;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
          transition: width 0.5s ease;
        }

        .step-card {
          background: white;
          border-radius: 16px;
          padding: 3rem;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
          min-height: 400px;
        }

        .step-card h2 {
          font-size: 2rem;
          margin-bottom: 1rem;
        }

        .scan-animation {
          margin: 3rem auto;
          width: 200px;
          height: 200px;
          position: relative;
        }

        .radar-pulse {
          width: 100%;
          height: 100%;
          border: 4px solid #8b5cf6;
          border-radius: 50%;
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.2); opacity: 0.5; }
        }

        .results-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1.5rem;
          margin: 2rem 0;
        }

        .metric-card {
          background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
          border-radius: 12px;
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .metric-label {
          font-size: 0.9rem;
          color: #666;
          margin-bottom: 0.5rem;
        }

        .metric-value {
          font-size: 2rem;
          font-weight: bold;
          color: #8b5cf6;
        }

        .social-profiles-list {
          display: grid;
          gap: 1rem;
          margin: 2rem 0;
        }

        .social-card {
          border: 2px solid #e0e0e0;
          border-radius: 12px;
          padding: 1rem;
        }

        .social-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .platform-icon {
          font-size: 1.2rem;
          font-weight: bold;
        }

        .status-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.85rem;
        }

        .status-badge.found {
          background: #10b98120;
          color: #10b981;
        }

        .status-badge.not-found {
          background: #ef444420;
          color: #ef4444;
        }

        .social-stats {
          display: flex;
          gap: 1rem;
          font-size: 0.9rem;
          color: #666;
        }

        .review-summary {
          margin: 2rem 0;
        }

        .rating-display {
          text-align: center;
          margin-bottom: 2rem;
        }

        .rating-number {
          font-size: 3rem;
          font-weight: bold;
          color: #8b5cf6;
          margin-right: 1rem;
        }

        .rating-stars {
          font-size: 2rem;
          color: #fbbf24;
        }

        .rating-count {
          display: block;
          margin-top: 0.5rem;
          color: #666;
        }

        .sentiment-breakdown {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .sentiment-bar {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .sentiment-label {
          width: 100px;
          font-weight: 500;
        }

        .bar-container {
          flex: 1;
          height: 24px;
          background: #e0e0e0;
          border-radius: 12px;
          overflow: hidden;
        }

        .bar {
          height: 100%;
          transition: width 0.5s ease;
        }

        .bar.positive { background: #10b981; }
        .bar.neutral { background: #f59e0b; }
        .bar.negative { background: #ef4444; }

        .sentiment-value {
          width: 60px;
          text-align: right;
          font-weight: 500;
        }

        .score-circle {
          width: 300px;
          margin: 2rem auto;
          position: relative;
        }

        .score-svg {
          width: 100%;
          height: auto;
        }

        .grade-badge {
          position: absolute;
          bottom: 20px;
          left: 50%;
          transform: translateX(-50%);
          background: #8b5cf6;
          color: white;
          padding: 0.5rem 1.5rem;
          border-radius: 20px;
          font-weight: bold;
        }

        .score-breakdown {
          margin: 2rem 0;
        }

        .component-score {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .component-name {
          width: 150px;
          text-transform: capitalize;
        }

        .component-bar {
          flex: 1;
          height: 24px;
          background: #e0e0e0;
          border-radius: 12px;
          overflow: hidden;
        }

        .component-fill {
          height: 100%;
          background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
          transition: width 0.5s ease;
        }

        .component-value {
          width: 50px;
          text-align: right;
          font-weight: 500;
        }

        .investigator-verdict {
          background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
          border-radius: 12px;
          padding: 2rem;
          margin-top: 2rem;
        }

        .verdict-text {
          font-size: 1.2rem;
          font-weight: 500;
          margin-bottom: 1rem;
        }

        .recommendations {
          list-style: none;
          padding: 0;
        }

        .recommendations li {
          padding: 0.5rem 0;
          padding-left: 1.5rem;
          position: relative;
        }

        .recommendations li::before {
          content: '→';
          position: absolute;
          left: 0;
          color: #8b5cf6;
          font-weight: bold;
        }

        .next-prompt {
          margin-top: 2rem;
          text-align: center;
          font-size: 1.1rem;
          color: #8b5cf6;
          font-style: italic;
        }

        .chapter-actions {
          display: flex;
          justify-content: space-between;
          margin-top: 2rem;
        }

        .btn-primary, .btn-secondary {
          padding: 1rem 2rem;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 500;
          border: none;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .btn-primary {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
        }

        .btn-secondary {
          background: white;
          color: #8b5cf6;
          border: 2px solid #8b5cf6;
        }

        .btn-secondary:hover:not(:disabled) {
          background: #8b5cf610;
        }

        .btn-primary:disabled, .btn-secondary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default Chapter2Discovery;
