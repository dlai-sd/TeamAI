// Global State Management
const AppState = {
    currentPane: 'pane-landing',
    milestones: {},
    completedMilestones: [],
    userEmail: '',
    aiAnalysis: null,
    statistics: null,
    roadmap: null
};

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// API Communication Functions
const API = {
    async submitMilestone(milestoneNumber, data) {
        try {
            const response = await fetch(`${API_BASE_URL}/milestones/${milestoneNumber}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error submitting milestone:', error);
            // Fallback to local storage if backend unavailable
            this.saveToLocalStorage(milestoneNumber, data);
            return { success: true, localOnly: true };
        }
    },
    
    async analyzeData() {
        try {
            const response = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(AppState.milestones)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error analyzing data:', error);
            // Return mock data if backend unavailable
            return this.getMockAnalysis();
        }
    },
    
    async sendEmail(email) {
        try {
            const response = await fetch(`${API_BASE_URL}/send-report`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    milestones: AppState.milestones,
                    analysis: AppState.aiAnalysis
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error sending email:', error);
            return { success: false, error: error.message };
        }
    },
    
    saveToLocalStorage(milestoneNumber, data) {
        localStorage.setItem(`milestone_${milestoneNumber}`, JSON.stringify(data));
    },
    
    loadFromLocalStorage() {
        for (let i = 1; i <= 9; i++) {
            const data = localStorage.getItem(`milestone_${i}`);
            if (data) {
                AppState.milestones[i] = JSON.parse(data);
                AppState.completedMilestones.push(i);
            }
        }
    },
    
    getMockAnalysis() {
        return {
            insights: [
                {
                    title: "Market Positioning Strength",
                    content: "Your product positioning shows strong differentiation in a competitive market. Consider emphasizing unique value propositions in early marketing materials."
                },
                {
                    title: "Target Audience Clarity",
                    content: "Well-defined target audience with specific pain points. Recommend persona-based content strategy for maximum engagement."
                },
                {
                    title: "Growth Potential",
                    content: "High growth potential identified based on market trends and competitive analysis. Focus on scalable acquisition channels."
                }
            ],
            statistics: {
                "Market Fit Score": 78,
                "Competitive Advantage": 65,
                "Scalability Index": 82,
                "Brand Readiness": 71
            },
            roadmap: [
                {
                    priority: 1,
                    title: "Define Core Brand Identity",
                    description: "Establish brand voice, visual identity, and messaging framework within 2 weeks."
                },
                {
                    priority: 2,
                    title: "Build Minimum Viable Audience",
                    description: "Launch targeted content marketing to acquire first 1000 engaged followers."
                },
                {
                    priority: 3,
                    title: "Implement Analytics Stack",
                    description: "Set up tracking and measurement infrastructure for data-driven decisions."
                },
                {
                    priority: 4,
                    title: "Launch Paid Acquisition Test",
                    description: "Run controlled experiments across 3 channels with $5k budget."
                },
                {
                    priority: 5,
                    title: "Optimize Conversion Funnel",
                    description: "Analyze user journey and improve key conversion points for 2x improvement."
                }
            ]
        };
    }
};

// Initialization
function initializeApp() {
    console.log('🚀 WoWYashus initializing...');
    
    // Load saved progress from localStorage
    API.loadFromLocalStorage();
    
    // Update monopoly board if returning user
    if (AppState.completedMilestones.length > 0) {
        updateMonopolyBoard();
    }
    
    // Add keyboard navigation
    document.addEventListener('keydown', handleKeyboardNavigation);
    
    console.log('✅ App ready');
}

// Keyboard Navigation
function handleKeyboardNavigation(event) {
    if (event.key === 'Escape') {
        const currentPane = document.getElementById(AppState.currentPane);
        if (currentPane && !currentPane.classList.contains('pane-landing')) {
            goBack();
        }
    }
}

// Navigation Back
function goBack() {
    if (AppState.currentPane === 'pane-monopoly') {
        navigateTo('pane-landing');
    } else if (AppState.currentPane.startsWith('pane-milestone-')) {
        navigateTo('pane-monopoly');
    } else if (AppState.currentPane === 'pane-dashboard') {
        navigateTo('pane-monopoly');
    }
}

// Character Counter
function setupCharCounters() {
    document.querySelectorAll('textarea[maxlength]').forEach(textarea => {
        const counter = document.createElement('div');
        counter.className = 'char-counter';
        counter.textContent = `0 / ${textarea.maxLength}`;
        textarea.parentElement.appendChild(counter);
        
        textarea.addEventListener('input', () => {
            counter.textContent = `${textarea.value.length} / ${textarea.maxLength}`;
        });
    });
}

// Auto-save on Form Input
function setupAutoSave() {
    document.querySelectorAll('.milestone-form input, .milestone-form select, .milestone-form textarea').forEach(input => {
        input.addEventListener('change', () => {
            const formId = input.closest('form').id;
            const milestoneNumber = formId.match(/\d+/)[0];
            const formData = new FormData(input.closest('form'));
            const data = Object.fromEntries(formData);
            API.saveToLocalStorage(milestoneNumber, data);
        });
    });
}

// Initialize on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Export for use in other modules
window.AppState = AppState;
window.API = API;
