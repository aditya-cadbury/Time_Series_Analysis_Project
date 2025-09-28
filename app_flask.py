from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np  # noqa: F401
import json  # noqa: F401
from datetime import datetime, timedelta  # noqa: F401
import warnings
import logging
warnings.filterwarnings('ignore')
# Import our existing models
from models.arima_model import ARIMAForecaster  # noqa: E402
from models.sarima_model import SARIMAForecaster  # noqa: E402
# from models.prophet_model import ProphetForecaster  # Commented out due to PyArrow issues
from utils.data_loader import DataLoader  # noqa: E402

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5000', 'http://127.0.0.1:5000'])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize models and data loader
data_loader = DataLoader()
arima_forecaster = ARIMAForecaster()
sarima_forecaster = SARIMAForecaster()
# prophet_forecaster = ProphetForecaster()  # Commented out due to PyArrow issues

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/load_stock_data', methods=['POST'])
def api_load_stock_data():
    """API endpoint to load stock data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        ticker = data.get('ticker', 'AAPL')
        period = data.get('period', '1y')
        
        # Validate ticker format
        if not ticker or not isinstance(ticker, str) or len(ticker) > 10:
            return jsonify({'error': 'Invalid ticker symbol'}), 400
            
        # Validate period
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        if period not in valid_periods:
            return jsonify({'error': f'Invalid period. Must be one of: {valid_periods}'}), 400
        
        # Load stock data using our existing data loader
        df = data_loader.load_stock_data(ticker, period)
        
        if df is None:
            return jsonify({'error': 'Failed to load stock data'}), 400
        
        # Convert to JSON-serializable format
        result = {
            'dates': [date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date) for date in df.index],
            'values': df.iloc[:, 0].tolist(),
            'ticker': ticker,
            'period': period,
            'data_points': len(df)
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in load_stock_data: {str(e)}")
        return jsonify({'error': f'Failed to load stock data: {str(e)}'}), 500

@app.route('/api/load_sample_data', methods=['GET'])
def api_load_sample_data():
    """API endpoint to load sample data"""
    try:
        # Load sample data using our existing data loader
        df = data_loader.load_sample_data()
        
        # Convert to JSON-serializable format
        result = {
            'dates': [date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date) for date in df.index],
            'values': df.iloc[:, 0].tolist(),
            'ticker': 'SAMPLE',
            'period': 'generated',
            'data_points': len(df)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/load_csv_data', methods=['POST'])
def api_load_csv_data():
    """API endpoint to load CSV data"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read CSV file
        df = pd.read_csv(file)
        
        # Process the CSV data using data_loader for consistency
        try:
            df = data_loader.load_csv_data(file)
            if df is None:
                return jsonify({'error': 'Failed to process CSV file'}), 400
        except Exception as csv_error:
            return jsonify({'error': f'CSV processing error: {str(csv_error)}'}), 400
        
        # Convert to JSON-serializable format
        result = {
            'dates': [date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date) for date in df.index],
            'values': df.iloc[:, 0].tolist(),
            'ticker': 'CSV_DATA',
            'period': 'uploaded',
            'data_points': len(df)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/forecast', methods=['POST'])
def api_forecast():
    """API endpoint to run forecasting"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract and validate parameters
        model = data.get('model', 'arima')
        time_series_data = data.get('data')
        forecast_periods = data.get('forecast_periods', 30)
        confidence_interval = data.get('confidence_interval', 95)
        auto_params = data.get('auto_params', True)
        fast_mode = data.get('fast_mode', True)
        
        # Validate required data
        if not time_series_data:
            return jsonify({'error': 'Time series data is required'}), 400
            
        if not isinstance(time_series_data, dict) or 'values' not in time_series_data or 'dates' not in time_series_data:
            return jsonify({'error': 'Invalid time series data format'}), 400
            
        # Validate parameters
        if not isinstance(forecast_periods, int) or forecast_periods < 1 or forecast_periods > 1000:
            return jsonify({'error': 'Forecast periods must be between 1 and 1000'}), 400
            
        if not isinstance(confidence_interval, (int, float)) or confidence_interval < 50 or confidence_interval > 99:
            return jsonify({'error': 'Confidence interval must be between 50 and 99'}), 400
            
        # Validate model type
        valid_models = ['arima', 'sarima', 'prophet', 'compare']
        if model not in valid_models:
            return jsonify({'error': f'Invalid model. Must be one of: {valid_models}'}), 400
        
        # Convert data to DataFrame with error handling
        try:
            df = pd.DataFrame({
                'value': time_series_data['values']
            }, index=pd.to_datetime(time_series_data['dates']))
            
            # Validate DataFrame
            if df.empty or len(df) < 10:
                return jsonify({'error': 'Insufficient data points. Need at least 10 data points for forecasting.'}), 400
                
        except Exception as df_error:
            return jsonify({'error': f'Data conversion error: {str(df_error)}'}), 400
        
        results = {}
        
        # In fast mode, cap the training window to keep response time reasonable
        if fast_mode and len(df) > 500:
            logger.info(f"Fast mode enabled: using last 500 points out of {len(df)}")
            df = df.tail(500)

        if model == 'arima':
            if auto_params:
                # Reduce search space in fast mode
                if fast_mode:
                    results = arima_forecaster.auto_fit_forecast(
                        df, forecast_periods, confidence_interval, max_p=3, max_q=3
                    )
                else:
                    results = arima_forecaster.auto_fit_forecast(df, forecast_periods, confidence_interval)
            else:
                manual_params = data.get('manual_params', {})
                order = (manual_params.get('p', 1), manual_params.get('d', 1), manual_params.get('q', 1))
                results = arima_forecaster.fit_forecast(df, order, forecast_periods, confidence_interval)
                
        elif model == 'sarima':
            if auto_params:
                if fast_mode:
                    results = sarima_forecaster.auto_fit_forecast(
                        df, forecast_periods, confidence_interval, max_p=2, max_q=2, max_P=1, max_Q=1
                    )
                else:
                    results = sarima_forecaster.auto_fit_forecast(df, forecast_periods, confidence_interval)
            else:
                manual_params = data.get('manual_params', {})
                seasonal_params = data.get('seasonal_params', {})
                order = (manual_params.get('p', 1), manual_params.get('d', 1), manual_params.get('q', 1))
                seasonal_order = (
                    seasonal_params.get('P', 1), seasonal_params.get('D', 1), 
                    seasonal_params.get('Q', 1), seasonal_params.get('period', 12)
                )
                results = sarima_forecaster.fit_forecast(df, order, seasonal_order, forecast_periods, confidence_interval)
                
        elif model == 'prophet':
            # Prophet model removed due to PyArrow dependency issues
            return jsonify({'error': 'Prophet model not available due to dependency issues'}), 400
            
        elif model == 'compare':
            # Run all models and compare
            results = {
                'models': {},
                'comparison': {}
            }
            
            # ARIMA
            try:
                arima_results = arima_forecaster.auto_fit_forecast(df, forecast_periods, confidence_interval)
                if arima_results:
                    results['models']['ARIMA'] = arima_results
            except:  # noqa: E722
                pass
            
            # SARIMA
            try:
                sarima_results = sarima_forecaster.auto_fit_forecast(df, forecast_periods, confidence_interval)
                if sarima_results:
                    results['models']['SARIMA'] = sarima_results
            except:  # noqa: E722
                pass
            
            # Prophet removed due to PyArrow dependency issues
        
        if not results:
            return jsonify({'error': 'Forecasting failed'}), 500
        
        # Convert results to JSON-serializable format
        json_results = convert_results_to_json(results, model)
        
        return jsonify(json_results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def convert_results_to_json(results, model):
    """Convert model results to JSON-serializable format"""
    if model == 'compare':
        # Handle comparison results
        json_results = {
            'model': 'compare',
            'models': {},
            'comparison': {}
        }
        
        for model_name, model_results in results['models'].items():
            json_results['models'][model_name] = convert_single_result(model_results, model_name=model_name.lower())
        
        return json_results
    else:
        return convert_single_result(results, model_name=model)

def convert_single_result(results, model_name=None):
    """Convert single model results to JSON format"""
    try:
        # Extract forecast data
        forecast_df = results['forecast']
        
        json_result = {
            # Use model name string for the frontend mapping
            'model': model_name or 'unknown',
            'forecast': {
                'dates': [date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date) 
                         for date in forecast_df.index],
                'values': forecast_df['forecast'].tolist() if 'forecast' in forecast_df.columns else forecast_df['yhat'].tolist(),
                'lower_bound': forecast_df['lower_bound'].tolist() if 'lower_bound' in forecast_df.columns else forecast_df['yhat_lower'].tolist(),
                'upper_bound': forecast_df['upper_bound'].tolist() if 'upper_bound' in forecast_df.columns else forecast_df['yhat_upper'].tolist()
            },
            'metrics': {
                'rmse': results.get('rmse', 0),
                'mae': results.get('mae', 0),
                'mape': results.get('mape', 0),
                'aic': results.get('aic', 0),
                'bic': results.get('bic', 0),
                'r2': results.get('r2', 0)
            },
            'fitted_values': results['fitted_values'].tolist() if 'fitted_values' in results else [],
            'residuals': results['residuals'].tolist() if 'residuals' in results else []
        }
        
        return json_result
        
    except Exception as e:
        print(f"Error converting results: {e}")
        return {
            'model': 'unknown',
            'forecast': {'dates': [], 'values': [], 'lower_bound': [], 'upper_bound': []},
            'metrics': {'rmse': 0, 'mae': 0, 'mape': 0, 'aic': 0, 'bic': 0, 'r2': 0},
            'fitted_values': [],
            'residuals': []
        }

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation endpoint"""
    docs = {
        'endpoints': {
            '/api/load_stock_data': {
                'method': 'POST',
                'description': 'Load stock data from Yahoo Finance',
                'parameters': {
                    'ticker': 'Stock symbol (e.g., AAPL)',
                    'period': 'Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)'
                }
            },
            '/api/load_sample_data': {
                'method': 'GET',
                'description': 'Load sample time series data'
            },
            '/api/load_csv_data': {
                'method': 'POST',
                'description': 'Upload and process CSV file',
                'parameters': {
                    'file': 'CSV file with date and value columns'
                }
            },
            '/api/forecast': {
                'method': 'POST',
                'description': 'Run forecasting models',
                'parameters': {
                    'model': 'Model type (arima, sarima, compare)',
                    'data': 'Time series data with dates and values',
                    'forecast_periods': 'Number of periods to forecast (1-1000)',
                    'confidence_interval': 'Confidence interval (50-99)',
                    'auto_params': 'Use automatic parameter selection (boolean)'
                }
            },
            '/api/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            }
        },
        'available_models': ['ARIMA', 'SARIMA'],
        'note': 'Prophet model is temporarily disabled due to dependency issues'
    }
    return jsonify(docs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
