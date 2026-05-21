import pandas as pd
import plotly.graph_objects as go

_DARK_LAYOUT = dict(
    plot_bgcolor='#0e1117',
    paper_bgcolor='#0e1117',
    font=dict(color='white'),
    xaxis_title='Date',
    yaxis_title='Price (USD)',
)

def build_historical_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['close'],
        mode='lines', name='S&P 500',
        line=dict(color='#4a9eff', width=2)
    ))
    fig.update_layout(**_DARK_LAYOUT, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    return fig

def build_forecast_chart(actual_df: pd.DataFrame, pred_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=actual_df['date'], y=actual_df['close'],
        mode='lines', name='Actual',
        line=dict(color='#4a9eff', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=pred_df['forecast_date'], y=pred_df['predicted_close'],
        mode='lines', name='Forecast',
        line=dict(color='#ff884a', width=2, dash='dot')
    ))
    fig.update_layout(**_DARK_LAYOUT, legend=dict(orientation='h', y=1.1), margin=dict(l=0, r=0, t=20, b=0))
    return fig
