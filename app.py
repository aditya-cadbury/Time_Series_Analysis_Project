import streamlit as st
import pandas as pd
import numpy as np  # noqa: F401
import matplotlib.pyplot as plt  # noqa: F401
import seaborn as sns  # noqa: F401
import plotly.graph_objects as go
import plotly.express as px  # noqa: F401
from plotly.subplots import make_subplots  # noqa: F401
import yfinance as yf  # noqa: F401
from datetime import datetime, timedelta  # noqa: F401
import warnings

from models.arima_model import ARIMAForecaster
from models.sarima_model import SARIMAForecaster
# from models.prophet_model import ProphetForecaster  # Commented out due to PyArrow issues
from utils.data_loader import DataLoader
from utils.visualizations import create_forecast_plots, create_model_comparison

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Time Series Forecasting Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e8b57;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #2e8b57;
        padding-bottom: 0.5rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">📈 Time Series Forecasting Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar for data selection and model parameters
    st.sidebar.markdown("## 🔧 Configuration")
    
    # Data source selection
    data_source = st.sidebar.selectbox(
        "Select Data Source",
        ["Stock Data (Yahoo Finance)", "Upload CSV", "Sample Data"]
    )
    
    # Initialize data loader
    data_loader = DataLoader()
    
    # Load data based on selection
    if data_source == "Stock Data (Yahoo Finance)":
        st.sidebar.markdown("### 📊 Stock Data Configuration")
        ticker = st.sidebar.text_input("Enter Stock Ticker", value="AAPL")
        period = st.sidebar.selectbox("Time Period", ["1y", "2y", "5y", "10y", "max"])
        
        if st.sidebar.button("Load Stock Data"):
            with st.spinner("Loading stock data..."):
                df = data_loader.load_stock_data(ticker, period)
                if df is not None:
                    st.session_state.data = df
                    st.session_state.ticker = ticker
                    st.success(f"✅ Loaded {ticker} data successfully!")
    
    elif data_source == "Upload CSV":
        uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=['csv'])
        if uploaded_file is not None:
            df = data_loader.load_csv_data(uploaded_file)
            if df is not None:
                st.session_state.data = df
                st.success("✅ CSV data loaded successfully!")
    
    else:  # Sample Data
        if st.sidebar.button("Load Sample Data"):
            df = data_loader.load_sample_data()
            st.session_state.data = df
            st.success("✅ Sample data loaded successfully!")
    
    # Check if data is loaded
    if 'data' not in st.session_state:
        st.info("👈 Please select a data source from the sidebar to get started!")
        return
    
    df = st.session_state.data
    
    # Data overview section
    st.markdown('<h2 class="section-header">📊 Data Overview</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Data Points", len(df))
    with col2:
        st.metric("Date Range", f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
    with col3:
        st.metric("Mean Value", f"{df.iloc[:, 0].mean():.2f}")
    with col4:
        st.metric("Std Deviation", f"{df.iloc[:, 0].std():.2f}")
    
    # Display raw data
    st.subheader("📋 Raw Data Preview")
    st.dataframe(df.head(10), use_container_width=True)
    
    # Time series plot
    st.subheader("📈 Time Series Visualization")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df.iloc[:, 0],
        mode='lines',
        name='Time Series',
        line=dict(color='#1f77b4', width=2)
    ))
    fig.update_layout(
        title="Time Series Data",
        xaxis_title="Date",
        yaxis_title="Value",
        height=500,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Model selection and parameters
    st.markdown('<h2 class="section-header">🤖 Model Configuration</h2>', unsafe_allow_html=True)
    
    model_choice = st.selectbox(
        "Select Forecasting Model",
        ["ARIMA", "SARIMA", "Compare All Models"]
    )
    
    # Forecasting parameters
    st.sidebar.markdown("### ⚙️ Forecasting Parameters")
    forecast_periods = st.sidebar.slider("Forecast Periods", 10, 100, 30)
    confidence_interval = st.sidebar.slider("Confidence Interval", 80, 99, 95)
    
    # Model-specific parameters
    if model_choice in ["ARIMA", "SARIMA"]:
        st.sidebar.markdown("### 🔧 ARIMA/SARIMA Parameters")
        auto_params = st.sidebar.checkbox("Auto Parameter Selection", value=True)
        
        if not auto_params:
            col1, col2, col3 = st.sidebar.columns(3)
            with col1:
                p = st.number_input("p (AR)", 0, 5, 1)
            with col2:
                d = st.number_input("d (I)", 0, 3, 1)
            with col3:
                q = st.number_input("q (MA)", 0, 5, 1)
            
            if model_choice == "SARIMA":
                st.sidebar.markdown("#### Seasonal Parameters")
                col1, col2, col3 = st.sidebar.columns(3)
                with col1:
                    P = st.number_input("P (Seasonal AR)", 0, 3, 1)
                with col2:
                    D = st.number_input("D (Seasonal I)", 0, 2, 1)
                with col3:
                    Q = st.number_input("Q (Seasonal MA)", 0, 3, 1)
                seasonal_period = st.sidebar.number_input("Seasonal Period", 2, 52, 12)
    
    # Run forecasting
    if st.button("🚀 Run Forecasting", type="primary"):
        with st.spinner("Training models and generating forecasts..."):
            
            if model_choice == "ARIMA":
                # ARIMA Model
                st.markdown('<h2 class="section-header">🔮 ARIMA Forecast</h2>', unsafe_allow_html=True)
                
                arima_model = ARIMAForecaster()
                if auto_params:
                    arima_results = arima_model.auto_fit_forecast(df, forecast_periods, confidence_interval)
                else:
                    arima_results = arima_model.fit_forecast(df, (p, d, q), forecast_periods, confidence_interval)
                
                if arima_results:
                    create_forecast_plots(df, arima_results, "ARIMA", forecast_periods)
                    
                    # Model metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("AIC", f"{arima_results['aic']:.2f}")
                    with col2:
                        st.metric("BIC", f"{arima_results['bic']:.2f}")
                    with col3:
                        st.metric("RMSE", f"{arima_results['rmse']:.2f}")
                    with col4:
                        st.metric("MAPE", f"{arima_results['mape']:.2f}%")
            
            elif model_choice == "SARIMA":
                # SARIMA Model
                st.markdown('<h2 class="section-header">🔮 SARIMA Forecast</h2>', unsafe_allow_html=True)
                
                sarima_model = SARIMAForecaster()
                if auto_params:
                    sarima_results = sarima_model.auto_fit_forecast(df, forecast_periods, confidence_interval)
                else:
                    sarima_results = sarima_model.fit_forecast(
                        df, (p, d, q), (P, D, Q, seasonal_period), forecast_periods, confidence_interval
                    )
                
                if sarima_results:
                    create_forecast_plots(df, sarima_results, "SARIMA", forecast_periods)
                    
                    # Model metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("AIC", f"{sarima_results['aic']:.2f}")
                    with col2:
                        st.metric("BIC", f"{sarima_results['bic']:.2f}")
                    with col3:
                        st.metric("RMSE", f"{sarima_results['rmse']:.2f}")
                    with col4:
                        st.metric("MAPE", f"{sarima_results['mape']:.2f}%")
            
            # Prophet model removed due to PyArrow dependency issues
            elif model_choice == "Compare All Models":
                # Compare all models
                st.markdown('<h2 class="section-header">🏆 Model Comparison</h2>', unsafe_allow_html=True)
                
                models_results = {}
                
                # ARIMA
                arima_model = ARIMAForecaster()
                arima_results = arima_model.auto_fit_forecast(df, forecast_periods, confidence_interval)
                if arima_results:
                    models_results['ARIMA'] = arima_results
                
                # SARIMA
                sarima_model = SARIMAForecaster()
                sarima_results = sarima_model.auto_fit_forecast(df, forecast_periods, confidence_interval)
                if sarima_results:
                    models_results['SARIMA'] = sarima_results
                
                # Prophet removed due to PyArrow dependency issues
                
                if models_results:
                    create_model_comparison(df, models_results, forecast_periods)
                    
                    # Comparison metrics table
                    st.subheader("📊 Model Performance Comparison")
                    comparison_df = pd.DataFrame({
                        'Model': list(models_results.keys()),
                        'RMSE': [results.get('rmse', 0) for results in models_results.values()],
                        'MAPE': [results.get('mape', 0) for results in models_results.values()],
                        'AIC': [results.get('aic', 0) for results in models_results.values()],
                        'BIC': [results.get('bic', 0) for results in models_results.values()]
                    })
                    st.dataframe(comparison_df, use_container_width=True)

if __name__ == "__main__":
    main()
