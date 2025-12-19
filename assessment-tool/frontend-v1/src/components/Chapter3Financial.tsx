/**
 * Frontend Component: Chapter 3 - The Money Story (Financial Analysis)
 */
import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface FinancialData {
  revenue: any;
  expenses: any;
  cash_flow: any;
  debt: any;
  score: any;
}

interface Chapter3Props {
  assessmentId: string;
  onComplete: () => void;
  onBack: () => void;
}

const Chapter3Financial: React.FC<Chapter3Props> = ({ assessmentId, onComplete, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [financialData, setFinancialData] = useState<FinancialData>({
    revenue: null,
    expenses: null,
    cash_flow: null,
    debt: null,
    score: null,
  });

  const API_BASE = API_BASE_URL;

  const analyzeRevenue = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/financial/${assessmentId}/analyze-revenue`);
      setFinancialData(prev => ({ ...prev, revenue: response.data.revenue_analysis }));
      setStep(2);
    } catch (error) {
      console.error('Revenue analysis failed:', error);
      alert('Failed to analyze revenue. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const analyzeExpenses = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/financial/${assessmentId}/analyze-expenses`);
      setFinancialData(prev => ({ ...prev, expenses: response.data.expense_analysis }));
      setStep(3);
    } catch (error) {
      console.error('Expense analysis failed:', error);
      alert('Failed to analyze expenses. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const analyzeCashFlow = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/financial/${assessmentId}/analyze-cash-flow`);
      setFinancialData(prev => ({ ...prev, cash_flow: response.data.cash_flow_analysis }));
      setStep(4);
    } catch (error) {
      console.error('Cash flow analysis failed:', error);
      alert('Failed to analyze cash flow. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const analyzeDebt = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/financial/${assessmentId}/analyze-debt`);
      setFinancialData(prev => ({ ...prev, debt: response.data.debt_analysis }));
      setStep(5);
    } catch (error) {
      console.error('Debt analysis failed:', error);
      alert('Failed to analyze debt. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const calculateScore = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/v1/financial/${assessmentId}/financial-score`);
      setFinancialData(prev => ({ ...prev, score: response.data.financial_health_score }));
      setStep(6);
    } catch (error) {
      console.error('Score calculation failed:', error);
      alert('Failed to calculate financial score. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (step === 1) analyzeRevenue();
    else if (step === 2) analyzeExpenses();
    else if (step === 3) analyzeCashFlow();
    else if (step === 4) analyzeDebt();
    else if (step === 5) calculateScore();
    else if (step === 6) onComplete();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="chapter-container">
      <div className="chapter-header">
        <h1>💰 Chapter 3: The Money Story</h1>
        <p className="persona-intro">
          I'm the CFO. Let me understand your financial health...
        </p>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${(step / 6) * 100}%` }}></div>
      </div>

      <div className="financial-content">
        {step === 1 && (
          <div className="step-card">
            <h2>📈 Analyzing Revenue Patterns</h2>
            <p>Understanding your revenue growth trajectory and business model...</p>
            <div className="chart-placeholder">
              <div className="pulse-loader"></div>
            </div>
          </div>
        )}

        {step === 2 && financialData.revenue && (
          <div className="step-card">
            <h2>✅ Revenue Analysis Complete</h2>
            <div className="financial-metrics">
              <div className="metric-large">
                <span className="metric-label">Annual Revenue</span>
                <span className="metric-value">{formatCurrency(financialData.revenue.annual_revenue.current_year)}</span>
                <span className={`growth-badge ${financialData.revenue.annual_revenue.growth_rate > 0 ? 'positive' : 'negative'}`}>
                  {financialData.revenue.annual_revenue.growth_rate > 0 ? '↑' : '↓'} {Math.abs(financialData.revenue.annual_revenue.growth_rate)}% YoY
                </span>
              </div>
              <div className="revenue-breakdown">
                <h3>Revenue Mix</h3>
                <div className="pie-chart-placeholder">
                  {Object.entries(financialData.revenue.revenue_breakdown).map(([key, value]) => (
                    <div key={key} className="breakdown-item">
                      <span className="breakdown-label">{key.replace(/_/g, ' ')}</span>
                      <div className="breakdown-bar">
                        <div className="breakdown-fill" style={{ width: `${value}%` }}></div>
                      </div>
                      <span className="breakdown-value">{value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <p className="next-prompt">Now let's examine your expense structure...</p>
          </div>
        )}

        {step === 3 && financialData.expenses && (
          <div className="step-card">
            <h2>💸 Expense Analysis</h2>
            <div className="expense-overview">
              <div className="metric-row">
                <div className="metric-box">
                  <span className="metric-label">Total Expenses</span>
                  <span className="metric-value">{formatCurrency(financialData.expenses.total_annual_expenses)}</span>
                </div>
                <div className="metric-box">
                  <span className="metric-label">Monthly Burn</span>
                  <span className="metric-value">{formatCurrency(financialData.expenses.monthly_burn_rate)}</span>
                </div>
                <div className="metric-box">
                  <span className="metric-label">Gross Margin</span>
                  <span className="metric-value">{financialData.expenses.efficiency_metrics.gross_margin}%</span>
                </div>
              </div>
              <div className="expense-breakdown">
                <h3>Cost Structure</h3>
                {Object.entries(financialData.expenses.expense_breakdown).map(([key, value]) => (
                  <div key={key} className="expense-item">
                    <span className="expense-label">{key.replace(/_/g, ' ')}</span>
                    <div className="expense-bar">
                      <div className="expense-fill" style={{ width: `${value}%` }}></div>
                    </div>
                    <span className="expense-value">{value}%</span>
                  </div>
                ))}
              </div>
              {financialData.expenses.areas_of_concern && (
                <div className="concerns-box">
                  <h4>⚠️ Areas of Concern</h4>
                  <ul>
                    {financialData.expenses.areas_of_concern.map((concern: string, idx: number) => (
                      <li key={idx}>{concern}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            <p className="next-prompt">Let's analyze your cash flow position...</p>
          </div>
        )}

        {step === 4 && financialData.cash_flow && (
          <div className="step-card">
            <h2>💵 Cash Flow Health</h2>
            <div className="cashflow-dashboard">
              <div className="runway-alert">
                <span className="runway-label">Cash Runway</span>
                <span className="runway-value">{financialData.cash_flow.runway_months} months</span>
                <span className={`runway-status ${financialData.cash_flow.runway_months > 6 ? 'good' : 'warning'}`}>
                  {financialData.cash_flow.runway_months > 6 ? '✓ Healthy' : '⚠️ Watch'}
                </span>
              </div>
              <div className="cashflow-metrics">
                <div className="cashflow-item">
                  <span className="label">Current Balance</span>
                  <span className="value">{formatCurrency(financialData.cash_flow.current_cash_balance)}</span>
                </div>
                <div className="cashflow-item">
                  <span className="label">Net Operating Cash Flow</span>
                  <span className="value positive">{formatCurrency(financialData.cash_flow.operating_cash_flow.net_operating_cashflow)}</span>
                </div>
                <div className="cashflow-item">
                  <span className="label">Current Ratio</span>
                  <span className="value">{financialData.cash_flow.working_capital.current_ratio}x</span>
                </div>
                <div className="cashflow-item">
                  <span className="label">Cash Conversion Cycle</span>
                  <span className="value">{financialData.cash_flow.cash_conversion_cycle.ccc_days} days</span>
                </div>
              </div>
              <div className="liquidity-score-display">
                <span>Liquidity Score</span>
                <div className="score-bar">
                  <div className="score-fill" style={{ width: `${financialData.cash_flow.liquidity_score}%` }}></div>
                  <span className="score-text">{financialData.cash_flow.liquidity_score}/100</span>
                </div>
              </div>
            </div>
            <p className="next-prompt">Now let's review your debt obligations...</p>
          </div>
        )}

        {step === 5 && financialData.debt && (
          <div className="step-card">
            <h2>📊 Debt Analysis</h2>
            <div className="debt-overview">
              <div className="total-debt">
                <span className="debt-label">Total Outstanding Debt</span>
                <span className="debt-value">{formatCurrency(financialData.debt.total_debt)}</span>
              </div>
              <div className="debt-list">
                {financialData.debt.debt_breakdown.map((loan: any, idx: number) => (
                  <div key={idx} className="debt-card">
                    <div className="debt-header">
                      <span className="debt-type">{loan.type}</span>
                      <span className="debt-amount">{formatCurrency(loan.amount)}</span>
                    </div>
                    <div className="debt-details">
                      <span>Interest: {loan.interest_rate}%</span>
                      {loan.monthly_emi && <span>EMI: {formatCurrency(loan.monthly_emi)}</span>}
                      {loan.remaining_tenure_months && <span>Tenure: {loan.remaining_tenure_months} months</span>}
                    </div>
                  </div>
                ))}
              </div>
              <div className="debt-ratios">
                <h3>Debt Health Indicators</h3>
                <div className="ratio-grid">
                  <div className="ratio-item">
                    <span className="ratio-label">Debt-to-Equity</span>
                    <span className="ratio-value">{financialData.debt.debt_ratios.debt_to_equity}</span>
                  </div>
                  <div className="ratio-item">
                    <span className="ratio-label">Debt-to-Revenue</span>
                    <span className="ratio-value">{financialData.debt.debt_ratios.debt_to_revenue}</span>
                  </div>
                  <div className="ratio-item">
                    <span className="ratio-label">Interest Coverage</span>
                    <span className="ratio-value">{financialData.debt.debt_ratios.interest_coverage_ratio}x</span>
                  </div>
                  <div className="ratio-item">
                    <span className="ratio-label">Credit Score</span>
                    <span className="ratio-value">{financialData.debt.credit_score}</span>
                  </div>
                </div>
              </div>
            </div>
            <p className="next-prompt">Time for the CFO's final verdict...</p>
          </div>
        )}

        {step === 6 && financialData.score && (
          <div className="step-card final-score">
            <h2>🎯 Financial Health Score</h2>
            <div className="score-hero">
              <div className="score-circle-large">
                <svg viewBox="0 0 200 200" className="score-svg">
                  <circle cx="100" cy="100" r="80" fill="none" stroke="#e0e0e0" strokeWidth="20" />
                  <circle 
                    cx="100" 
                    cy="100" 
                    r="80" 
                    fill="none" 
                    stroke="#10b981" 
                    strokeWidth="20"
                    strokeDasharray={`${financialData.score.overall_score * 5.03} 503`}
                    transform="rotate(-90 100 100)"
                  />
                  <text x="100" y="110" textAnchor="middle" fontSize="48" fill="#10b981" fontWeight="bold">
                    {financialData.score.overall_score}
                  </text>
                </svg>
                <div className="grade-display">
                  <span className="grade">{financialData.score.grade}</span>
                  <span className="percentile">Top {100 - financialData.score.percentile}%</span>
                </div>
              </div>
            </div>
            
            <div className="component-scores">
              <h3>Detailed Breakdown</h3>
              {Object.entries(financialData.score.component_scores).map(([key, value]) => (
                <div key={key} className="component-row">
                  <span className="component-name">{key.replace(/_/g, ' ')}</span>
                  <div className="component-bar">
                    <div className="component-fill" style={{ width: `${value}%` }}></div>
                  </div>
                  <span className="component-value">{value}</span>
                </div>
              ))}
            </div>

            <div className="swot-grid">
              <div className="swot-box strengths">
                <h4>💪 Strengths</h4>
                <ul>
                  {financialData.score.strengths.map((item: string, idx: number) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
              <div className="swot-box weaknesses">
                <h4>⚠️ Weaknesses</h4>
                <ul>
                  {financialData.score.weaknesses.map((item: string, idx: number) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="cfo-verdict">
              <h3>💼 CFO's Verdict</h3>
              <div className="verdict-content">
                <p className="verdict-summary">{financialData.score.cfo_verdict.summary}</p>
                <div className="verdict-metrics">
                  <div className="verdict-item">
                    <span className="verdict-label">Investment Readiness</span>
                    <span className="verdict-value">{financialData.score.cfo_verdict.investment_readiness}</span>
                  </div>
                  <div className="verdict-item">
                    <span className="verdict-label">Risk Level</span>
                    <span className="verdict-value">{financialData.score.cfo_verdict.risk_level}</span>
                  </div>
                </div>
                <div className="key-recommendation">
                  <span className="recommendation-label">Key Recommendation:</span>
                  <p className="recommendation-text">{financialData.score.cfo_verdict.key_recommendation}</p>
                </div>
              </div>
            </div>

            <div className="benchmark-comparison">
              <h3>Industry Benchmarks</h3>
              <div className="benchmark-bars">
                <div className="benchmark-item">
                  <span>Industry Average</span>
                  <div className="benchmark-bar">
                    <div className="benchmark-fill gray" style={{ width: `${financialData.score.benchmarks.industry_average_score}%` }}></div>
                  </div>
                  <span>{financialData.score.benchmarks.industry_average_score}</span>
                </div>
                <div className="benchmark-item">
                  <span>Your Score</span>
                  <div className="benchmark-bar">
                    <div className="benchmark-fill green" style={{ width: `${financialData.score.overall_score}%` }}></div>
                  </div>
                  <span>{financialData.score.overall_score}</span>
                </div>
                <div className="benchmark-item">
                  <span>Top Quartile</span>
                  <div className="benchmark-bar">
                    <div className="benchmark-fill gold" style={{ width: `${financialData.score.benchmarks.top_quartile_score}%` }}></div>
                  </div>
                  <span>{financialData.score.benchmarks.top_quartile_score}</span>
                </div>
              </div>
              <p className="position-text">You are <strong>{financialData.score.benchmarks.your_position}</strong></p>
            </div>
          </div>
        )}
      </div>

      <div className="chapter-actions">
        <button onClick={onBack} className="btn-secondary" disabled={loading}>
          ← Back
        </button>
        <button onClick={handleNext} className="btn-primary" disabled={loading}>
          {loading ? 'Analyzing...' : step === 6 ? 'Continue to Chapter 4 →' : 'Continue →'}
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
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
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
          background: linear-gradient(90deg, #10b981 0%, #059669 100%);
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

        .pulse-loader {
          width: 60px;
          height: 60px;
          border: 4px solid #10b981;
          border-radius: 50%;
          margin: 3rem auto;
          animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.3); opacity: 0.3; }
        }

        .metric-large {
          text-align: center;
          padding: 2rem;
          background: linear-gradient(135deg, #10b98120 0%, #05966920 100%);
          border-radius: 16px;
          margin-bottom: 2rem;
        }

        .metric-label {
          display: block;
          font-size: 0.9rem;
          color: #666;
          margin-bottom: 0.5rem;
        }

        .metric-value {
          display: block;
          font-size: 3rem;
          font-weight: bold;
          color: #10b981;
          margin-bottom: 0.5rem;
        }

        .growth-badge {
          display: inline-block;
          padding: 0.5rem 1rem;
          border-radius: 20px;
          font-weight: 500;
          font-size: 1rem;
        }

        .growth-badge.positive {
          background: #10b98120;
          color: #10b981;
        }

        .growth-badge.negative {
          background: #ef444420;
          color: #ef4444;
        }

        .revenue-breakdown, .expense-breakdown {
          margin-top: 2rem;
        }

        .breakdown-item, .expense-item {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .breakdown-label, .expense-label {
          width: 150px;
          text-transform: capitalize;
        }

        .breakdown-bar, .expense-bar {
          flex: 1;
          height: 24px;
          background: #e0e0e0;
          border-radius: 12px;
          overflow: hidden;
        }

        .breakdown-fill {
          height: 100%;
          background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        }

        .expense-fill {
          height: 100%;
          background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
        }

        .breakdown-value, .expense-value {
          width: 60px;
          text-align: right;
          font-weight: 500;
        }

        .metric-row {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .metric-box {
          padding: 1.5rem;
          background: linear-gradient(135deg, #10b98110 0%, #05966910 100%);
          border-radius: 12px;
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .concerns-box {
          margin-top: 2rem;
          padding: 1.5rem;
          background: #fef3c7;
          border-left: 4px solid #f59e0b;
          border-radius: 8px;
        }

        .concerns-box h4 {
          margin-bottom: 1rem;
        }

        .concerns-box ul {
          list-style: none;
          padding: 0;
        }

        .concerns-box li {
          padding: 0.5rem 0;
          padding-left: 1.5rem;
          position: relative;
        }

        .concerns-box li::before {
          content: '⚠️';
          position: absolute;
          left: 0;
        }

        .cashflow-dashboard {
          margin-top: 2rem;
        }

        .runway-alert {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1rem;
          padding: 2rem;
          background: linear-gradient(135deg, #10b98120 0%, #05966920 100%);
          border-radius: 16px;
          margin-bottom: 2rem;
        }

        .runway-value {
          font-size: 3rem;
          font-weight: bold;
          color: #10b981;
        }

        .runway-status {
          padding: 0.5rem 1rem;
          border-radius: 20px;
          font-weight: 500;
        }

        .runway-status.good {
          background: #10b98120;
          color: #10b981;
        }

        .runway-status.warning {
          background: #f59e0b20;
          color: #f59e0b;
        }

        .cashflow-metrics {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .cashflow-item {
          padding: 1.5rem;
          border: 2px solid #e0e0e0;
          border-radius: 12px;
          display: flex;
          flex-direction: column;
        }

        .cashflow-item .label {
          font-size: 0.9rem;
          color: #666;
          margin-bottom: 0.5rem;
        }

        .cashflow-item .value {
          font-size: 1.8rem;
          font-weight: bold;
          color: #333;
        }

        .cashflow-item .value.positive {
          color: #10b981;
        }

        .liquidity-score-display {
          padding: 1.5rem;
          background: linear-gradient(135deg, #10b98110 0%, #05966910 100%);
          border-radius: 12px;
        }

        .score-bar {
          position: relative;
          height: 40px;
          background: #e0e0e0;
          border-radius: 20px;
          overflow: hidden;
          margin-top: 1rem;
        }

        .score-fill {
          height: 100%;
          background: linear-gradient(90deg, #10b981 0%, #059669 100%);
          transition: width 0.5s ease;
        }

        .score-text {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          font-weight: bold;
          color: #333;
        }

        .debt-overview {
          margin-top: 2rem;
        }

        .total-debt {
          text-align: center;
          padding: 2rem;
          background: linear-gradient(135deg, #ef444420 0%, #dc262620 100%);
          border-radius: 16px;
          margin-bottom: 2rem;
        }

        .debt-label {
          display: block;
          font-size: 0.9rem;
          color: #666;
          margin-bottom: 0.5rem;
        }

        .debt-value {
          display: block;
          font-size: 3rem;
          font-weight: bold;
          color: #ef4444;
        }

        .debt-list {
          display: grid;
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .debt-card {
          border: 2px solid #e0e0e0;
          border-radius: 12px;
          padding: 1.5rem;
        }

        .debt-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .debt-type {
          font-weight: bold;
          font-size: 1.1rem;
        }

        .debt-amount {
          font-size: 1.3rem;
          color: #ef4444;
          font-weight: bold;
        }

        .debt-details {
          display: flex;
          gap: 1.5rem;
          font-size: 0.9rem;
          color: #666;
        }

        .ratio-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 1rem;
          margin-top: 1rem;
        }

        .ratio-item {
          padding: 1rem;
          background: linear-gradient(135deg, #10b98110 0%, #05966910 100%);
          border-radius: 8px;
          text-align: center;
        }

        .ratio-label {
          display: block;
          font-size: 0.85rem;
          color: #666;
          margin-bottom: 0.5rem;
        }

        .ratio-value {
          display: block;
          font-size: 1.5rem;
          font-weight: bold;
          color: #10b981;
        }

        .score-hero {
          margin: 2rem 0;
        }

        .score-circle-large {
          width: 300px;
          margin: 0 auto;
          position: relative;
        }

        .score-svg {
          width: 100%;
          height: auto;
        }

        .grade-display {
          text-align: center;
          margin-top: 1rem;
        }

        .grade {
          display: block;
          font-size: 3rem;
          font-weight: bold;
          color: #10b981;
        }

        .percentile {
          display: block;
          font-size: 1.2rem;
          color: #666;
        }

        .component-scores {
          margin: 2rem 0;
        }

        .component-row {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .component-name {
          width: 180px;
          text-transform: capitalize;
        }

        .component-bar {
          flex: 1;
          height: 28px;
          background: #e0e0e0;
          border-radius: 14px;
          overflow: hidden;
        }

        .component-fill {
          height: 100%;
          background: linear-gradient(90deg, #10b981 0%, #059669 100%);
          transition: width 0.5s ease;
        }

        .component-value {
          width: 50px;
          text-align: right;
          font-weight: 500;
        }

        .swot-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 2rem;
          margin: 2rem 0;
        }

        .swot-box {
          padding: 1.5rem;
          border-radius: 12px;
        }

        .swot-box.strengths {
          background: linear-gradient(135deg, #10b98120 0%, #05966920 100%);
          border-left: 4px solid #10b981;
        }

        .swot-box.weaknesses {
          background: linear-gradient(135deg, #f59e0b20 0%, #d9770620 100%);
          border-left: 4px solid #f59e0b;
        }

        .swot-box h4 {
          margin-bottom: 1rem;
        }

        .swot-box ul {
          list-style: none;
          padding: 0;
        }

        .swot-box li {
          padding: 0.5rem 0;
          padding-left: 1.5rem;
          position: relative;
        }

        .swot-box.strengths li::before {
          content: '✓';
          position: absolute;
          left: 0;
          color: #10b981;
          font-weight: bold;
        }

        .swot-box.weaknesses li::before {
          content: '→';
          position: absolute;
          left: 0;
          color: #f59e0b;
          font-weight: bold;
        }

        .cfo-verdict {
          margin: 2rem 0;
          padding: 2rem;
          background: linear-gradient(135deg, #10b98110 0%, #05966910 100%);
          border-radius: 16px;
        }

        .cfo-verdict h3 {
          margin-bottom: 1rem;
        }

        .verdict-summary {
          font-size: 1.2rem;
          font-weight: 500;
          margin-bottom: 1.5rem;
        }

        .verdict-metrics {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .verdict-item {
          display: flex;
          flex-direction: column;
          padding: 1rem;
          background: white;
          border-radius: 8px;
        }

        .verdict-label {
          font-size: 0.9rem;
          color: #666;
          margin-bottom: 0.5rem;
        }

        .verdict-value {
          font-size: 1.3rem;
          font-weight: bold;
          color: #10b981;
        }

        .key-recommendation {
          padding: 1.5rem;
          background: white;
          border-radius: 8px;
        }

        .recommendation-label {
          display: block;
          font-weight: bold;
          margin-bottom: 0.5rem;
        }

        .recommendation-text {
          font-size: 1.1rem;
          color: #333;
        }

        .benchmark-comparison {
          margin: 2rem 0;
          padding: 2rem;
          background: #f9fafb;
          border-radius: 12px;
        }

        .benchmark-bars {
          margin: 1.5rem 0;
        }

        .benchmark-item {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .benchmark-item > span:first-child {
          width: 150px;
        }

        .benchmark-bar {
          flex: 1;
          height: 32px;
          background: #e0e0e0;
          border-radius: 16px;
          overflow: hidden;
        }

        .benchmark-fill {
          height: 100%;
          transition: width 0.5s ease;
        }

        .benchmark-fill.gray {
          background: #9ca3af;
        }

        .benchmark-fill.green {
          background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        }

        .benchmark-fill.gold {
          background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
        }

        .benchmark-item > span:last-child {
          width: 50px;
          text-align: right;
          font-weight: 500;
        }

        .position-text {
          text-align: center;
          margin-top: 1rem;
          font-size: 1.1rem;
        }

        .next-prompt {
          margin-top: 2rem;
          text-align: center;
          font-size: 1.1rem;
          color: #10b981;
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
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 16px rgba(16, 185, 129, 0.4);
        }

        .btn-secondary {
          background: white;
          color: #10b981;
          border: 2px solid #10b981;
        }

        .btn-secondary:hover:not(:disabled) {
          background: #10b98110;
        }

        .btn-primary:disabled, .btn-secondary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default Chapter3Financial;
