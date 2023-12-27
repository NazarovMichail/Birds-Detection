import dash
from dash import dcc
from dash import html, dcc, callback, Output, Input, State, clientside_callback
import dash_mantine_components as dmc
from roboflow import Roboflow
from save_target import save_target_func
import base64
import os


app = dash.Dash(__name__)
TOKEN = os.environ.get('TOKEN')
rf = Roboflow(api_key=TOKEN)
project = rf.workspace().project("birds-detection-riiaw")
model = project.version(5).model
UPLOAD_DIRECTORY = 'data/data_for_prediction'
PREDICTED_DATA_DIRECTORY = 'data/prediction_data'

style = {
    "height": 100,
    'lineHeight': '60px',
    'borderWidth': '1px',
    "border": f"1px solid {dmc.theme.DEFAULT_COLORS['indigo'][4]}",
    'borderStyle': 'dashed',
    'margin': '10px'
}
app.layout = html.Div(
    style={'background-image': 'url("/assets/gradients_app.png")','background-size': 'cover', 'height': '100vh',
           'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
    children=[
                html.Div(
                            style={'width': '75%', 'background-color': 'white', 'padding': '20px'},
                            children=[
                    html.Div(
                        children=[
                            dmc.Container(style=style,
                                      children=
                                            dcc.Upload(
                                                id='upload_data',
                                                children= dmc.Image(
                                                        id = 'classified_img',
                                                        width='100%',
                                                        height=100,
                                                        withPlaceholder=True,
                                                        placeholder="Нажмите или перетащите картинку",
                                                    ),

                                                multiple=False
                                            )
                                      )
                    ]
                ),
                dmc.Button(
                            "Классифицировать",
                            id='classify-button',
                            variant="gradient",
                            gradient={"from": "indigo", "to": "cyan"},
                        ),
                #html.Button('Классифицировать', id='classify-button'),
                html.Div(id='output-image-upload'),
                dmc.Center(
                    children=[
                        dmc.Text(
                            id = 'place_for_class',
                            variant="gradient",
                            gradient={"from": "red", "to": "yellow", "deg": 45},
                            style={"fontSize": 20},
                        )
                    ]
                )
            ]
        )
    ]
)
@callback(
    [Output(component_id='output-image-upload', component_property='children', allow_duplicate=True),
     Output(component_id='place_for_class', component_property='children'),
     Output("classify-button", "loading")],
    Input(component_id='classify-button', component_property='n_clicks'),
    State(component_id="upload_data", component_property="contents"),# upload_data , contents
    prevent_initial_call=True)
def classify_bird(n_clicks, contents):
    y_pred =model.predict("/".join([UPLOAD_DIRECTORY,"new_target.jpg"]), confidence=40, overlap=30).json()
    y_pred = y_pred['predictions'][0]['class']
    model.predict("/".join([UPLOAD_DIRECTORY,"new_target.jpg"]), confidence=40, overlap=30).save('/'.join(
        [PREDICTED_DATA_DIRECTORY,"prediction.jpg"]))
    with open('/'.join([PREDICTED_DATA_DIRECTORY,"prediction.jpg"]), "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        predicted_image = f"data:image/jpeg;base64,{encoded_string}"

    return html.Img(src=predicted_image,
        style={'width': '50%', 'display': 'block', 'margin': 'auto'}),y_pred,False

@callback(Output('output-image-upload', 'children', allow_duplicate=True),
          Input('upload_data', 'contents'),
          prevent_initial_call = True)
def update_output(contents):
    if contents is not None:
        save_target_func(contents)
        return html.Img(src=contents, style={'width': '50%', 'display': 'block', 'margin': 'auto'})

clientside_callback(# функция JS, будет выполнена на стороне клиента
    """
    function updateLoadingState(n_clicks) {
        return true
    }
    """,
    Output("classify-button", "loading", allow_duplicate=True),
    Input("classify-button", "n_clicks"),
    prevent_initial_call=True,
)

if __name__ == '__main__':
    app.run_server(debug=True)
