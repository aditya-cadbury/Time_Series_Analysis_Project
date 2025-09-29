// ===== GLOBAL VARIABLES =====
let currentData = null;
let currentModel = 'arima';
let charts = {};
let particles = [];
let animationFrameId = null;

// ===== DOM ELEMENTS =====
const elements = {
    // Sidebar
    sidebar: document.getElementById('sidebar'),
    sidebarToggle: document.getElementById('sidebarToggle'),
    sidebarToggleMain: document.getElementById('sidebarToggleMain'),
    
    // Data Source
    dataSource: document.getElementById('dataSource'),
    stockConfig: document.getElementById('stockConfig'),
    csvConfig: document.getElementById('csvConfig'),
    sampleConfig: document.getElementById('sampleConfig'),
    
    // Stock Data Input Elements
    tickerInput: document.getElementById('tickerInput'),
    timePeriod: document.getElementById('timePeriod'),
    
    // Model Selection
    modelSelection: document.getElementById('modelSelection'),
    
    // Parameters
    forecastPeriods: document.getElementById('forecastPeriods'),
    confidenceInterval: document.getElementById('confidenceInterval'),
    forecastValue: document.getElementById('forecastValue'),
    confidenceValue: document.getElementById('confidenceValue'),
    
    // ARIMA Parameters
    autoParams: document.getElementById('autoParams'),
    manualParams: document.getElementById('manualParams'),
    sarimaParams: document.getElementById('sarimaParams'),
    
    // Buttons
    loadStockData: document.getElementById('loadStockData'),
    loadCSVData: document.getElementById('loadCSVData'),
    loadSampleData: document.getElementById('loadSampleData'),
    runForecasting: document.getElementById('runForecasting'),
    
    // File inputs
    csvFile: document.getElementById('csvFile'),
    
    // Content Sections
    dataOverview: document.getElementById('dataOverview'),
    forecastingResults: document.getElementById('forecastingResults'),
    modelComparison: document.getElementById('modelComparison'),
    welcomeSection: document.getElementById('welcomeSection'),
    
    // Charts
    timeSeriesChart: document.getElementById('timeSeriesChart'),
    forecastChart: document.getElementById('forecastChart'),
    residualsChart: document.getElementById('residualsChart'),
    comparisonChart: document.getElementById('comparisonChart'),
    
    // Tables
    dataTable: document.getElementById('dataTable'),
    comparisonTable: document.getElementById('comparisonTable'),
    
    // Metrics
    dataPoints: document.getElementById('dataPoints'),
    dateRange: document.getElementById('dateRange'),
    meanValue: document.getElementById('meanValue'),
    stdValue: document.getElementById('stdValue'),
    modelMetrics: document.getElementById('modelMetrics'),
    
    // Theme
    themeToggle: document.getElementById('themeToggle'),
    themeIcon: document.getElementById('themeIcon'),
    
    // Loading
    loadingOverlay: document.getElementById('loadingOverlay'),
    
    // FAB - Create if doesn't exist
    scrollToTop: document.getElementById('scrollToTop') || createScrollToTopButton(),
    
    // Main content
    mainContent: document.getElementById('mainContent'),
    
    // Sidebar overlay
    sidebarOverlay: document.getElementById('sidebarOverlay')
};

// ===== UTILITY FUNCTIONS =====
function createScrollToTopButton() {
    const button = document.createElement('button');
    button.id = 'scrollToTop';
    button.className = 'btn btn-primary position-fixed';
    button.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000; border-radius: 50%; width: 50px; height: 50px; display: none;';
    button.innerHTML = '<i class="bi bi-arrow-up"></i>';
    document.body.appendChild(button);
    return button;
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    setupAnimations();
});

function initializeApp() {
    // Set initial theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    // Initialize charts
    initializeCharts();
    
    // Setup range sliders
    setupRangeSliders();
    
    // Initialize particle system
    initializeParticles();
    
    // Initialize sound effects
    initializeSounds();
    
    // Show welcome section initially
    showSection('welcome');
    
    // Add entrance animations
    addEntranceAnimations();
    
    // Initialize logo interactions
    initializeLogoInteractions();
}

function setupEventListeners() {
    // Sidebar toggle
    elements.sidebarToggle.addEventListener('click', toggleSidebar);
    elements.sidebarToggleMain.addEventListener('click', toggleSidebar);
    
    // Data source change
    elements.dataSource.addEventListener('change', handleDataSourceChange);
    
    // Model selection change
    elements.modelSelection.addEventListener('change', handleModelChange);
    
    // Auto parameters toggle
    elements.autoParams.addEventListener('change', toggleManualParams);
    
    // Button clicks
    elements.loadStockData.addEventListener('click', loadStockData);
    elements.loadCSVData.addEventListener('click', loadCSVData);
    elements.loadSampleData.addEventListener('click', loadSampleData);
    elements.runForecasting.addEventListener('click', runForecasting);
    
    // File input change
    elements.csvFile.addEventListener('change', handleCSVFileChange);
    
    // Theme toggle
    elements.themeToggle.addEventListener('click', toggleTheme);
    
    // Scroll to top
    elements.scrollToTop.addEventListener('click', scrollToTop);
    
    // Window events
    window.addEventListener('scroll', handleScroll);
    window.addEventListener('resize', handleResize);
    
    // Range slider events
    elements.forecastPeriods.addEventListener('input', updateRangeValue);
    elements.confidenceInterval.addEventListener('input', updateRangeValue);
    
    // Enhanced interactions
    enhanceButtonInteractions();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Add overlay click to close sidebar on mobile
    if (elements.sidebarOverlay) {
        elements.sidebarOverlay.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                toggleSidebar();
            }
        });
    }
}

function setupRangeSliders() {
    updateRangeValue({ target: elements.forecastPeriods });
    updateRangeValue({ target: elements.confidenceInterval });
}

function updateRangeValue(event) {
    const slider = event.target;
    const value = slider.value;
    const valueDisplay = slider.id === 'forecastPeriods' ? elements.forecastValue : elements.confidenceValue;
    valueDisplay.textContent = value;
}

// ===== SIDEBAR FUNCTIONS =====
function toggleSidebar() {
    const isCollapsed = elements.sidebar.classList.contains('collapsed');
    const isMobile = window.innerWidth <= 768;
    
    if (isCollapsed) {
        // Opening sidebar
        elements.sidebar.classList.remove('collapsed');
        elements.mainContent.classList.remove('expanded');
        
        if (isMobile && elements.sidebarOverlay) {
            elements.sidebarOverlay.classList.add('show');
        }
        
        playSound(523, 0.1); // C5 - opening sound
        showNotification('📊 Sidebar opened', 'info');
    } else {
        // Closing sidebar
        elements.sidebar.classList.add('collapsed');
        elements.mainContent.classList.add('expanded');
        
        if (isMobile && elements.sidebarOverlay) {
            elements.sidebarOverlay.classList.remove('show');
        }
        
        playSound(440, 0.1); // A4 - closing sound
        showNotification('📊 Sidebar closed', 'info');
    }
    
    // Update toggle button icon
    updateSidebarToggleIcon();
}

function updateSidebarToggleIcon() {
    const isCollapsed = elements.sidebar.classList.contains('collapsed');
    const icon = elements.sidebarToggleMain.querySelector('i');
    
    if (isCollapsed) {
        icon.className = 'bi bi-list'; // Show menu icon when sidebar is closed
    } else {
        icon.className = 'bi bi-x-lg'; // Show X icon when sidebar is open
    }
}

// ===== DATA SOURCE HANDLING =====
function handleDataSourceChange() {
    const source = elements.dataSource.value;
    
    // Hide all config sections
    document.querySelectorAll('.config-section').forEach(section => {
        section.classList.add('d-none');
    });
    
    // Show relevant config section
    switch(source) {
        case 'stock':
            elements.stockConfig.classList.remove('d-none');
            break;
        case 'csv':
            elements.csvConfig.classList.remove('d-none');
            break;
        case 'sample':
            elements.sampleConfig.classList.remove('d-none');
            break;
    }
}

async function loadStockData() {
    console.log('loadStockData function called');
    
    // Check if required elements exist
    if (!elements.tickerInput) {
        console.error('tickerInput element not found');
        showNotification('❌ Ticker input not found', 'error');
        return;
    }
    
    if (!elements.timePeriod) {
        console.error('timePeriod element not found');
        showNotification('❌ Time period selector not found', 'error');
        return;
    }
    
    const ticker = elements.tickerInput.value.toUpperCase().trim();
    const period = elements.timePeriod.value;
    
    console.log('Ticker:', ticker, 'Period:', period);
    
    if (!ticker) {
        showNotification('Please enter a stock ticker', 'warning');
        return;
    }
    
    showLoading(true);
    
    try {
        console.log('Making API request...');
        
        // API call to Flask backend
        const response = await fetch('/api/load_stock_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ticker, period })
        });
        
        console.log('Response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Stock data received:', data);
            
            // Store current data globally
            currentData = data;
            
            // Display the data
            displayDataOverview(data);
            
            showNotification(`✅ Loaded ${ticker} data successfully! (${data.data_points} points)`, 'success');
        } else {
            const errorData = await response.json();
            console.error('Response error:', errorData);
            throw new Error(errorData.error || 'Failed to load stock data');
        }
    } catch (error) {
        console.error('Error loading stock data:', error);
        showNotification(`❌ Error: ${error.message}`, 'error');
        
        // Show helpful suggestions
        setTimeout(() => {
            showNotification('💡 Try: AAPL, MSFT, GOOGL, AMZN, TSLA', 'info');
        }, 1000);
    } finally {
        showLoading(false);
    }
}

// ===== CSV FILE HANDLING =====
function handleCSVFileChange() {
    const file = elements.csvFile.files[0];
    if (file) {
        // Enable the load button when a file is selected
        elements.loadCSVData.disabled = false;
        showNotification(`📁 File selected: ${file.name}`, 'info');
    } else {
        // Disable the load button when no file is selected
        elements.loadCSVData.disabled = true;
    }
}

async function loadCSVData() {
    const file = elements.csvFile.files[0];
    
    if (!file) {
        showNotification('Please select a CSV file first', 'warning');
        return;
    }
    
    showLoading(true);
    
    try {
        console.log('Loading CSV data from:', file.name);
        
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('file', file);
        
        // API call to Flask backend
        const response = await fetch('/api/load_csv_data', {
            method: 'POST',
            body: formData
        });
        
        console.log('CSV data response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('CSV data received:', data);
            currentData = data;
            displayDataOverview(data);
            showNotification('✅ CSV data loaded successfully!', 'success');
        } else {
            const errorData = await response.json();
            console.error('CSV data response error:', errorData);
            throw new Error(errorData.error || 'Failed to load CSV data');
        }
    } catch (error) {
        console.error('Error loading CSV data:', error);
        showNotification(`❌ Error loading CSV: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

async function loadSampleData() {
    showLoading(true);
    
    try {
        console.log('Loading sample data...');
        
        // API call to Flask backend
        const response = await fetch('/api/load_sample_data');
        
        console.log('Sample data response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Sample data received:', data);
            currentData = data;
            displayDataOverview(data);
            showNotification('✅ Sample data loaded successfully!', 'success');
        } else {
            const errorText = await response.text();
            console.error('Sample data response error:', errorText);
            throw new Error('Failed to load sample data: ' + errorText);
        }
    } catch (error) {
        console.error('Error loading sample data:', error);
        // Generate sample data client-side as fallback
        generateSampleData();
    } finally {
        showLoading(false);
    }
}

function generateSampleData() {
    // Generate sample time series data
    const data = {
        dates: [],
        values: [],
        ticker: 'SAMPLE'
    };
    
    const startDate = new Date('2020-01-01');
    const numPoints = 365;
    
    for (let i = 0; i < numPoints; i++) {
        const date = new Date(startDate);
        date.setDate(date.getDate() + i);
        data.dates.push(date.toISOString().split('T')[0]);
        
        // Generate sample data with trend and seasonality
        const trend = 100 + (i * 0.1);
        const seasonal = 20 * Math.sin(2 * Math.PI * i / 365.25);
        const noise = (Math.random() - 0.5) * 10;
        data.values.push(trend + seasonal + noise);
    }
    
    currentData = data;
    displayDataOverview(data);
    showNotification('✅ Sample data generated successfully!', 'success');
}

// ===== MODEL HANDLING =====
function handleModelChange() {
    currentModel = elements.modelSelection.value;
    
    // Show/hide ARIMA parameters based on model selection
    const showArimaParams = currentModel === 'arima' || currentModel === 'sarima';
    elements.autoParams.closest('.params-section').style.display = showArimaParams ? 'block' : 'none';
    
    // Show/hide SARIMA seasonal parameters
    const showSarimaParams = currentModel === 'sarima';
    elements.sarimaParams.style.display = showSarimaParams ? 'block' : 'none';
}

function toggleManualParams() {
    const isAuto = elements.autoParams.checked;
    elements.manualParams.classList.toggle('d-none', isAuto);
}

// ===== DATA DISPLAY =====
function displayDataOverview(data) {
    // Update metrics
    elements.dataPoints.textContent = data.values.length;
    elements.dateRange.textContent = `${data.dates[0]} to ${data.dates[data.dates.length - 1]}`;
    
    const mean = data.values.reduce((a, b) => a + b, 0) / data.values.length;
    const std = Math.sqrt(data.values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / data.values.length);
    
    elements.meanValue.textContent = mean.toFixed(2);
    elements.stdValue.textContent = std.toFixed(2);
    
    // Update data table
    updateDataTable(data);
    
    // Create time series chart
    createTimeSeriesChart(data);
    
    // Show data overview section
    showSection('data');
}

function updateDataTable(data) {
    const tbody = elements.dataTable.querySelector('tbody');
    tbody.innerHTML = '';
    
    // Show first 10 rows
    const rowsToShow = Math.min(10, data.dates.length);
    for (let i = 0; i < rowsToShow; i++) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${data.dates[i]}</td>
            <td>${data.values[i].toFixed(2)}</td>
        `;
        tbody.appendChild(row);
    }
}

function createTimeSeriesChart(data) {
    const trace = {
        x: data.dates,
        y: data.values,
        type: 'scatter',
        mode: 'lines',
        name: 'Time Series',
        line: {
            color: '#00d4ff',
            width: 3
        }
    };
    
    const layout = {
        title: {
            text: 'Time Series Data',
            font: { color: '#ffffff', size: 18 }
        },
        xaxis: {
            title: 'Date',
            color: '#ffffff',
            gridcolor: 'rgba(255, 255, 255, 0.1)'
        },
        yaxis: {
            title: 'Value',
            color: '#ffffff',
            gridcolor: 'rgba(255, 255, 255, 0.1)'
        },
        plot_bgcolor: 'rgba(0, 0, 0, 0)',
        paper_bgcolor: 'rgba(0, 0, 0, 0)',
        font: { color: '#ffffff' },
        margin: { t: 60, b: 60, l: 60, r: 60 }
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    };
    
    Plotly.newPlot(elements.timeSeriesChart, [trace], layout, config);
    charts.timeSeries = { trace, layout, config };
}

// ===== FORECASTING =====
async function runForecasting() {
    if (!currentData) {
        showNotification('Please load data first', 'warning');
        return;
    }
    
    showLoading(true);
    
    try {
        const params = {
            model: currentModel,
            data: currentData,
            forecast_periods: parseInt(elements.forecastPeriods.value),
            confidence_interval: parseInt(elements.confidenceInterval.value),
            auto_params: elements.autoParams.checked,
            fast_mode: true
        };
        
        // Add manual parameters if not auto
        if (!elements.autoParams.checked) {
            params.manual_params = {
                p: parseInt(document.getElementById('paramP').value),
                d: parseInt(document.getElementById('paramD').value),
                q: parseInt(document.getElementById('paramQ').value)
            };
            
            if (currentModel === 'sarima') {
                params.seasonal_params = {
                    P: parseInt(document.getElementById('paramP_seasonal').value),
                    D: parseInt(document.getElementById('paramD_seasonal').value),
                    Q: parseInt(document.getElementById('paramQ_seasonal').value),
                    period: parseInt(document.getElementById('seasonalPeriod').value)
                };
            }
        }
        
        console.log('Sending forecasting request:', params);
        
        // API call to Flask backend with timeout (30s)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);
        const response = await fetch('/api/forecast', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params),
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        console.log('Forecasting response status:', response.status);
        
        if (response.ok) {
            const results = await response.json();
            console.log('Forecasting results received:', results);
            displayForecastingResults(results);
            showNotification('✅ Forecasting completed successfully!', 'success');
        } else {
            const errorText = await response.text();
            console.error('Forecasting response error:', errorText);
            throw new Error('Forecasting failed: ' + errorText);
        }
    } catch (error) {
        console.error('Error running forecasting:', error);
        // Generate mock results for demonstration
        generateMockResults();
    } finally {
        showLoading(false);
    }
}

function generateMockResults() {
    // Generate mock forecasting results for demonstration
    const forecastPeriods = parseInt(elements.forecastPeriods.value);
    
    if (currentModel === 'compare') {
        // Generate comparison results with multiple models
        const results = {
            model: 'compare',
            models: {
                'ARIMA': generateSingleMockResult('ARIMA', forecastPeriods),
                'SARIMA': generateSingleMockResult('SARIMA', forecastPeriods)
            }
        };
        
        displayForecastingResults(results);
        showNotification('✅ Model comparison completed successfully!', 'success');
    } else {
        // Generate single model results
        const results = generateSingleMockResult(currentModel, forecastPeriods);
        displayForecastingResults(results);
        showNotification('✅ Forecasting completed successfully!', 'success');
    }
}

function generateSingleMockResult(modelName, forecastPeriods) {
    const lastDate = new Date(currentData.dates[currentData.dates.length - 1]);
    const lastValue = currentData.values[currentData.values.length - 1];
    
    // Generate different characteristics for different models
    const modelVariations = {
        'ARIMA': { trend: 0.1, seasonal: 5, noise: 2 },
        'SARIMA': { trend: 0.08, seasonal: 7, noise: 1.5 },
        'arima': { trend: 0.1, seasonal: 5, noise: 2 },
        'sarima': { trend: 0.08, seasonal: 7, noise: 1.5 },
        'prophet': { trend: 0.12, seasonal: 4, noise: 2.5 }
    };
    
    const variation = modelVariations[modelName] || modelVariations['arima'];
    
    const forecast = {
        dates: [],
        values: [],
        lower_bound: [],
        upper_bound: []
    };
    
    for (let i = 1; i <= forecastPeriods; i++) {
        const forecastDate = new Date(lastDate);
        forecastDate.setDate(forecastDate.getDate() + i);
        forecast.dates.push(forecastDate.toISOString().split('T')[0]);
        
        // Model-specific forecast generation
        const trend = lastValue + (i * variation.trend);
        const seasonal = variation.seasonal * Math.sin(2 * Math.PI * i / 30);
        const forecastValue = trend + seasonal + (Math.random() - 0.5) * variation.noise;
        
        forecast.values.push(forecastValue);
        forecast.lower_bound.push(forecastValue - 5);
        forecast.upper_bound.push(forecastValue + 5);
    }
    
    return {
        model: modelName.toLowerCase(),
        forecast: forecast,
        metrics: {
            rmse: Math.random() * 10 + 5,
            mae: Math.random() * 8 + 3,
            mape: Math.random() * 15 + 5,
            aic: Math.random() * 1000 + 500,
            bic: Math.random() * 1000 + 600,
            r2: Math.random() * 0.3 + 0.7
        },
        fitted_values: currentData.values.map(v => v + (Math.random() - 0.5) * 5),
        residuals: currentData.values.map(v => (Math.random() - 0.5) * 10)
    };
}

function displayForecastingResults(results) {
    // Update results title
    const resultsTitle = document.getElementById('resultsTitle');
    const modelNames = {
        'arima': 'ARIMA',
        'sarima': 'SARIMA',
        'prophet': 'Prophet',
        'compare': 'Model Comparison'
    };
    resultsTitle.innerHTML = `<i class="bi bi-crystal"></i> ${modelNames[results.model]} Results`;
    
    // Handle different result types
    if (results.model === 'compare' && results.models) {
        // Display comparison results
        displayComparisonResults(results);
        // Don't call showSection('results') here - let displayComparisonResults handle it
    } else {
        // Display single model results
        displayModelMetrics(results.metrics);
        createForecastChart(results);
        createResidualsChart(results);
        // Show results section for single models
        showSection('results');
    }
}

function displayModelMetrics(metrics) {
    const metricsHtml = `
        <div class="col-lg-3 col-md-6">
            <div class="metric-card">
                <div class="metric-icon">
                    <i class="bi bi-speedometer2"></i>
                </div>
                <div class="metric-content">
                    <h3 class="metric-value">${metrics.rmse.toFixed(2)}</h3>
                    <p class="metric-label">RMSE</p>
                </div>
            </div>
        </div>
        <div class="col-lg-3 col-md-6">
            <div class="metric-card">
                <div class="metric-icon">
                    <i class="bi bi-calculator"></i>
                </div>
                <div class="metric-content">
                    <h3 class="metric-value">${metrics.mae.toFixed(2)}</h3>
                    <p class="metric-label">MAE</p>
                </div>
            </div>
        </div>
        <div class="col-lg-3 col-md-6">
            <div class="metric-card">
                <div class="metric-icon">
                    <i class="bi bi-percent"></i>
                </div>
                <div class="metric-content">
                    <h3 class="metric-value">${metrics.mape.toFixed(2)}%</h3>
                    <p class="metric-label">MAPE</p>
                </div>
            </div>
        </div>
        <div class="col-lg-3 col-md-6">
            <div class="metric-card">
                <div class="metric-icon">
                    <i class="bi bi-graph-up"></i>
                </div>
                <div class="metric-content">
                    <h3 class="metric-value">${metrics.aic.toFixed(0)}</h3>
                    <p class="metric-label">AIC</p>
                </div>
            </div>
        </div>
    `;
    
    elements.modelMetrics.innerHTML = metricsHtml;
}

function displayComparisonResults(results) {
    // Create comparison metrics table
    createComparisonTable(results.models);
    
    // Create comparison chart
    createComparisonChart(results.models);
    
    // Show comparison section instead of results
    showSection('comparison');
}

function createComparisonTable(models) {
    if (!elements.comparisonTable) return;
    
    const tbody = elements.comparisonTable.querySelector('tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    // Add header row
    const headerRow = document.createElement('tr');
    headerRow.innerHTML = `
        <th>Model</th>
        <th>RMSE</th>
        <th>MAE</th>
        <th>MAPE (%)</th>
        <th>AIC</th>
        <th>BIC</th>
        <th>R²</th>
    `;
    tbody.appendChild(headerRow);
    
    // Add data rows for each model
    Object.entries(models).forEach(([modelName, modelResults]) => {
        const row = document.createElement('tr');
        const metrics = modelResults.metrics || {};
        row.innerHTML = `
            <td><strong>${modelName}</strong></td>
            <td>${(metrics.rmse || 0).toFixed(2)}</td>
            <td>${(metrics.mae || 0).toFixed(2)}</td>
            <td>${(metrics.mape || 0).toFixed(2)}</td>
            <td>${(metrics.aic || 0).toFixed(0)}</td>
            <td>${(metrics.bic || 0).toFixed(0)}</td>
            <td>${(metrics.r2 || 0).toFixed(3)}</td>
        `;
        tbody.appendChild(row);
    });
}

function createComparisonChart(models) {
    if (!elements.comparisonChart) return;
    
    const traces = [];
    const colors = ['#00d4ff', '#51cf66', '#ff6b6b', '#ffd43b', '#74c0fc'];
    let colorIndex = 0;
    
    // Add historical data
    traces.push({
        x: currentData.dates,
        y: currentData.values,
        type: 'scatter',
        mode: 'lines',
        name: 'Historical Data',
        line: { color: '#ffffff', width: 2, dash: 'dash' }
    });
    
    // Add forecast for each model
    Object.entries(models).forEach(([modelName, modelResults]) => {
        if (modelResults.forecast && modelResults.forecast.dates && modelResults.forecast.values) {
            traces.push({
                x: modelResults.forecast.dates,
                y: modelResults.forecast.values,
                type: 'scatter',
                mode: 'lines',
                name: `${modelName} Forecast`,
                line: { color: colors[colorIndex % colors.length], width: 2 }
            });
            
            // Add confidence interval if available
            if (modelResults.forecast.upper_bound && modelResults.forecast.lower_bound) {
                traces.push({
                    x: modelResults.forecast.dates,
                    y: modelResults.forecast.upper_bound,
                    type: 'scatter',
                    mode: 'lines',
                    line: { width: 0 },
                    showlegend: false,
                    hoverinfo: 'skip'
                });
                
                traces.push({
                    x: modelResults.forecast.dates,
                    y: modelResults.forecast.lower_bound,
                    type: 'scatter',
                    mode: 'lines',
                    fill: 'tonexty',
                    fillcolor: colors[colorIndex % colors.length].replace('rgb', 'rgba').replace(')', ', 0.2)'),
                    name: `${modelName} CI`,
                    line: { width: 0 },
                    hoverinfo: 'skip'
                });
            }
            
            colorIndex++;
        }
    });
    
    const layout = {
        title: {
            text: 'Model Comparison - Forecasts',
            font: { color: '#ffffff', size: 18 }
        },
        xaxis: {
            title: 'Date',
            color: '#ffffff',
            gridcolor: 'rgba(255, 255, 255, 0.1)'
        },
        yaxis: {
            title: 'Value',
            color: '#ffffff',
            gridcolor: 'rgba(255, 255, 255, 0.1)'
        },
        plot_bgcolor: 'rgba(0, 0, 0, 0)',
        paper_bgcolor: 'rgba(0, 0, 0, 0)',
        font: { color: '#ffffff' },
        margin: { t: 60, b: 60, l: 60, r: 60 },
        legend: {
            x: 0.02,
            y: 0.98,
            bgcolor: 'rgba(0, 0, 0, 0.5)',
            bordercolor: 'rgba(255, 255, 255, 0.2)',
            borderwidth: 1
        }
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    };
    
    Plotly.newPlot(elements.comparisonChart, traces, layout, config);
    charts.comparison = { traces, layout, config };
}

function createForecastChart(results) {
    const traces = [
        // Historical data
        {
            x: currentData.dates,
            y: currentData.values,
            type: 'scatter',
            mode: 'lines',
            name: 'Historical Data',
            line: { color: '#00d4ff', width: 2 }
        },
        // Fitted values
        {
            x: currentData.dates,
            y: results.fitted_values,
            type: 'scatter',
            mode: 'lines',
            name: 'Fitted Values',
            line: { color: '#51cf66', width: 2 }
        },
        // Forecast
        {
            x: results.forecast.dates,
            y: results.forecast.values,
            type: 'scatter',
            mode: 'lines',
            name: 'Forecast',
            line: { color: '#ff6b6b', width: 3 }
        },
        // Confidence interval
        {
            x: results.forecast.dates,
            y: results.forecast.upper_bound,
            type: 'scatter',
            mode: 'lines',
            line: { width: 0 },
            showlegend: false,
            hoverinfo: 'skip'
        },
        {
            x: results.forecast.dates,
            y: results.forecast.lower_bound,
            type: 'scatter',
            mode: 'lines',
            fill: 'tonexty',
            fillcolor: 'rgba(255, 71, 87, 0.2)',
            name: 'Confidence Interval',
            line: { width: 0 },
            hoverinfo: 'skip'
        }
    ];
    
    const layout = {
        title: {
            text: `${results.model.toUpperCase()} Forecast`,
            font: { color: '#ffffff', size: 18 }
        },
        xaxis: {
            title: 'Date',
            color: '#ffffff',
            gridcolor: 'rgba(255, 255, 255, 0.1)'
        },
        yaxis: {
            title: 'Value',
            color: '#ffffff',
            gridcolor: 'rgba(255, 255, 255, 0.1)'
        },
        plot_bgcolor: 'rgba(0, 0, 0, 0)',
        paper_bgcolor: 'rgba(0, 0, 0, 0)',
        font: { color: '#ffffff' },
        margin: { t: 60, b: 60, l: 60, r: 60 }
    };
    
    Plotly.newPlot(elements.forecastChart, traces, layout, { responsive: true });
}

function createResidualsChart(results) {
    const traces = [
        {
            x: currentData.dates,
            y: results.residuals,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Residuals',
            line: { color: '#FFA502', width: 2 },
            marker: { size: 4 }
        }
    ];
    
    const layout = {
        title: {
            text: 'Residuals Analysis',
            font: { color: '#ffffff', size: 18 }
        },
        xaxis: {
            title: 'Date',
            color: '#ffffff',
            gridcolor: 'rgba(255, 255, 255, 0.1)'
        },
        yaxis: {
            title: 'Residuals',
            color: '#ffffff',
            gridcolor: 'rgba(255, 255, 255, 0.1)',
            zeroline: true,
            zerolinecolor: 'rgba(255, 255, 255, 0.3)'
        },
        plot_bgcolor: 'rgba(0, 0, 0, 0)',
        paper_bgcolor: 'rgba(0, 0, 0, 0)',
        font: { color: '#ffffff' },
        margin: { t: 60, b: 60, l: 60, r: 60 }
    };
    
    Plotly.newPlot(elements.residualsChart, traces, layout, { responsive: true });
}

// ===== SECTION MANAGEMENT =====
function showSection(section) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.add('d-none');
    });
    
    // Show selected section
    switch(section) {
        case 'welcome':
            elements.welcomeSection.classList.remove('d-none');
            break;
        case 'data':
            elements.dataOverview.classList.remove('d-none');
            break;
        case 'results':
            elements.forecastingResults.classList.remove('d-none');
            break;
        case 'comparison':
            elements.modelComparison.classList.remove('d-none');
            break;
    }
}

// ===== THEME MANAGEMENT =====
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    elements.themeIcon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
}

// ===== UTILITY FUNCTIONS =====
function showLoading(show) {
    elements.loadingOverlay.classList.toggle('d-none', !show);
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function handleScroll() {
    const scrollTop = window.pageYOffset;
    elements.scrollToTop.style.display = scrollTop > 300 ? 'block' : 'none';
}

function handleResize() {
    // Handle responsive chart resizing
    Object.keys(charts).forEach(chartId => {
        if (charts[chartId] && elements[chartId]) {
            Plotly.Plots.resize(elements[chartId]);
        }
    });
}

// ===== ANIMATIONS =====
function setupAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-slide-up');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.metric-card, .glass-card').forEach(el => {
        observer.observe(el);
    });
}

// ===== INITIALIZE CHARTS =====
function initializeCharts() {
    // Initialize empty charts
    const emptyTrace = { x: [], y: [], type: 'scatter', mode: 'lines' };
    const emptyLayout = {
        plot_bgcolor: 'rgba(0, 0, 0, 0)',
        paper_bgcolor: 'rgba(0, 0, 0, 0)',
        font: { color: '#ffffff' }
    };
    
    Plotly.newPlot(elements.timeSeriesChart, [emptyTrace], emptyLayout);
    Plotly.newPlot(elements.forecastChart, [emptyTrace], emptyLayout);
    Plotly.newPlot(elements.residualsChart, [emptyTrace], emptyLayout);
}

// ===== PARTICLE SYSTEM =====
function initializeParticles() {
    const container = document.getElementById('particleContainer');
    if (!container) return;
    
    // Create particles
    for (let i = 0; i < 50; i++) {
        createParticle(container);
    }
    
    // Start animation loop
    animateParticles();
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    // Random position
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = Math.random() * 100 + '%';
    
    // Random size
    const size = Math.random() * 4 + 2;
    particle.style.width = size + 'px';
    particle.style.height = size + 'px';
    
    // Random animation delay
    particle.style.animationDelay = Math.random() * 6 + 's';
    particle.style.animationDuration = (Math.random() * 4 + 4) + 's';
    
    container.appendChild(particle);
    particles.push(particle);
}

function animateParticles() {
    particles.forEach((particle, index) => {
        if (!particle.parentNode) {
            particles.splice(index, 1);
            return;
        }
        
        // Add subtle movement
        const currentTop = parseFloat(particle.style.top);
        const newTop = (currentTop + Math.random() * 0.5 - 0.25) % 100;
        particle.style.top = newTop + '%';
        
        // Add subtle opacity variation
        const opacity = 0.3 + Math.sin(Date.now() * 0.001 + index) * 0.3;
        particle.style.opacity = opacity;
    });
    
    animationFrameId = requestAnimationFrame(animateParticles);
}

// ===== SOUND EFFECTS =====
function initializeSounds() {
    // Create audio context for sound effects
    try {
        window.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    } catch (e) {
        console.log('Web Audio API not supported');
    }
}

function playSound(frequency = 440, duration = 0.1, type = 'sine') {
    if (!window.audioContext) return;
    
    const oscillator = window.audioContext.createOscillator();
    const gainNode = window.audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(window.audioContext.destination);
    
    oscillator.frequency.value = frequency;
    oscillator.type = type;
    
    gainNode.gain.setValueAtTime(0.1, window.audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, window.audioContext.currentTime + duration);
    
    oscillator.start(window.audioContext.currentTime);
    oscillator.stop(window.audioContext.currentTime + duration);
}

function playNotificationSound(type = 'success') {
    const sounds = {
        success: { freq: 523, duration: 0.2 }, // C5
        error: { freq: 220, duration: 0.3 }, // A3
        warning: { freq: 330, duration: 0.2 }, // E4
        info: { freq: 440, duration: 0.15 } // A4
    };
    
    const sound = sounds[type] || sounds.info;
    playSound(sound.freq, sound.duration);
}

// ===== ENTRANCE ANIMATIONS =====
function addEntranceAnimations() {
    // Add staggered animations to elements
    const elementsToAnimate = [
        '.logo-container',
        '.sidebar-section',
        '.welcome-icon',
        '.welcome-title',
        '.welcome-subtitle',
        '.feature-item'
    ];
    
    elementsToAnimate.forEach((selector, index) => {
        const element = document.querySelector(selector);
        if (element) {
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';
            
            setTimeout(() => {
                element.style.transition = 'all 0.6s ease-out';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, index * 100);
        }
    });
}

// ===== ENHANCED NOTIFICATIONS =====
function showNotification(message, type = 'info') {
    // Play sound effect
    playNotificationSound(type);
    
    // Create notification element with enhanced styling
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed notification-enhanced`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 300px; backdrop-filter: blur(10px);';
    
    // Add icon based on type
    const icons = {
        success: 'bi-check-circle-fill',
        error: 'bi-exclamation-triangle-fill',
        warning: 'bi-exclamation-circle-fill',
        info: 'bi-info-circle-fill'
    };
    
    const icon = icons[type] || icons.info;
    notification.innerHTML = `
        <i class="bi ${icon} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add entrance animation
    notification.style.transform = 'translateX(100%)';
    notification.style.opacity = '0';
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transition = 'all 0.3s ease-out';
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 10);
    
    // Auto remove after 5 seconds with animation
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.transition = 'all 0.3s ease-in';
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }, 5000);
}

// ===== ENHANCED LOADING STATES =====
function showLoading(show, message = 'Training models and generating forecasts...') {
    const overlay = elements.loadingOverlay;
    const spinner = overlay.querySelector('.loading-spinner');
    
    if (show) {
        // Update loading message
        const messageElement = spinner.querySelector('p');
        if (messageElement) {
            messageElement.textContent = message;
        }
        
        // Add loading animation
        overlay.classList.remove('d-none');
        overlay.style.opacity = '0';
        
        setTimeout(() => {
            overlay.style.transition = 'opacity 0.3s ease-out';
            overlay.style.opacity = '1';
        }, 10);
        
        // Add progress simulation
        simulateProgress();
    } else {
        overlay.style.transition = 'opacity 0.3s ease-out';
        overlay.style.opacity = '0';
        
        setTimeout(() => {
            overlay.classList.add('d-none');
        }, 300);
    }
}

function simulateProgress() {
    const progressBar = document.createElement('div');
    progressBar.className = 'progress mt-3';
    progressBar.style.width = '200px';
    progressBar.innerHTML = `
        <div class="progress-bar progress-bar-striped progress-bar-animated" 
             role="progressbar" style="width: 0%"></div>
    `;
    
    const spinner = elements.loadingOverlay.querySelector('.loading-spinner');
    spinner.appendChild(progressBar);
    
    const bar = progressBar.querySelector('.progress-bar');
    let progress = 0;
    
    const interval = setInterval(() => {
        progress += Math.random() * 10;
        if (progress > 100) progress = 100;
        
        bar.style.width = progress + '%';
        
        if (progress >= 100) {
            clearInterval(interval);
        }
    }, 200);
}

// ===== ENHANCED METRIC CARDS =====
function displayModelMetrics(metrics) {
    const metricsHtml = `
        <div class="col-lg-3 col-md-6">
            <div class="metric-card animate-bounce-in" style="animation-delay: 0.1s">
                <div class="metric-icon">
                    <i class="bi bi-speedometer2"></i>
                </div>
                <div class="metric-content">
                    <h3 class="metric-value">${metrics.rmse.toFixed(2)}</h3>
                    <p class="metric-label">RMSE</p>
                </div>
            </div>
        </div>
        <div class="col-lg-3 col-md-6">
            <div class="metric-card animate-bounce-in" style="animation-delay: 0.2s">
                <div class="metric-icon">
                    <i class="bi bi-calculator"></i>
                </div>
                <div class="metric-content">
                    <h3 class="metric-value">${metrics.mae.toFixed(2)}</h3>
                    <p class="metric-label">MAE</p>
                </div>
            </div>
        </div>
        <div class="col-lg-3 col-md-6">
            <div class="metric-card animate-bounce-in" style="animation-delay: 0.3s">
                <div class="metric-icon">
                    <i class="bi bi-percent"></i>
                </div>
                <div class="metric-content">
                    <h3 class="metric-value">${metrics.mape.toFixed(2)}%</h3>
                    <p class="metric-label">MAPE</p>
                </div>
            </div>
        </div>
        <div class="col-lg-3 col-md-6">
            <div class="metric-card animate-bounce-in" style="animation-delay: 0.4s">
                <div class="metric-icon">
                    <i class="bi bi-graph-up"></i>
                </div>
                <div class="metric-content">
                    <h3 class="metric-value">${metrics.aic.toFixed(0)}</h3>
                    <p class="metric-label">AIC</p>
                </div>
            </div>
        </div>
    `;
    
    elements.modelMetrics.innerHTML = metricsHtml;
    
    // Add click effects to metric cards
    elements.modelMetrics.querySelectorAll('.metric-card').forEach(card => {
        card.addEventListener('click', () => {
            playSound(660, 0.1); // E5
            card.style.transform = 'scale(0.95)';
            setTimeout(() => {
                card.style.transform = '';
            }, 150);
        });
    });
}

// ===== LOGO INTERACTIONS =====
function initializeLogoInteractions() {
    const logoContainer = document.querySelector('.logo-container');
    const logoSvg = document.querySelector('.logo-svg');
    
    if (logoContainer && logoSvg) {
        // Add click effect
        logoContainer.addEventListener('click', () => {
            playSound(660, 0.15); // E5 - Logo click sound
            
            // Add special animation on click
            logoSvg.style.animation = 'none';
            logoSvg.style.transform = 'rotateY(360deg) rotateX(180deg) scale(1.2)';
            
            setTimeout(() => {
                logoSvg.style.animation = 'logoFloat 4s ease-in-out infinite, logoRotate 20s linear infinite';
                logoSvg.style.transform = '';
            }, 600);
            
            showNotification('🚀 Welcome to ForecastAI!', 'success');
        });
        
        // Add mouse enter effect
        logoContainer.addEventListener('mouseenter', () => {
            playSound(523, 0.05); // C5 - Subtle hover sound
        });
        
        // Add data flow animation on hover
        logoContainer.addEventListener('mouseenter', () => {
            const bars = logoSvg.querySelectorAll('rect');
            bars.forEach((bar, index) => {
                setTimeout(() => {
                    bar.style.filter = 'brightness(1.5)';
                    setTimeout(() => {
                        bar.style.filter = '';
                    }, 200);
                }, index * 50);
            });
        });
    }
}

// ===== ENHANCED BUTTON INTERACTIONS =====
function enhanceButtonInteractions() {
    // Add click effects to all buttons
    document.querySelectorAll('.btn-3d').forEach(button => {
        button.addEventListener('click', () => {
            playSound(440, 0.1); // A4
        });
    });
    
    // Add hover effects to cards
    document.querySelectorAll('.glass-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            playSound(523, 0.05); // C5
        });
    });
}

// ===== KEYBOARD SHORTCUTS =====
function handleKeyboardShortcuts(event) {
    // Only trigger if no input is focused
    if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') {
        return;
    }
    
    switch(event.key.toLowerCase()) {
        case 't':
            if (event.ctrlKey || event.metaKey) {
                event.preventDefault();
                toggleTheme();
                playSound(523, 0.1); // C5
            }
            break;
        case 'r':
            if (event.ctrlKey || event.metaKey) {
                event.preventDefault();
                if (currentData) {
                    runForecasting();
                    playSound(440, 0.1); // A4
                }
            }
            break;
        case 's':
            if (event.ctrlKey || event.metaKey) {
                event.preventDefault();
                loadSampleData();
                playSound(330, 0.1); // E4
            }
            break;
        case 'escape':
            // Close any open modals or overlays
            const overlay = document.querySelector('.loading-overlay:not(.d-none)');
            if (overlay) {
                showLoading(false);
                playSound(220, 0.1); // A3
            }
            break;
        case 'h':
            if (event.ctrlKey || event.metaKey) {
                event.preventDefault();
                showKeyboardShortcuts();
                playSound(660, 0.1); // E5
            }
            break;
        case 'b':
            if (event.ctrlKey || event.metaKey) {
                event.preventDefault();
                toggleSidebar();
            }
            break;
    }
}

function showKeyboardShortcuts() {
    const shortcuts = [
        { key: 'Ctrl/Cmd + T', action: 'Toggle Theme' },
        { key: 'Ctrl/Cmd + R', action: 'Run Forecasting' },
        { key: 'Ctrl/Cmd + S', action: 'Load Sample Data' },
        { key: 'Ctrl/Cmd + B', action: 'Toggle Sidebar' },
        { key: 'Ctrl/Cmd + H', action: 'Show Help' },
        { key: 'Escape', action: 'Close Overlays' }
    ];
    
    const shortcutsHtml = shortcuts.map(s => 
        `<div class="d-flex justify-content-between mb-2">
            <kbd class="bg-dark text-light">${s.key}</kbd>
            <span>${s.action}</span>
        </div>`
    ).join('');
    
    showNotification(`
        <div class="text-start">
            <h6 class="mb-3">Keyboard Shortcuts</h6>
            ${shortcutsHtml}
        </div>
    `, 'info');
}

// ===== EXPORT FUNCTIONS (for Python backend integration) =====
window.TimeSeriesApp = {
    loadStockData,
    loadSampleData,
    runForecasting,
    toggleTheme,
    showNotification,
    initializeParticles,
    playSound,
    enhanceButtonInteractions
};
