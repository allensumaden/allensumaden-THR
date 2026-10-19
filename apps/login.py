import hashlib

import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from apps import dbconnect as db

layout = html.Div(
    dbc.Card(
        [
            dbc.CardHeader(html.H3('Please Login', className='text-center mb-0')),
            dbc.CardBody(
                [
                    dbc.Label("Username"),
                    dbc.Input(type="text", id="login_username",
                              placeholder="Enter username", className="mb-3"),
                    dbc.Label("Password"),
                    dbc.Input(type="password", id="login_password",
                              placeholder="Enter password", className="mb-3"),
                    dbc.Button('Login', color="secondary", id='login_loginbtn',
                               className="w-100"),
                    html.Hr(),
                    html.Div(html.A('Signup Now!', href='/signup'),
                             className='text-center'),
                ]
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Incorrect username/password")),
                    dbc.ModalBody("Please check your credentials and try again."),
                    dbc.ModalFooter(
                        dbc.Button("Okay", id='login_modal_close', color="secondary")
                    ),
                ],
                id="login_modal",
                is_open=False,
            ),
        ],
        style={'width': '400px'},
    ),
    style={'display': 'flex', 'justifyContent': 'center',
           'alignItems': 'center', 'minHeight': '80vh'},
)


@app.callback(
    [
        Output('login_modal', 'is_open'),
        Output('currentuserid', 'data'),
    ],
    [
        Input('login_loginbtn', 'n_clicks'),
        Input('login_modal_close', 'n_clicks'),
        Input('sessionlogout', 'modified_timestamp'),
    ],
    [
        State('login_username', 'value'),
        State('login_password', 'value'),
        State('sessionlogout', 'data'),
        State('currentuserid', 'data'),
        State('url', 'pathname'),
    ]
)
def loginprocess(loginbtn, closebtn, sessionlogout_time,
                 username, password,
                 sessionlogout, currentuserid,
                 pathname):

    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    openalert = False
    eventid = ctx.triggered[0]['prop_id'].split('.')[0]

    if eventid == 'login_loginbtn':
        # ignore the automatic call when the page first loads
        if not loginbtn:
            raise PreventUpdate

        if username and password:
            sql = """SELECT user_id
            FROM users
            WHERE
                user_name = %s AND
                user_password = %s AND
                NOT user_delete_ind"""
            encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest()
            values = [username, encrypt_string(password)]
            df = db.getDataFromDB(sql, values, ['userid'])

            if df.shape[0]:
                currentuserid = df['userid'][0]
            else:
                currentuserid = -1
                openalert = True
        else:
            return [True, no_update]

    elif eventid == 'login_modal_close':
        if not closebtn:
            raise PreventUpdate
        return [False, no_update]

    elif eventid == 'sessionlogout' and pathname == '/logout':
        currentuserid = -1

    else:
        raise PreventUpdate

    return [openalert, currentuserid]


@app.callback(
    [
        Output('url', 'pathname'),
    ],
    [
        Input('currentuserid', 'modified_timestamp'),
    ],
    [
        State('currentuserid', 'data'),
    ]
)
def routelogin(logintime, userid):
    ctx = callback_context
    if ctx.triggered:
        if userid > 0:
            url = '/home'
        else:
            url = '/'
    else:
        raise PreventUpdate
    return [url]