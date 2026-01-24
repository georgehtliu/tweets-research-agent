const API_BASE = window.location.origin;

// DOM elements
const queryInput = document.getElementById('queryInput');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');
const btnSpinner = document.getElementById('btnSpinner');
const resultSection = document.getElementById('resultSection');
const resultContent = document.getElementById('resultContent');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');

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

async function submitQuery() {
    const query = queryInput.value.trim();
    
    if (!query) {
        showError('Please enter a query');
        return;
    }
    
    // Hide previous results/errors
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    
    // Show loading state
    setLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }
        
        if (data.success && data.result) {
            // Display results
            resultContent.innerHTML = formatResult(data.result);
            resultSection.classList.remove('hidden');
            
            // Scroll to results
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            throw new Error(data.error || 'Unknown error occurred');
        }
        
    } catch (error) {
        console.error('Error:', error);
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
    }
}

// Run health check on page load
checkHealth();
