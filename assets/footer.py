from dash import html
import dash_bootstrap_components as dbc

_footer = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([html.Hr([], className = 'hr-footer')], width = 12)
        ]),
        dbc.Row([
	        dbc.Col([], width = 1),
            dbc.Col(['CSCI 6612 Shuya Chen | Haoyuan Lu, Created with Plotly Dash'], width = 6),
            dbc.Col([], width =2),
	        dbc.Col([
                html.Ul([
                    html.Li([
                    ])
                ], className='list-unstyled d-flex justify-content-center justify-content-md-start')
            ], width = 2)
        ])
    ], fluid=True)
], className = 'footer')