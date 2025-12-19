// Monopoly Board Interactions & Animations

// Update Board State
function updateMonopolyBoard() {
    const properties = document.querySelectorAll('.board-property');
    
    properties.forEach(property => {
        const milestoneNumber = parseInt(property.dataset.milestone);
        
        // Mark as completed
        if (AppState.completedMilestones.includes(milestoneNumber)) {
            property.classList.add('completed');
            property.classList.remove('current');
        }
    });
    
    // Mark current milestone
    const nextMilestone = getNextMilestone();
    if (nextMilestone) {
        const currentProperty = document.querySelector(`[data-milestone="${nextMilestone}"]`);
        if (currentProperty) {
            currentProperty.classList.add('current');
        }
    }
    
    // Update progress bar
    updateProgressIndicator();
    
    // Check if all completed
    if (AppState.completedMilestones.length === 9) {
        celebrateCompletion();
    }
}

// Get Next Milestone
function getNextMilestone() {
    for (let i = 1; i <= 9; i++) {
        if (!AppState.completedMilestones.includes(i)) {
            return i;
        }
    }
    return null;
}

// Property Click Handler
function handlePropertyClick(milestoneNumber) {
    // If already completed, allow review
    if (AppState.completedMilestones.includes(milestoneNumber)) {
        if (confirm('This milestone is already completed. Review your answers?')) {
            navigateTo(`pane-milestone-${milestoneNumber}`);
        }
    } else {
        // Navigate to milestone
        navigateTo(`pane-milestone-${milestoneNumber}`);
    }
}

// Celebrate Completion
function celebrateCompletion() {
    // Add confetti effect
    createConfetti();
    
    // Update finish corner
    const finishCorner = document.querySelector('.finish-corner');
    if (finishCorner) {
        finishCorner.innerHTML = '🎉<br>COMPLETE!';
        finishCorner.style.animation = 'pulse 1.5s ease-in-out infinite';
    }
    
    // Show completion message
    setTimeout(() => {
        if (AppState.currentPane === 'pane-monopoly') {
            const centerMessage = document.createElement('div');
            centerMessage.className = 'completion-message';
            centerMessage.innerHTML = `
                <h2>🎉 Congratulations!</h2>
                <p>All milestones completed!</p>
                <button onclick="navigateTo('pane-dashboard')" class="cta-button">
                    View Your Results →
                </button>
            `;
            centerMessage.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(251, 191, 36, 0.95);
                color: var(--bg-dark);
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                z-index: 10000;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                animation: fadeIn 0.5s ease;
            `;
            document.body.appendChild(centerMessage);
        }
    }, 1000);
}

// Create Confetti Animation
function createConfetti() {
    const colors = ['#fbbf24', '#f59e0b', '#d97706', '#fb923c'];
    const confettiCount = 50;
    
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.cssText = `
            position: fixed;
            width: 10px;
            height: 10px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            left: ${Math.random() * 100}%;
            top: -10px;
            opacity: ${Math.random()};
            animation: confettiFall ${2 + Math.random() * 3}s linear;
            z-index: 9999;
        `;
        document.body.appendChild(confetti);
        
        // Remove after animation
        setTimeout(() => confetti.remove(), 5000);
    }
}

// Add confetti animation to document
if (!document.querySelector('#confetti-style')) {
    const style = document.createElement('style');
    style.id = 'confetti-style';
    style.textContent = `
        @keyframes confettiFall {
            to {
                top: 100vh;
                transform: translateX(${Math.random() * 200 - 100}px) rotateZ(${Math.random() * 720}deg);
            }
        }
    `;
    document.head.appendChild(style);
}

// Property Hover Effects
function setupPropertyHoverEffects() {
    const properties = document.querySelectorAll('.board-property');
    
    properties.forEach(property => {
        property.addEventListener('mouseenter', () => {
            const milestoneNumber = property.dataset.milestone;
            showPropertyPreview(milestoneNumber);
        });
        
        property.addEventListener('mouseleave', () => {
            hidePropertyPreview();
        });
    });
}

// Show Property Preview (Tooltip)
function showPropertyPreview(milestoneNumber) {
    const milestoneNames = {
        1: "Define Your Foundation",
        2: "Understand Your Market",
        3: "Craft Your Message",
        4: "Build Your Platform",
        5: "Launch Your Campaign",
        6: "Measure Success",
        7: "Scale Operations",
        8: "Optimize Performance",
        9: "Plan for Growth"
    };
    
    const tooltip = document.createElement('div');
    tooltip.id = 'property-tooltip';
    tooltip.className = 'property-tooltip';
    tooltip.innerHTML = `
        <strong>Milestone ${milestoneNumber}</strong><br>
        ${milestoneNames[milestoneNumber]}
        ${AppState.completedMilestones.includes(parseInt(milestoneNumber)) ? '<br>✅ Completed' : '<br>🎯 Click to start'}
    `;
    tooltip.style.cssText = `
        position: fixed;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.9em;
        pointer-events: none;
        z-index: 10000;
        border: 1px solid var(--gold-primary);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip near cursor
    document.addEventListener('mousemove', updateTooltipPosition);
}

function updateTooltipPosition(event) {
    const tooltip = document.getElementById('property-tooltip');
    if (tooltip) {
        tooltip.style.left = (event.clientX + 15) + 'px';
        tooltip.style.top = (event.clientY + 15) + 'px';
    }
}

function hidePropertyPreview() {
    const tooltip = document.getElementById('property-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
    document.removeEventListener('mousemove', updateTooltipPosition);
}

// Attach Click Handlers to Properties
function attachPropertyClickHandlers() {
    const properties = document.querySelectorAll('.board-property');
    
    properties.forEach(property => {
        property.addEventListener('click', () => {
            const milestoneNumber = parseInt(property.dataset.milestone);
            handlePropertyClick(milestoneNumber);
        });
    });
}

// Initialize Monopoly Board
function initializeMonopolyBoard() {
    attachPropertyClickHandlers();
    setupPropertyHoverEffects();
    updateMonopolyBoard();
}

// Call init on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeMonopolyBoard);
} else {
    initializeMonopolyBoard();
}
