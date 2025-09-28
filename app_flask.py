from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np  # noqa: F401
import json  # noqa: F401
from datetime import datetime, timedelta  # noqa: F401
import warnings
warnings.filterwarnings('ignore')
# Import our existing models
from models.arima_model import ARIMAForecaster  # noqa: E402
from models.sarima_model import SARIMAForecaster  # noqa: E402
from models.prophet_model import ProphetForecaster  # noqa: E402
from utils.data_loader import DataLoader  # noqa: E402

app = Flask(__name__)
CORS(app)

# Initialize models and data loader
data_loader = DataLoader()
arima_forecaster = ARIMAForecaster()
sarima_forecaster = SARIMAForecaster()
prophet_forecaster = ProphetForecaster()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/load_stock_data', methods=['POST'])
def api_load_stock_data():
    """API endpoint to load stock data"""
    try:
        data = request.get_json()
        ticker = data.get('ticker', 'AAPL')
        period = data.get('period', '1y')
        
        # Load stock data using our existing data loader
        df = data_loader.load_stock_data(ticker, period)
        
        if df is None:
            return jsonify({'error': 'Failed to load stock data'}), 400
        
        # Convert to JSON-serializable format
        result = {
            'dates': [date.strftime('%Y-%m-%d') for date in df.index],
            'values': df.iloc[:, 0].tolist(),
            'ticker': ticker,
            'period': period
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/load_sample_data', methods=['GET'])
def api_load_sample_data():
    """API endpoint to load sample data"""
    try:
        # Load sample data using our existing data loader
        df = data_loader.load_sample_data()
        
        # Convert to JSON-serializable format
        result = {
            'dates': [date.strftime('%Y-%m-%d') for date in df.index],
            'values': df.iloc[:, 0].tolist(),
            'ticker': 'SAMPLE',
            'period': 'generated'
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
        
        # Process the CSV data (simplified - you might want to use your data_loader)
        # Assume first column is date, second is value
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
        df.set_index(df.iloc[:, 0], inplace=True)
        df = df.iloc[:, [1]]  # Take second column as values
        
        # Convert to JSON-serializable format
        result = {
            'dates': [date.strftime('%Y-%m-%d') for date in df.index],
            'values': df.iloc[:, 0].tolist(),
            'ticker': 'CSV_DATA',
            'period': 'uploaded'
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/forecast', methods=['POST'])
def api_forecast():
    """API endpoint to run forecasting"""
    try:
        data = request.get_json()
        
        # Extract parameters
        model = data.get('model', 'arima')
        time_series_data = data.get('data')
        forecast_periods = data.get('forecast_periods', 30)
        confidence_interval = data.get('confidence_interval', 95)
        auto_params = data.get('auto_params', True)
        
        # Convert data to DataFrame
        df = pd.DataFrame({
            'value': time_series_data['values']
        }, index=pd.to_datetime(time_series_data['dates']))
        
        results = {}
        
        if model == 'arima':
            if auto_params:
                results = arima_forecaster.auto_fit_forecast(df, forecast_periods, confidence_interval)
            else:
                manual_params = data.get('manual_params', {})
                order = (manual_params.get('p', 1), manual_params.get('d', 1), manual_params.get('q', 1))
                results = arima_forecaster.fit_forecast(df, order, forecast_periods, confidence_interval)
                
        elif model == 'sarima':
            if auto_params:
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
            results = prophet_forecaster.fit_forecast(df, forecast_periods, confidence_interval)
            
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
            
            # Prophet
            try:
                prophet_results = prophet_forecaster.fit_forecast(df, forecast_periods, confidence_interval)
                if prophet_results:
                    results['models']['Prophet'] = prophet_results
            except:  # noqa: E722
                pass
        
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
            json_results['models'][model_name] = convert_single_result(model_results)
        
        return json_results
    else:
        return convert_single_result(results)

def convert_single_result(results):
    """Convert single model results to JSON format"""
    try:
        # Extract forecast data
        forecast_df = results['forecast']
        
        json_result = {
            'model': results.get('order', 'unknown'),
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
