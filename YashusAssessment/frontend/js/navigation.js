// Navigation & State Management

const AppState = {
    currentPane: 'pane-landing',
    initialAnswer: '',
    aiContext: {},
    dimensionAnswers: {
        strategy: [],
        technology: [],
        content: [],
        channels: [],
        skills: [],
        measurement: [],
        cx: []
    },
    completedDimensions: [],
    dimensionScores: {},
    overallScore: 0,
    results: null
};

// Navigate between panes
function navigateTo(paneId) {
    // Hide current pane
    const currentPane = document.getElementById(AppState.currentPane);
    if (currentPane) {
        currentPane.classList.remove('active');
    }
    
    // Show target pane
    const targetPane = document.getElementById(paneId);
    if (targetPane) {
        targetPane.classList.add('active');
        AppState.currentPane = paneId;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Handle initial business description
async function handleInitialSensing(event) {
    event.preventDefault();
    
    const description = document.getElementById('business-description').value;
    AppState.initialAnswer = description;
    
    // Show AI processing
    document.getElementById('ai-processing').style.display = 'flex';
    
    // Process with AI
    const context = await window.aiOrchestrator.processInitialAnswer(description);
    AppState.aiContext = context;
    
    // Hide processing, navigate to overview
    setTimeout(() => {
        document.getElementById('ai-processing').style.display = 'none';
        navigateTo('pane-progress-overview');
        updateProgressOverview();
    }, 1500);
}

// Update progress overview page
function updateProgressOverview() {
    // Update estimated maturity
    const maturityEl = document.getElementById('estimated-maturity');
    if (maturityEl && AppState.aiContext.estimatedMaturity) {
        maturityEl.textContent = `~${Math.round(AppState.aiContext.estimatedMaturity * 10) / 10}/7`;
    }
    
    // Update completed dimensions count
    const completedEl = document.getElementById('completed-dimensions');
    if (completedEl) {
        completedEl.textContent = `${AppState.completedDimensions.length}/7`;
    }
    
    // Update time remaining
    const timeEl = document.getElementById('time-remaining');
    if (timeEl) {
        const remaining = 7 - AppState.completedDimensions.length;
        timeEl.textContent = `~${remaining * 1.5} min`;
    }
    
    // Unlock/lock dimensions
    ['strategy', 'technology', 'content', 'channels', 'skills', 'measurement', 'cx'].forEach((dim, index) => {
        const node = document.querySelector(`[data-dimension="${dim}"]`);
        if (node) {
            if (AppState.completedDimensions.includes(dim)) {
                node.classList.remove('locked', 'current');
                node.classList.add('completed');
                const dot = node.querySelector('.milestone-dot');
                if (dot) {
                    dot.textContent = '✓';
                    dot.classList.add('completed');
                    dot.classList.remove('locked', 'current');
                }
                const scoreEl = node.querySelector('.node-score');
                if (scoreEl && AppState.dimensionScores[dim]) {
                    scoreEl.textContent = `${AppState.dimensionScores[dim]}/7`;
                }
            } else if (index === 0 || AppState.completedDimensions.includes(['strategy', 'technology', 'content', 'channels', 'skills', 'measurement', 'cx'][index-1])) {
                // Unlock if first or previous completed
                node.classList.remove('locked');
            }
        }
    });
}

// Navigate to dimension assessment
function navigateToDimension(dimension) {
    const node = document.querySelector(`[data-dimension="${dimension}"]`);
    if (node && node.classList.contains('locked')) {
        alert('Please complete previous dimensions first');
        return;
    }
    
    navigateTo(`pane-dimension-${dimension}`);
    loadDimensionQuestions(dimension);
}

// Load adaptive questions for a dimension
function loadDimensionQuestions(dimension) {
    const questions = window.aiOrchestrator.getAdaptiveQuestions(dimension);
    const container = document.getElementById(`questions-${dimension}`);
    
    if (!container) return;
    
    container.innerHTML = '';
    
    questions.forEach((question, index) => {
        const questionCard = document.createElement('div');
        questionCard.className = 'question-card';
        questionCard.innerHTML = `
            <div class="question-number">Question ${index + 1}/${questions.length}</div>
            <h3 class="question-title">${window.aiOrchestrator.adaptTone(question.text)}</h3>
            ${renderQuestionInput(question, dimension, index)}
        `;
        container.appendChild(questionCard);
    });
    
    // Add submit button
    const submitBtn = document.createElement('div');
    submitBtn.className = 'button-row';
    submitBtn.innerHTML = `
        <button onclick="navigateTo('pane-progress-overview')" class="btn-secondary">
            Back to Overview
        </button>
        <button onclick="submitDimension('${dimension}')" class="btn-primary">
            Complete ${dimension.charAt(0).toUpperCase() + dimension.slice(1)}
        </button>
    `;
    container.appendChild(submitBtn);
}

// Render question input based on type
function renderQuestionInput(question, dimension, index) {
    const inputId = `${dimension}-q${index}`;
    
    if (question.type === 'radio') {
        return `
            <div class="form-group">
                ${question.options.map((option, optIndex) => `
                    <label class="radio-option" style="display: block; margin-bottom: 12px; padding: 12px; border: 2px solid var(--border-color); border-radius: 8px; cursor: pointer;">
                        <input type="radio" name="${inputId}" value="${optIndex}" required style="margin-right: 8px;">
                        ${option}
                    </label>
                `).join('')}
            </div>
        `;
    } else if (question.type === 'checkbox') {
        return `
            <div class="form-group">
                ${question.options.map((option, optIndex) => `
                    <label style="display: block; margin-bottom: 8px;">
                        <input type="checkbox" name="${inputId}" value="${optIndex}" style="margin-right: 8px;">
                        ${option}
                    </label>
                `).join('')}
            </div>
        `;
    }
    
    return '';
}

// Submit dimension answers
function submitDimension(dimension) {
    const container = document.getElementById(`questions-${dimension}`);
    const questions = window.aiOrchestrator.getAdaptiveQuestions(dimension);
    
    const answers = questions.map((question, index) => {
        const inputId = `${dimension}-q${index}`;
        
        if (question.type === 'radio') {
            const selected = container.querySelector(`input[name="${inputId}"]:checked`);
            if (!selected) {
                alert('Please answer all questions');
                return null;
            }
            return {
                question: question.text,
                type: 'radio',
                selectedIndex: parseInt(selected.value),
                options: question.options
            };
        } else if (question.type === 'checkbox') {
            const checkboxes = container.querySelectorAll(`input[name="${inputId}"]`);
            const selected = Array.from(checkboxes).filter(cb => cb.checked).map(cb => parseInt(cb.value));
            return {
                question: question.text,
                type: 'checkbox',
                selected: selected,
                options: question.options
            };
        }
    });
    
    if (answers.includes(null)) return;
    
    // Save answers
    AppState.dimensionAnswers[dimension] = answers;
    AppState.completedDimensions.push(dimension);
    
    // Update AI context
    window.aiOrchestrator.updateContext(dimension, answers);
    
    // Calculate dimension score
    AppState.dimensionScores[dimension] = window.statisticalEngine.scoreDimension(answers);
    
    // Check if all completed
    if (AppState.completedDimensions.length === 7) {
        // Generate results
        generateResults();
    } else {
        // Return to overview
        navigateTo('pane-progress-overview');
        updateProgressOverview();
    }
}

// Generate final results
function generateResults() {
    console.log('📊 Generating results...');
    
    // Statistical analysis
    const dimensionScores = window.statisticalEngine.factorAnalysis(AppState.dimensionAnswers);
    const overallScoreData = window.statisticalEngine.predictMaturityScore(dimensionScores);
    const benchmark = window.statisticalEngine.benchmarkAgainstIndustry(overallScoreData.score, AppState.aiContext.industry);
    const roi = window.statisticalEngine.predictROI(overallScoreData.score, AppState.aiContext.industry);
    const swot = window.statisticalEngine.generateSWOT(dimensionScores, AppState.aiContext);
    
    AppState.overallScore = overallScoreData.score;
    AppState.results = {
        overall: overallScoreData,
        dimensions: dimensionScores,
        benchmark: benchmark,
        roi: roi,
        swot: swot
    };
    
    // Navigate to results
    navigateTo('pane-results-score');
    renderResults();
}

// Render results on page
function renderResults() {
    const results = AppState.results;
    
    // Overall score
    document.getElementById('overall-score').textContent = results.overall.score;
    document.getElementById('industry-avg').textContent = results.benchmark.industryAvg;
    document.getElementById('percentile-rank').textContent = `${results.benchmark.percentile}th percentile`;
    document.getElementById('confidence-level').textContent = `${Math.round(results.overall.confidence * 100)}%`;
    document.getElementById('data-points-count').textContent = AppState.completedDimensions.length * 3;
    
    // Update dimension scores in list (already rendered in HTML, update dynamically)
    const dimNames = ['strategy', 'technology', 'content', 'channels', 'skills', 'measurement', 'cx'];
    dimNames.forEach((dim, index) => {
        const score = results.dimensions[dim];
        const item = document.querySelectorAll('.dimension-score-item')[index];
        if (item && score) {
            const scoreEl = item.querySelector('.dimension-score');
            const barEl = item.querySelector('.score-bar');
            if (scoreEl) scoreEl.textContent = `${score} / 7`;
            if (barEl) {
                barEl.style.width = `${(score / 7) * 100}%`;
            }
        }
    });
}

// Handle email submission
function handleEmailSubmit(event) {
    event.preventDefault();
    const email = document.getElementById('user-email').value;
    
    // Mock email send
    alert(`Report will be sent to ${email}\n\nIn production, this would trigger:\n- PDF generation\n- Email via backend API\n- CRM entry`);
    
    // Show success message
    document.querySelector('.email-capture-form').innerHTML = `
        <div style="padding: 20px; background: var(--success-50); border-radius: 12px; color: var(--success-700);">
            <h4>✓ Report Sent!</h4>
            <p>Check your inbox at <strong>${email}</strong></p>
        </div>
    `;
}

// Download PDF
function downloadPDF() {
    alert('PDF download would be implemented with jsPDF or backend PDF generation');
}

// Share results
function shareResults() {
    if (navigator.share) {
        navigator.share({
            title: 'My Digital Marketing Maturity Score',
            text: `I scored ${AppState.overallScore}/7 on Yashus Assessment!`,
            url: window.location.href
        });
    } else {
        alert('Share functionality:\n- LinkedIn\n- Twitter\n- Copy link\n\nNot available in this environment');
    }
}

// Book strategy call
function bookCall() {
    window.open('https://calendly.com/yashus', '_blank');
}

// Character counter for textareas
document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('business-description');
    if (textarea) {
        const counter = textarea.parentElement.querySelector('.char-counter');
        textarea.addEventListener('input', () => {
            if (counter) {
                counter.textContent = `${textarea.value.length} / ${textarea.maxLength}`;
            }
        });
    }
});
