import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st

def create_forecast_plots(df, model_results, model_name, forecast_periods):
    """
    Create interactive forecast plots using Plotly.
    
    Args:
        df (pd.DataFrame): Original time series data
        model_results (dict): Model results with forecasts
        model_name (str): Name of the model
        forecast_periods (int): Number of forecast periods
    """
    # Main forecast plot
    fig = go.Figure()
    
    # Add original data
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df.iloc[:, 0],
        mode='lines',
        name='Historical Data',
        line=dict(color='#1f77b4', width=2),
        opacity=0.8
    ))
    
    # Add fitted values
    if 'fitted_values' in model_results:
        fitted_values = model_results['fitted_values']
        fig.add_trace(go.Scatter(
            x=fitted_values.index,
            y=fitted_values,
            mode='lines',
            name='Fitted Values',
            line=dict(color='#2ca02c', width=2),
            opacity=0.7
        ))
    
    # Add forecast
    forecast_df = model_results['forecast']
    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['forecast'] if 'forecast' in forecast_df.columns else forecast_df['yhat'],
        mode='lines',
        name='Forecast',
        line=dict(color='#d62728', width=3),
        opacity=0.9
    ))
    
    # Add confidence intervals
    if 'forecast' in forecast_df.columns:
        # ARIMA/SARIMA format
        lower_col = 'lower_bound'
        upper_col = 'upper_bound'
    else:
        # Prophet format
        lower_col = 'yhat_lower'
        upper_col = 'yhat_upper'
    
    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df[upper_col],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df[lower_col],
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(214, 39, 40, 0.2)',
        name='Confidence Interval',
        hoverinfo='skip'
    ))
    
    # Update layout
    fig.update_layout(
        title=f'{model_name} Forecast',
        xaxis_title='Date',
        yaxis_title='Value',
        height=500,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Residuals plot
    if 'residuals' in model_results:
        create_residuals_plot(model_results['residuals'], model_name)
    
    # Forecast statistics
    create_forecast_stats(model_results, model_name)

def create_residuals_plot(residuals, model_name):
    """
    Create residuals analysis plots.
    
    Args:
        residuals (pd.Series): Model residuals
        model_name (str): Name of the model
    """
    # Create subplots for residuals analysis
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Residuals Over Time', 'Residuals Distribution', 
                       'Q-Q Plot', 'Residuals vs Fitted'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Residuals over time
    fig.add_trace(
        go.Scatter(
            x=residuals.index,
            y=residuals,
            mode='lines+markers',
            name='Residuals',
            line=dict(color='blue', width=1),
            marker=dict(size=3)
        ),
        row=1, col=1
    )
    
    # Residuals distribution
    fig.add_trace(
        go.Histogram(
            x=residuals,
            nbinsx=30,
            name='Distribution',
            marker_color='lightblue',
            opacity=0.7
        ),
        row=1, col=2
    )
    
    # Q-Q plot (simplified)
    from scipy import stats
    qq_data = stats.probplot(residuals.dropna(), dist="norm")
    fig.add_trace(
        go.Scatter(
            x=qq_data[0][0],
            y=qq_data[0][1],
            mode='markers',
            name='Q-Q Plot',
            marker=dict(color='red', size=4)
        ),
        row=2, col=1
    )
    
    # Add Q-Q line
    fig.add_trace(
        go.Scatter(
            x=qq_data[0][0],
            y=qq_data[1][1] + qq_data[1][0] * qq_data[0][0],
            mode='lines',
            name='Q-Q Line',
            line=dict(color='black', dash='dash')
        ),
        row=2, col=1
    )
    
    # Residuals vs fitted (if available)
    if hasattr(residuals, 'index') and len(residuals) > 0:
        # Create a simple residuals vs index plot
        fig.add_trace(
            go.Scatter(
                x=list(range(len(residuals))),
                y=residuals,
                mode='markers',
                name='Residuals vs Index',
                marker=dict(color='green', size=4)
            ),
            row=2, col=2
        )
    
    fig.update_layout(
        title=f'{model_name} - Residuals Analysis',
        height=600,
        template='plotly_white',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_forecast_stats(model_results, model_name):
    """
    Create forecast statistics and metrics.
    
    Args:
        model_results (dict): Model results
        model_name (str): Name of the model
    """
    st.subheader(f"📊 {model_name} Model Statistics")
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    # Display available metrics
    metrics_to_show = ['rmse', 'mae', 'mape', 'aic', 'bic', 'r2', 'mse']
    metric_labels = {
        'rmse': 'RMSE',
        'mae': 'MAE', 
        'mape': 'MAPE (%)',
        'aic': 'AIC',
        'bic': 'BIC',
        'r2': 'R²',
        'mse': 'MSE'
    }
    
    available_metrics = [metric for metric in metrics_to_show if metric in model_results]
    
    for i, metric in enumerate(available_metrics[:4]):
        with [col1, col2, col3, col4][i]:
            value = model_results[metric]
            if metric == 'mape':
                st.metric(metric_labels[metric], f"{value:.2f}%")
            elif metric == 'r2':
                st.metric(metric_labels[metric], f"{value:.3f}")
            else:
                st.metric(metric_labels[metric], f"{value:.2f}")

def create_model_comparison(df, models_results, forecast_periods):
    """
    Create model comparison plots.
    
    Args:
        df (pd.DataFrame): Original time series data
        models_results (dict): Dictionary of model results
        forecast_periods (int): Number of forecast periods
    """
    # Main comparison plot
    fig = go.Figure()
    
    # Add original data
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df.iloc[:, 0],
        mode='lines',
        name='Historical Data',
        line=dict(color='black', width=3),
        opacity=0.8
    ))
    
    # Add forecasts for each model
    colors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#9467bd']
    
    for i, (model_name, results) in enumerate(models_results.items()):
        forecast_df = results['forecast']
        
        # Get forecast values
        if 'forecast' in forecast_df.columns:
            forecast_values = forecast_df['forecast']
            lower_col = 'lower_bound'
            upper_col = 'upper_bound'
        else:
            forecast_values = forecast_df['yhat']
            lower_col = 'yhat_lower'
            upper_col = 'yhat_upper'
        
        # Add forecast line
        fig.add_trace(go.Scatter(
            x=forecast_df.index,
            y=forecast_values,
            mode='lines',
            name=f'{model_name} Forecast',
            line=dict(color=colors[i % len(colors)], width=2),
            opacity=0.8
        ))
        
        # Add confidence intervals
        fig.add_trace(go.Scatter(
            x=forecast_df.index,
            y=forecast_df[upper_col],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_df.index,
            y=forecast_df[lower_col],
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor=f'rgba{tuple(list(px.colors.hex_to_rgb(colors[i % len(colors)])) + [0.2])}',
            name=f'{model_name} CI',
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Update layout
    fig.update_layout(
        title='Model Comparison - Forecasts',
        xaxis_title='Date',
        yaxis_title='Value',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance comparison bar chart
    create_performance_comparison(models_results)

def create_performance_comparison(models_results):
    """
    Create performance metrics comparison chart.
    
    Args:
        models_results (dict): Dictionary of model results
    """
    # Extract metrics
    models = list(models_results.keys())
    metrics_data = {
        'RMSE': [],
        'MAE': [],
        'MAPE': []
    }
    
    for model_name in models:
        results = models_results[model_name]
        metrics_data['RMSE'].append(results.get('rmse', 0))
        metrics_data['MAE'].append(results.get('mae', 0))
        metrics_data['MAPE'].append(results.get('mape', 0))
    
    # Create bar chart
    fig = go.Figure()
    
    colors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#9467bd']
    
    for i, (metric, values) in enumerate(metrics_data.items()):
        fig.add_trace(go.Bar(
            name=metric,
            x=models,
            y=values,
            marker_color=colors[i % len(colors)],
            opacity=0.8
        ))
    
    fig.update_layout(
        title='Model Performance Comparison',
        xaxis_title='Models',
        yaxis_title='Metric Value',
        barmode='group',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_time_series_decomposition(df, model_name="Time Series"):
    """
    Create time series decomposition plot.
    
    Args:
        df (pd.DataFrame): Time series data
        model_name (str): Name for the plot
    """
    from statsmodels.tsa.seasonal import seasonal_decompose
    
    try:
        # Perform decomposition
        decomposition = seasonal_decompose(df.iloc[:, 0], model='additive', period=12)
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=('Original', 'Trend', 'Seasonal', 'Residual'),
            vertical_spacing=0.08
        )
        
        # Original series
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=decomposition.observed,
                mode='lines',
                name='Original',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        # Trend
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=decomposition.trend,
                mode='lines',
                name='Trend',
                line=dict(color='green', width=2)
            ),
            row=2, col=1
        )
        
        # Seasonal
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=decomposition.seasonal,
                mode='lines',
                name='Seasonal',
                line=dict(color='orange', width=2)
            ),
            row=3, col=1
        )
        
        # Residual
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=decomposition.resid,
                mode='lines',
                name='Residual',
                line=dict(color='red', width=2)
            ),
            row=4, col=1
        )
        
        fig.update_layout(
            title=f'{model_name} - Time Series Decomposition',
            height=600,
            template='plotly_white',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.warning(f"Could not create decomposition plot: {str(e)}")

def create_correlation_heatmap(df):
    """
    Create correlation heatmap for multiple time series.
    
    Args:
        df (pd.DataFrame): Time series data
    """
    if len(df.columns) > 1:
        # Calculate correlation matrix
        corr_matrix = df.corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Correlation Matrix',
            template='plotly_white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def create_distribution_plot(df):
    """
    Create distribution plots for time series data.
    
    Args:
        df (pd.DataFrame): Time series data
    """
    fig = go.Figure()
    
    for col in df.columns:
        fig.add_trace(go.Histogram(
            x=df[col],
            name=col,
            opacity=0.7,
            nbinsx=30
        ))
    
    fig.update_layout(
        title='Data Distribution',
        xaxis_title='Value',
        yaxis_title='Frequency',
        barmode='overlay',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_box_plot(df):
    """
    Create box plots for time series data.
    
    Args:
        df (pd.DataFrame): Time series data
    """
    fig = go.Figure()
    
    for col in df.columns:
        fig.add_trace(go.Box(
            y=df[col],
            name=col,
            boxpoints='outliers'
        ))
    
    fig.update_layout(
        title='Data Distribution (Box Plot)',
        yaxis_title='Value',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
