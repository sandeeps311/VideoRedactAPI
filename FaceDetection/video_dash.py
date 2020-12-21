import dash
import json
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import os
from flask import Flask, Response


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])

app.config.suppress_callback_exceptions = True

app.title = 'Video Dashboard'

server = app.server

app.layout = html.Div(
    [
         dbc.Navbar(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3("Video Dashboard")
                            ]
                        )
                    ]
                )
            ],
            color="White",
            dark=False,
            fixed='top',
            style={
                'textAlign': 'center',
                'marginBottom': '10px'
            }
        ),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H5(  ## H5 Header size H1, H2,H3
                                                        "Import your video",
                                                        className="importvideo",
                                                        style={
                                                            # 'marginBottom': '10px',
                                                            'textAlign': 'center'
                                                        }
                                                ),
                                                dcc.Upload(  # Upload component
                                                    id='upload-data',  # Input for callback
                                                    children=html.Div(
                                                        [
                                                            'Drag and Drop or ',
                                                            html.A('Select Files')  # Attribute
                                                        ]
                                                    ),

                                                    style={
                                                        'width': '100%',
                                                        'height': '50px',
                                                        'lineHeight': '60px',
                                                        'borderWidth': '1px',
                                                        'borderStyle': 'dashed',
                                                        'borderRadius': '10px',
                                                        'textAlign': 'center',
                                                        # 'margin': '10px',
                                                        'padding': '40px'
                                                    },

                                                    # Allow multiple files to be uploaded
                                                    multiple=True
                                                ),
                                            ]
                                        )
                                    ],
                                    # style={'margin': '25px', 'padding': '20px'},  # Cardbody style
                                ),

                            ]
                        )
                    ],
                    style={"marginTop": "80px"}
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Video(
                                    src=r"static\test.mp4",
                                    controls=True,
                                )
                            ],
                            width=9
                        ),
                        dbc.Col(
                            [

                            ],
                            width=3
                        )
                    ]
                )
            ]
        )


    ]
)


if __name__ == '__main__':
    app.run_server(debug=True)