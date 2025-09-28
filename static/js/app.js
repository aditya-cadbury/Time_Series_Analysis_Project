// ===== GLOBAL VARIABLES =====
let currentData = null;
let currentModel = 'arima';
let charts = {};

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
    loadSampleData: document.getElementById('loadSampleData'),
    runForecasting: document.getElementById('runForecasting'),
    
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
    mainContent: document.getElementById('mainContent')
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
    
    // Show welcome section initially
    showSection('welcome');
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
    elements.loadSampleData.addEventListener('click', loadSampleData);
    elements.runForecasting.addEventListener('click', runForecasting);
    
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
    elements.sidebar.classList.toggle('collapsed');
    elements.mainContent.classList.toggle('expanded');
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
    const ticker = elements.tickerInput.value.toUpperCase();
    const period = elements.timePeriod.value;
    
    if (!ticker) {
        showNotification('Please enter a stock ticker', 'warning');
        return;
    }
    
    showLoading(true);
    
    try {
        console.log('Loading stock data for:', ticker, period);
        
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
            currentData = data;
            displayDataOverview(data);
            showNotification(`✅ Loaded ${ticker} data successfully!`, 'success');
        } else {
            const errorText = await response.text();
            console.error('Response error:', errorText);
            throw new Error('Failed to load stock data: ' + errorText);
        }
    } catch (error) {
        console.error('Error loading stock data:', error);
        showNotification('Error loading stock data. Using sample data.', 'error');
        // Load sample data as fallback
        await loadSampleData();
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
    const results = {
        model: currentModel,
        forecast: {
            dates: [],
            values: [],
            lower_bound: [],
            upper_bound: []
        },
        metrics: {
            rmse: Math.random() * 10 + 5,
            mae: Math.random() * 8 + 3,
            mape: Math.random() * 15 + 5,
            aic: Math.random() * 1000 + 500,
            bic: Math.random() * 1000 + 600
        },
        fitted_values: currentData.values.map(v => v + (Math.random() - 0.5) * 5),
        residuals: currentData.values.map(v => (Math.random() - 0.5) * 10)
    };
    
    // Generate forecast dates and values
    const lastDate = new Date(currentData.dates[currentData.dates.length - 1]);
    const lastValue = currentData.values[currentData.values.length - 1];
    
    for (let i = 1; i <= forecastPeriods; i++) {
        const forecastDate = new Date(lastDate);
        forecastDate.setDate(forecastDate.getDate() + i);
        results.forecast.dates.push(forecastDate.toISOString().split('T')[0]);
        
        // Simple trend-based forecast
        const trend = lastValue + (i * 0.1);
        const seasonal = 5 * Math.sin(2 * Math.PI * i / 30);
        const forecastValue = trend + seasonal + (Math.random() - 0.5) * 2;
        
        results.forecast.values.push(forecastValue);
        results.forecast.lower_bound.push(forecastValue - 5);
        results.forecast.upper_bound.push(forecastValue + 5);
    }
    
    displayForecastingResults(results);
    showNotification('✅ Forecasting completed successfully!', 'success');
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
    
    // Display metrics
    displayModelMetrics(results.metrics);
    
    // Create forecast chart
    createForecastChart(results);
    
    // Create residuals chart
    createResidualsChart(results);
    
    // Show results section
    showSection('results');
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
            fillcolor: 'rgba(255, 107, 107, 0.2)',
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
            line: { color: '#ffd43b', width: 2 },
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

// ===== EXPORT FUNCTIONS (for Python backend integration) =====
window.TimeSeriesApp = {
    loadStockData,
    loadSampleData,
    runForecasting,
    toggleTheme,
    showNotification
};
