# 🚀 Modern Dark-Themed Time Series Forecasting Dashboard

A futuristic, 3D-style web application for time series analysis and forecasting with a stunning dark UI built with Bootstrap 5, featuring glassmorphism effects, neon glows, and smooth animations.

## ✨ Features

### 🎨 **Modern Dark UI Design**
- **Glassmorphism Effects**: Translucent cards with backdrop blur
- **3D Buttons**: Elevated buttons with hover animations and shimmer effects
- **Neon Glows**: Subtle neon accents and shadows
- **Smooth Animations**: CSS transitions and keyframe animations
- **Responsive Design**: Mobile-first approach with Bootstrap 5

### 📊 **Advanced Visualizations**
- **Interactive Plotly Charts**: Zoom, pan, hover with dark theme
- **Real-time Metrics**: Animated counters and performance indicators
- **Model Comparison**: Side-by-side model performance visualization
- **Residual Analysis**: Comprehensive diagnostic plots

### 🤖 **Multiple Forecasting Models**
- **ARIMA**: Auto-regressive Integrated Moving Average with parameter optimization
- **SARIMA**: Seasonal ARIMA with automatic seasonality detection
- **Prophet**: Facebook's robust forecasting with trend and seasonality
- **Model Comparison**: Compare all models simultaneously

### 📱 **User Experience**
- **Collapsible Sidebar**: Space-efficient navigation
- **Theme Toggle**: Switch between dark and light modes
- **Loading States**: Smooth loading animations
- **Notifications**: Toast-style feedback messages
- **Floating Actions**: Quick access buttons

## 🛠️ Technology Stack

### Frontend
- **HTML5**: Semantic markup structure
- **Bootstrap 5**: Responsive framework with dark theme
- **Custom CSS**: Advanced styling with CSS variables and animations
- **JavaScript (ES6+)**: Modern JavaScript with async/await
- **Plotly.js**: Interactive charting library

### Backend
- **Flask**: Lightweight Python web framework
- **Existing Models**: ARIMA, SARIMA, Prophet implementations
- **RESTful API**: Clean API endpoints for data and forecasting

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Run the Application**

#### Option A: Flask Backend (Recommended)
```bash
python app_flask.py
```
Then open: `http://localhost:5000`

#### Option B: Streamlit (Original)
```bash
streamlit run app.py
```
Then open: `http://localhost:8501`

### 3. **Access the Dashboard**
- **Local**: `http://localhost:5000`
- **Network**: `http://[your-ip]:5000`

## 📁 Project Structure

```
Project_ATSA/
├── app_flask.py              # Flask backend application
├── app.py                    # Original Streamlit app
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Main dashboard template
├── static/
│   ├── css/
│   │   └── style.css        # Custom dark theme styles
│   └── js/
│       └── app.js           # Frontend JavaScript
├── models/                   # Forecasting models
│   ├── arima_model.py
│   ├── sarima_model.py
│   └── prophet_model.py
├── utils/                    # Utility functions
│   ├── data_loader.py
│   └── visualizations.py
└── sample_data.csv          # Sample time series data
```

## 🎯 How to Use

### 1. **Load Data**
- **Stock Data**: Enter ticker symbol (AAPL, GOOGL, etc.) and select time period
- **CSV Upload**: Upload your own time series CSV file
- **Sample Data**: Use built-in sample datasets for testing

### 2. **Select Model**
- **ARIMA**: For non-seasonal time series
- **SARIMA**: For seasonal time series
- **Prophet**: For robust forecasting with holidays
- **Compare All**: Run all models and compare performance

### 3. **Configure Parameters**
- **Forecast Periods**: Set number of future periods (10-100)
- **Confidence Interval**: Set prediction confidence (80-99%)
- **Auto Parameters**: Enable automatic parameter selection
- **Manual Parameters**: Set custom ARIMA/SARIMA parameters

### 4. **Run Forecasting**
- Click "🚀 Run Forecasting" button
- View interactive charts and performance metrics
- Analyze residuals and model diagnostics

## 🎨 UI Components

### **Navigation Sidebar**
- Collapsible design with smooth animations
- Data source selection with dynamic forms
- Model configuration with parameter controls
- Theme toggle and settings

### **Metric Cards**
- Glassmorphism design with hover effects
- Animated counters for key statistics
- Color-coded performance indicators
- Responsive grid layout

### **Interactive Charts**
- Plotly.js integration with dark theme
- Zoom, pan, and hover interactions
- Confidence intervals and prediction bands
- Real-time data updates

### **Data Tables**
- Dark-themed responsive tables
- Sortable columns and pagination
- Hover effects and smooth transitions

## 🔧 Customization

### **Theme Variables**
```css
:root {
    --bg-primary: #0a0a0a;
    --accent-primary: #00d4ff;
    --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --shadow-neon: 0 0 20px rgba(0, 212, 255, 0.3);
}
```

### **Color Schemes**
- **Dark Theme**: Default futuristic dark mode
- **Light Theme**: Clean light mode option
- **Custom Colors**: Easily customizable via CSS variables

### **Animations**
- **Hover Effects**: Scale, glow, and shadow transitions
- **Loading States**: Spinner and progress animations
- **Scroll Animations**: Intersection Observer for reveal effects

## 📱 Responsive Design

### **Breakpoints**
- **Mobile**: < 768px - Single column layout
- **Tablet**: 768px - 1024px - Two column layout
- **Desktop**: > 1024px - Full sidebar layout

### **Mobile Features**
- Collapsible sidebar with overlay
- Touch-friendly buttons and sliders
- Optimized chart sizing
- Swipe gestures support

## 🔌 API Endpoints

### **Data Loading**
- `POST /api/load_stock_data` - Load stock data from Yahoo Finance
- `GET /api/load_sample_data` - Load built-in sample data
- `POST /api/load_csv_data` - Upload and process CSV files

### **Forecasting**
- `POST /api/forecast` - Run forecasting models
- `GET /api/health` - Health check endpoint

### **Example API Call**
```javascript
fetch('/api/forecast', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        model: 'arima',
        data: timeSeriesData,
        forecast_periods: 30,
        confidence_interval: 95,
        auto_params: true
    })
})
```

## 🎯 Performance Features

### **Optimizations**
- **Lazy Loading**: Charts load only when needed
- **Debounced Inputs**: Reduced API calls during typing
- **Cached Results**: Store model results for faster switching
- **Responsive Charts**: Auto-resize on window changes

### **Error Handling**
- **Graceful Degradation**: Fallback to mock data
- **User Notifications**: Toast-style error messages
- **Loading States**: Clear feedback during operations

## 🔮 Future Enhancements

### **Planned Features**
- **Real-time Data**: Live stock price updates
- **Advanced Models**: LSTM, XGBoost integration
- **Export Options**: PDF reports, CSV downloads
- **User Accounts**: Save and share forecasts
- **Mobile App**: React Native companion app

### **UI Improvements**
- **More Themes**: Cyberpunk, Matrix, Minimal
- **3D Visualizations**: WebGL-based 3D charts
- **Voice Commands**: Speech recognition integration
- **AR/VR Support**: Immersive forecasting experience

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### **Code Style**
- **HTML**: Semantic markup with accessibility
- **CSS**: BEM methodology with CSS variables
- **JavaScript**: ES6+ with async/await
- **Python**: PEP 8 with type hints

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Bootstrap Team**: For the amazing responsive framework
- **Plotly.js**: For interactive charting capabilities
- **Prophet Team**: For the robust forecasting library
- **Design Inspiration**: Modern UI/UX trends and glassmorphism

---

**Experience the future of time series forecasting with our cutting-edge dark-themed dashboard! 🚀✨**
