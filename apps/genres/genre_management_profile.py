from urllib.parse import parse_qs, urlparse

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB, modifyDB

layout = html.Div(
    [

        dcc.Store(id='genreprofile_genreid', storage_type='memory', data=0),

        html.H2('Genre Details'), # Page Header
        html.Hr(),
        dbc.Alert(id='genreprofile_alert', is_open=False), # For feedback purposes
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Name", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='text',
                                id='genreprofile_name',
                                placeholder="Genre Name"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                html.Div(
                    [
                        dbc.Checklist(
                            id='genreprofile_deleteind',
                            options= [dict(value=1, label="Mark as Deleted")],
                            value=[]
                        )
                    ],
                    id='genreprofile_deletediv'
                )

            ]
        ),
          dbc.Button(
            'Submit',
            id='genreprofile_submit',
            n_clicks=0 # Initialize number of clicks
        ),
        dbc.Modal( # Modal = dialog box; feedback for successful saving.
            [
                dbc.ModalHeader(
                    html.H4('Save Success',
                    id='genreprofile_modaltitle')
                ),
                dbc.ModalBody(
                    'Added to database!',
                    id='genreprofile_modalbody'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/genres/genre_management'
                    )
                )
            ],
            centered=True,
            id='genreprofile_successmodal',
            backdrop='static'
        )
    ]
)

@app.callback(
    [
        Output('genreprofile_genreid', 'data'),
        Output('genreprofile_deletediv', 'className')
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('url', 'search'),
    ]
)
def genreprofile_setupmode(pathname, urlsearch):
    if pathname == '/genres/genre_management_profile':

        parsed = urlparse(urlsearch)
        create_mode = parse_qs(parsed.query)['mode'][0]

        if create_mode == 'add':
            genreid = 0
            deletediv = 'd-none'
        else:
            genreid = int(parse_qs(parsed.query)['id'][0])
            deletediv = ''

        return [genreid, deletediv]
    else:
        raise PreventUpdate


@app.callback(
    [
        # dbc.Alert Properties
        Output('genreprofile_alert', 'color'),
        Output('genreprofile_alert', 'children'),
        Output('genreprofile_alert', 'is_open'),
        # dbc.Modal Properties
        Output('genreprofile_successmodal', 'is_open'),
        Output('genreprofile_modaltitle', 'children'),
        Output('genreprofile_modalbody', 'children'),
    ],
    [
        Input('genreprofile_submit', 'n_clicks')
    ],
    [
        State('genreprofile_name', 'value'),
        State('url', 'search'),
        State('genreprofile_genreid', 'data'),
        State('genreprofile_deleteind', 'value'),
    ]
)
def genreprofile_saveprofile(submitbtn, name, urlsearch, genreid, deleteind):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        parsed = urlparse(urlsearch)
        create_mode = parse_qs(parsed.query)['mode'][0]
    else:
        raise PreventUpdate

    if eventid == 'genreprofile_submit' and submitbtn:

        alert_open = False
        modal_open = False
        modal_title = ''
        modal_text = ''
        alert_color = ''
        alert_text = ''

        if not name:
            alert_open = True
            alert_color = 'danger'
            alert_text = 'Check your inputs. Please supply the genre name.'
        else:

            if create_mode == 'add':
            
                check_sql = """
                    SELECT genre_id
                    FROM genres
                    WHERE LOWER(genre_name) = LOWER(%s)
                        AND genre_delete_ind = False
                """
                check_df = getDataFromDB(check_sql, [name.strip()], ['genre_id'])

                if not check_df.empty:
                    alert_open = True
                    alert_color = 'danger'
                    alert_text = 'Genre name already exists. Please enter a unique genre name.'
                    return [alert_color, alert_text, alert_open, modal_open, modal_title, modal_text]

                sql = '''
                    INSERT INTO genres (genre_name, genre_delete_ind)
                    VALUES (%s, %s)
                '''
                values = [name.strip(), False]

                modal_title = 'Genre Added'
                modal_text = 'The genre was added successfully.'

            elif create_mode == 'edit':
                sql = '''
                    UPDATE genres
                    SET
                        genre_name = %s,
                        genre_delete_ind = %s
                    WHERE
                        genre_id = %s
                '''
                values = [name, bool(deleteind), genreid]

                if deleteind:
                    modal_title = 'Genre Deleted'
                    modal_text = 'The genre was marked as deleted.'
                else:
                    modal_title = 'Genre Updated'
                    modal_text = 'The genre details were updated successfully.'

            else:
                raise PreventUpdate

            modifyDB(sql, values)
            modal_open = True

        return [alert_color, alert_text, alert_open, modal_open, modal_title, modal_text]

    else:
        raise PreventUpdate


@app.callback(
    [
        Output('genreprofile_name', 'value'),
    ],
    [
        Input('genreprofile_genreid', 'modified_timestamp')
    ],
    [
        State('genreprofile_genreid', 'data'),
    ]
)
def genreprofile_loadprofile(timestamp, genreid):
    if genreid: # check if genreid > 0

        # Query from db
        sql = """
            SELECT genre_name
            FROM genres
            WHERE genre_id = %s
        """
        values = [genreid]
        col = ['genrename']

        df = getDataFromDB(sql, values, col)
        genrename = df['genrename'][0]

        return [genrename]

    else:
        raise PreventUpdate

@app.callback(
    Output('genreprofile_submit', 'children'),
    Output('genreprofile_submit', 'color'),
    Input('genreprofile_deleteind', 'value')
)
def genreprofile_togglesubmit(deleteind):
    if deleteind:
        return "Delete Record", "danger"
    return "Submit", "primary"