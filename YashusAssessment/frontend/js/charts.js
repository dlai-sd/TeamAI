// Chart Rendering with Canvas API

// Spider/Radar Chart for Dimension Scores
function renderSpiderChart() {
    const canvas = document.getElementById('spider-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const maxRadius = Math.min(centerX, centerY) - 60;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Dimensions
    const dimensions = [
        { name: 'Strategy', score: AppState.results.dimensions.strategy || 0 },
        { name: 'Technology', score: AppState.results.dimensions.technology || 0 },
        { name: 'Content', score: AppState.results.dimensions.content || 0 },
        { name: 'Channels', score: AppState.results.dimensions.channels || 0 },
        { name: 'Skills', score: AppState.results.dimensions.skills || 0 },
        { name: 'Measurement', score: AppState.results.dimensions.measurement || 0 },
        { name: 'CX', score: AppState.results.dimensions.cx || 0 }
    ];
    
    const angleStep = (2 * Math.PI) / dimensions.length;
    
    // Draw grid circles (1-7 scale)
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    for (let i = 1; i <= 7; i++) {
        ctx.beginPath();
        ctx.arc(centerX, centerY, (maxRadius / 7) * i, 0, 2 * Math.PI);
        ctx.stroke();
    }
    
    // Draw axes
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 1;
    dimensions.forEach((dim, index) => {
        const angle = angleStep * index - Math.PI / 2;
        const x = centerX + maxRadius * Math.cos(angle);
        const y = centerY + maxRadius * Math.sin(angle);
        
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(x, y);
        ctx.stroke();
        
        // Draw labels
        ctx.fillStyle = '#334155';
        ctx.font = '14px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        const labelX = centerX + (maxRadius + 30) * Math.cos(angle);
        const labelY = centerY + (maxRadius + 30) * Math.sin(angle);
        ctx.fillText(dim.name, labelX, labelY);
    });
    
    // Draw score polygon
    ctx.beginPath();
    ctx.fillStyle = 'rgba(37, 99, 235, 0.2)';
    ctx.strokeStyle = 'rgba(37, 99, 235, 1)';
    ctx.lineWidth = 3;
    
    dimensions.forEach((dim, index) => {
        const angle = angleStep * index - Math.PI / 2;
        const radius = (maxRadius / 7) * dim.score;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    
    // Draw score points
    ctx.fillStyle = '#2563eb';
    dimensions.forEach((dim, index) => {
        const angle = angleStep * index - Math.PI / 2;
        const radius = (maxRadius / 7) * dim.score;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
        
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, 2 * Math.PI);
        ctx.fill();
    });
}

// ROI Projection Chart (Line/Bar chart)
function renderROIChart() {
    const canvas = document.getElementById('roi-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const padding = 60;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Mock data: 12-month projection
    const months = ['Month 1', 'Month 3', 'Month 6', 'Month 9', 'Month 12'];
    const currentROI = [1.0, 1.5, 2.2, 2.8, 3.2]; // Cumulative ROI
    const projectedROI = [1.0, 1.8, 2.8, 3.5, 4.0]; // Best case
    
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;
    const maxROI = 5;
    const xStep = chartWidth / (months.length - 1);
    
    // Draw axes
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Draw Y-axis labels (ROI)
    ctx.fillStyle = '#64748b';
    ctx.font = '12px Inter, sans-serif';
    ctx.textAlign = 'right';
    for (let i = 0; i <= 5; i++) {
        const y = height - padding - (chartHeight / 5) * i;
        ctx.fillText(`${i}x`, padding - 10, y + 4);
        
        // Grid lines
        ctx.strokeStyle = '#e2e8f0';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }
    
    // Draw X-axis labels (months)
    ctx.textAlign = 'center';
    months.forEach((month, index) => {
        const x = padding + xStep * index;
        ctx.fillText(month, x, height - padding + 20);
    });
    
    // Plot current ROI line
    ctx.strokeStyle = '#2563eb';
    ctx.lineWidth = 3;
    ctx.beginPath();
    currentROI.forEach((roi, index) => {
        const x = padding + xStep * index;
        const y = height - padding - (chartHeight / maxROI) * roi;
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();
    
    // Plot projected ROI line (dashed)
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    projectedROI.forEach((roi, index) => {
        const x = padding + xStep * index;
        const y = height - padding - (chartHeight / maxROI) * roi;
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Draw data points
    currentROI.forEach((roi, index) => {
        const x = padding + xStep * index;
        const y = height - padding - (chartHeight / maxROI) * roi;
        
        ctx.fillStyle = '#2563eb';
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, 2 * Math.PI);
        ctx.fill();
    });
    
    projectedROI.forEach((roi, index) => {
        const x = padding + xStep * index;
        const y = height - padding - (chartHeight / maxROI) * roi;
        
        ctx.fillStyle = '#10b981';
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fill();
    });
    
    // Legend
    ctx.font = '14px Inter, sans-serif';
    ctx.fillStyle = '#2563eb';
    ctx.fillText('● Current Path', width - 150, 30);
    ctx.fillStyle = '#10b981';
    ctx.fillText('● With Optimization', width - 150, 50);
}

// Render SWOT analysis
function renderSWOT() {
    const swot = AppState.results.swot;
    
    // Strengths
    const strengthsEl = document.getElementById('swot-strengths');
    if (strengthsEl) {
        strengthsEl.innerHTML = swot.strengths.map(item => `
            <div class="swot-item">
                <strong>${item.title}</strong>
                <p>${item.description}</p>
                ${item.stat ? `<small style="color: var(--text-tertiary);">${item.stat}</small>` : ''}
            </div>
        `).join('');
    }
    
    // Weaknesses
    const weaknessesEl = document.getElementById('swot-weaknesses');
    if (weaknessesEl) {
        weaknessesEl.innerHTML = swot.weaknesses.map(item => `
            <div class="swot-item">
                <strong>${item.title}</strong>
                <p>${item.description}</p>
                ${item.stat ? `<small style="color: var(--text-tertiary);">${item.stat}</small>` : ''}
            </div>
        `).join('');
    }
    
    // Opportunities
    const opportunitiesEl = document.getElementById('swot-opportunities');
    if (opportunitiesEl) {
        opportunitiesEl.innerHTML = swot.opportunities.map(item => `
            <div class="swot-item">
                <strong>${item.title}</strong>
                <p>${item.description}</p>
                ${item.stat ? `<small style="color: var(--text-tertiary);">${item.stat}</small>` : ''}
            </div>
        `).join('');
    }
    
    // Threats
    const threatsEl = document.getElementById('swot-threats');
    if (threatsEl) {
        threatsEl.innerHTML = swot.threats.map(item => `
            <div class="swot-item">
                <strong>${item.title}</strong>
                <p>${item.description}</p>
                ${item.stat ? `<small style="color: var(--text-tertiary);">${item.stat}</small>` : ''}
            </div>
        `).join('');
    }
}

// Initialize charts when results page loads
function initializeCharts() {
    if (AppState.results) {
        renderSpiderChart();
        renderROIChart();
        renderSWOT();
    }
}

// Override renderResults to include chart initialization
const originalRenderResults = renderResults;
renderResults = function() {
    originalRenderResults();
    setTimeout(initializeCharts, 100);
};
