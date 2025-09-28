import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose  # noqa: F401
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.metrics import mean_squared_error, mean_absolute_error
import itertools
import warnings
warnings.filterwarnings('ignore')

class ARIMAForecaster:
    """ARIMA model implementation for time series forecasting."""
    
    def __init__(self):
        self.model = None
        self.fitted_model = None
        self.results = None
    
    def check_stationarity(self, series):
        """
        Check if the time series is stationary using Augmented Dickey-Fuller test.
        
        Args:
            series (pd.Series): Time series data
        
        Returns:
            tuple: (is_stationary, p_value, test_statistic)
        """
        result = adfuller(series.dropna())
        p_value = result[1]
        test_statistic = result[0]
        is_stationary = p_value < 0.05
        
        return is_stationary, p_value, test_statistic
    
    def make_stationary(self, series, max_diff=3):
        """
        Make time series stationary by differencing.
        
        Args:
            series (pd.Series): Time series data
            max_diff (int): Maximum number of differences to apply
        
        Returns:
            tuple: (stationary_series, d_value)
        """
        d = 0
        current_series = series.copy()
        
        while d < max_diff:
            is_stationary, _, _ = self.check_stationarity(current_series)
            if is_stationary:
                break
            current_series = current_series.diff().dropna()
            d += 1
        
        return current_series, d
    
    def find_optimal_parameters(self, series, max_p=5, max_q=5, max_d=3):
        """
        Find optimal ARIMA parameters using grid search with AIC.
        
        Args:
            series (pd.Series): Time series data
            max_p (int): Maximum AR order
            max_q (int): Maximum MA order
            max_d (int): Maximum differencing order
        
        Returns:
            tuple: (best_p, best_d, best_q, best_aic)
        """
        best_aic = float('inf')
        best_params = None
        
        # Generate all combinations of p, d, q
        p_values = range(0, max_p + 1)
        d_values = range(0, max_d + 1)
        q_values = range(0, max_q + 1)
        
        for p, d, q in itertools.product(p_values, d_values, q_values):
            try:
                model = ARIMA(series, order=(p, d, q))
                fitted_model = model.fit()
                aic = fitted_model.aic
                
                if aic < best_aic:
                    best_aic = aic
                    best_params = (p, d, q)
                    
            except:  # noqa: E722
                continue
        
        return best_params if best_params else (1, 1, 1)
    
    def fit_forecast(self, df, order, forecast_periods=30, confidence_level=95):
        """
        Fit ARIMA model and generate forecasts.
        
        Args:
            df (pd.DataFrame): Time series data
            order (tuple): ARIMA order (p, d, q)
            forecast_periods (int): Number of periods to forecast
            confidence_level (int): Confidence level for prediction intervals
        
        Returns:
            dict: Model results and forecasts
        """
        try:
            # Extract the first column (assuming single time series)
            series = df.iloc[:, 0]
            
            # Fit ARIMA model
            model = ARIMA(series, order=order)
            fitted_model = model.fit()
            
            # Generate forecasts
            forecast_result = fitted_model.get_forecast(steps=forecast_periods)
            forecast_mean = forecast_result.predicted_mean
            forecast_ci = forecast_result.conf_int()
            
            # Calculate metrics
            fitted_values = fitted_model.fittedvalues
            residuals = fitted_model.resid
            
            # Calculate performance metrics
            mse = mean_squared_error(series.iloc[1:], fitted_values.iloc[1:])
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(series.iloc[1:], fitted_values.iloc[1:])
            
            # Calculate MAPE
            actual = series.iloc[1:]
            fitted = fitted_values.iloc[1:]
            mape = np.mean(np.abs((actual - fitted) / actual)) * 100
            
            # Create forecast dataframe
            last_date = df.index[-1]
            if isinstance(last_date, pd.Timestamp):
                forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_periods)
            else:
                forecast_dates = range(len(df), len(df) + forecast_periods)
            
            forecast_df = pd.DataFrame({
                'forecast': forecast_mean.values,
                'lower_bound': forecast_ci.iloc[:, 0].values,
                'upper_bound': forecast_ci.iloc[:, 1].values
            }, index=forecast_dates)
            
            # Store results
            self.results = {
                'model': fitted_model,
                'order': order,
                'forecast': forecast_df,
                'fitted_values': fitted_values,
                'residuals': residuals,
                'aic': fitted_model.aic,
                'bic': fitted_model.bic,
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'mape': mape,
                'summary': fitted_model.summary()
            }
            
            return self.results
            
        except Exception as e:
            print(f"Error fitting ARIMA model: {str(e)}")
            return None
    
    def auto_fit_forecast(self, df, forecast_periods=30, confidence_level=95, max_p=5, max_q=5):
        """
        Automatically find optimal parameters and fit ARIMA model.
        
        Args:
            df (pd.DataFrame): Time series data
            forecast_periods (int): Number of periods to forecast
            confidence_level (int): Confidence level for prediction intervals
            max_p (int): Maximum AR order
            max_q (int): Maximum MA order
        
        Returns:
            dict: Model results and forecasts
        """
        try:
            # Extract the first column
            series = df.iloc[:, 0]
            
            # Find optimal parameters
            optimal_params = self.find_optimal_parameters(series, max_p, max_q)
            
            # Fit model with optimal parameters
            return self.fit_forecast(df, optimal_params, forecast_periods, confidence_level)
            
        except Exception as e:
            print(f"Error in auto ARIMA fitting: {str(e)}")
            return None
    
    def get_model_diagnostics(self):
        """
        Get model diagnostic information.
        
        Returns:
            dict: Diagnostic information
        """
        if self.results is None:
            return None
        
        diagnostics = {
            'aic': self.results['aic'],
            'bic': self.results['bic'],
            'order': self.results['order'],
            'log_likelihood': self.results['model'].llf,
            'residuals_mean': self.results['residuals'].mean(),
            'residuals_std': self.results['residuals'].std()
        }
        
        return diagnostics
    
    def get_residual_analysis(self):
        """
        Perform residual analysis.
        
        Returns:
            dict: Residual analysis results
        """
        if self.results is None:
            return None
        
        residuals = self.results['residuals']
        
        # Ljung-Box test for residual autocorrelation
        lb_stat, lb_pvalue = acorr_ljungbox(residuals, lags=10, return_df=False)
        
        analysis = {
            'residuals_mean': residuals.mean(),
            'residuals_std': residuals.std(),
            'ljung_box_stat': lb_stat[0],
            'ljung_box_pvalue': lb_pvalue[0],
            'residuals_autocorr': residuals.autocorr(lag=1)
        }
        
        return analysis
    
    def plot_forecast(self, df, forecast_periods=30):
        """
        Plot the original data, fitted values, and forecast.
        
        Args:
            df (pd.DataFrame): Original time series data
            forecast_periods (int): Number of forecast periods to show
        
        Returns:
            matplotlib.figure.Figure: Plot figure
        """
        if self.results is None:
            return None
        
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot original data
        ax.plot(df.index, df.iloc[:, 0], label='Original Data', color='blue', alpha=0.7)
        
        # Plot fitted values
        fitted_values = self.results['fitted_values']
        ax.plot(fitted_values.index, fitted_values, label='Fitted Values', color='green', alpha=0.8)
        
        # Plot forecast
        forecast_df = self.results['forecast']
        ax.plot(forecast_df.index, forecast_df['forecast'], label='Forecast', color='red', linewidth=2)
        
        # Plot confidence intervals
        ax.fill_between(
            forecast_df.index,
            forecast_df['lower_bound'],
            forecast_df['upper_bound'],
            alpha=0.3,
            color='red',
            label='Confidence Interval'
        )
        
        ax.set_title(f'ARIMA{self.results["order"]} Forecast')
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
