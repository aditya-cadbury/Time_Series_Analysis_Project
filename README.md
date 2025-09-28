# 📈 Time Series Forecasting Dashboard

A comprehensive web application for time series analysis and forecasting using multiple advanced models including ARIMA, SARIMA, and Prophet. Built with Streamlit for an intuitive and visually appealing user interface.

## 🚀 Features

### 📊 Data Sources
- **Stock Data**: Real-time data from Yahoo Finance (AAPL, GOOGL, MSFT, etc.)
- **CSV Upload**: Upload your own time series data
- **Sample Data**: Built-in sample datasets for testing

### 🤖 Forecasting Models
- **ARIMA (AutoRegressive Integrated Moving Average)**: Classic time series model with automatic parameter selection
- **SARIMA (Seasonal ARIMA)**: Enhanced ARIMA with seasonal components
- **Prophet**: Facebook's robust forecasting tool with trend and seasonality detection

### 📈 Visualizations
- Interactive time series plots with Plotly
- Model comparison charts
- Residual analysis plots
- Seasonal decomposition
- Performance metrics visualization
- Confidence intervals and prediction bands

### 📊 Model Evaluation
- RMSE (Root Mean Square Error)
- MAE (Mean Absolute Error)
- MAPE (Mean Absolute Percentage Error)
- AIC/BIC (Information Criteria)
- R-squared (Prophet)
- Cross-validation metrics

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd /Users/adityakurup/Documents/SEM7/ATSA/Project_ATSA
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**
   - The app will automatically open at `http://localhost:8501`
   - If it doesn't open automatically, manually navigate to the URL

## 📁 Project Structure

```
Project_ATSA/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── models/                         # Model implementations
│   ├── __init__.py
│   ├── arima_model.py             # ARIMA model class
│   ├── sarima_model.py            # SARIMA model class
│   └── prophet_model.py           # Prophet model class
└── utils/                         # Utility functions
    ├── __init__.py
    ├── data_loader.py             # Data loading and preprocessing
    └── visualizations.py          # Plotting and visualization functions
```

## 🎯 How to Use

### 1. Load Data
- **Stock Data**: Enter a ticker symbol (e.g., AAPL, GOOGL) and select time period
- **CSV Upload**: Upload a CSV file with date and value columns
- **Sample Data**: Use built-in sample datasets

### 2. Configure Model
- Select forecasting model (ARIMA, SARIMA, Prophet, or Compare All)
- Adjust forecast periods (10-100)
- Set confidence interval (80-99%)
- For ARIMA/SARIMA: Enable auto-parameter selection or set manual parameters

### 3. Run Forecasting
- Click "🚀 Run Forecasting" button
- Wait for model training and prediction generation
- View interactive plots and performance metrics

### 4. Analyze Results
- Examine forecast plots with confidence intervals
- Review model performance metrics
- Compare multiple models side-by-side
- Analyze residuals for model diagnostics

## 📊 Sample Data Formats

### CSV Format
Your CSV file should have:
- Date column (any of: 'date', 'Date', 'DATE', 'timestamp', 'time')
- Numeric value column(s)
- Date format should be recognizable by pandas

Example:
```csv
date,value
2020-01-01,100
2020-01-02,102
2020-01-03,98
...
```

### Stock Data
Supported tickers include:
- **Technology**: AAPL, GOOGL, MSFT, AMZN, TSLA
- **Finance**: JPM, BAC, WFC, GS
- **Healthcare**: JNJ, PFE, UNH, ABBV
- **Energy**: XOM, CVX, COP
- And many more...

## 🔧 Model Parameters

### ARIMA Parameters
- **p**: Autoregressive order (0-5)
- **d**: Differencing order (0-3)
- **q**: Moving average order (0-5)

### SARIMA Parameters
- **p, d, q**: Non-seasonal parameters
- **P, D, Q**: Seasonal parameters
- **s**: Seasonal period (auto-detected)

### Prophet Parameters
- **Yearly Seasonality**: Automatic detection
- **Weekly Seasonality**: Automatic detection
- **Daily Seasonality**: Disabled by default
- **Seasonality Mode**: Additive or Multiplicative

## 📈 Performance Tips

1. **Data Quality**: Ensure your data has minimal missing values
2. **Data Length**: More historical data generally improves forecast accuracy
3. **Parameter Selection**: Use auto-parameter selection for best results
4. **Model Comparison**: Always compare multiple models for robust forecasts
5. **Residual Analysis**: Check residuals for model adequacy

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

2. **Data Loading Issues**
   - Verify CSV format has proper date and numeric columns
   - Check internet connection for stock data downloads
   - Ensure date column is in recognizable format

3. **Model Fitting Errors**
   - Try different parameter ranges
   - Use auto-parameter selection
   - Ensure sufficient data points (minimum 30-50 recommended)

4. **Memory Issues**
   - Reduce forecast periods
   - Use smaller parameter search ranges
   - Close other applications to free memory

## 📚 Model Descriptions

### ARIMA
- **Best for**: Non-seasonal time series with trends
- **Strengths**: Simple, interpretable, works well with short series
- **Limitations**: Doesn't handle seasonality well

### SARIMA
- **Best for**: Seasonal time series data
- **Strengths**: Handles both trend and seasonality
- **Limitations**: More complex, requires more data

### Prophet
- **Best for**: Business time series with holidays and seasonality
- **Strengths**: Robust to missing data, handles holidays, easy to use
- **Limitations**: Less interpretable, requires more computational resources

## 🤝 Contributing

Feel free to contribute to this project by:
- Adding new forecasting models
- Improving visualizations
- Enhancing data loading capabilities
- Adding new evaluation metrics
- Improving documentation

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Streamlit** for the amazing web framework
- **Plotly** for interactive visualizations
- **Statsmodels** for ARIMA/SARIMA implementations
- **Prophet** by Facebook for the forecasting library
- **Yahoo Finance** for providing stock data

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the model documentation
3. Ensure your data meets the required format
4. Try with sample data first to verify installation

---

**Happy Forecasting! 📈✨**
