import hashlib

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from apps import dbconnect as db

layout = html.Div(
    dbc.Card(
        [
            dbc.CardHeader(html.H3('Sign Up', className='text-center mb-0')),
            dbc.CardBody(
                [
                    dbc.Alert('Please supply details.', color="danger",
                              id='signup_alert', is_open=False),
                    dbc.Label("Username"),
                    dbc.Input(type="text", id="signup_username",
                              placeholder="Enter a username", className="mb-3"),
                    dbc.Label("Password"),
                    dbc.Input(type="password", id="signup_password",
                              placeholder="Enter a password", className="mb-3"),
                    dbc.Label("Confirm Password"),
                    dbc.Input(type="password", id="signup_passwordconf",
                              placeholder="Re-type the password", className="mb-3"),
                    dbc.Button('Sign up', color="secondary",
                               id='singup_signupbtn', className="w-100"),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("User Saved")),
                            dbc.ModalBody("User has been saved", id='signup_confirmation'),
                            dbc.ModalFooter(
                                dbc.Button("Okay", href='/')
                            ),
                        ],
                        id="signup_modal",
                        is_open=False,
                    ),
                ]
            ),
        ],
        style={'width': '400px'},
    ),
    style={'display': 'flex', 'justifyContent': 'center',
           'alignItems': 'center', 'minHeight': '80vh'},
)


@app.callback(
    [
        Output('signup_alert', 'is_open'),
        Output('signup_alert', 'children'),
        Output('signup_modal', 'is_open')
    ],
    [
        Input('singup_signupbtn', 'n_clicks')
    ],
    [
        State('signup_username', 'value'),
        State('signup_password', 'value')
    ]
)
def saveuser(loginbtn, username, password):
    if not loginbtn:
        raise PreventUpdate

    if not (username and password):
        return [True, 'Please supply details.', False]

    # check for an existing username first
    sql_check = """SELECT user_id FROM users
                   WHERE user_name = %s AND NOT user_delete_ind"""
    df = db.getDataFromDB(sql_check, [username], ['userid'])
    if df.shape[0]:
        return [True, 'Username already exists. Please choose another.', False]

    sql = """INSERT INTO users (user_name, user_password)
             VALUES (%s, %s)"""
    encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest()
    db.modifyDB(sql, [username, encrypt_string(password)])

    return [False, 'Please supply details.', True]

def deactivatesignup(password, passwordconf):

    # enable button if password exists and passwordconf exists
    #  and password = passwordconf
    enablebtn = password and passwordconf and password == passwordconf

    return [not enablebtn]


# To save the user
@app.callback(
    [
        Output('signup_alert', 'is_open'),
        Output('signup_modal', 'is_open')
    ],
    [
        Input('singup_signupbtn', 'n_clicks')
    ],
    [
        State('signup_username', 'value'),
        State('signup_password', 'value')
    ]
)
def saveuser(loginbtn, username, password):
    openalert = openmodal = False
    if loginbtn:
        if username and password:
            sql = """INSERT INTO users (user_name, user_password)
            VALUES (%s, %s)"""

            # This lambda fcn encrypts the password before saving it
            # for security purposes, not even database admins should see
            # user passwords
            encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest()

            values = [username, encrypt_string(password)]
            db.modifyDB(sql, values)

            openmodal = True
        else:
            openalert = True
    else:
        raise PreventUpdate

    return [openalert, openmodal]