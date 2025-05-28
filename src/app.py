import dash
from dash import html, dcc, Input, Output, State, callback, ctx, ClientsideFunction
import dash_bootstrap_components as dbc
import base64
import json

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True,
)

# Use default Dash index string (CSS is now in assets/custom_styles.css)

# Set the title of the app
app.title = "Panel de Palabras Fantasma"

# Define the header style with light blue background
header_style = {
    "backgroundColor": "#ADD8E6",  # Light blue color
    "padding": "2rem 1rem",
    "textAlign": "center",
    "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
    "marginBottom": "2rem",
}

# Define the layout of the app
app.layout = html.Div([
    # Header section
    html.Div([
        html.H1("Panel de Palabras Fantasma", className="display-4"),
        html.P("Una demostración del efecto de Palabras Fantasma", className="lead"),
    ], style=header_style),

    # Main content container
    dbc.Container([
        # Audio upload section
        dbc.Row([
            dbc.Col([
                html.H3("Subir Archivos de Audio", className="mb-3"),
                html.P("Seleccione archivos de audio para experimentar el efecto de Palabras Fantasma. Los archivos deben ser archivos de audio y menos de 5MB cada uno."),
            ], width=12),
        ], className="mb-2"),

        # Track mode selector
        dbc.Row([
            dbc.Col([
                html.Label("Seleccionar Modo de Pista:"),
                dcc.Dropdown(
                    id='track-mode-selector',
                    options=[
                        {'label': 'Pista Única', 'value': 'single'},
                        {'label': 'Pistas Duales', 'value': 'dual'}
                    ],
                    value='dual',
                    clearable=False,
                    style={'width': '100%'}
                ),
            ], width=12),
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                html.H5("Pista 1", className="mb-2"),
                dcc.Upload(
                    id='upload-audio-1',
                    children=html.Div([
                        'Arrastrar y Soltar o ',
                        html.A('Seleccionar Pista de Audio 1')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px 0'
                    },
                    multiple=False
                ),
                html.Div(id='upload-error-1', className="text-danger mt-2"),
                html.Div(id='audio-output-1'),
            ], md=6),

            dbc.Col([
                html.Div(
                    id='track-2-container',
                    children=[
                        html.H5("Pista 2", className="mb-2"),
                        dcc.Upload(
                            id='upload-audio-2',
                            children=html.Div([
                                'Arrastrar y Soltar o ',
                                html.A('Seleccionar Pista de Audio 2')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px 0'
                            },
                            multiple=False
                        ),
                        html.Div(id='upload-error-2', className="text-danger mt-2"),
                        html.Div(id='audio-output-2'),
                    ]
                )
            ], md=6),
        ], className="mb-4"),

        # Controls section
        dbc.Row([
            dbc.Col([
                html.H4("Control de Retraso", className="mb-3"),
                html.P("Ajuste el retraso entre los canales de audio izquierdo y derecho:"),
                dcc.Slider(
                    id='delay-slider',
                    min=0,
                    max=500,
                    step=10,
                    value=200,
                    marks={i: f'{i} ms' for i in range(0, 501, 100)},
                    className="mb-2"
                ),
                html.Div(id='delay-value-display', className="text-center mb-4"),
            ], md=6),

            dbc.Col([
                html.H4("Control de Repetición", className="mb-3"),
                html.P("Establezca el número de veces para repetir el audio:"),
                dbc.InputGroup([
                    dbc.InputGroupText("Repeticiones:"),
                    dbc.Input(
                        id="loop-count",
                        type="number",
                        min=1,
                        max=100,
                        step=1,
                        value=10
                    ),
                ], className="mb-4"),
            ], md=6),
        ], className="mb-4"),

        # Speed control sliders
        dbc.Row([
            dbc.Col([
                html.H4("Control de Velocidad - Pista 1", className="mb-3"),
                html.P("Ajuste la velocidad de reproducción de la Pista 1:"),
                dcc.Slider(
                    id='speed-slider-1',
                    min=0.5,
                    max=2.0,
                    step=0.1,
                    value=1.0,
                    marks={i/10: f'{i/10}x' for i in range(5, 21, 5)},
                    className="mb-2"
                ),
                html.Div(id='speed-value-display-1', className="text-center mb-4"),
            ], md=6),

            dbc.Col([
                html.Div(
                    id='speed-control-2-container',
                    children=[
                        html.H4("Control de Velocidad - Pista 2", className="mb-3"),
                        html.P("Ajuste la velocidad de reproducción de la Pista 2:"),
                        dcc.Slider(
                            id='speed-slider-2',
                            min=0.5,
                            max=2.0,
                            step=0.1,
                            value=1.0,
                            marks={i/10: f'{i/10}x' for i in range(5, 21, 5)},
                            className="mb-2"
                        ),
                        html.Div(id='speed-value-display-2', className="text-center mb-4"),
                    ]
                )
            ], md=6),
        ], className="mb-4"),

        # Play button for phantom words effect
        dbc.Row([
            dbc.Col([
                html.H4("Reproducir Efecto de Palabras Fantasma", className="mb-3"),
                html.P("Haga clic en los botones a continuación para reproducir o detener el audio con el efecto de palabras fantasma:"),
            ], width=12),
        ], className="mb-2"),

        # Buttons row with gap
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Reproducir Audio",
                    id="play-button",
                    color="primary",
                    className="w-100",
                    n_clicks=0
                ),
            ], width=5),

            # Empty column for spacing
            dbc.Col(width=2),

            dbc.Col([
                dbc.Button(
                    "Detener Audio",
                    id="stop-button",
                    color="danger",
                    className="w-100",
                    n_clicks=0
                ),
            ], width=5),
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                html.Div(id="playback-status", className="mt-2 text-center")
            ], width=12),
        ], className="mb-4"),


        # Hidden divs for storing the audio data
        html.Div(id='audio-storage-1', style={'display': 'none'}),
        html.Div(id='audio-storage-2', style={'display': 'none'}),

    ]),

    # Footer
    html.Footer([
        html.P("Proyecto de Palabras Fantasma - 2025", className="text-center text-muted"),
    ], style={"padding": "2rem 0", "marginTop": "2rem", "borderTop": "1px solid #e7e7e7"}),
])

# Callback to validate uploaded file and store audio data for Track 1
@callback(
    [Output('upload-error-1', 'children'),
     Output('audio-output-1', 'children'),
     Output('audio-storage-1', 'children')],
    [Input('upload-audio-1', 'contents')],
    [State('upload-audio-1', 'filename')]
)
def update_output_track1(contents, filename):
    if contents is None:
        return None, None, None

    # Check file extension
    if not filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
        return "Error: Por favor suba un archivo de audio (MP3, WAV, OGG, M4A).", None, None

    # Decode the file content
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    # Check file size (5MB limit)
    if len(decoded) > 5 * 1024 * 1024:  # 5MB in bytes
        return "Error: El tamaño del archivo excede el límite de 5MB.", None, None

    # Store the audio data
    audio_data = {
        'content': contents,
        'filename': filename
    }

    # Create audio player component
    audio_player = html.Div([
        html.H6(f"Archivo seleccionado: {filename}", className="mt-2"),
        html.Audio(
            id='audio-player-1',
            src=contents,
            controls=True,
            style={'width': '100%', 'marginTop': '5px'}
        )
    ])

    return None, audio_player, json.dumps(audio_data)

# Callback to validate uploaded file and store audio data for Track 2
@callback(
    [Output('upload-error-2', 'children'),
     Output('audio-output-2', 'children'),
     Output('audio-storage-2', 'children')],
    [Input('upload-audio-2', 'contents')],
    [State('upload-audio-2', 'filename')]
)
def update_output_track2(contents, filename):
    if contents is None:
        return None, None, None

    # Check file extension
    if not filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
        return "Error: Por favor suba un archivo de audio (MP3, WAV, OGG, M4A).", None, None

    # Decode the file content
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    # Check file size (5MB limit)
    if len(decoded) > 5 * 1024 * 1024:  # 5MB in bytes
        return "Error: El tamaño del archivo excede el límite de 5MB.", None, None

    # Store the audio data
    audio_data = {
        'content': contents,
        'filename': filename
    }

    # Create audio player component
    audio_player = html.Div([
        html.H6(f"Archivo seleccionado: {filename}", className="mt-2"),
        html.Audio(
            id='audio-player-2',
            src=contents,
            controls=True,
            style={'width': '100%', 'marginTop': '5px'}
        )
    ])

    return None, audio_player, json.dumps(audio_data)

# Callbacks to show/hide track 2 and speed slider 2 based on track mode
@callback(
    [Output('track-2-container', 'style'),
     Output('speed-control-2-container', 'style')],
    [Input('track-mode-selector', 'value')]
)
def toggle_track2_visibility(track_mode):
    if track_mode == 'single':
        return {'display': 'none'}, {'display': 'none'}
    else:
        return {'display': 'block'}, {'display': 'block'}


# Callbacks to update the value displays for sliders
@callback(
    Output('delay-value-display', 'children'),
    [Input('delay-slider', 'value')]
)
def update_delay_display(value):
    return f"Retraso actual: {value} ms"

@callback(
    Output('speed-value-display-1', 'children'),
    [Input('speed-slider-1', 'value')]
)
def update_speed1_display(value):
    return f"Velocidad actual: {value}x"

@callback(
    Output('speed-value-display-2', 'children'),
    [Input('speed-slider-2', 'value')]
)
def update_speed2_display(value):
    return f"Velocidad actual: {value}x"

# Register clientside callbacks for audio playback
app.clientside_callback(
    ClientsideFunction(
        namespace='audio_processor',
        function_name='processAudioWithDelay'
    ),
    Output('playback-status', 'children'),
    [Input('play-button', 'n_clicks')],
    [State('delay-slider', 'value'),
     State('loop-count', 'value'),
     State('audio-storage-1', 'children'),
     State('audio-storage-2', 'children'),
     State('track-mode-selector', 'value'),
     State('speed-slider-1', 'value'),
     State('speed-slider-2', 'value')]
)

app.clientside_callback(
    ClientsideFunction(
        namespace='audio_processor',
        function_name='stopAudioPlayback'
    ),
    Output('playback-status', 'children', allow_duplicate=True),
    [Input('stop-button', 'n_clicks')],
    prevent_initial_call=True
)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
