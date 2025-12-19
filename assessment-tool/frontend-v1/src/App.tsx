import { useState } from 'react'
import './App.css'
import Chapter2Discovery from './components/Chapter2Discovery'
import Chapter3Financial from './components/Chapter3Financial'
import Chapter4Legal from './components/Chapter4Legal'
import Chapter5Operations from './components/Chapter5Operations'
import Chapter6Customers from './components/Chapter6Customers'
import Chapter7AI from './components/Chapter7AI'
import Chapter8Verdict from './components/Chapter8Verdict'

interface Candidate {
  id: string
  name: string
  confidence: number
  cin?: string
  registered_address?: string
  founded_year?: number
}

type Chapter = 'ch1' | 'ch2' | 'ch3' | 'ch4' | 'ch5' | 'ch6' | 'ch7' | 'ch8' | 'complete'

function App() {
  const [chapter, setChapter] = useState<Chapter>('ch1')
  const [step, setStep] = useState<'search' | 'results' | 'confirmed'>('search')
  const [companyName, setCompanyName] = useState('')
  const [location, setLocation] = useState('')
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [selectedId, setSelectedId] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [assessmentId, setAssessmentId] = useState('')

  const handleSearch = async () => {
    if (!companyName.trim()) return
    
    setLoading(true)
    
    try {
      // Initialize assessment
      const initRes = await fetch('/api/v1/init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ industry: 'restaurant' })
      })
      const initData = await initRes.json()
      setAssessmentId(initData.assessment_id)
      
      // Search for identity
      const searchRes = await fetch(`/api/v1/${initData.assessment_id}/identify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: companyName, location })
      })
      const searchData = await searchRes.json()
      
      // Safely handle candidates array
      setCandidates(searchData.candidates || [])
      setStep('results')
    } catch (error) {
      console.error('Search failed:', error)
      alert('Search failed. Check console.')
    } finally {
      setLoading(false)
    }
  }

  const handleConfirm = async () => {
    if (!selectedId) return
    
    setLoading(true)
    
    try {
      await fetch(`/api/v1/${assessmentId}/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          company_name: companyName,
          website: `https://${companyName.toLowerCase().replace(/\s+/g, '')}.com`
        })
      })
      setStep('confirmed')
      // Move to Chapter 2 after confirmation
      setTimeout(() => setChapter('ch2'), 1500)
    } catch (error) {
      console.error('Confirm failed:', error)
      alert('Confirm failed. Check console.')
    } finally {
      setLoading(false)
    }
  }

  // Chapter navigation - render appropriate chapter component
  if (chapter === 'ch2') {
    return (
      <Chapter2Discovery 
        assessmentId={assessmentId}
        onComplete={() => setChapter('ch3')}
        onBack={() => setChapter('ch1')}
      />
    )
  }

  if (chapter === 'ch3') {
    return (
      <Chapter3Financial 
        assessmentId={assessmentId}
        onComplete={() => setChapter('ch4')}
        onBack={() => setChapter('ch2')}
      />
    )
  }

  if (chapter === 'ch4') {
    return (
      <Chapter4Legal 
        assessmentId={assessmentId}
        onComplete={() => setChapter('ch5')}
        onBack={() => setChapter('ch3')}
      />
    )
  }

  if (chapter === 'ch5') {
    return (
      <Chapter5Operations 
        assessmentId={assessmentId}
        onComplete={() => setChapter('ch6')}
        onBack={() => setChapter('ch4')}
      />
    )
  }

  if (chapter === 'ch6') {
    return (
      <Chapter6Customers 
        assessmentId={assessmentId}
        onComplete={() => setChapter('ch7')}
        onBack={() => setChapter('ch5')}
      />
    )
  }

  if (chapter === 'ch7') {
    return (
      <Chapter7AI 
        assessmentId={assessmentId}
        onComplete={() => setChapter('ch8')}
        onBack={() => setChapter('ch6')}
      />
    )
  }

  if (chapter === 'ch8') {
    return (
      <Chapter8Verdict 
        assessmentId={assessmentId}
        onBack={() => setChapter('ch7')}
      />
    )
  }

  if (chapter === 'complete') {
    return (
      <div className="app">
        <div className="container">
          <h1 className="title">🎉 Assessment Complete!</h1>
          <p className="subtitle">All 8 chapters completed successfully!</p>
          <p>Assessment ID: {assessmentId}</p>
          <button 
            onClick={() => {
              setChapter('ch1')
              setStep('search')
              setCompanyName('')
              setLocation('')
              setCandidates([])
              setSelectedId('')
              setAssessmentId('')
            }} 
            className="button"
          >
            Start New Assessment
          </button>
        </div>
      </div>
    )
  }

  // Chapter 1 UI (existing code)
  return (
    <div className="app">
      <div className="container">
        <h1 className="title">🔍 Who Are You?</h1>
        <p className="subtitle">Let's discover your digital identity</p>

        {step === 'search' && (
          <div className="search-form">
            <input
              type="text"
              placeholder="Company name (e.g., Noya Foods)"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="input"
            />
            <input
              type="text"
              placeholder="Location (e.g., Mumbai)"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="input"
            />
            <button
              onClick={handleSearch}
              disabled={loading || !companyName.trim()}
              className="button"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        )}

        {step === 'results' && (
          <div className="results">
            <h2>Found {candidates?.length || 0} matches:</h2>
            {candidates && candidates.length > 0 ? (
              <>
                <div className="candidates-grid">
                  {candidates.map((candidate) => (
                    <div
                      key={candidate.id}
                      className={`candidate-card ${selectedId === candidate.id ? 'selected' : ''}`}
                      onClick={() => setSelectedId(candidate.id)}
                    >
                      <h3>{candidate.name}</h3>
                      <div className="confidence">
                        Confidence: {(candidate.confidence * 100).toFixed(0)}%
                      </div>
                      {candidate.cin && <div className="meta">CIN: {candidate.cin}</div>}
                      {candidate.registered_address && (
                        <div className="meta">📍 {candidate.registered_address}</div>
                      )}
                      {candidate.founded_year && (
                        <div className="meta">Founded: {candidate.founded_year}</div>
                      )}
                    </div>
                  ))}
                </div>
                <button
                  onClick={handleConfirm}
                  disabled={loading || !selectedId}
                  className="button"
                >
                  {loading ? 'Confirming...' : 'Confirm Selection'}
                </button>
              </>
            ) : (
              <div>
                <p>No matches found. Please try a different search.</p>
                <button
                  onClick={() => setStep('search')}
                  className="button"
                >
                  Back to Search
                </button>
              </div>
            )}
          </div>
        )}

        {step === 'confirmed' && (
          <div className="confirmed">
            <div className="success">✅ Identity Confirmed!</div>
            <p>Assessment ID: {assessmentId}</p>
            <p>Moving to Chapter 2: Digital Discovery...</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
