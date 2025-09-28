import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import io
import warnings
warnings.filterwarnings('ignore')

class DataLoader:
    """Class for loading and preprocessing time series data from various sources."""
    
    def __init__(self):
        self.data = None
    
    def load_stock_data(self, ticker, period="1y"):
        """
        Load stock data from Yahoo Finance.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
            period (str): Time period ('1y', '2y', '5y', '10y', 'max')
        
        Returns:
            pd.DataFrame: Stock data with date index and adjusted close price
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                print(f"No data found for ticker: {ticker}")
                return None
            
            # Use adjusted close price
            df = pd.DataFrame({
                'Close': hist['Close']
            })
            
            # Ensure proper datetime index
            df.index = pd.to_datetime(df.index)
            df.index.name = 'Date'
            
            return df
            
        except Exception as e:
            print(f"Error loading stock data for {ticker}: {str(e)}")
            return None
    
    def load_csv_data(self, uploaded_file):
        """
        Load time series data from uploaded CSV file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
        
        Returns:
            pd.DataFrame: Time series data
        """
        try:
            # Read CSV from uploaded file
            df = pd.read_csv(uploaded_file)
            
            # Try to identify date column
            date_columns = ['date', 'Date', 'DATE', 'timestamp', 'Timestamp', 'time', 'Time']
            date_col = None
            
            for col in date_columns:
                if col in df.columns:
                    date_col = col
                    break
            
            if date_col is None:
                # If no date column found, assume first column is date
                date_col = df.columns[0]
            
            # Convert date column to datetime
            df[date_col] = pd.to_datetime(df[date_col])
            df.set_index(date_col, inplace=True)
            df.index.name = 'Date'
            
            # Select numeric columns only
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df = df[numeric_cols]
            
            # If multiple columns, use the first one
            if len(df.columns) > 1:
                df = df.iloc[:, [0]]
            
            return df
            
        except Exception as e:
            print(f"Error loading CSV data: {str(e)}")
            return None
    
    def load_sample_data(self):
        """
        Load sample time series data for demonstration.
        
        Returns:
            pd.DataFrame: Sample time series data
        """
        # Generate sample data with trend, seasonality, and noise
        np.random.seed(42)
        
        # Create date range
        dates = pd.date_range(start='2020-01-01', end='2024-01-01', freq='D')
        
        # Generate trend component
        trend = np.linspace(100, 200, len(dates))
        
        # Generate seasonal component (annual seasonality)
        seasonal = 20 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
        
        # Generate noise
        noise = np.random.normal(0, 10, len(dates))
        
        # Combine components
        values = trend + seasonal + noise
        
        df = pd.DataFrame({
            'Value': values
        }, index=dates)
        
        df.index.name = 'Date'
        
        return df
    
    def load_economic_data(self):
        """
        Load sample economic time series data.
        
        Returns:
            pd.DataFrame: Economic time series data
        """
        # Generate economic data with business cycles
        np.random.seed(42)
        
        dates = pd.date_range(start='2010-01-01', end='2024-01-01', freq='M')
        
        # Economic growth with cycles
        trend = np.linspace(2.5, 3.2, len(dates))
        
        # Business cycle (8-year cycle)
        business_cycle = 0.5 * np.sin(2 * np.pi * np.arange(len(dates)) / (8 * 12))
        
        # Seasonal effects
        seasonal = 0.2 * np.sin(2 * np.pi * np.arange(len(dates)) / 12)
        
        # Random shocks
        noise = np.random.normal(0, 0.1, len(dates))
        
        # GDP growth rate
        gdp_growth = trend + business_cycle + seasonal + noise
        
        df = pd.DataFrame({
            'GDP_Growth': gdp_growth
        }, index=dates)
        
        df.index.name = 'Date'
        
        return df
    
    def load_temperature_data(self):
        """
        Load sample temperature time series data.
        
        Returns:
            pd.DataFrame: Temperature time series data
        """
        np.random.seed(42)
        
        # Daily data for 3 years
        dates = pd.date_range(start='2021-01-01', end='2024-01-01', freq='D')
        
        # Base temperature with warming trend
        base_temp = 15 + 0.02 * np.arange(len(dates)) / 365  # 2°C warming over 3 years
        
        # Strong annual seasonality
        seasonal = 15 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25 - np.pi/2)
        
        # Weekly patterns (weekends slightly warmer)
        weekly = 2 * np.sin(2 * np.pi * np.arange(len(dates)) / 7)
        
        # Random weather variations
        noise = np.random.normal(0, 3, len(dates))
        
        temperature = base_temp + seasonal + weekly + noise
        
        df = pd.DataFrame({
            'Temperature': temperature
        }, index=dates)
        
        df.index.name = 'Date'
        
        return df
    
    def preprocess_data(self, df):
        """
        Preprocess time series data for modeling.
        
        Args:
            df (pd.DataFrame): Input time series data
        
        Returns:
            pd.DataFrame: Preprocessed data
        """
        # Remove any missing values
        df = df.dropna()
        
        # Ensure numeric data
        df = df.select_dtypes(include=[np.number])
        
        # Sort by date
        df = df.sort_index()
        
        return df
    
    def get_data_info(self, df):
        """
        Get information about the loaded data.
        
        Args:
            df (pd.DataFrame): Time series data
        
        Returns:
            dict: Data information
        """
        info = {
            'length': len(df),
            'start_date': df.index[0],
            'end_date': df.index[-1],
            'frequency': pd.infer_freq(df.index),
            'columns': list(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'mean': df.mean().iloc[0],
            'std': df.std().iloc[0],
            'min': df.min().iloc[0],
            'max': df.max().iloc[0]
        }
        
        return info
