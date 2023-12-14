import dash
from dash import dash_table, html, dcc, Output, Input, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
 
 
dash.register_page(__name__, name='1-Data Stats', title='DH | 1-Data Stats')
 

### PAGE LAYOUT ###############################################################################################################

layout = dbc.Container([
    # title
    dbc.Row([
        dbc.Col([html.H3(['Data Stats'])], width=12, className='row-titles')
    ]),
 
    # data input
    dbc.Row([
        dbc.Col([], width = 3),
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
        dbc.Col([], width=3),
    ], className='row-content'),
    dbc.Row([
            dbc.Col([], width=1),
            dbc.Col([dcc.Graph(id='stats-graph', className='my-graph')], width=10),  # Graph to display the statistics
            dbc.Col([], width=1),
    ]),

])
 
### PAGE CALLBACKS ###############################################################################################################
 

@callback(
    Output('stats-graph', 'figure'),  # Assuming you have a Graph component with this ID
    Input('buoy-selector', 'value')
)
def update_graph(selected_buoy):
    try:
        if selected_buoy == 'H1':     
            df = pd.read_csv('data/H1.csv')
        elif selected_buoy == 'HKB':
            df = pd.read_csv('data/HKB.csv')
        elif selected_buoy == 'COVE':
            df = pd.read_csv('data/COVE.csv')
        df['time'] = pd.to_datetime(df['time'], errors='raise')

        # Calculate statistics
        data_table = calculate_statistics(df)

        # Calculate number of rows needed for subplots based on number of columns
        num_columns = len(df.columns) - 1  # subtracting the 'time' column
        rows = (num_columns + 2) // 3  # 3 columns per row, adjust as needed
        
        # Create a figure with subplots
        fig = make_subplots(rows=rows, cols=3, subplot_titles=[name for name in data_table['Column Names']])  # Exclude 'time' column

        # Fill in the subplots with line charts or box plots for each column
    # Fill in the subplots with box plots for each column
        for i, column_name in enumerate(data_table['Column Names'], start=1):
            row = (i - 1) // 3 + 1
            col = (i - 1) % 3 + 1
            
            # Extract the column data for the current statistic
            column_data = {
                'Mean': float(data_table['Mean'][i-1]),
                'Std Dev': float(data_table['Std Dev'][i-1]),
                'Minimum': float(data_table['Minimum'][i-1]),
                'Maximum': float(data_table['Maximum'][i-1])
            }

            # Add a box plot for the current column's data
            fig.add_trace(
                go.Box(y=list(column_data.values()), name=column_name),
                row=row, 
                col=col
            )

        # Update the layout for the entire figure
        fig.update_layout(
            title='Statistical Measures of Each Parameter',
            showlegend=False,
            height=300*rows,  # Adjust the height based on number of rows
            paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
            font=dict(color='white'),  # White text
        )
        # Update axes colors and remove gridlines
        #fig.update_xaxes(showline=False, linewidth=1, linecolor='white', gridcolor='grey', showgrid=False)
        #fig.update_yaxes(showline=False, linewidth=1, linecolor='white', gridcolor='grey', showgrid=False)
        return fig
    except Exception as e:
        print(f"Error: {e}")
        return go.Figure()  # Return an empty figure in case of error
    
def calculate_statistics(df):
    column_means = df.mean()
    column_std = df.std()
    column_min = df.min()
    column_max = df.max()
    column_names = df.columns[df.columns != 'time'].tolist()

    data_table = {
        'Column Names': column_names,
        'Mean': [f"{x:.2f}" for x in column_means[column_means.index != 'time']],
        'Std Dev': [f"{x:.2f}" for x in column_std[column_std.index != 'time']],
        'Minimum': [f"{x:.2f}" for x in column_min[column_min.index != 'time']],
        'Maximum': [f"{x:.2f}" for x in column_max[column_max.index != 'time']]
    }
    return data_table