from urllib.parse import parse_qs, urlparse

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB, modifyDB

layout = html.Div(
    [
        dcc.Store(id='actorprofile_actorid', storage_type='memory', data=0),

        html.H2('Actor Details'),
        html.Hr(),
        dbc.Alert(id='actorprofile_alert', is_open=False),
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("First Name", width=1),
                        dbc.Col(
                            dbc.Input(type='text', id='actorprofile_fname',
                                      placeholder="First Name"),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Last Name", width=1),
                        dbc.Col(
                            dbc.Input(type='text', id='actorprofile_lname',
                                      placeholder="Last Name"),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                html.Div(
                    [
                        dbc.Checklist(
                            id='actorprofile_deleteind',
                            options=[dict(value=1, label="Mark as Deleted")],
                            value=[]
                        )
                    ],
                    id='actorprofile_deletediv'
                )
            ]
        ),
        dbc.Button(
            'Submit',
            id='actorprofile_submit',
            n_clicks=0
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(html.H4('Save Success', id='actorprofile_modaltitle')),
                dbc.ModalBody('Added to database!', id='actorprofile_modalbody'),
                dbc.ModalFooter(
                    dbc.Button("Proceed", href='/actors/actor_management')
                )
            ],
            centered=True,
            id='actorprofile_successmodal',
            backdrop='static'
        )
    ]
)


@app.callback(
    [
        Output('actorprofile_actorid', 'data'),
        Output('actorprofile_deletediv', 'className')
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('url', 'search'),
    ]
)
def actorprofile_setupmode(pathname, urlsearch):
    if pathname == '/actors/actor_management_profile':

        parsed = urlparse(urlsearch)
        create_mode = parse_qs(parsed.query)['mode'][0]

        if create_mode == 'add':
            actorid = 0
            deletediv = 'd-none'
        else:
            actorid = int(parse_qs(parsed.query)['id'][0])
            deletediv = ''

        return [actorid, deletediv]
    else:
        raise PreventUpdate


@app.callback(
    [
        Output('actorprofile_alert', 'color'),
        Output('actorprofile_alert', 'children'),
        Output('actorprofile_alert', 'is_open'),
        Output('actorprofile_successmodal', 'is_open'),
        Output('actorprofile_modaltitle', 'children'),
        Output('actorprofile_modalbody', 'children'),
    ],
    [
        Input('actorprofile_submit', 'n_clicks')
    ],
    [
        State('actorprofile_fname', 'value'),
        State('actorprofile_lname', 'value'),
        State('url', 'search'),
        State('actorprofile_actorid', 'data'),
        State('actorprofile_deleteind', 'value'),
    ]
)
def actorprofile_saveprofile(submitbtn, fname, lname, urlsearch, actorid, deleteind):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        parsed = urlparse(urlsearch)
        create_mode = parse_qs(parsed.query)['mode'][0]
    else:
        raise PreventUpdate

    if eventid == 'actorprofile_submit' and submitbtn:

        alert_open = False
        modal_open = False
        modal_title = ''
        modal_text = ''
        alert_color = ''
        alert_text = ''

        if not fname or not lname:
            alert_open = True
            alert_color = 'danger'
            alert_text = 'Check your inputs. Please supply both first and last name.'
        else:

            # Duplicate check: skipped when deleting, and excludes the current actor
            # so saving an unchanged record does not count as a duplicate
            if not deleteind:
                check_sql = """
                    SELECT actor_id
                    FROM actors
                    WHERE LOWER(TRIM(actor_fname)) = LOWER(TRIM(%s))
                        AND LOWER(TRIM(actor_lname)) = LOWER(TRIM(%s))
                        AND NOT actor_delete_ind
                        AND actor_id <> %s
                """
                check_df = getDataFromDB(
                    check_sql, [fname.strip(), lname.strip(), actorid], ['actor_id']
                )

                if not check_df.empty:
                    alert_open = True
                    alert_color = 'danger'
                    alert_text = 'An active actor with this name already exists.'
                    return [alert_color, alert_text, alert_open, modal_open, modal_title, modal_text]

            if create_mode == 'add':
                sql = '''
                    INSERT INTO actors (actor_fname, actor_lname, actor_delete_ind)
                    VALUES (%s, %s, %s)
                '''
                values = [fname.strip(), lname.strip(), False]

                modal_title = 'Actor Added'
                modal_text = 'The actor was added successfully.'

            elif create_mode == 'edit':
                sql = '''
                    UPDATE actors
                    SET
                        actor_fname = %s,
                        actor_lname = %s,
                        actor_delete_ind = %s
                    WHERE
                        actor_id = %s
                '''
                values = [fname.strip(), lname.strip(), bool(deleteind), actorid]

                if deleteind:
                    modal_title = 'Actor Deleted'
                    modal_text = 'The actor was marked as deleted.'
                else:
                    modal_title = 'Actor Updated'
                    modal_text = 'The actor details were updated successfully.'

            else:
                raise PreventUpdate

            modifyDB(sql, values)
            modal_open = True

        return [alert_color, alert_text, alert_open, modal_open, modal_title, modal_text]

    else:
        raise PreventUpdate


@app.callback(
    [
        Output('actorprofile_fname', 'value'),
        Output('actorprofile_lname', 'value'),
        Output('actorprofile_deleteind', 'value'),
    ],
    [
        Input('actorprofile_actorid', 'modified_timestamp')
    ],
    [
        State('actorprofile_actorid', 'data'),
    ]
)
def actorprofile_loadprofile(timestamp, actorid):
    if actorid:

        sql = """
            SELECT actor_fname, actor_lname, actor_delete_ind
            FROM actors
            WHERE actor_id = %s
        """
        col = ['fname', 'lname', 'deleteind']

        df = getDataFromDB(sql, [actorid], col)

        fname = df['fname'][0]
        lname = df['lname'][0]
        deleteind = [1] if df['deleteind'][0] else []

        return [fname, lname, deleteind]

    else:
        raise PreventUpdate


@app.callback(
    Output('actorprofile_submit', 'children'),
    Output('actorprofile_submit', 'color'),
    Input('actorprofile_deleteind', 'value')
)
def actorprofile_togglesubmit(deleteind):
    if deleteind:
        return "Delete Record", "danger"
    return "Submit", "primary"