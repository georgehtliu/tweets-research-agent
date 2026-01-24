// Get API base URL
// If opened as file:// (direct file access), use default server URL
// Otherwise use the same origin as the page
function getApiBase() {
    if (window.location.protocol === 'file:') {
        // Default to port 8080, but allow override via localStorage
        const savedPort = localStorage.getItem('apiPort') || '8080';
        return `http://localhost:${savedPort}`;
    }
    return window.location.origin;
}

const API_BASE = getApiBase();

// DOM elements
const queryInput = document.getElementById('queryInput');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');
const btnSpinner = document.getElementById('btnSpinner');
const resultSection = document.getElementById('resultSection');
const resultContent = document.getElementById('resultContent');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const progressSection = document.getElementById('progressSection');
const progressSteps = document.getElementById('progressSteps');

// Allow Enter key to submit
queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !submitBtn.disabled) {
        submitQuery();
    }
});

function useExample(query) {
    queryInput.value = query;
    queryInput.focus();
}

function setLoading(loading) {
    submitBtn.disabled = loading;
    queryInput.disabled = loading;
    
    if (loading) {
        btnText.textContent = 'Processing...';
        btnSpinner.classList.remove('hidden');
    } else {
        btnText.textContent = 'Ask';
        btnSpinner.classList.add('hidden');
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorSection.classList.remove('hidden');
    resultSection.classList.add('hidden');
}

function closeError() {
    errorSection.classList.add('hidden');
}

function closeResults() {
    resultSection.classList.add('hidden');
}

function formatResult(result) {
    let html = '';
    
    // Metadata section
    html += '<div class="result-meta">';
    html += `<div class="meta-item">
        <div class="meta-label">Query Type</div>
        <div class="meta-value">${result.plan?.query_type || 'N/A'}</div>
    </div>`;
    html += `<div class="meta-item">
        <div class="meta-label">Results Found</div>
        <div class="meta-value">${result.results_count || 0}</div>
    </div>`;
    html += `<div class="meta-item">
        <div class="meta-label">Refinement Iterations</div>
        <div class="meta-value">${result.refinement_iterations || 0}</div>
    </div>`;
    html += `<div class="meta-item">
        <div class="meta-label">Total Steps</div>
        <div class="meta-value">${result.execution_steps || 0}</div>
    </div>`;
    html += `<div class="meta-item">
        <div class="meta-label">Confidence</div>
        <div class="meta-value">${(result.analysis?.confidence * 100 || 0).toFixed(0)}%</div>
    </div>`;
    html += '</div>';
    
    // Summary section
    if (result.final_summary) {
        html += '<div class="summary-section">';
        html += '<h3>📝 Final Summary</h3>';
        html += `<div class="summary-text">${escapeHtml(result.final_summary)}</div>`;
        html += '</div>';
    }
    
    // Analysis section
    if (result.analysis) {
        html += '<div class="summary-section">';
        html += '<h3>🔍 Analysis</h3>';
        
        if (result.analysis.main_themes && result.analysis.main_themes.length > 0) {
            html += '<p><strong>Main Themes:</strong> ' + result.analysis.main_themes.join(', ') + '</p>';
        }
        
        if (result.analysis.key_insights && result.analysis.key_insights.length > 0) {
            html += '<p><strong>Key Insights:</strong></p><ul>';
            result.analysis.key_insights.forEach(insight => {
                html += `<li>${escapeHtml(insight)}</li>`;
            });
            html += '</ul>';
        }
        
        if (result.analysis.sentiment_analysis) {
            const sent = result.analysis.sentiment_analysis;
            html += '<p><strong>Sentiment Distribution:</strong></p>';
            html += '<ul>';
            if (sent.positive !== undefined) html += `<li>Positive: ${sent.positive}</li>`;
            if (sent.negative !== undefined) html += `<li>Negative: ${sent.negative}</li>`;
            if (sent.neutral !== undefined) html += `<li>Neutral: ${sent.neutral}</li>`;
            html += '</ul>';
        }
        
        html += '</div>';
    }
    
    // Plan section
    if (result.plan && result.plan.steps) {
        html += '<div class="plan-section">';
        html += '<h3>📋 Execution Plan</h3>';
        result.plan.steps.forEach((step, index) => {
            html += `<div class="step-item">`;
            html += `<strong>Step ${step.step_number || index + 1}:</strong> ${escapeHtml(step.description || step.action || 'N/A')}`;
            html += `</div>`;
        });
        html += '</div>';
    }
    
    return html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Progress tracking
const progressState = {
    planning: { status: 'pending', step: null },
    executing: { status: 'pending', step: null },
    analyzing: { status: 'pending', step: null },
    refining: { status: 'pending', step: null },
    summarizing: { status: 'pending', step: null }
};

function updateProgressStep(stepType, data) {
    const stepNames = {
        'planning': { icon: '📋', title: 'Planning', order: 1 },
        'executing': { icon: '⚙️', title: 'Executing', order: 2 },
        'analyzing': { icon: '🔍', title: 'Analyzing', order: 3 },
        'refining': { icon: '🔄', title: 'Refining', order: 4 },
        'summarizing': { icon: '📝', title: 'Summarizing', order: 5 }
    };
    
    if (stepNames[stepType]) {
        progressState[stepType] = { ...progressState[stepType], ...data };
        renderProgressSteps();
    }
}

function renderProgressSteps() {
    const steps = [
        { key: 'planning', icon: '📋', title: 'Planning' },
        { key: 'executing', icon: '⚙️', title: 'Executing' },
        { key: 'analyzing', icon: '🔍', title: 'Analyzing' },
        { key: 'refining', icon: '🔄', title: 'Refining' },
        { key: 'summarizing', icon: '📝', title: 'Summarizing' }
    ];
    
    progressSteps.innerHTML = steps.map(step => {
        const state = progressState[step.key];
        let statusClass = 'pending';
        let message = '';
        let details = '';
        
        if (state.status === 'started' || state.status === 'checking' || state.status === 'refining') {
            statusClass = 'active';
            message = state.message || `${step.title} in progress...`;
        } else if (state.status === 'completed' || state.status === 'updated') {
            statusClass = 'completed';
            message = `${step.title} completed`;
            
            // Add details based on step type
            if (step.key === 'planning' && state.query_type) {
                details = `Type: ${state.query_type} | Steps: ${state.steps_count || 0}`;
            } else if (step.key === 'executing' && state.results_count !== undefined) {
                details = `Retrieved ${state.results_count} items`;
            } else if (step.key === 'analyzing' && state.confidence !== undefined) {
                details = `Confidence: ${(state.confidence * 100).toFixed(0)}%`;
                if (state.main_themes && state.main_themes.length > 0) {
                    details += ` | Themes: ${state.main_themes.join(', ')}`;
                }
            } else if (step.key === 'refining' && state.iteration) {
                details = `Iteration ${state.iteration}`;
                if (state.reason) {
                    details += ` | ${state.reason}`;
                }
            }
        }
        
        return `
            <div class="progress-step ${statusClass}">
                <div class="progress-step-title">
                    <span class="icon">${step.icon}</span>
                    <span>${step.title}</span>
                </div>
                ${message ? `<div class="progress-step-message">${message}</div>` : ''}
                ${details ? `<div class="progress-step-details">${details}</div>` : ''}
            </div>
        `;
    }).join('');
}

function resetProgress() {
    Object.keys(progressState).forEach(key => {
        progressState[key] = { status: 'pending', step: null };
    });
    renderProgressSteps();
}

async function submitQuery() {
    const query = queryInput.value.trim();
    
    if (!query) {
        showError('Please enter a query');
        return;
    }
    
    // Hide previous results/errors
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    
    // Show loading state and progress
    setLoading(true);
    resetProgress();
    progressSection.classList.remove('hidden');
    progressSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    try {
        const response = await fetch(`${API_BASE}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Handle Server-Sent Events
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let finalResult = null;
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line in buffer
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        
                        if (data.type === 'error') {
                            throw new Error(data.message);
                        } else if (data.type === 'complete') {
                            finalResult = data.result;
                        } else {
                            // Update progress
                            updateProgressStep(data.type, data);
                        }
                    } catch (e) {
                        if (e instanceof SyntaxError) {
                            // Skip malformed JSON
                            continue;
                        }
                        throw e;
                    }
                }
            }
        }
        
        if (finalResult) {
            // Display results
            resultContent.innerHTML = formatResult(finalResult);
            progressSection.classList.add('hidden');
            resultSection.classList.remove('hidden');
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            throw new Error('No result received');
        }
        
    } catch (error) {
        console.error('Error:', error);
        progressSection.classList.add('hidden');
        showError(error.message || 'An error occurred while processing your query. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Check API health on load
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            console.log('✅ API is healthy');
        } else {
            console.warn('⚠️ API health check failed:', data);
        }
    } catch (error) {
        console.error('❌ Health check failed:', error);
        if (window.location.protocol === 'file:') {
            console.warn('💡 Tip: Make sure the API server is running on', API_BASE);
            console.warn('   Start it with: python server/api_server.py');
        }
    }
}

// Run health check on page load
checkHealth();
