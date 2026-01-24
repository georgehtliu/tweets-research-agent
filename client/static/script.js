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
        btnText.textContent = 'Generate';
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
    
    // Compact metadata bar
    const conf = Math.max(0, Number(result.analysis?.confidence) || 0) * 100;
    const confColor = conf >= 80 ? '#10b981' : conf >= 60 ? '#f59e0b' : '#f87171';
    
    html += '<div class="result-meta-bar">';
    html += `<span class="meta-badge"><span class="meta-badge-label">Results</span><span class="meta-badge-value">${result.results_count || 0}</span></span>`;
    html += `<span class="meta-badge"><span class="meta-badge-label">Confidence</span><span class="meta-badge-value" style="color: ${confColor}">${conf.toFixed(0)}%</span></span>`;
    if (result.execution_steps) {
        html += `<span class="meta-badge"><span class="meta-badge-label">Steps</span><span class="meta-badge-value">${result.execution_steps}</span></span>`;
    }
    if (result.replan_count > 0) {
        html += `<span class="meta-badge"><span class="meta-badge-label">Replans</span><span class="meta-badge-value">${result.replan_count}</span></span>`;
    }
    html += '</div>';
    
    // Summary section (primary content)
    if (result.final_summary) {
        html += '<div class="result-section-primary">';
        html += '<div class="section-header">';
        html += '<span class="section-icon">📄</span>';
        html += '<h3>Summary</h3>';
        html += '</div>';
        const markdownHtml = convertMarkdownToHtml(result.final_summary);
        html += `<div class="summary-text">${markdownHtml}</div>`;
        html += '</div>';
    }
    
    // Key insights (simplified)
    if (result.analysis?.key_insights && result.analysis.key_insights.length > 0) {
        html += '<div class="result-section-secondary">';
        html += '<div class="section-header">';
        html += '<span class="section-icon">💡</span>';
        html += '<h3>Key Insights</h3>';
        html += '</div>';
        html += '<ul class="insights-list">';
        result.analysis.key_insights.slice(0, 5).forEach(insight => {
            html += `<li>${escapeHtml(insight)}</li>`;
        });
        html += '</ul>';
        html += '</div>';
    }
    
    // Themes & Sentiment (compact)
    if (result.analysis) {
        const themes = result.analysis.main_themes || [];
        const sent = result.analysis.sentiment_analysis || {};
        
        if (themes.length > 0 || Object.keys(sent).length > 0) {
            html += '<div class="result-section-tertiary">';
            html += '<div class="section-header">';
            html += '<span class="section-icon">📊</span>';
            html += '<h3>Analysis</h3>';
            html += '</div>';
            
            if (themes.length > 0) {
                html += '<div class="analysis-item">';
                html += '<span class="analysis-label">Themes:</span>';
                html += `<span class="analysis-value">${themes.slice(0, 3).join(', ')}</span>`;
                html += '</div>';
            }
            
            if (sent.positive !== undefined || sent.negative !== undefined || sent.neutral !== undefined) {
                html += '<div class="analysis-item">';
                html += '<span class="analysis-label">Sentiment:</span>';
                const sentParts = [];
                if (sent.positive) sentParts.push(`<span style="color: #10b981">+${sent.positive}</span>`);
                if (sent.negative) sentParts.push(`<span style="color: #f87171">-${sent.negative}</span>`);
                if (sent.neutral) sentParts.push(`<span style="color: #94a3b8">~${sent.neutral}</span>`);
                html += `<span class="analysis-value">${sentParts.join(' ')}</span>`;
                html += '</div>';
            }
            
            html += '</div>';
        }
    }
    
    // Critique (simplified, only show if issues found)
    if (result.critique) {
        const critique = result.critique;
        const passed = critique.critique_passed !== false;
        const hasIssues = (critique.hallucinations && critique.hallucinations.length > 0) ||
                         (critique.biases && critique.biases.length > 0);
        
        if (!passed || hasIssues) {
            html += '<div class="result-section-critique">';
            html += '<div class="section-header">';
            html += '<span class="section-icon">🔬</span>';
            html += '<h3>Quality Check</h3>';
            html += `<span class="critique-badge ${passed ? 'passed' : 'failed'}">${passed ? '✓ Passed' : '⚠ Issues Found'}</span>`;
            html += '</div>';
            
            if (critique.hallucinations && critique.hallucinations.length > 0) {
                html += '<div class="critique-item"><span class="critique-label">Hallucinations:</span> ' + critique.hallucinations.length + '</div>';
            }
            if (critique.biases && critique.biases.length > 0) {
                html += '<div class="critique-item"><span class="critique-label">Biases:</span> ' + critique.biases.length + '</div>';
            }
            html += '</div>';
        }
    }
    
    return html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function convertMarkdownToHtml(markdown) {
    if (!markdown) return '';
    
    // Split into lines for processing
    let lines = markdown.split('\n');
    let html = '';
    let inList = false;
    let listType = null;
    
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        
        if (!line) {
            // Close any open list
            if (inList) {
                html += listType === 'ol' ? '</ol>' : '</ul>';
                inList = false;
                listType = null;
            }
            html += '\n';
            continue;
        }
        
        // Headers (must be at start of line)
        if (line.startsWith('### ')) {
            if (inList) {
                html += listType === 'ol' ? '</ol>' : '</ul>';
                inList = false;
            }
            html += `<h4>${escapeHtml(line.substring(4))}</h4>\n`;
            continue;
        }
        if (line.startsWith('## ')) {
            if (inList) {
                html += listType === 'ol' ? '</ol>' : '</ul>';
                inList = false;
            }
            html += `<h3>${escapeHtml(line.substring(3))}</h3>\n`;
            continue;
        }
        if (line.startsWith('# ')) {
            if (inList) {
                html += listType === 'ol' ? '</ol>' : '</ul>';
                inList = false;
            }
            html += `<h2>${escapeHtml(line.substring(2))}</h2>\n`;
            continue;
        }
        
        // Numbered lists
        const numberedMatch = line.match(/^(\d+)\.\s+(.*)$/);
        if (numberedMatch) {
            if (!inList || listType !== 'ol') {
                if (inList) html += listType === 'ul' ? '</ul>' : '';
                html += '<ol>';
                inList = true;
                listType = 'ol';
            }
            html += `<li>${escapeHtml(numberedMatch[2])}</li>\n`;
            continue;
        }
        
        // Bullet lists
        const bulletMatch = line.match(/^[-*]\s+(.*)$/);
        if (bulletMatch) {
            if (!inList || listType !== 'ul') {
                if (inList) html += listType === 'ol' ? '</ol>' : '';
                html += '<ul>';
                inList = true;
                listType = 'ul';
            }
            html += `<li>${escapeHtml(bulletMatch[1])}</li>\n`;
            continue;
        }
        
        // Regular paragraph
        if (inList) {
            html += listType === 'ol' ? '</ol>' : '</ul>';
            inList = false;
            listType = null;
        }
        
        // Process inline markdown
        let processedLine = escapeHtml(line);
        // Bold (must be ** or __) - process first
        processedLine = processedLine.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        processedLine = processedLine.replace(/__(.*?)__/g, '<strong>$1</strong>');
        // Italic (single * or _) - only process if not already inside strong tags
        // Split by strong tags, process italic in non-strong parts
        const parts = processedLine.split(/(<strong>.*?<\/strong>)/g);
        processedLine = parts.map(part => {
            if (part.startsWith('<strong>')) {
                return part; // Don't process italic inside strong tags
            }
            // Process italic in this part
            part = part.replace(/\*([^*\n]+?)\*/g, '<em>$1</em>');
            part = part.replace(/_([^_\n]+?)_/g, '<em>$1</em>');
            return part;
        }).join('');
        
        html += `<p>${processedLine}</p>\n`;
    }
    
    // Close any remaining list
    if (inList) {
        html += listType === 'ol' ? '</ol>' : '</ul>';
    }
    
    return html;
}

// Progress tracking
const progressState = {
    planning: { status: 'pending', step: null },
    executing: { status: 'pending', step: null },
    analyzing: { status: 'pending', step: null },
    evaluating: { status: 'pending', step: null },
    replanning: { status: 'pending', step: null },
    refining: { status: 'pending', step: null },
    critiquing: { status: 'pending', step: null },
    summarizing: { status: 'pending', step: null }
};

function updateProgressStep(stepType, data) {
    const stepNames = {
        'planning': { icon: '📋', title: 'Planning', order: 1 },
        'executing': { icon: '⚙️', title: 'Executing', order: 2 },
        'analyzing': { icon: '🔍', title: 'Analyzing', order: 3 },
        'evaluating': { icon: '🔎', title: 'Evaluating Strategy', order: 4 },
        'replanning': { icon: '🔄', title: 'Replanning', order: 4.5 },
        'refining': { icon: '🔄', title: 'Refining', order: 5 },
        'critiquing': { icon: '🔬', title: 'Critiquing', order: 6 },
        'summarizing': { icon: '📝', title: 'Summarizing', order: 7 }
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
        { key: 'evaluating', icon: '🔎', title: 'Evaluating Strategy' },
        { key: 'replanning', icon: '🔄', title: 'Replanning', conditional: true },
        { key: 'refining', icon: '🔄', title: 'Refining' },
        { key: 'critiquing', icon: '🔬', title: 'Critiquing' },
        { key: 'summarizing', icon: '📝', title: 'Summarizing' }
    ];
    
    // Filter out conditional steps that haven't been activated
    const visibleSteps = steps.filter(step => {
        if (step.conditional) {
            const state = progressState[step.key];
            return state.status !== 'pending';
        }
        return true;
    });
    
    progressSteps.innerHTML = visibleSteps.map(step => {
        const state = progressState[step.key];
        let statusClass = 'pending';
        let message = '';
        let details = '';
        
        if (state.status === 'started' || state.status === 'checking' || state.status === 'refining' || state.status === 'replanning' || state.status === 'tool_calling') {
            statusClass = 'active';
            message = state.message || `${step.title} in progress...`;
        } else if (state.status === 'completed' || state.status === 'updated' || state.status === 'skipped') {
            statusClass = 'completed';
            message = state.status === 'skipped' ? `${step.title} skipped` : `${step.title} completed`;
            
            // Add details based on step type (simplified)
            if (step.key === 'planning' && state.query_type) {
                details = `${state.query_type} · ${state.steps_count || 0} steps`;
            } else if (step.key === 'executing') {
                if (state.tool_calling_mode && state.tool_calls && state.tool_calls.length > 0) {
                    details = `${state.total_tool_calls || state.tool_calls.length} tools · ${state.total_results || state.results_count || 0} results`;
                } else if (state.results_count !== undefined) {
                    details = `${state.results_count} items`;
                }
            } else if (step.key === 'analyzing' && state.confidence !== undefined) {
                const conf = Number(state.confidence);
                details = `${(isNaN(conf) ? 0 : conf * 100).toFixed(0)}% confidence`;
                if (state.main_themes && state.main_themes.length > 0) {
                    details += ` · ${state.main_themes.slice(0, 2).join(', ')}`;
                }
            } else if (step.key === 'evaluating') {
                details = state.reason ? state.reason.slice(0, 60) : 'Strategy checked';
            } else if (step.key === 'replanning' && state.attempt) {
                details = `Attempt ${state.attempt}`;
            } else if (step.key === 'refining' && state.iteration) {
                details = `Iteration ${state.iteration}`;
            } else if (step.key === 'critiquing') {
                details = state.critique_passed !== undefined 
                    ? (state.critique_passed ? '✓ Passed' : '⚠ Issues')
                    : 'Reviewed';
            }
        }
        
        const iconStyle = statusClass === 'completed' ? '✓' : statusClass === 'active' ? '→' : '○';
        const phaseSummary = state.summary || '';
        
        // Tool calls visualization for executing step
        let toolCallsHtml = '';
        if (step.key === 'executing' && state.tool_calling_mode && state.tool_calls && state.tool_calls.length > 0) {
            toolCallsHtml = '<div class="tool-calls-container">';
            toolCallsHtml += '<div class="tool-calls-header">🔧 Tool Calls:</div>';
            toolCallsHtml += '<div class="tool-calls-list">';
            state.tool_calls.forEach((toolCall, idx) => {
                const successClass = toolCall.success ? 'success' : 'failed';
                const statusIcon = toolCall.success ? '✓' : '✗';
                toolCallsHtml += `
                    <div class="tool-call-item ${successClass}">
                        <div class="tool-call-header">
                            <span class="tool-call-icon">${statusIcon}</span>
                            <span class="tool-call-name">${escapeHtml(toolCall.name)}</span>
                            <span class="tool-call-results">${toolCall.results_count || 0} results</span>
                        </div>
                        <div class="tool-call-args">
                            ${Object.keys(toolCall.arguments || {}).length > 0 
                                ? `<div class="tool-call-args-label">Arguments:</div>
                                   <div class="tool-call-args-content">${escapeHtml(JSON.stringify(toolCall.arguments, null, 2))}</div>`
                                : ''}
                        </div>
                        ${toolCall.message ? `<div class="tool-call-message">${escapeHtml(toolCall.message)}</div>` : ''}
                    </div>
                `;
            });
            toolCallsHtml += '</div></div>';
        }
        
        return `
            <div class="progress-step ${statusClass}">
                <div class="progress-step-title">
                    <span class="icon" style="font-weight: 600;">${iconStyle}</span>
                    <span>${step.title}</span>
                </div>
                ${message ? `<div class="progress-step-message">${message}</div>` : ''}
                ${details ? `<div class="progress-step-details">${details}</div>` : ''}
                ${toolCallsHtml}
                ${phaseSummary ? `<div class="progress-step-summary">${escapeHtml(phaseSummary)}</div>` : ''}
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

// Tab switching
function switchTab(tabName) {
    const queryTab = document.getElementById('queryTab');
    const evaluationTab = document.getElementById('evaluationTab');
    const queryContent = document.getElementById('queryTabContent');
    const evaluationContent = document.getElementById('evaluationTabContent');
    
    if (tabName === 'query') {
        queryTab.classList.add('active');
        evaluationTab.classList.remove('active');
        queryContent.classList.remove('hidden');
        evaluationContent.classList.add('hidden');
    } else {
        evaluationTab.classList.add('active');
        queryTab.classList.remove('active');
        evaluationContent.classList.remove('hidden');
        queryContent.classList.add('hidden');
        loadEvaluationModels();
    }
}

// Load available models and populate Batch Evaluation + Model Comparison controls
let evaluationModelsLoaded = false;
async function loadEvaluationModels() {
    if (evaluationModelsLoaded) return;
    const selectEl = document.getElementById('evalModel');
    const containerEl = document.getElementById('compareModelsContainer');
    if (!selectEl || !containerEl) return;
    try {
        const response = await fetch(`${API_BASE}/api/evaluation/models`);
        if (!response.ok) return;
        const data = await response.json();
        const models = data.models || [];
        evaluationModelsLoaded = true;

        // Populate Batch Evaluation model select (keep "Default" option)
        selectEl.innerHTML = '<option value="">Default (from config)</option>';
        models.forEach(function (m) {
            const opt = document.createElement('option');
            opt.value = m;
            opt.textContent = m;
            selectEl.appendChild(opt);
        });

        // Populate Model Comparison checkboxes
        containerEl.innerHTML = '';
        models.forEach(function (m) {
            const label = document.createElement('label');
            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.name = 'compareModel';
            cb.value = m;
            label.appendChild(cb);
            label.appendChild(document.createTextNode(m));
            containerEl.appendChild(label);
        });
        
        // Show/hide max workers based on parallel checkbox
        const parallelCheckbox = document.getElementById('evalParallel');
        const maxWorkersGroup = document.getElementById('evalMaxWorkersGroup');
        if (parallelCheckbox && maxWorkersGroup) {
            parallelCheckbox.addEventListener('change', function() {
                maxWorkersGroup.style.display = this.checked ? 'block' : 'none';
            });
        }
    } catch (e) {
        console.warn('Could not load evaluation models:', e);
    }
}

function toggleCompareModels(checked) {
    var inputs = document.querySelectorAll('#compareModelsContainer input[name="compareModel"]');
    inputs.forEach(function (c) { c.checked = !!checked; });
}

// Evaluation functions
function setEvaluationLoading(loading) {
    const btn = document.getElementById('runEvaluationBtn');
    const btnText = document.getElementById('evalBtnText');
    const btnSpinner = document.getElementById('evalBtnSpinner');
    
    btn.disabled = loading;
    if (loading) {
        btnText.textContent = 'Running...';
        btnSpinner.classList.remove('hidden');
    } else {
        btnText.textContent = 'Run Evaluation';
        btnSpinner.classList.add('hidden');
    }
}

function setCompareLoading(loading) {
    const btn = document.getElementById('compareModelsBtn');
    const btnText = document.getElementById('compareBtnText');
    const btnSpinner = document.getElementById('compareBtnSpinner');
    
    btn.disabled = loading;
    if (loading) {
        btnText.textContent = 'Comparing...';
        btnSpinner.classList.remove('hidden');
    } else {
        btnText.textContent = 'Compare Models';
        btnSpinner.classList.add('hidden');
    }
}

function formatEvaluationResult(evaluationData) {
    let html = '<div class="evaluation-results">';
    
    const metrics = evaluationData.metrics || {};
    
    // Summary metrics
    html += '<div class="metrics-summary">';
    html += '<h3>📊 Evaluation Summary</h3>';
    
    const cr = metrics.completion_rate || {};
    html += `<div class="metric-card">
        <div class="metric-label">Completion Rate</div>
        <div class="metric-value large">${(cr.completion_rate || 0).toFixed(1)}%</div>
        <div class="metric-detail">${cr.completed || 0}/${cr.total_queries || 0} queries completed</div>
    </div>`;
    
    const se = metrics.step_efficiency || {};
    html += `<div class="metric-card">
        <div class="metric-label">Step Efficiency</div>
        <div class="metric-value">${se.avg_execution_steps || 0}</div>
        <div class="metric-detail">Avg steps per query</div>
    </div>`;
    
    const sq = metrics.summary_quality || {};
    html += `<div class="metric-card">
        <div class="metric-label">Avg Confidence</div>
        <div class="metric-value">${(sq.avg_confidence || 0).toFixed(3)}</div>
        <div class="metric-detail">${(sq.high_confidence_rate || 0).toFixed(1)}% high confidence</div>
    </div>`;
    
    const am = metrics.autonomy_metrics || {};
    html += `<div class="metric-card">
        <div class="metric-label">Autonomy Score</div>
        <div class="metric-value">${(am.avg_autonomy_score || 0).toFixed(3)}</div>
        <div class="metric-detail">Higher is better</div>
    </div>`;
    
    html += '</div>';
    
    // Queries run
    const results = evaluationData.results || [];
    if (results.length > 0) {
        html += '<div class="queries-run-section">';
        html += '<h4>📋 Queries Run</h4>';
        html += '<ul class="queries-run-list">';
        results.forEach(function (r, idx) {
            const q = r.query || '(no query text)';
            const id = r.query_id || ('query_' + (idx + 1));
            const cat = r.query_category || 'unknown';
            const complexity = r.query_complexity || 'unknown';
            const ok = r.success;
            const time = r.query_time_seconds;
            const err = r.error;
            const status = ok
                ? (time != null ? '✓ ' + time + 's' : '✓')
                : (err ? '✗ ' + escapeHtml(String(err).slice(0, 80)) : '✗');
            html += '<li class="queries-run-item">';
            html += '<span class="queries-run-status ' + (ok ? 'success' : 'failed') + '">' + status + '</span>';
            html += '<span class="queries-run-meta">' + escapeHtml(id) + ' · ' + escapeHtml(cat) + ' · ' + escapeHtml(complexity) + '</span>';
            html += '<div class="queries-run-text">' + escapeHtml(q) + '</div>';
            html += '</li>';
        });
        html += '</ul>';
        html += '</div>';
    }
    
    // Detailed metrics
    html += '<div class="metrics-details">';
    html += '<h4>Detailed Metrics</h4>';
    
    html += '<div class="detail-section">';
    html += '<h5>Step Efficiency</h5>';
    html += `<p>Avg Steps: ${se.avg_execution_steps || 0}</p>`;
    html += `<p>Avg Refinement Iterations: ${se.avg_refinement_iterations || 0}</p>`;
    html += `<p>Avg Replan Count: ${se.avg_replan_count || 0}</p>`;
    html += `<p>Avg Tokens/Query: ${Math.round(se.avg_tokens_per_query || 0)}</p>`;
    html += '</div>';
    
    html += '<div class="detail-section">';
    html += '<h5>Summary Quality</h5>';
    html += `<p>Avg Confidence: ${(sq.avg_confidence || 0).toFixed(3)}</p>`;
    html += `<p>Avg Summary Length: ${Math.round(sq.avg_summary_length || 0)} chars</p>`;
    if (sq.quality_distribution) {
        html += `<p>Quality Distribution: High: ${sq.quality_distribution.high || 0}, Medium: ${sq.quality_distribution.medium || 0}, Low: ${sq.quality_distribution.low || 0}</p>`;
    }
    html += '</div>';
    
    html += '<div class="detail-section">';
    html += '<h5>Autonomy Metrics</h5>';
    html += `<p>Replan Rate: ${((am.replan_rate || 0) * 100).toFixed(1)}%</p>`;
    html += `<p>Refinement Rate: ${((am.refinement_rate || 0) * 100).toFixed(1)}%</p>`;
    html += `<p>Critique Pass Rate: ${((am.critique_pass_rate || 0) * 100).toFixed(1)}%</p>`;
    html += '</div>';
    
    // Category breakdown if available
    if (metrics.category_breakdown) {
        html += '<div class="detail-section">';
        html += '<h5>Category Breakdown</h5>';
        const byCategory = metrics.category_breakdown.by_category || {};
        for (const [category, stats] of Object.entries(byCategory)) {
            const catCr = stats.completion_rate?.completion_rate || 0;
            html += `<p><strong>${category}</strong>: ${(catCr * 100).toFixed(1)}% completion (${stats.count || 0} queries)</p>`;
        }
        html += '</div>';
    }
    
    html += '</div>';
    
    // Output file info
    if (evaluationData.output_file) {
        html += `<div class="output-info"><p>📁 Results saved to: <code>${evaluationData.output_file}</code></p></div>`;
    }
    
    html += '</div>';
    return html;
}

function formatComparisonResult(comparisonData) {
    let html = '<div class="comparison-results">';
    html += '<h3>🔬 Model Comparison Results</h3>';
    
    const results = comparisonData.comparison_results || {};
    const summary = comparisonData.comparison_summary || {};
    
    // Comparison table
    html += '<table class="comparison-table">';
    html += '<thead><tr>';
    html += '<th>Model</th><th>Completion</th><th>Confidence</th><th>Avg Steps</th><th>Avg Tokens</th><th>Autonomy</th>';
    html += '</tr></thead><tbody>';
    
    for (const [modelName, modelResult] of Object.entries(results)) {
        if (modelResult.error) {
            html += `<tr><td>${escapeHtml(modelName)}</td><td colspan="5">Error: ${escapeHtml(modelResult.error)}</td></tr>`;
            continue;
        }
        
        const metrics = modelResult.metrics || {};
        const cr = metrics.completion_rate?.completion_rate || 0;
        const conf = metrics.summary_quality?.avg_confidence || 0;
        const steps = metrics.step_efficiency?.avg_execution_steps || 0;
        const tokens = metrics.step_efficiency?.avg_tokens_per_query || 0;
        const autonomy = metrics.autonomy_metrics?.avg_autonomy_score || 0;
        
        html += `<tr>`;
        html += `<td><strong>${escapeHtml(modelName)}</strong></td>`;
        html += `<td>${(cr * 100).toFixed(1)}%</td>`;
        html += `<td>${conf.toFixed(3)}</td>`;
        html += `<td>${steps.toFixed(1)}</td>`;
        html += `<td>${Math.round(tokens)}</td>`;
        html += `<td>${autonomy.toFixed(3)}</td>`;
        html += `</tr>`;
    }
    
    html += '</tbody></table>';
    
    // Best performers
    html += '<div class="best-performers">';
    html += '<h4>🏆 Best Performers</h4>';
    if (summary.best_completion_rate?.model) {
        html += `<p><strong>Completion Rate:</strong> ${summary.best_completion_rate.model} (${(summary.best_completion_rate.rate * 100).toFixed(1)}%)</p>`;
    }
    if (summary.best_confidence?.model) {
        html += `<p><strong>Confidence:</strong> ${summary.best_confidence.model} (${summary.best_confidence.confidence.toFixed(3)})</p>`;
    }
    if (summary.most_efficient?.model) {
        html += `<p><strong>Efficiency:</strong> ${summary.most_efficient.model} (${summary.most_efficient.steps.toFixed(1)} steps)</p>`;
    }
    if (summary.most_autonomous?.model) {
        html += `<p><strong>Autonomy:</strong> ${summary.most_autonomous.model} (${summary.most_autonomous.score.toFixed(3)})</p>`;
    }
    html += '</div>';
    
    html += '</div>';
    return html;
}

async function runEvaluation() {
    const maxQueries = document.getElementById('maxQueries').value;
    const delay = parseFloat(document.getElementById('evalDelay').value) || 1.0;
    const model = document.getElementById('evalModel').value.trim();
    const parallel = document.getElementById('evalParallel').checked;
    const maxWorkers = parseInt(document.getElementById('evalMaxWorkers').value) || 3;
    
    // Hide previous results/errors
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    
    // Show loading
    setEvaluationLoading(true);
    resetProgress();
    progressSection.classList.remove('hidden');
    progressSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    try {
        const requestBody = {
            delay: delay,
            save_individual: true,
            parallel: parallel,
            max_workers: maxWorkers
        };
        
        if (maxQueries && parseInt(maxQueries) > 0) {
            requestBody.max_queries = parseInt(maxQueries);
        }
        if (model) {
            requestBody.model = model;
        }
        
        const response = await fetch(`${API_BASE}/api/evaluate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Handle SSE
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let finalResult = null;
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        
                        if (data.type === 'error') {
                            throw new Error(data.message);
                        } else if (data.type === 'evaluation_progress') {
                            // Update progress
                            updateProgressStep('evaluating', {
                                status: 'started',
                                message: data.message,
                                query_number: data.query_number,
                                total_queries: data.total_queries
                            });
                        } else if (data.type === 'complete') {
                            finalResult = data.result;
                        }
                    } catch (e) {
                        if (e instanceof SyntaxError) {
                            continue;
                        }
                        throw e;
                    }
                }
            }
        }
        
        if (finalResult) {
            resultContent.innerHTML = formatEvaluationResult(finalResult);
            progressSection.classList.add('hidden');
            resultSection.classList.remove('hidden');
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            throw new Error('No result received');
        }
        
    } catch (error) {
        console.error('Error:', error);
        progressSection.classList.add('hidden');
        showError(error.message || 'An error occurred during evaluation.');
    } finally {
        setEvaluationLoading(false);
    }
}

async function compareModels() {
    const maxQueries = document.getElementById('compareMaxQueries').value;
    const delay = parseFloat(document.getElementById('compareDelay').value) || 1.0;
    const checked = document.querySelectorAll('#compareModelsContainer input[name="compareModel"]:checked');
    const selectedModels = Array.from(checked).map(function (c) { return c.value; });
    
    // Hide previous results/errors
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    
    // Show loading
    setCompareLoading(true);
    resetProgress();
    progressSection.classList.remove('hidden');
    progressSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    try {
        const requestBody = {
            delay: delay
        };
        
        if (maxQueries && parseInt(maxQueries) > 0) {
            requestBody.max_queries = parseInt(maxQueries);
        }
        if (selectedModels.length > 0) {
            requestBody.models = selectedModels;
        }
        
        const response = await fetch(`${API_BASE}/api/compare-models`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Handle SSE
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let finalResult = null;
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        
                        if (data.type === 'error') {
                            throw new Error(data.message);
                        } else if (data.type === 'comparison_start') {
                            updateProgressStep('evaluating', {
                                status: 'started',
                                message: `Comparing ${data.models.length} models on ${data.total_queries} queries...`
                            });
                        } else if (data.type === 'complete') {
                            finalResult = data.result;
                        }
                    } catch (e) {
                        if (e instanceof SyntaxError) {
                            continue;
                        }
                        throw e;
                    }
                }
            }
        }
        
        if (finalResult) {
            resultContent.innerHTML = formatComparisonResult(finalResult);
            progressSection.classList.add('hidden');
            resultSection.classList.remove('hidden');
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            throw new Error('No result received');
        }
        
    } catch (error) {
        console.error('Error:', error);
        progressSection.classList.add('hidden');
        showError(error.message || 'An error occurred during model comparison.');
    } finally {
        setCompareLoading(false);
    }
}

// Run health check and load evaluation models on page load
checkHealth();
loadEvaluationModels();
