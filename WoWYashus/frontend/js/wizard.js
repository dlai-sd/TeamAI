// Wizard Navigation & Form Management

// Navigate Between Panes
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
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        // Special actions for specific panes
        if (paneId === 'pane-dashboard') {
            loadDashboard();
        }
    }
}

// Submit Milestone Form
async function submitMilestone(event, milestoneNumber) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Validation
    const isValid = validateMilestoneForm(milestoneNumber, data);
    if (!isValid) {
        return;
    }
    
    // Show loading state
    const submitButton = form.querySelector('.submit-button');
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '<span class="loading-spinner"></span> Saving...';
    submitButton.disabled = true;
    
    // Save data
    AppState.milestones[milestoneNumber] = data;
    
    // Submit to backend
    const result = await API.submitMilestone(milestoneNumber, data);
    
    // Mark as completed
    if (!AppState.completedMilestones.includes(milestoneNumber)) {
        AppState.completedMilestones.push(milestoneNumber);
    }
    
    // Update monopoly board
    updateMonopolyBoard();
    
    // Reset button
    submitButton.innerHTML = originalText;
    submitButton.disabled = false;
    
    // Navigate to next pane
    if (milestoneNumber < 9) {
        navigateTo(`pane-milestone-${milestoneNumber + 1}`);
    } else {
        navigateTo('pane-dashboard');
    }
}

// Validate Form Data
function validateMilestoneForm(milestoneNumber, data) {
    const errors = [];
    
    // Check required fields
    Object.entries(data).forEach(([key, value]) => {
        if (!value || value.trim() === '') {
            errors.push(`${key.replace('m' + milestoneNumber + '-', '')} is required`);
        }
    });
    
    if (errors.length > 0) {
        alert('Please fill in all required fields:\n' + errors.join('\n'));
        return false;
    }
    
    return true;
}

// Skip Milestone
function skipMilestone(milestoneNumber) {
    if (confirm('Skip this milestone? You can always come back later.')) {
        if (milestoneNumber < 9) {
            navigateTo(`pane-milestone-${milestoneNumber + 1}`);
        } else {
            navigateTo('pane-dashboard');
        }
    }
}

// Load Dashboard Data
async function loadDashboard() {
    // Show loading states
    document.getElementById('ai-insights').innerHTML = '<div class="loading-spinner"></div><p style="text-align: center; color: var(--text-muted);">Analyzing your data with AI...</p>';
    document.getElementById('stats-chart').innerHTML = '<div class="loading-spinner"></div>';
    document.getElementById('roadmap-list').innerHTML = '<div class="loading-spinner"></div>';
    
    // Fetch analysis from backend (or use mock data)
    const analysis = await API.analyzeData();
    
    AppState.aiAnalysis = analysis.insights;
    AppState.statistics = analysis.statistics;
    AppState.roadmap = analysis.roadmap;
    
    // Render insights
    renderAIInsights(analysis.insights);
    
    // Render statistics
    setTimeout(() => renderStatistics(analysis.statistics), 500);
    
    // Render roadmap
    setTimeout(() => renderRoadmap(analysis.roadmap), 1000);
}

// Render AI Insights
function renderAIInsights(insights) {
    const container = document.getElementById('ai-insights');
    
    if (!insights || insights.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted);">Complete more milestones to unlock AI insights.</p>';
        return;
    }
    
    container.innerHTML = insights.map(insight => `
        <div class="insight-item">
            <h4>${insight.title}</h4>
            <p>${insight.content}</p>
        </div>
    `).join('');
}

// Render Statistics
function renderStatistics(statistics) {
    const container = document.getElementById('stats-chart');
    
    if (!statistics || Object.keys(statistics).length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted);">Statistics will appear as you complete milestones.</p>';
        return;
    }
    
    container.innerHTML = Object.entries(statistics).map(([label, value]) => `
        <div class="stat-bar">
            <span class="stat-label">${label}</span>
            <div class="stat-bar-bg">
                <div class="stat-bar-fill" style="width: ${value}%">
                    ${value}%
                </div>
            </div>
        </div>
    `).join('');
}

// Render Roadmap
function renderRoadmap(roadmap) {
    const container = document.getElementById('roadmap-list');
    
    if (!roadmap || roadmap.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted);">Your personalized roadmap will appear here.</p>';
        return;
    }
    
    container.innerHTML = roadmap.map(item => `
        <div class="roadmap-item">
            <div class="roadmap-priority">${item.priority}</div>
            <div class="roadmap-content">
                <h4>${item.title}</h4>
                <p>${item.description}</p>
            </div>
        </div>
    `).join('');
}

// Submit Email
async function submitEmail(event) {
    event.preventDefault();
    
    const form = event.target;
    const emailInput = form.querySelector('input[type="email"]');
    const email = emailInput.value;
    
    // Validation
    if (!email || !email.includes('@')) {
        alert('Please enter a valid email address');
        return;
    }
    
    AppState.userEmail = email;
    
    // Show loading
    const submitButton = form.querySelector('button');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Sending...';
    submitButton.disabled = true;
    
    // Send to backend
    const result = await API.sendEmail(email);
    
    // Show result
    if (result.success) {
        form.innerHTML = `
            <div class="success-message">
                <h3>✅ Report Sent!</h3>
                <p>Check your inbox at <strong>${email}</strong></p>
                <p style="margin-top: 10px; font-size: 0.9em;">Don't see it? Check your spam folder.</p>
            </div>
        `;
    } else {
        alert('Failed to send report. Please try again.');
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    }
}

// Progress Calculation
function calculateProgress() {
    return (AppState.completedMilestones.length / 9) * 100;
}

// Update Progress Indicator
function updateProgressIndicator() {
    const progressFill = document.querySelector('.progress-fill');
    const progressIndicator = document.querySelector('.progress-indicator');
    
    if (progressFill) {
        const progress = calculateProgress();
        progressFill.style.width = `${progress}%`;
    }
    
    if (progressIndicator) {
        progressIndicator.textContent = `${AppState.completedMilestones.length}/9 Milestones Completed`;
    }
}

// Auto-fill Forms from Local Storage
function autoFillForm(milestoneNumber) {
    const data = localStorage.getItem(`milestone_${milestoneNumber}`);
    if (!data) return;
    
    const parsedData = JSON.parse(data);
    const form = document.querySelector(`#pane-milestone-${milestoneNumber} form`);
    
    if (form) {
        Object.entries(parsedData).forEach(([key, value]) => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = value;
            }
        });
    }
}

// Initialize Wizard Features
function initializeWizard() {
    // Auto-fill forms with saved data
    for (let i = 1; i <= 9; i++) {
        autoFillForm(i);
    }
    
    // Update progress
    updateProgressIndicator();
}

// Call init on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeWizard);
} else {
    initializeWizard();
}
