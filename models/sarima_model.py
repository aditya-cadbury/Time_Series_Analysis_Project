import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.metrics import mean_squared_error, mean_absolute_error
import itertools
import warnings
warnings.filterwarnings('ignore')

class SARIMAForecaster:
    """SARIMA model implementation for seasonal time series forecasting."""
    
    def __init__(self):
        self.model = None
        self.fitted_model = None
        self.results = None
    
    def detect_seasonality(self, series, max_period=24):
        """
        Detect seasonal period using autocorrelation.
        
        Args:
            series (pd.Series): Time series data
            max_period (int): Maximum period to check for seasonality
        
        Returns:
            int: Detected seasonal period
        """
        # Calculate autocorrelation for different lags
        autocorr = series.autocorr(lag=1)  # noqa: F841
        
        # Check for strong autocorrelation at potential seasonal periods
        potential_periods = [4, 12, 24, 52]  # Common seasonal periods
        
        for period in potential_periods:
            if period <= len(series) // 2:
                lag_autocorr = series.autocorr(lag=period)
                if abs(lag_autocorr) > 0.3:  # Threshold for significant seasonality
                    return period
        
        # If no clear seasonality, use default
        return 12
    
    def find_optimal_parameters(self, series, seasonal_period=12, max_p=3, max_q=3, max_P=2, max_Q=2, max_d=2, max_D=1):
        """
        Find optimal SARIMA parameters using grid search with AIC.
        
        Args:
            series (pd.Series): Time series data
            seasonal_period (int): Seasonal period
            max_p (int): Maximum AR order
            max_q (int): Maximum MA order
            max_P (int): Maximum seasonal AR order
            max_Q (int): Maximum seasonal MA order
            max_d (int): Maximum differencing order
            max_D (int): Maximum seasonal differencing order
        
        Returns:
            tuple: (best_order, best_seasonal_order, best_aic)
        """
        best_aic = float('inf')
        best_order = None
        best_seasonal_order = None
        
        # Generate parameter combinations
        p_values = range(0, max_p + 1)
        d_values = range(0, max_d + 1)
        q_values = range(0, max_q + 1)
        
        P_values = range(0, max_P + 1)
        D_values = range(0, max_D + 1)
        Q_values = range(0, max_Q + 1)
        
        # Limit combinations to avoid excessive computation
        param_combinations = []
        for p, d, q in itertools.product(p_values, d_values, q_values):
            if p + d + q <= 4:  # Limit non-seasonal parameters
                for P, D, Q in itertools.product(P_values, D_values, Q_values):
                    if P + D + Q <= 3:  # Limit seasonal parameters
                        param_combinations.append(((p, d, q), (P, D, Q, seasonal_period)))
        
        # Try each combination
        for order, seasonal_order in param_combinations:
            try:
                model = SARIMAX(series, order=order, seasonal_order=seasonal_order)
                fitted_model = model.fit(disp=False, maxiter=50)
                aic = fitted_model.aic
                
                if aic < best_aic:
                    best_aic = aic
                    best_order = order
                    best_seasonal_order = seasonal_order
                    
            except:  # noqa: E722
                continue
        
        return best_order if best_order else (1, 1, 1), best_seasonal_order if best_seasonal_order else (1, 1, 1, seasonal_period)
    
    def fit_forecast(self, df, order, seasonal_order, forecast_periods=30, confidence_level=95):
        """
        Fit SARIMA model and generate forecasts.
        
        Args:
            df (pd.DataFrame): Time series data
            order (tuple): SARIMA order (p, d, q)
            seasonal_order (tuple): Seasonal order (P, D, Q, s)
            forecast_periods (int): Number of periods to forecast
            confidence_level (int): Confidence level for prediction intervals
        
        Returns:
            dict: Model results and forecasts
        """
        try:
            # Extract the first column
            series = df.iloc[:, 0]
            
            # Fit SARIMA model
            model = SARIMAX(series, order=order, seasonal_order=seasonal_order)
            fitted_model = model.fit(disp=False, maxiter=100)
            
            # Generate forecasts
            forecast_result = fitted_model.get_forecast(steps=forecast_periods)
            forecast_mean = forecast_result.predicted_mean
            forecast_ci = forecast_result.conf_int()
            
            # Calculate fitted values and residuals
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
                # Determine frequency for forecast dates
                freq = pd.infer_freq(df.index) or 'D'
                forecast_dates = pd.date_range(start=last_date, periods=forecast_periods + 1, freq=freq)[1:]
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
                'seasonal_order': seasonal_order,
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
            print(f"Error fitting SARIMA model: {str(e)}")
            return None
    
    def auto_fit_forecast(self, df, forecast_periods=30, confidence_level=95, max_p=3, max_q=3, max_P=2, max_Q=2):
        """
        Automatically find optimal parameters and fit SARIMA model.
        
        Args:
            df (pd.DataFrame): Time series data
            forecast_periods (int): Number of periods to forecast
            confidence_level (int): Confidence level for prediction intervals
            max_p (int): Maximum AR order
            max_q (int): Maximum MA order
            max_P (int): Maximum seasonal AR order
            max_Q (int): Maximum seasonal MA order
        
        Returns:
            dict: Model results and forecasts
        """
        try:
            # Extract the first column
            series = df.iloc[:, 0]
            
            # Detect seasonality
            seasonal_period = self.detect_seasonality(series)
            
            # Find optimal parameters
            optimal_order, optimal_seasonal_order = self.find_optimal_parameters(
                series, seasonal_period, max_p, max_q, max_P, max_Q
            )
            
            # Fit model with optimal parameters
            return self.fit_forecast(df, optimal_order, optimal_seasonal_order, forecast_periods, confidence_level)
            
        except Exception as e:
            print(f"Error in auto SARIMA fitting: {str(e)}")
            return None
    
    def seasonal_decomposition(self, series, model='additive', period=12):
        """
        Perform seasonal decomposition.
        
        Args:
            series (pd.Series): Time series data
            model (str): Decomposition model ('additive' or 'multiplicative')
            period (int): Seasonal period
        
        Returns:
            dict: Decomposition results
        """
        try:
            decomposition = seasonal_decompose(series, model=model, period=period)
            
            decomposition_results = {
                'observed': decomposition.observed,
                'trend': decomposition.trend,
                'seasonal': decomposition.seasonal,
                'residual': decomposition.resid,
                'model': model,
                'period': period
            }
            
            return decomposition_results
            
        except Exception as e:
            print(f"Error in seasonal decomposition: {str(e)}")
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
            'seasonal_order': self.results['seasonal_order'],
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
        try:
            lb_stat, lb_pvalue = acorr_ljungbox(residuals, lags=10, return_df=False)
            ljung_box_stat = lb_stat[0] if len(lb_stat) > 0 else 0
            ljung_box_pvalue = lb_pvalue[0] if len(lb_pvalue) > 0 else 1
        except:  # noqa: E722
            ljung_box_stat = 0
            ljung_box_pvalue = 1
        
        analysis = {
            'residuals_mean': residuals.mean(),
            'residuals_std': residuals.std(),
            'ljung_box_stat': ljung_box_stat,
            'ljung_box_pvalue': ljung_box_pvalue,
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
        
        ax.set_title(f'SARIMA{self.results["order"]}x{self.results["seasonal_order"]} Forecast')
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def plot_seasonal_decomposition(self, df, period=12):
        """
        Plot seasonal decomposition.
        
        Args:
            df (pd.DataFrame): Time series data
            period (int): Seasonal period
        
        Returns:
            matplotlib.figure.Figure: Decomposition plot
        """
        series = df.iloc[:, 0]
        decomposition = self.seasonal_decomposition(series, period=period)
        
        if decomposition is None:
            return None
        
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(4, 1, figsize=(12, 10))
        
        # Original series
        axes[0].plot(decomposition['observed'].index, decomposition['observed'], color='blue')
        axes[0].set_title('Original Series')
        axes[0].grid(True, alpha=0.3)
        
        # Trend
        axes[1].plot(decomposition['trend'].index, decomposition['trend'], color='green')
        axes[1].set_title('Trend Component')
        axes[1].grid(True, alpha=0.3)
        
        # Seasonal
        axes[2].plot(decomposition['seasonal'].index, decomposition['seasonal'], color='orange')
        axes[2].set_title('Seasonal Component')
        axes[2].grid(True, alpha=0.3)
        
        # Residual
        axes[3].plot(decomposition['residual'].index, decomposition['residual'], color='red')
        axes[3].set_title('Residual Component')
        axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
