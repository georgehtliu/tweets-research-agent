// Tweets pagination state (declare early for global access)
var currentTweetsPage = 1;
var tweetsPerPage = 20;
var totalTweets = 0;

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

// DOM elements (may be null on tweets page)
const queryInput = document.getElementById('queryInput');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');
const btnSpinner = document.getElementById('btnSpinner');
const resultSection = document.getElementById('resultSection');
const resultContent = document.getElementById('resultContent');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');

// Allow Enter key to submit (only if queryInput exists)
if (queryInput && submitBtn) {
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !submitBtn.disabled) {
            submitQuery();
        }
    });
}

function useExample(query) {
    if (queryInput) {
        queryInput.value = query;
        queryInput.focus();
    }
}

function setLoading(loading) {
    if (submitBtn) submitBtn.disabled = loading;
    if (queryInput) queryInput.disabled = loading;
    
    if (btnText && btnSpinner) {
        if (loading) {
            btnText.textContent = 'Processing...';
            btnSpinner.classList.remove('hidden');
        } else {
            btnText.textContent = 'Generate';
            btnSpinner.classList.add('hidden');
        }
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
        
        // Only wrap in <p> if line has content
        if (processedLine.trim()) {
            html += `<p>${processedLine}</p>\n`;
        }
    }
    
    // Close any remaining list
    if (inList) {
        html += listType === 'ol' ? '</ol>' : '</ul>';
    }
    
    return html;
}


async function submitQuery() {
    const query = queryInput.value.trim();
    
    if (!query) {
        showError('Please enter a query');
        return;
    }
    
    const selectedModels = getSelectedModels();
    const fastMode = document.getElementById('fastMode').checked;
    
    // Hide previous results/errors
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    
    // Show loading state
    setLoading(true);
    
    // Initialize logs container immediately for both single and comparison queries
    const logsEl = document.getElementById('modelLogs');
    if (logsEl) {
        logsEl.innerHTML = '<div class="log-info">Starting query...</div>';
    }
    
    // Show results container immediately with logs tab active
    const resultsContainer = document.getElementById('resultsTabsContainer');
    resultsContainer.classList.remove('hidden');
    switchResultsTab('logs');
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    try {
        let endpoint, body;
        
        if (selectedModels.length > 0) {
            // Use model comparison endpoint
            endpoint = `${API_BASE}/api/query/compare-models`;
            body = JSON.stringify({ 
                query: query, 
                models: selectedModels,
                fast_mode: fastMode 
            });
        } else {
            // Use single query endpoint
            endpoint = `${API_BASE}/api/query`;
            body = JSON.stringify({ query: query, fast_mode: fastMode });
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: body
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Handle Server-Sent Events
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let finalResult = null;
        let comparisonData = null;
        const modelResults = {};
        const modelLogs = {}; // model -> array of logs
        const singleQueryLogs = []; // For single query mode
        
        // Initialize progress tracking for comparison mode
        const modelProgress = {}; // model -> {current, total, status}
        if (selectedModels.length > 0) {
            selectedModels.forEach(model => {
                modelProgress[model] = { current: 0, total: 0, status: 'waiting' };
                modelLogs[model] = [];
            });
            // Show progress bars
            showModelProgressBars(selectedModels, modelProgress);
        }
        
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
                        } else if (data.type === 'comparison_start') {
                            // Initialize comparison tracking
                            comparisonData = { models: data.models, query: data.query, results: {} };
                            // Initialize logs for each model
                            data.models.forEach(model => {
                                modelLogs[model] = [];
                                if (!modelProgress[model]) {
                                    modelProgress[model] = { current: 0, total: 0, status: 'running' };
                                } else {
                                    modelProgress[model].status = 'running';
                                }
                            });
                            // Show progress bars
                            showModelProgressBars(data.models, modelProgress);
                            // Show logs tab and start streaming
                            if (selectedModels.length > 0) {
                                document.getElementById('resultsTabsContainer').classList.remove('hidden');
                                switchResultsTab('logs');
                            }
                        } else if (data.type === 'model_log') {
                            // Stream log in real-time
                            const log = data.log;
                            const model = log.model;
                            if (!modelLogs[model]) {
                                modelLogs[model] = [];
                            }
                            modelLogs[model].push(log);
                            // Store logs globally for carousel
                            window.currentModelLogs = modelLogs;
                            // Update progress based on log type
                            if (modelProgress[model]) {
                                const progressMap = {
                                    'planning': 1, 'executing': 2, 'analyzing': 3,
                                    'evaluating': 4, 'refining': 5, 'critiquing': 6, 'summarizing': 7
                                };
                                if (progressMap[log.type] !== undefined) {
                                    modelProgress[model].current = Math.max(modelProgress[model].current, progressMap[log.type]);
                                    modelProgress[model].total = 7;
                                }
                            }
                            // Update logs display immediately
                            updateModelLogsDisplay(modelLogs, selectedModels);
                            // Update progress bars
                            updateModelProgressBars(modelProgress);
                        } else if (data.type === 'model_complete') {
                            // Track model results
                            const model = data.model;
                            modelResults[model] = data.result || null;
                            if (data.status === 'error') {
                                modelResults[model] = { error: data.error };
                                if (modelProgress[model]) {
                                    modelProgress[model].status = 'error';
                                }
                            } else {
                                if (modelProgress[model]) {
                                    modelProgress[model].status = 'complete';
                                    modelProgress[model].current = modelProgress[model].total;
                                }
                            }
                            updateModelProgressBars(modelProgress);
                        } else if (data.type === 'comparison_complete') {
                            // Final comparison summary
                            comparisonData = data.summary;
                            // Merge real-time logs into summary
                            for (const [model, logs] of Object.entries(modelLogs)) {
                                if (comparisonData.results[model] && !comparisonData.results[model].error) {
                                    comparisonData.results[model].logs = logs;
                                }
                            }
                            displayComparisonResults(comparisonData);
                            switchResultsTab('summary');
                        } else if (!selectedModels.length && data.type) {
                            // Handle single query progress events
                            const logEntry = {
                                type: data.type,
                                message: data.message || data.summary || `${data.type}...`,
                                timestamp: data.timestamp || Date.now() / 1000,
                                model: 'default',
                                ...data
                            };
                            singleQueryLogs.push(logEntry);
                            
                            // Store in modelLogs format for consistent display
                            if (!modelLogs['default']) {
                                modelLogs['default'] = [];
                            }
                            modelLogs['default'].push(logEntry);
                            
                            // Display single query logs using the same display function
                            updateModelLogsDisplay(modelLogs, ['default']);
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
        
        if (selectedModels.length > 0 && comparisonData) {
            // Display comparison results - summary tab already shown
            displayComparisonResults(comparisonData);
            switchResultsTab('summary');
        } else if (finalResult) {
            // Display single result in summary tab
            const summaryEl = document.getElementById('comparisonSummary');
            if (summaryEl) {
                summaryEl.innerHTML = formatResult(finalResult);
            }
            switchResultsTab('summary');
        } else {
            throw new Error('No result received');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred while processing your query. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Global state for log carousel
let currentLogModelIndex = 0;
let logCarouselModels = [];

function showModelProgressBars(models, progress) {
    const progressContainer = document.getElementById('modelProgressBars');
    if (!progressContainer) {
        return;
    }
    
    // Show the container
    progressContainer.classList.remove('hidden');
    
    const container = progressContainer;
    let html = '<div class="model-progress-header"><h4>Model Progress</h4></div>';
    html += '<div class="model-progress-list">';
    
    models.forEach((model, idx) => {
        const prog = progress[model] || { current: 0, total: 0, status: 'waiting' };
        const percent = prog.total > 0 ? (prog.current / prog.total * 100) : 0;
        const statusClass = prog.status === 'complete' ? 'complete' : prog.status === 'error' ? 'error' : 'running';
        
        html += `<div class="model-progress-item ${statusClass}">`;
        html += `<div class="progress-model-name">${model}</div>`;
        html += `<div class="progress-bar-container">`;
        html += `<div class="progress-bar" style="width: ${percent}%"></div>`;
        html += `</div>`;
        html += `<div class="progress-status">${prog.status === 'complete' ? '✓ Complete' : prog.status === 'error' ? '✗ Error' : `${Math.round(percent)}%`}</div>`;
        html += `</div>`;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function updateModelProgressBars(progress) {
    const container = document.getElementById('modelProgressBars');
    if (!container) return;
    
    const items = container.querySelectorAll('.model-progress-item');
    items.forEach(item => {
        const modelName = item.querySelector('.progress-model-name').textContent;
        const prog = progress[modelName];
        if (prog) {
            const percent = prog.total > 0 ? (prog.current / prog.total * 100) : 0;
            const statusClass = prog.status === 'complete' ? 'complete' : prog.status === 'error' ? 'error' : 'running';
            item.className = `model-progress-item ${statusClass}`;
            const bar = item.querySelector('.progress-bar');
            if (bar) bar.style.width = `${percent}%`;
            const status = item.querySelector('.progress-status');
            if (status) {
                status.textContent = prog.status === 'complete' ? '✓ Complete' : prog.status === 'error' ? '✗ Error' : `${Math.round(percent)}%`;
            }
        }
    });
}

function updateModelLogsDisplay(modelLogs, models = null) {
    const logsEl = document.getElementById('modelLogs');
    if (!logsEl) return;
    
    // Update carousel models list
    if (models) {
        logCarouselModels = models.filter(m => modelLogs[m] && modelLogs[m].length > 0);
        if (logCarouselModels.length === 0) {
            logCarouselModels = Object.keys(modelLogs).filter(m => modelLogs[m] && modelLogs[m].length > 0);
        }
        if (currentLogModelIndex >= logCarouselModels.length) {
            currentLogModelIndex = 0;
        }
    } else {
        logCarouselModels = Object.keys(modelLogs).filter(m => modelLogs[m] && modelLogs[m].length > 0);
    }
    
    if (logCarouselModels.length === 0) {
        logsEl.innerHTML = '<div class="log-info">Waiting for logs...</div>';
        return;
    }
    
    const currentModel = logCarouselModels[currentLogModelIndex];
    const logs = modelLogs[currentModel] || [];
    
    // Carousel controls
    let html = '<div class="log-carousel">';
    html += '<div class="log-carousel-header">';
    html += '<button class="carousel-btn" onclick="switchLogModel(-1)" ' + (logCarouselModels.length <= 1 ? 'disabled' : '') + '>‹</button>';
    html += `<div class="carousel-title">${currentModel} <span class="carousel-counter">(${currentLogModelIndex + 1}/${logCarouselModels.length})</span></div>`;
    html += '<button class="carousel-btn" onclick="switchLogModel(1)" ' + (logCarouselModels.length <= 1 ? 'disabled' : '') + '>›</button>';
    html += '</div>';
    
    // Model tabs (quick switch)
    if (logCarouselModels.length > 1) {
        html += '<div class="log-model-tabs">';
        logCarouselModels.forEach((model, idx) => {
            html += `<button class="log-model-tab ${idx === currentLogModelIndex ? 'active' : ''}" onclick="switchLogModelTo(${idx})">${model}</button>`;
        });
        html += '</div>';
    }
    
    // Log entries for current model
    html += '<div class="log-entries-container">';
    if (logs.length === 0) {
        html += '<div class="log-info">No logs yet for this model</div>';
    } else {
        logs.forEach(log => {
            const logType = log.type || 'info';
            const timestamp = new Date((log.timestamp || Date.now() / 1000) * 1000);
            
            html += `<div class="log-entry log-${logType}">`;
            html += `<span class="log-time">${timestamp.toLocaleTimeString()}</span>`;
            html += `<span class="log-type">${logType}</span>`;
            
            // Extract and display key information
            let logMessage = '';
            const logData = {...log};
            delete logData.timestamp;
            delete logData.model;
            delete logData.type;
            
            // Handle tool calling information
            if (log.tool_calling_mode && log.tool_calls && log.tool_calls.length > 0) {
                logMessage += '<div class="log-tool-calls">';
                logMessage += '<div class="log-tool-header">🔧 Tools Used:</div>';
                log.tool_calls.forEach((toolCall, idx) => {
                    const successIcon = toolCall.success ? '✓' : '✗';
                    const successClass = toolCall.success ? 'tool-success' : 'tool-failed';
                    logMessage += `<div class="log-tool-item ${successClass}">`;
                    logMessage += `<span class="tool-icon">${successIcon}</span>`;
                    logMessage += `<span class="tool-name">${escapeHtml(toolCall.name)}</span>`;
                    if (toolCall.results_count !== undefined) {
                        logMessage += `<span class="tool-results">(${toolCall.results_count} results)</span>`;
                    }
                    if (toolCall.arguments && Object.keys(toolCall.arguments).length > 0) {
                        logMessage += `<div class="tool-args">Args: ${escapeHtml(JSON.stringify(toolCall.arguments, null, 2))}</div>`;
                    }
                    if (toolCall.message) {
                        logMessage += `<div class="tool-message">${escapeHtml(toolCall.message)}</div>`;
                    }
                    logMessage += '</div>';
                });
                logMessage += '</div>';
            }
            
            // Handle current tool being executed
            if (log.current_tool) {
                logMessage += '<div class="log-current-tool">';
                logMessage += `🔧 Executing: <strong>${escapeHtml(log.current_tool.name)}</strong>`;
                if (log.current_tool.arguments) {
                    logMessage += ` with args: ${escapeHtml(JSON.stringify(log.current_tool.arguments))}`;
                }
                logMessage += '</div>';
            }
            
            // Display message if present
            if (log.message) {
                logMessage += `<div class="log-main-message">${escapeHtml(log.message)}</div>`;
            }
            
            // Display summary if present
            if (log.summary) {
                logMessage += `<div class="log-summary">${escapeHtml(log.summary)}</div>`;
            }
            
            // Display other data as formatted JSON
            const remainingData = {};
            const skipKeys = ['tool_calling_mode', 'tool_calls', 'current_tool', 'message', 'summary', 'status'];
            for (const [key, value] of Object.entries(logData)) {
                if (!skipKeys.includes(key) && value !== undefined && value !== null) {
                    remainingData[key] = value;
                }
            }
            
            if (Object.keys(remainingData).length > 0) {
                logMessage += `<div class="log-extra-data"><pre>${escapeHtml(JSON.stringify(remainingData, null, 2))}</pre></div>`;
            }
            
            if (!logMessage) {
                logMessage = '<span class="log-empty">No additional data</span>';
            }
            
            html += `<div class="log-message">${logMessage}</div>`;
            html += `</div>`;
        });
    }
    html += '</div>';
    html += '</div>';
    
    logsEl.innerHTML = html;
    // Auto-scroll to bottom
    const entriesContainer = logsEl.querySelector('.log-entries-container');
    if (entriesContainer) {
        entriesContainer.scrollTop = entriesContainer.scrollHeight;
    }
}

function switchLogModel(direction) {
    if (logCarouselModels.length <= 1) return;
    currentLogModelIndex = (currentLogModelIndex + direction + logCarouselModels.length) % logCarouselModels.length;
    // Re-render with current model logs
    const logsEl = document.getElementById('modelLogs');
    if (logsEl) {
        // Get logs from the stored state (we'll need to maintain this)
        const allLogs = window.currentModelLogs || {};
        updateModelLogsDisplay(allLogs);
    }
}

function switchLogModelTo(index) {
    if (index >= 0 && index < logCarouselModels.length) {
        currentLogModelIndex = index;
        const allLogs = window.currentModelLogs || {};
        updateModelLogsDisplay(allLogs);
    }
}

function displayComparisonResults(summary) {
    const summaryEl = document.getElementById('comparisonSummary');
    const logsEl = document.getElementById('modelLogs');
    
    let summaryHtml = '<div class="comparison-header">';
    summaryHtml += `<h3>Comparison Results</h3>`;
    summaryHtml += `<p class="comparison-query">Query: "${summary.query}"</p>`;
    summaryHtml += '</div>';
    
    // Summary metrics
    if (summary.summary && Object.keys(summary.summary).length > 0) {
        summaryHtml += '<div class="comparison-best">';
        summaryHtml += '<h4>🏆 Best Performers</h4>';
        if (summary.summary.best_confidence) {
            summaryHtml += `<p><strong>Highest Confidence:</strong> ${summary.summary.best_confidence.model} (${(summary.summary.best_confidence.value * 100).toFixed(1)}%)</p>`;
        }
        if (summary.summary.most_efficient) {
            summaryHtml += `<p><strong>Most Efficient:</strong> ${summary.summary.most_efficient.model} (${summary.summary.most_efficient.value} steps)</p>`;
        }
        summaryHtml += '</div>';
    }
    
    // Results table
    summaryHtml += '<div class="comparison-table-container">';
    summaryHtml += '<table class="comparison-table">';
    summaryHtml += '<thead><tr><th>Model</th><th>Status</th><th>Confidence</th><th>Steps</th><th>Replans</th></tr></thead>';
    summaryHtml += '<tbody>';
    
    for (const [model, result] of Object.entries(summary.results)) {
        if (result.error) {
            summaryHtml += `<tr><td>${model}</td><td class="error">Error</td><td>-</td><td>-</td><td>-</td></tr>`;
        } else {
            const conf = (result.confidence * 100).toFixed(1);
            summaryHtml += `<tr>
                <td>${model}</td>
                <td class="success">✓ Success</td>
                <td>${conf}%</td>
                <td>${result.execution_steps}</td>
                <td>${result.replan_count}</td>
            </tr>`;
        }
    }
    
    summaryHtml += '</tbody></table></div>';
    
    // Model summaries
    summaryHtml += '<div class="model-summaries">';
    for (const [model, result] of Object.entries(summary.results)) {
        if (!result.error && result.summary) {
            summaryHtml += `<div class="model-summary-card">`;
            summaryHtml += `<h4>${model}</h4>`;
            const summaryText = result.summary || '';
            const markdownHtml = convertMarkdownToHtml(summaryText);
            summaryHtml += `<div class="model-summary-text">${markdownHtml}</div>`;
            summaryHtml += `</div>`;
        }
    }
    summaryHtml += '</div>';
    
    summaryEl.innerHTML = summaryHtml;
    
    // Logs - use carousel display
    window.currentModelLogs = {};
    for (const [model, result] of Object.entries(summary.results)) {
        if (result.logs && result.logs.length > 0) {
            window.currentModelLogs[model] = result.logs;
        }
    }
    updateModelLogsDisplay(window.currentModelLogs, summary.models || Object.keys(summary.results));
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

// Model metadata
const MODEL_INFO = {
    "grok-4-fast-reasoning": {
        name: "grok-4-fast-reasoning",
        description: "Fast reasoning, large context",
        context: "2M tokens",
        pricing: "$0.20/$0.50",
        tpm: "4M tpm",
        badge: "Recommended"
    },
    "grok-4-0709": {
        name: "grok-4-0709",
        description: "Higher quality reasoning",
        context: "256K tokens",
        pricing: "$3.00/$15.00",
        tpm: "2M tpm",
        badge: "Premium"
    },
    "grok-3-mini": {
        name: "grok-3-mini",
        description: "Budget-friendly option",
        context: "131K tokens",
        pricing: "$0.30/$0.50",
        tpm: "480 rpm",
        badge: "Budget"
    }
};

// Load available models on page load
let modelsLoaded = false;
async function loadModels() {
    if (modelsLoaded) return;
    const containerEl = document.getElementById('modelCheckboxes');
    if (!containerEl) {
        console.warn('modelCheckboxes element not found');
        return;
    }
    
    // Show loading state
    containerEl.innerHTML = '<div style="color: #94a3b8; padding: 20px; text-align: center;">Loading models...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/evaluation/models`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        const models = data.models || [];
        
        if (models.length === 0) {
            containerEl.innerHTML = '<div style="color: #f87171; padding: 20px; text-align: center;">No models available</div>';
            return;
        }
        
        modelsLoaded = true;
        console.log('Loaded models:', models);

        // Populate model checkboxes with enhanced info
        containerEl.innerHTML = '';
        models.forEach(function (modelName) {
            const info = MODEL_INFO[modelName] || {
                name: modelName,
                description: "Available model",
                context: "",
                pricing: "",
                tpm: "",
                badge: ""
            };
            
            const card = document.createElement('div');
            card.className = 'model-card';
            
            const label = document.createElement('label');
            label.className = 'model-checkbox-label';
            
            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.name = 'model';
            cb.value = modelName;
            label.appendChild(cb);
            
            const content = document.createElement('div');
            content.className = 'model-card-content';
            
            const header = document.createElement('div');
            header.className = 'model-card-header';
            
            const nameSpan = document.createElement('span');
            nameSpan.className = 'model-name';
            nameSpan.textContent = info.name;
            header.appendChild(nameSpan);
            
            if (info.badge) {
                const badge = document.createElement('span');
                badge.className = `model-badge model-badge-${info.badge.toLowerCase()}`;
                badge.textContent = info.badge;
                header.appendChild(badge);
            }
            
            content.appendChild(header);
            
            const desc = document.createElement('div');
            desc.className = 'model-description';
            desc.textContent = info.description;
            content.appendChild(desc);
            
            const details = document.createElement('div');
            details.className = 'model-details';
            
            if (info.context) {
                const ctx = document.createElement('span');
                ctx.className = 'model-detail-item';
                ctx.innerHTML = `<span class="detail-icon">📄</span> ${info.context}`;
                details.appendChild(ctx);
            }
            
            if (info.pricing) {
                const price = document.createElement('span');
                price.className = 'model-detail-item';
                price.innerHTML = `<span class="detail-icon">💰</span> ${info.pricing}`;
                details.appendChild(price);
            }
            
            if (info.tpm) {
                const speed = document.createElement('span');
                speed.className = 'model-detail-item';
                speed.innerHTML = `<span class="detail-icon">⚡</span> ${info.tpm}`;
                details.appendChild(speed);
            }
            
            content.appendChild(details);
            label.appendChild(content);
            card.appendChild(label);
            containerEl.appendChild(card);
            
            // Add change listener to update card styling
            cb.addEventListener('change', function() {
                if (this.checked) {
                    card.classList.add('selected');
                } else {
                    card.classList.remove('selected');
                }
            });
        });
        
        console.log(`✅ Loaded ${models.length} model(s)`);
    } catch (e) {
        console.error('❌ Could not load models from API:', e);
        // Fallback: use models from MODEL_INFO
        const fallbackModels = Object.keys(MODEL_INFO);
        if (fallbackModels.length > 0) {
            console.log('Using fallback models:', fallbackModels);
            modelsLoaded = true;
            containerEl.innerHTML = '';
            fallbackModels.forEach(function (modelName) {
                const info = MODEL_INFO[modelName];
                if (!info) return;
                
                const card = document.createElement('div');
                card.className = 'model-card';
                
                const label = document.createElement('label');
                label.className = 'model-checkbox-label';
                
                const cb = document.createElement('input');
                cb.type = 'checkbox';
                cb.name = 'model';
                cb.value = modelName;
                label.appendChild(cb);
                
                const content = document.createElement('div');
                content.className = 'model-card-content';
                
                const header = document.createElement('div');
                header.className = 'model-card-header';
                
                const nameSpan = document.createElement('span');
                nameSpan.className = 'model-name';
                nameSpan.textContent = info.name;
                header.appendChild(nameSpan);
                
                if (info.badge) {
                    const badge = document.createElement('span');
                    badge.className = `model-badge model-badge-${info.badge.toLowerCase()}`;
                    badge.textContent = info.badge;
                    header.appendChild(badge);
                }
                
                content.appendChild(header);
                
                const desc = document.createElement('div');
                desc.className = 'model-description';
                desc.textContent = info.description;
                content.appendChild(desc);
                
                const details = document.createElement('div');
                details.className = 'model-details';
                
                if (info.context) {
                    const ctx = document.createElement('span');
                    ctx.className = 'model-detail-item';
                    ctx.innerHTML = `<span class="detail-icon">📄</span> ${info.context}`;
                    details.appendChild(ctx);
                }
                
                if (info.pricing) {
                    const price = document.createElement('span');
                    price.className = 'model-detail-item';
                    price.innerHTML = `<span class="detail-icon">💰</span> ${info.pricing}`;
                    details.appendChild(price);
                }
                
                if (info.tpm) {
                    const speed = document.createElement('span');
                    speed.className = 'model-detail-item';
                    speed.innerHTML = `<span class="detail-icon">⚡</span> ${info.tpm}`;
                    details.appendChild(speed);
                }
                
                content.appendChild(details);
                label.appendChild(content);
                card.appendChild(label);
                containerEl.appendChild(card);
                
                // Add change listener
                cb.addEventListener('change', function() {
                    if (this.checked) {
                        card.classList.add('selected');
                    } else {
                        card.classList.remove('selected');
                    }
                });
            });
            console.log(`✅ Loaded ${fallbackModels.length} fallback model(s)`);
        } else {
            containerEl.innerHTML = `<div style="color: #f87171; padding: 20px; text-align: center;">
                <p>Failed to load models</p>
                <p style="font-size: 12px; margin-top: 8px;">${escapeHtml(e.message)}</p>
                <button onclick="loadModels()" style="margin-top: 12px; padding: 8px 16px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer;">Retry</button>
            </div>`;
        }
    }
}

function toggleModelSelection(checked) {
    const inputs = document.querySelectorAll('#modelCheckboxes input[name="model"]');
    inputs.forEach(function (c) { 
        c.checked = !!checked;
        // Trigger visual update
        const card = c.closest('.model-card');
        if (card) {
            if (checked) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        }
    });
}

function getSelectedModels() {
    const inputs = document.querySelectorAll('#modelCheckboxes input[name="model"]:checked');
    return Array.from(inputs).map(cb => cb.value);
}

// Results tab switching (Summary / Logs only; Tweets is a standalone section)
function switchResultsTab(tabName) {
    const summaryTab = document.getElementById('summaryTab');
    const logsTab = document.getElementById('logsTab');
    const summaryContent = document.getElementById('summaryTabContent');
    const logsContent = document.getElementById('logsTabContent');
    
    [summaryTab, logsTab].forEach(tab => tab?.classList.remove('active'));
    [summaryContent, logsContent].forEach(content => content?.classList.add('hidden'));
    
    if (tabName === 'summary') {
        summaryTab?.classList.add('active');
        summaryContent?.classList.remove('hidden');
    } else if (tabName === 'logs') {
        logsTab?.classList.add('active');
        logsContent?.classList.remove('hidden');
    }
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
            resultSection.classList.remove('hidden');
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            throw new Error('No result received');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred during model comparison.');
    } finally {
        setCompareLoading(false);
    }
}

// Tweets functions
async function loadTweets(resetPage = false) {
    const tweetsList = document.getElementById('tweetsList');
    if (!tweetsList) {
        console.error('tweetsList element not found');
        return;
    }
    
    if (resetPage) {
        currentTweetsPage = 1;
    }
    
    const category = document.getElementById('tweetsCategoryFilter')?.value || '';
    const language = document.getElementById('tweetsLanguageFilter')?.value || '';
    
    tweetsList.innerHTML = '<div class="tweets-loading">Loading tweets...</div>';
    
    try {
        // Ensure API_BASE is defined
        if (typeof API_BASE === 'undefined') {
            const apiBase = getApiBase();
            window.API_BASE = apiBase;
        }
        
        const params = new URLSearchParams({
            page: currentTweetsPage.toString(),
            per_page: tweetsPerPage.toString()
        });
        if (category) params.append('category', category);
        if (language) params.append('language', language);
        
        const apiUrl = `${typeof API_BASE !== 'undefined' ? API_BASE : getApiBase()}/api/tweets?${params}`;
        console.log('Loading tweets from:', apiUrl);
        
        const response = await fetch(apiUrl);
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Tweets API error:', response.status, errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Tweets loaded:', data.tweets.length, 'tweets');
        totalTweets = data.pagination.total;
        
        // Render tweets
        if (data.tweets.length === 0) {
            tweetsList.innerHTML = '<div class="tweets-empty">No tweets found</div>';
        } else {
            let html = '';
            data.tweets.forEach(tweet => {
                const author = tweet.author || {};
                const engagement = tweet.engagement || {};
                const totalEngagement = (engagement.likes || 0) + (engagement.retweets || 0) + (engagement.replies || 0);
                const date = new Date(tweet.created_at).toLocaleDateString();
                
                html += '<div class="tweet-card">';
                html += '<div class="tweet-header">';
                html += `<div class="tweet-author">`;
                if (author.verified) {
                    html += '<span class="verified-badge">✓</span>';
                }
                html += `<span class="author-name">${escapeHtml(author.display_name || 'Unknown')}</span>`;
                html += `<span class="author-handle">@${escapeHtml(author.username || 'unknown')}</span>`;
                html += `</div>`;
                html += `<div class="tweet-date">${date}</div>`;
                html += '</div>';
                
                html += `<div class="tweet-text">${escapeHtml(tweet.text)}</div>`;
                
                if (tweet.topics && tweet.topics.length > 0) {
                    html += '<div class="tweet-topics">';
                    tweet.topics.forEach(topic => {
                        html += `<span class="topic-tag">${escapeHtml(topic)}</span>`;
                    });
                    html += '</div>';
                }
                
                html += '<div class="tweet-footer">';
                html += `<div class="tweet-meta">`;
                if (tweet.category) {
                    html += `<span class="meta-item category-${tweet.category}">${tweet.category}</span>`;
                }
                if (tweet.language && tweet.language !== 'en') {
                    html += `<span class="meta-item">${tweet.language.toUpperCase()}</span>`;
                }
                html += `</div>`;
                html += `<div class="tweet-engagement">`;
                html += `<span class="engagement-item">❤️ ${engagement.likes || 0}</span>`;
                html += `<span class="engagement-item">🔄 ${engagement.retweets || 0}</span>`;
                html += `<span class="engagement-item">💬 ${engagement.replies || 0}</span>`;
                html += `</div>`;
                html += '</div>';
                html += '</div>';
            });
            tweetsList.innerHTML = html;
        }
        
        // Update pagination controls
        updateTweetsPagination(data.pagination);
        
    } catch (error) {
        console.error('Error loading tweets:', error);
        const errorMsg = error.message || 'Unknown error';
        tweetsList.innerHTML = `<div class="tweets-error">Error loading tweets: ${escapeHtml(errorMsg)}<br><small>Check browser console for details</small></div>`;
    }
}

function updateTweetsPagination(pagination) {
    const prevBtn = document.getElementById('tweetsPrevBtn');
    const nextBtn = document.getElementById('tweetsNextBtn');
    const pageInfo = document.getElementById('tweetsPageInfo');
    
    if (prevBtn) {
        prevBtn.disabled = !pagination.has_prev;
    }
    if (nextBtn) {
        nextBtn.disabled = !pagination.has_next;
    }
    if (pageInfo) {
        pageInfo.textContent = `Page ${pagination.page} of ${pagination.total_pages} (${pagination.total} total)`;
    }
}

function changeTweetsPage(direction) {
    const newPage = currentTweetsPage + direction;
    if (newPage < 1) return;
    
    currentTweetsPage = newPage;
    loadTweets();
    const el = document.getElementById('tweetsSection') || document.getElementById('tweetsList');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Run health check and load models on page load (only on main page)
if (document.getElementById('queryInput')) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            checkHealth();
            loadModels();
        });
    } else {
        checkHealth();
        loadModels();
    }
}
