import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from statsmodels.tsa.stattools import adfuller
from assets.fig_layout import my_figlayout, my_linelayout
from assets.acf_pacf_plots import acf_pacf

dash.register_page(__name__, name='2-Data Visualization', title='DH | 2-Data Visulization')


 
default_dataset_path = 'data/H1.csv'  # 
default_df = pd.read_csv(default_dataset_path)
default_df['time'] = pd.to_datetime(default_df['time'], errors='raise')
initial_feature_options = [{'label': col, 'value': col} for col in default_df.columns if col not in ['station_name', 'time']]


### PAGE LAYOUT ###############################################################################################################

layout = dbc.Container([
    # title
    dbc.Row([
        dbc.Col([html.H3(['Data Visualization'])], width=12, className='row-titles')
    ]),
    # data input
    dbc.Row([
        dbc.Col([], width = 1),
        dbc.Col([html.P(['Selected buoy:'], className='par')], width=2),
        dbc.Col([
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
 

    # Transformations
    dbc.Row([
        dbc.Col([], width = 2),
        dbc.Col([
            dcc.Checklist(
                ['1) Apply log'], 
                persistence=True, 
                persistence_type='session', 
                id='log-check'
            ),
        ], width=3),  # Adjusted width
        dbc.Col([], width = 1),
        dbc.Col([
            html.P(['2) Apply difference']),
        ], width=2),  # Adjusted width

        dbc.Col([
            dcc.Dropdown(
                options=[{'label': str(i), 'value': i} for i in range(1, 11)],
                value=1,
                id='d1-dropdown'
            ),
        ], width=1),  # Adjusted width

    ], className='row-content'),
    
    # Graphs
    dbc.Row([ 
        dbc.Col([
            dcc.Loading(id='p2-2-loading', type='circle', children=dcc.Graph(id='fig-1', className='my-graph')),
           
        ], width=6, className='multi-graph'),
        dbc.Col([
             dcc.Loading(id='p2-2-loading', type='circle', children=dcc.Graph(id='fig-lineplot', className='my-graph')),
           # dcc.Loading(id='p2-2-loading', type='circle', children=dcc.Graph(id='fig-acf', className='my-graph'))
        ], width=6, className='multi-graph'),
    ]),
    dbc.Row([
    dbc.Col(width=2),  
    dbc.Col([
        dcc.Loading(id='p2-2-loading', type='circle', children=dcc.Graph(id='fig-acf', className='my-graph')),
    ], width=8, className='multi-graph'),
    dbc.Col(width=2),  
], justify='center'),  

])


### PAGE CALLBACKS ###############################################################################################################


@callback(
    Output('feature-selector', 'options'),
    Input('buoy-selector', 'value'),
)
def update_feature_options(selected_buoy):
    if selected_buoy == 'H1':     
        df = pd.read_csv('data/H1.csv')
    elif selected_buoy == 'HKB':
        df = pd.read_csv('data/HKB.csv')
    elif selected_buoy == 'COVE':
        df = pd.read_csv('data/COVE.csv')
    df['time'] = pd.to_datetime(df['time'], errors='raise')
    return [{'label': col, 'value': col} for col in df.columns if col != 'station_name' and col != 'time']


@callback(
    #Output(component_id='stationarity-test', component_property='children'),
    Output(component_id='fig-1', component_property='figure'),
    Output(component_id='fig-lineplot', component_property='figure'),
    Output(component_id='fig-acf', component_property='figure'),
    Input(component_id='buoy-selector',component_property='value'),
    Input(component_id='feature-selector',component_property='value'),
    Input(component_id='log-check', component_property='value'),
    Input(component_id='d1-dropdown', component_property='value'),
)
def data_transform(selected_buoy ,selected_feature, _logtr, _d1v):
    if selected_buoy:
        _data = pd.read_csv(f'data/{selected_buoy}.csv')
        _data['time'] = pd.to_datetime(_data['time'], errors='raise')
    # Transform the data
    #if selected_feature:  
    fig_1 = go.Figure(layout=my_figlayout)
    fig_1.add_trace(go.Scatter(x=_data['time'], y=_data[selected_feature], line=dict()))
    fig_1.update_layout(title='Original Data Linechart', xaxis_title='Time', yaxis_title=selected_feature)
    fig_1.update_traces(overwrite=True, line=my_linelayout)
    if _logtr:
        _min_value = min(_data[selected_feature]) # correct for 0 or negative values
        if _min_value == 0:
            _data[selected_feature] = _data[selected_feature] + 0.5
        elif _min_value < 0:
            _data[selected_feature] = _data[selected_feature] + np.abs(_min_value) + 0.5
        _data[selected_feature] = list(np.log(_data[selected_feature])) # apply log 
        _data.replace([np.inf, -np.inf], np.nan, inplace=True)  # Replace inf with NaN
        _data.dropna(subset=[selected_feature], inplace=True)   # Drop NaN values
    if  _d1v:
        #_data[selected_feature] = _data[selected_feature].diff(periods=_d1v).dropna()

        _dvalues = _data[selected_feature].diff(periods=_d1v).dropna()  # Calculate the difference using pandas
        _data = _data.iloc[_d1v:]  # Align the length of the data to match the differenced data
        _data[selected_feature] = _dvalues.values    # Assign the differenced values back to the dataframe
        _data.dropna(subset=[selected_feature], inplace=True) 
    
    # Perform test
    # if not _data[selected_feature].isnull().any(): 
    #     stat_test = adfuller(_data[selected_feature])
    #     pv = stat_test[1]
    #     if pv <= .05:
    #         _test_output = dbc.Alert(children=['Test p-value: {:.4f}'.format(pv),  html.Br(), 'The data is ', html.B(['stationary'], className='alert-bold')], color='success')
    #         #_test_output = dbc.Alert(children=[f'Test p-value: {pv}',  html.Br(), 'The data is ', html.B(['stationary'], className='alert-bold')], color='success')
    #     else:
    #         _test_output = dbc.Alert(children=['Test p-value: {:.4f}'.format(pv), html.Br(), 'The data is ', html.B(['not stationary'], className='alert-bold')], color='danger')
    # else:
    #     _test_output =dbc.Alert(children=['Test p-value: {:.4f}'.format(pv),html.Br(),'The data is ',html.B(['not stationary'], className='alert-bold')], color='danger')
    # #Charts
    #   Transformed data linechart
    fig_2 = go.Figure(layout=my_figlayout)
    fig_2.add_trace(go.Scatter(x=_data['time'], y=_data[selected_feature], line=dict()))
    fig_2.update_layout(title='Transformed Data Linechart', xaxis_title='Time', yaxis_title=selected_feature)
    fig_2.update_traces(overwrite=True, line=my_linelayout)

        # ACF, PACF
    fig_3, fig_ = acf_pacf(_data, selected_feature)
    return fig_1, fig_2, fig_3



 
