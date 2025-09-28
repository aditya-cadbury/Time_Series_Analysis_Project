import pandas as pd
import numpy as np
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly  # noqa: F401
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class ProphetForecaster:
    """Prophet model implementation for robust time series forecasting."""
    
    def __init__(self):
        self.model = None
        self.fitted_model = None
        self.results = None
    
    def prepare_data(self, df):
        """
        Prepare data for Prophet model.
        
        Args:
            df (pd.DataFrame): Time series data
        
        Returns:
            pd.DataFrame: Prophet-formatted data with 'ds' and 'y' columns
        """
        # Extract the first column
        series = df.iloc[:, 0]
        
        # Create Prophet dataframe
        prophet_df = pd.DataFrame({
            'ds': series.index,
            'y': series.values
        })
        
        # Ensure datetime index
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
        
        # Remove any missing values
        prophet_df = prophet_df.dropna()
        
        return prophet_df
    
    def fit_forecast(self, df, forecast_periods=30, confidence_level=95, 
                    yearly_seasonality='auto', weekly_seasonality='auto', 
                    daily_seasonality=False, seasonality_mode='additive'):
        """
        Fit Prophet model and generate forecasts.
        
        Args:
            df (pd.DataFrame): Time series data
            forecast_periods (int): Number of periods to forecast
            confidence_level (int): Confidence level for prediction intervals
            yearly_seasonality (str or bool): Yearly seasonality ('auto', True, False)
            weekly_seasonality (str or bool): Weekly seasonality ('auto', True, False)
            daily_seasonality (bool): Daily seasonality
            seasonality_mode (str): Seasonality mode ('additive' or 'multiplicative')
        
        Returns:
            dict: Model results and forecasts
        """
        try:
            # Prepare data for Prophet
            prophet_df = self.prepare_data(df)
            
            # Initialize Prophet model
            self.model = Prophet(
                interval_width=confidence_level/100,
                yearly_seasonality=yearly_seasonality,
                weekly_seasonality=weekly_seasonality,
                daily_seasonality=daily_seasonality,
                seasonality_mode=seasonality_mode,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0,
                holidays_prior_scale=10.0,
                changepoint_range=0.8
            )
            
            # Fit the model
            self.fitted_model = self.model.fit(prophet_df)
            
            # Create future dataframe
            last_date = prophet_df['ds'].max()  # noqa: F841
            
            # Determine frequency based on data
            freq = self._detect_frequency(prophet_df)
            
            future = self.model.make_future_dataframe(
                periods=forecast_periods, 
                freq=freq
            )
            
            # Generate forecast
            forecast = self.fitted_model.predict(future)
            
            # Extract forecast components
            forecast_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
            
            # Get only the forecasted period
            forecast_only = forecast_df.tail(forecast_periods).copy()
            forecast_only.set_index('ds', inplace=True)
            
            # Calculate fitted values (in-sample predictions)
            fitted_values = forecast['yhat'].iloc[:-forecast_periods].values
            fitted_dates = forecast['ds'].iloc[:-forecast_periods]
            
            # Calculate performance metrics
            actual_values = prophet_df['y'].values
            
            # Calculate metrics
            mse = mean_squared_error(actual_values, fitted_values)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(actual_values, fitted_values)
            
            # Calculate MAPE
            mape = np.mean(np.abs((actual_values - fitted_values) / actual_values)) * 100
            
            # Calculate R-squared
            r2 = r2_score(actual_values, fitted_values)
            
            # Create residuals
            residuals = actual_values - fitted_values
            
            # Store results
            self.results = {
                'model': self.model,
                'fitted_model': self.fitted_model,
                'forecast': forecast_only,
                'full_forecast': forecast,
                'fitted_values': pd.Series(fitted_values, index=fitted_dates),
                'residuals': pd.Series(residuals, index=fitted_dates),
                'actual_values': pd.Series(actual_values, index=prophet_df['ds']),
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'mape': mape,
                'r2': r2,
                'confidence_level': confidence_level,
                'forecast_periods': forecast_periods
            }
            
            return self.results
            
        except Exception as e:
            print(f"Error fitting Prophet model: {str(e)}")
            return None
    
    def _detect_frequency(self, prophet_df):
        """
        Detect the frequency of the time series data.
        
        Args:
            prophet_df (pd.DataFrame): Prophet-formatted data
        
        Returns:
            str: Detected frequency
        """
        # Calculate time differences
        time_diffs = prophet_df['ds'].diff().dropna()
        
        # Get the most common time difference
        most_common_diff = time_diffs.mode().iloc[0]
        
        # Convert to frequency string
        if most_common_diff == pd.Timedelta(days=1):
            return 'D'
        elif most_common_diff == pd.Timedelta(hours=1):
            return 'H'
        elif most_common_diff == pd.Timedelta(weeks=1):
            return 'W'
        elif most_common_diff == pd.Timedelta(days=30):
            return 'M'
        elif most_common_diff == pd.Timedelta(days=365):
            return 'Y'
        else:
            return 'D'  # Default to daily
    
    def add_regressors(self, df, regressor_columns):
        """
        Add additional regressors to the Prophet model.
        
        Args:
            df (pd.DataFrame): Data with regressor columns
            regressor_columns (list): List of column names to use as regressors
        
        Returns:
            ProphetForecaster: Self for method chaining
        """
        if self.model is None:
            raise ValueError("Model must be initialized first")
        
        for col in regressor_columns:
            if col in df.columns:
                self.model.add_regressor(col)
        
        return self
    
    def add_holidays(self, holidays_df):
        """
        Add holidays to the Prophet model.
        
        Args:
            holidays_df (pd.DataFrame): DataFrame with 'ds' and 'holiday' columns
        
        Returns:
            ProphetForecaster: Self for method chaining
        """
        if self.model is None:
            raise ValueError("Model must be initialized first")
        
        self.model = self.model.add_country_holidays(country_name='US')
        
        return self
    
    def cross_validation(self, prophet_df, initial_periods=365, forecast_periods=30, frequency='D'):
        """
        Perform cross-validation on the Prophet model.
        
        Args:
            prophet_df (pd.DataFrame): Prophet-formatted data
            initial_periods (int): Initial training period
            forecast_periods (int): Forecast horizon
            frequency (str): Data frequency
        
        Returns:
            pd.DataFrame: Cross-validation results
        """
        try:
            from prophet.diagnostics import cross_validation, performance_metrics
            
            # Perform cross-validation
            cv_results = cross_validation(
                self.fitted_model,
                initial=f'{initial_periods} days',
                period=f'{forecast_periods} days',
                horizon=f'{forecast_periods} days'
            )
            
            # Calculate performance metrics
            performance = performance_metrics(cv_results)
            
            return performance
            
        except Exception as e:
            print(f"Error in cross-validation: {str(e)}")
            return None
    
    def plot_components(self, figsize=(12, 10)):
        """
        Plot Prophet model components.
        
        Args:
            figsize (tuple): Figure size
        
        Returns:
            matplotlib.figure.Figure: Components plot
        """
        if self.results is None:
            return None
        
        try:
            import matplotlib.pyplot as plt
            
            # Create subplots
            fig, axes = plt.subplots(4, 1, figsize=figsize)
            
            # Trend
            axes[0].plot(self.results['full_forecast']['ds'], 
                        self.results['full_forecast']['trend'], 
                        color='blue')
            axes[0].set_title('Trend Component')
            axes[0].grid(True, alpha=0.3)
            
            # Yearly seasonality (if available)
            if 'yearly' in self.results['full_forecast'].columns:
                axes[1].plot(self.results['full_forecast']['ds'], 
                           self.results['full_forecast']['yearly'], 
                           color='green')
                axes[1].set_title('Yearly Seasonality')
                axes[1].grid(True, alpha=0.3)
            
            # Weekly seasonality (if available)
            if 'weekly' in self.results['full_forecast'].columns:
                axes[2].plot(self.results['full_forecast']['ds'], 
                           self.results['full_forecast']['weekly'], 
                           color='orange')
                axes[2].set_title('Weekly Seasonality')
                axes[2].grid(True, alpha=0.3)
            
            # Daily seasonality (if available)
            if 'daily' in self.results['full_forecast'].columns:
                axes[3].plot(self.results['full_forecast']['ds'], 
                           self.results['full_forecast']['daily'], 
                           color='red')
                axes[3].set_title('Daily Seasonality')
                axes[3].grid(True, alpha=0.3)
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"Error plotting components: {str(e)}")
            return None
    
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
        
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot original data
            ax.plot(df.index, df.iloc[:, 0], label='Original Data', color='blue', alpha=0.7)
            
            # Plot fitted values
            fitted_values = self.results['fitted_values']
            ax.plot(fitted_values.index, fitted_values, label='Fitted Values', color='green', alpha=0.8)
            
            # Plot forecast
            forecast_df = self.results['forecast']
            ax.plot(forecast_df.index, forecast_df['yhat'], label='Forecast', color='red', linewidth=2)
            
            # Plot confidence intervals
            ax.fill_between(
                forecast_df.index,
                forecast_df['yhat_lower'],
                forecast_df['yhat_upper'],
                alpha=0.3,
                color='red',
                label=f'{self.results["confidence_level"]}% Confidence Interval'
            )
            
            ax.set_title('Prophet Forecast')
            ax.set_xlabel('Date')
            ax.set_ylabel('Value')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            return fig
            
        except Exception as e:
            print(f"Error plotting forecast: {str(e)}")
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
            'rmse': self.results['rmse'],
            'mae': self.results['mae'],
            'mape': self.results['mape'],
            'r2': self.results['r2'],
            'residuals_mean': self.results['residuals'].mean(),
            'residuals_std': self.results['residuals'].std(),
            'confidence_level': self.results['confidence_level']
        }
        
        return diagnostics
    
    def get_forecast_components(self):
        """
        Get forecast components (trend, seasonality, etc.).
        
        Returns:
            dict: Forecast components
        """
        if self.results is None:
            return None
        
        components = {}
        forecast_df = self.results['full_forecast']
        
        # Extract available components
        available_components = ['trend', 'yearly', 'weekly', 'daily']
        
        for component in available_components:
            if component in forecast_df.columns:
                components[component] = forecast_df[['ds', component]].copy()
        
        return components
    
    def predict_future(self, future_periods, future_regressors=None):
        """
        Make predictions for future periods with optional regressors.
        
        Args:
            future_periods (int): Number of future periods to predict
            future_regressors (dict): Future regressor values
        
        Returns:
            pd.DataFrame: Future predictions
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fitted first")
        
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=future_periods)
        
        # Add regressors if provided
        if future_regressors:
            for regressor, values in future_regressors.items():
                future[regressor] = values
        
        # Make predictions
        forecast = self.fitted_model.predict(future)
        
        return forecast.tail(future_periods)
