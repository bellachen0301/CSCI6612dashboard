import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import statsmodels.api as sm
import pandas as pd
import plotly.express as px
import warnings
import plotly.graph_objects as go
warnings.filterwarnings("ignore")

 
# default
default_dataset_path = 'data/H1.csv'  # 
default_df = pd.read_csv(default_dataset_path)
default_df['time'] = pd.to_datetime(default_df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')  # Format datetime without timezone
default_df.set_index('time', inplace=True)
initial_feature_options = [{'label': col, 'value': col} for col in default_df.columns if col not in ['station_name', 'time']]

dash.register_page(__name__, name='3-Model Prediction', title='DH | 3-Prediction')

from assets.fig_layout import my_figlayout, train_linelayout, test_linelayout, pred_linelayout
from assets.acf_pacf_plots import acf_pacf


### PAGE LAYOUT ###############################################################################################################

layout = dbc.Container([
    # title
    dbc.Row([
        dbc.Col([html.H3(['ARIMA Model Fit & Prediction'])], width=12, className='row-titles')
    ]),
    dbc.Row([
        dbc.Col([], width = 1),
        dbc.Col([html.P(['Selected buoy:'], className='par')], width=2),
        dbc.Col([
            # dropdown for dataset
                dcc.Dropdown(
                            id='buoy-selector',  # ID for the dropdown, used in callbacks
                            options=[
                                {'label': 'H1', 'value': 'H1'},
                                {'label': 'HKB', 'value': 'HKB'},
                                {'label': 'COVE', 'value': 'COVE'},
                            ],
                            value='H1',  # Default value
                            style={'color': '#000'}  # Optional styling
                            )
                ], width=2),
           #dropdown for selected features
        dbc.Col([], width=1),
        dbc.Col([html.P(['Selected feature:'], className='par')], width=2),
        dbc.Col([
            dcc.Dropdown(
                id='feature-selector',
                options=initial_feature_options,
                multi=False,  # Single choice of feature
                value = 'temperature',
            ),     
        ], width = 2),
    ], className='row-content'),
    dbc.Row([
        dbc.Col(width=1),  # Empty column for spacing
        dbc.Col(html.P('Selected ARIMA (p,d,q) model parameters:'), width=4),
        dbc.Col(html.P('p'), width=1),
        dbc.Col(dcc.Dropdown(
            options=[{'label': str(i), 'value': i} for i in range(11)],
            placeholder='p', value=5, id='p'
        ), width=1),
        dbc.Col(html.P('d'), width=1),
        dbc.Col(dcc.Dropdown(
            options=[{'label': str(i), 'value': i} for i in range(11)],
            placeholder='d', value=1, id='d'
        ), width=1),
        dbc.Col(html.P('q'), width=1),
        dbc.Col(dcc.Dropdown(
            options=[{'label': str(i), 'value': i} for i in range(11)],
            placeholder='q', value=3, id='q'
        ), width=1),
        dbc.Col(width=1),  # Adjusted to fit the remaining space
    ]),


    dbc.Row([], style={'margin':'20px 0px 0px 0px'}),
    dbc.Row([
        dbc.Col([], width = 1),
        dbc.Col([
            #dcc.Graph(id='fig-pg41', className='my-graph'),
            dcc.Loading(id='m1-loading', type='circle', children=dcc.Graph(id='fig-pg41', className='my-graph'))
        ], width = 10),
        dbc.Col([], width = 1)
    ], className='row-content'),
])

### PAGE CALLBACKS ###############################################################################################################

@callback(
    Output('feature-selector', 'options', allow_duplicate=True),
    Input('buoy-selector', 'value'),
    prevent_initial_call=True,
)
def update_feature_options(selected_buoy):
    file_path = f'data/{selected_buoy}.csv'
    df = pd.read_csv(file_path)
    df['time'] = pd.to_datetime(df['time'])
    # Do not set 'time' as index here if it's used later in the app
    return [{'label': col, 'value': col} for col in df.columns if col != 'station_name' and col != 'time']


# Generate predictions & Graph
 
# Callback to update the plot based on data selection
@callback(
    Output('fig-pg41', 'figure'),
    [Input('fig-pg41', 'relayoutData'),
     Input('buoy-selector','value'),
     Input('feature-selector', 'value'),
     Input('p', 'value'),
     Input('d', 'value'),
     Input('q', 'value')],
    prevent_initial_call=True,
)
def update_plot(relayout_data, selected_buoy, selected_column, order_p, order_d, order_q):
    file_path = f'data/{selected_buoy}.csv'
    df = pd.read_csv(file_path)
    df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%d %H:%M:%S') 
    df.set_index('time', inplace=True)
    if relayout_data is None or 'xaxis.range[0]' not in relayout_data or 'xaxis.range[1]' not in relayout_data:
        # Initial plot or no data selected
                # Initial plot or no data selected
        initial_trace = go.Scatter(x=df.index, y=df[selected_column],
                                   mode='lines', name='Initial', line=train_linelayout)
        fig = go.Figure(initial_trace)
        fig.update_layout(my_figlayout)
        fig.update_layout(xaxis_title='Time', yaxis_title=selected_column, title=f'{selected_column} Over Time')
        return fig

    selected_start = relayout_data['xaxis.range[0]']
    selected_end = relayout_data['xaxis.range[1]']
 
    #Filter data based on the selected range
    selected_data = df.loc[selected_start:selected_end]
 
    # Perform ARIMA modeling on the selected data
    y = selected_data[selected_column]
    model = sm.tsa.ARIMA(y, order=(order_p, order_d, order_q))
    results = model.fit()
 
    # Predict 24 hours into the future
    forecast_steps = 24
    forecast = results.forecast(steps=forecast_steps)
    forecast = forecast.values

    # Create a DataFrame for the forecast
    forecast_index = pd.date_range(start=selected_data.index[-1], periods=forecast_steps + 1, freq='H')[1:]
    #future_df = pd.DataFrame({selected_column: forecast}, index=forecast_index)
 
    # Concatenate the original data and the forecasted data
    #combined_df = pd.concat([selected_data, future_df])
    actual_trace = go.Scatter(x=selected_data.index, y=selected_data[selected_column],
                          mode='lines', name='Actual', line=train_linelayout)
    # Create the figure and add the actual trace
    fig = go.Figure()
    fig.add_trace(actual_trace)
    # Create a trace for the forecasted values with custom layout
    forecast_trace = go.Scatter(x=forecast_index, y=forecast, 
                                mode='lines', name='Forecast', line=test_linelayout)
    fig.add_trace(forecast_trace)
    
    fig.update_layout(my_figlayout)
    # Update layout
    fig.update_layout(xaxis_title='Time', yaxis_title=selected_column, title=f'{selected_column} ARIMA Prediction')

 
    return fig