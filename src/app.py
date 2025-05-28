import dash
from dash import html, dcc, Input, Output, State, callback, ctx, ClientsideFunction
import dash_bootstrap_components as dbc
import base64
import json
import numpy as np
import plotly.graph_objs as go

# Función para calcular la escala de Bark
def bark_scale(f):
    """
    Calcula el valor en la escala de Bark para una frecuencia dada en Hz.

    Parámetros:
    f (float o array): Frecuencia en Hz

    Retorna:
    float o array: Valor correspondiente en la escala de Bark
    """
    return 13 * np.arctan(0.00076 * f) + 3.5 * np.arctan((f/7500)**2)

# Función para generar la gráfica de la escala de Bark
def generate_bark_scale_figure():
    """
    Genera una figura de Plotly que muestra la relación entre frecuencia (Hz) y la escala de Bark.

    Retorna:
    plotly.graph_objs.Figure: Figura con la gráfica de la escala de Bark
    """
    # Generar un rango de frecuencias de 20 Hz a 20 kHz (rango audible humano)
    frequencies = np.logspace(np.log10(20), np.log10(20000), 1000)

    # Calcular los valores correspondientes en la escala de Bark
    bark_values = bark_scale(frequencies)

    # Crear la figura
    fig = go.Figure()

    # Añadir la línea de la escala de Bark
    fig.add_trace(go.Scatter(
        x=frequencies,
        y=bark_values,
        mode='lines',
        name='Escala de Bark',
        line=dict(color='blue', width=2)
    ))

    # Definir las frecuencias límite de las bandas críticas de Bark
    band_boundaries = [
        0, 100, 200, 300, 400, 510, 630, 770, 920, 1080, 1270, 1480, 
        1720, 2000, 2320, 2700, 3150, 3700, 4400, 5300, 6400, 7700, 9500, 12000, 15500
    ]

    # Calcular los valores de Bark correspondientes a las frecuencias límite
    band_bark_values = bark_scale(np.array(band_boundaries))

    # Añadir puntos rojos para las bandas críticas
    fig.add_trace(go.Scatter(
        x=band_boundaries,
        y=band_bark_values,
        mode='markers',
        name='Bandas Críticas',
        marker=dict(
            color='red',
            size=8,
            symbol='circle'
        )
    ))

    # Configurar el diseño de la gráfica
    fig.update_layout(
        title='Relación entre Frecuencia y Escala de Bark',
        xaxis=dict(
            title='Frecuencia (Hz)',
            type='log',
            tickformat='.0f',
            gridcolor='lightgray'
        ),
        yaxis=dict(
            title='Escala de Bark (z)',
            gridcolor='lightgray'
        ),
        plot_bgcolor='white',
        margin=dict(l=40, r=40, t=50, b=40),
        height=500,
        width=700,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

# Inicializar la aplicación Dash con el tema Bootstrap
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True,
)

# Usar la cadena de índice predeterminada de Dash (CSS ahora está en assets/custom_styles.css)

# Establecer el título de la aplicación
app.title = "Panel de Palabras Fantasma"

# Definir el estilo del encabezado con fondo azul claro
header_style = {
    "backgroundColor": "#ADD8E6",  # Color azul claro
    "padding": "2rem 1rem",
    "textAlign": "center",
    "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
    "marginBottom": "2rem",
}

# Definir el diseño de la aplicación
app.layout = html.Div([
    # Sección de encabezado
    html.Div([
        html.H1("Panel de Palabras Fantasma", className="display-4"),
        html.P("Una demostración del efecto de Palabras Fantasma", className="lead"),
    ], style=header_style),

    # Contenedor principal de contenido
    dbc.Container([
        # Sección de carga de audio
        dbc.Row([
            dbc.Col([
                html.H3("Subir Archivos de Audio", className="mb-3"),
                html.P("Seleccione archivos de audio para experimentar el efecto de Palabras Fantasma. Los archivos deben ser archivos de audio y menos de 5MB cada uno."),
            ], width=12),
        ], className="mb-2"),

        # Selector de modo de pista
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

        # Sección de controles
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

        # Controles deslizantes de velocidad
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

        # Botón de reproducción para el efecto de palabras fantasma
        dbc.Row([
            dbc.Col([
                html.H4("Reproducir Efecto de Palabras Fantasma", className="mb-3"),
                html.P("Haga clic en los botones a continuación para reproducir o detener el audio con el efecto de palabras fantasma:"),
            ], width=12),
        ], className="mb-2"),

        # Fila de botones con espacio
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

            # Columna vacía para espaciado
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

        # Sección de ejemplo de la escala de Bark
        dbc.Row([
            dbc.Col([
                html.H4("Ejemplo de Escala de Bark", className="mb-3"),
                html.P([
                    "La escala de Bark es una escala psicoacústica que representa cómo los humanos perciben las frecuencias de sonido. ",
                    "Está dividida en bandas críticas (o 'barks') que corresponden a cómo nuestro sistema auditivo procesa diferentes rangos de frecuencia. ",
                    "Esta escala es relevante para el efecto de palabras fantasma porque ayuda a entender cómo nuestro cerebro interpreta y fusiona sonidos, ",
                    "especialmente cuando se presentan estímulos auditivos repetitivos y superpuestos como en este experimento."
                ]),
            ], width=12),
        ], className="mb-3"),

        # Visualización de la escala de Bark
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(
                        id='bark-scale-graph',
                        figure=generate_bark_scale_figure(),
                        config={'displayModeBar': False}
                    ),
                    html.Figcaption(
                        "Figura: Representación de la escala de Bark que muestra la relación no lineal entre la frecuencia (Hz) y la percepción auditiva (Bark). Generada con la ecuación: z(f) = 13 * arctan(0.00076 * f) + 3.5 * arctan((f/7500)²)",
                        style={"textAlign": "center", "marginTop": "10px", "fontStyle": "italic"}
                    )
                ]),
            ], width=12),
        ]),

        # Tabla de bandas críticas de Bark
        dbc.Row([
            dbc.Col([
                html.H5("Bandas Críticas de la Escala de Bark", className="mb-3"),
                html.P("La siguiente tabla muestra todas las bandas críticas de la escala de Bark y sus rangos de frecuencia correspondientes:"),
                dbc.Table([
                    html.Thead(
                        html.Tr([
                            html.Th("Banda Bark"),
                            html.Th("Rango de Frecuencia (Hz)"),
                            html.Th("Ancho de Banda (Hz)"),
                            html.Th("Frecuencia Central (Hz)")
                        ])
                    ),
                    html.Tbody([
                        html.Tr([html.Td("1"), html.Td("0 - 100"), html.Td("100"), html.Td("50")]),
                        html.Tr([html.Td("2"), html.Td("100 - 200"), html.Td("100"), html.Td("150")]),
                        html.Tr([html.Td("3"), html.Td("200 - 300"), html.Td("100"), html.Td("250")]),
                        html.Tr([html.Td("4"), html.Td("300 - 400"), html.Td("100"), html.Td("350")]),
                        html.Tr([html.Td("5"), html.Td("400 - 510"), html.Td("110"), html.Td("450")]),
                        html.Tr([html.Td("6"), html.Td("510 - 630"), html.Td("120"), html.Td("570")]),
                        html.Tr([html.Td("7"), html.Td("630 - 770"), html.Td("140"), html.Td("700")]),
                        html.Tr([html.Td("8"), html.Td("770 - 920"), html.Td("150"), html.Td("840")]),
                        html.Tr([html.Td("9"), html.Td("920 - 1080"), html.Td("160"), html.Td("1000")]),
                        html.Tr([html.Td("10"), html.Td("1080 - 1270"), html.Td("190"), html.Td("1170")]),
                        html.Tr([html.Td("11"), html.Td("1270 - 1480"), html.Td("210"), html.Td("1370")]),
                        html.Tr([html.Td("12"), html.Td("1480 - 1720"), html.Td("240"), html.Td("1600")]),
                        html.Tr([html.Td("13"), html.Td("1720 - 2000"), html.Td("280"), html.Td("1850")]),
                        html.Tr([html.Td("14"), html.Td("2000 - 2320"), html.Td("320"), html.Td("2150")]),
                        html.Tr([html.Td("15"), html.Td("2320 - 2700"), html.Td("380"), html.Td("2500")]),
                        html.Tr([html.Td("16"), html.Td("2700 - 3150"), html.Td("450"), html.Td("2900")]),
                        html.Tr([html.Td("17"), html.Td("3150 - 3700"), html.Td("550"), html.Td("3400")]),
                        html.Tr([html.Td("18"), html.Td("3700 - 4400"), html.Td("700"), html.Td("4000")]),
                        html.Tr([html.Td("19"), html.Td("4400 - 5300"), html.Td("900"), html.Td("4800")]),
                        html.Tr([html.Td("20"), html.Td("5300 - 6400"), html.Td("1100"), html.Td("5800")]),
                        html.Tr([html.Td("21"), html.Td("6400 - 7700"), html.Td("1300"), html.Td("7000")]),
                        html.Tr([html.Td("22"), html.Td("7700 - 9500"), html.Td("1800"), html.Td("8500")]),
                        html.Tr([html.Td("23"), html.Td("9500 - 12000"), html.Td("2500"), html.Td("10500")]),
                        html.Tr([html.Td("24"), html.Td("12000 - 15500"), html.Td("3500"), html.Td("13500")])
                    ])
                ], bordered=True, hover=True, responsive=True, striped=True, className="mb-3"),
                html.P([
                    "En el efecto de palabras fantasma, los sonidos que caen dentro de la misma banda crítica tienden a ser procesados juntos por el cerebro, ",
                    "lo que puede contribuir a la percepción de palabras o frases que no están realmente presentes en el estímulo auditivo original."
                ]),
            ], width=12),
        ], className="mb-4"),

        # Divs ocultos para almacenar los datos de audio
        html.Div(id='audio-storage-1', style={'display': 'none'}),
        html.Div(id='audio-storage-2', style={'display': 'none'}),

    ]),

    # Pie de página
    html.Footer([
        html.P("Proyecto de Palabras Fantasma - 2025", className="text-center text-muted"),
    ], style={"padding": "2rem 0", "marginTop": "2rem", "borderTop": "1px solid #e7e7e7"}),
])

# Callback para validar el archivo cargado y almacenar datos de audio para la Pista 1
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

    # Verificar la extensión del archivo
    if not filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
        return "Error: Por favor suba un archivo de audio (MP3, WAV, OGG, M4A).", None, None

    # Decodificar el contenido del archivo
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    # Verificar el tamaño del archivo (límite de 30MB)
    if len(decoded) > 30 * 1024 * 1024:  # 5MB en bytes
        return "Error: El tamaño del archivo excede el límite de 30MB.", None, None

    # Almacenar los datos de audio
    audio_data = {
        'content': contents,
        'filename': filename
    }

    # Crear componente de reproductor de audio
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

# Callback para validar el archivo cargado y almacenar datos de audio para la Pista 2
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

    # Verificar la extensión del archivo
    if not filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
        return "Error: Por favor suba un archivo de audio (MP3, WAV, OGG, M4A).", None, None

    # Decodificar el contenido del archivo
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    # Verificar el tamaño del archivo (límite de 5MB)
    if len(decoded) > 5 * 1024 * 1024:  # 5MB en bytes
        return "Error: El tamaño del archivo excede el límite de 5MB.", None, None

    # Almacenar los datos de audio
    audio_data = {
        'content': contents,
        'filename': filename
    }

    # Crear componente de reproductor de audio
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

# Callbacks para mostrar/ocultar la pista 2 y el control deslizante de velocidad 2 según el modo de pista
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


# Callbacks para actualizar las visualizaciones de valores para los controles deslizantes
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

# Registrar callbacks del lado del cliente para la reproducción de audio
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

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run_server(debug=True)
