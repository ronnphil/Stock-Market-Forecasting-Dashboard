import pandas as pd
import plotly.graph_objects as go
from dashboard.charts import build_historical_chart, build_forecast_chart

def _historical_df():
    return pd.DataFrame({
        'date': ['2024-01-02', '2024-01-03', '2024-01-04'],
        'close': [4742.83, 4704.81, 4697.24]
    })

def _pred_df():
    return pd.DataFrame({
        'forecast_date': ['2024-01-05', '2024-01-08'],
        'predicted_close': [4710.0, 4725.0]
    })

def test_build_historical_chart_returns_figure():
    fig = build_historical_chart(_historical_df())
    assert isinstance(fig, go.Figure)

def test_build_historical_chart_has_one_trace():
    fig = build_historical_chart(_historical_df())
    assert len(fig.data) == 1

def test_build_historical_chart_trace_is_blue():
    fig = build_historical_chart(_historical_df())
    assert fig.data[0].line.color == '#4a9eff'

def test_build_forecast_chart_returns_figure():
    fig = build_forecast_chart(_historical_df(), _pred_df())
    assert isinstance(fig, go.Figure)

def test_build_forecast_chart_has_two_traces():
    fig = build_forecast_chart(_historical_df(), _pred_df())
    assert len(fig.data) == 2

def test_build_forecast_chart_trace_names():
    fig = build_forecast_chart(_historical_df(), _pred_df())
    names = {t.name for t in fig.data}
    assert names == {'Actual', 'Forecast'}
