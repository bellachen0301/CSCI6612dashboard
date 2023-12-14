import dash
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import callback, dcc
import pandas as pd
import plotly.graph_objects as go
dash.register_page(__name__, path='/', name='Home', title='DH | Home')
# buoys data
buoys = pd.read_csv('data/buoys.csv')

# fig = go.Figure(go.Scattermapbox(
#     mode = "markers",
#     lon = buoys['lon'], lat = buoys['lat'],
#     marker = {'size': 20, 'symbol': "cross"},
#     ))
fig = px.scatter_mapbox(buoys, lat="lat", lon="lon", hover_name="id", hover_data={"id": False, "lat": True, "lon": True, "size": False}, size="size", size_max=10,  # Increase the size of the points
                        color_discrete_sequence=["BLUE"], zoom=9, height=600, width=600)
fig.update_layout(mapbox_style="open-street-map", mapbox_center={"lat": 44.6488, "lon": -63.5752})
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})




layout = dbc.Container([
    # title
    dbc.Row([
        dbc.Col([
            html.H3(['Welcome!']),
            html.P([html.B(['App Overview'])], className='par')
        ], width=12, className='row-titles')
    ]),
    # Guidelines
    dbc.Row([
        dbc.Col([], width = 2),
        dbc.Col([
            html.P(['This is an interactive dashboard interface designed for analyzing climate and environmental trends in Halifax Harbour. Select your target buoy and explore more!'], className='guide'),
         ], width = 8),
        dbc.Col([], width = 2)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='map-plot',  # id for the map
                figure=fig,  # 
            )
        ], width={'size': 6, 'offset': 3},  # Center the map horizontally
            className='text-center', 
            ),# Center the content vertically), 
               # store the click
         dcc.Store(id='selected-buoy-id'),#  
    ]),

])

