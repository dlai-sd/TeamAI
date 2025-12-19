// Main Application Initialization

console.log('🚀 YashusAssessment Professional Tool Loading...');

// Check dependencies
if (typeof window.aiOrchestrator === 'undefined') {
    console.error('❌ AI Orchestrator not loaded');
}

if (typeof window.statisticalEngine === 'undefined') {
    console.error('❌ Statistical Engine not loaded');
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ DOM Ready');
    
    // Initialize first pane
    navigateTo('pane-landing');
    
    // Bind form handlers
    const initialForm = document.getElementById('initial-sensing-form');
    if (initialForm) {
        initialForm.addEventListener('submit', handleInitialSensing);
    }
    
    const emailForm = document.getElementById('email-capture-form');
    if (emailForm) {
        emailForm.addEventListener('submit', handleEmailSubmit);
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Press 'Escape' to return to overview
        if (e.key === 'Escape' && AppState.currentPane !== 'pane-landing') {
            navigateTo('pane-progress-overview');
        }
    });
    
    // Dimension node click handlers
    document.querySelectorAll('.dimension-node').forEach(node => {
        node.addEventListener('click', () => {
            const dimension = node.dataset.dimension;
            if (dimension) {
                navigateToDimension(dimension);
            }
        });
    });
    
    // Load historical data for statistical engine
    window.statisticalEngine.loadHistoricalData();
    
    console.log('✅ YashusAssessment Initialized');
    console.log('📊 Statistical Engine Ready with 1,247 samples');
    console.log('🤖 AI Orchestrator Ready with 7-dimension question bank');
});

// Debug mode for development
if (window.location.search.includes('debug=true')) {
    console.log('🐛 Debug Mode Active');
    
    // Auto-fill demo data
    window.demoMode = () => {
        document.getElementById('business-description').value = 
            "We run a dental clinic in Mumbai with 3 locations. We have a website and active on social media. Looking to improve our patient acquisition through digital marketing.";
        
        alert('Demo data loaded. Click "Continue" to test AI sensing.');
    };
    
    // Quick navigation
    window.nav = navigateTo;
    window.goto = (pane) => navigateTo(`pane-${pane}`);
    
    // Inspect state
    window.state = AppState;
    window.ai = window.aiOrchestrator;
    window.stats = window.statisticalEngine;
    
    console.log('🔧 Debug commands available:');
    console.log('  demoMode() - Fill demo business description');
    console.log('  nav("pane-id") - Navigate to pane');
    console.log('  goto("landing") - Navigate shortcuts');
    console.log('  state - Inspect app state');
    console.log('  ai - AI orchestrator instance');
    console.log('  stats - Statistical engine instance');
}

// Service worker for offline capability (future)
if ('serviceWorker' in navigator && window.location.protocol === 'https:') {
    navigator.serviceWorker.register('/sw.js').then(() => {
        console.log('✅ Service Worker registered');
    }).catch(() => {
        console.log('⚠️ Service Worker not available');
    });
}

// Analytics placeholder
window.trackEvent = (category, action, label) => {
    console.log(`📈 Analytics: ${category} > ${action} > ${label}`);
    // In production: Google Analytics, Mixpanel, etc.
};

// Error boundary
window.addEventListener('error', (event) => {
    console.error('❌ Application Error:', event.error);
    
    // Show user-friendly message
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #fee2e2;
        border: 2px solid #dc2626;
        border-radius: 12px;
        padding: 16px;
        max-width: 400px;
        z-index: 10000;
    `;
    errorDiv.innerHTML = `
        <h4 style="margin: 0 0 8px 0; color: #991b1b;">Oops! Something went wrong</h4>
        <p style="margin: 0; color: #7f1d1d; font-size: 14px;">
            Please refresh the page. If this persists, contact support.
        </p>
        <button onclick="this.parentElement.remove()" 
                style="margin-top: 12px; padding: 6px 12px; background: #dc2626; color: white; border: none; border-radius: 6px; cursor: pointer;">
            Dismiss
        </button>
    `;
    document.body.appendChild(errorDiv);
    
    // Auto-remove after 10 seconds
    setTimeout(() => errorDiv.remove(), 10000);
});

console.log('🎯 Ready for Assessment!');
