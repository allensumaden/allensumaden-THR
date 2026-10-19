import webbrowser

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from apps import commonmodules as cm
from apps import home
from apps import signup
from apps import login
from apps.movies import movie_management, movie_management_profile
from apps.genres import genre_management, genre_management_profile
from apps.actors import actor_management, actor_management_profile
from apps.reports import report, genre_language_report

app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=True),

        # LOGIN DATA
        dcc.Store(id='sessionlogout', data=True, storage_type='session'),
        dcc.Store(id='currentuserid', data=-1, storage_type='session'),
        dcc.Store(id='currentrole', data=-1, storage_type='session'),

        html.Div(cm.navbar, id='navbar_div'),

        html.Div(id='page_content', className='m-2 p-2'),
    ]
)


@app.callback(
    [
        Output('page_content', 'children'),
        Output('sessionlogout', 'data'),
        Output('navbar_div', 'className'),
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('sessionlogout', 'data'),
        State('currentuserid', 'data'),
    ]
)
def displaypage(pathname, sessionlogout, userid):

    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
    else:
        raise PreventUpdate

    if eventid == 'url':
        if userid < 0:  # logged out
            if pathname == '/':
                returnlayout = login.layout
            elif pathname == '/signup':
                returnlayout = signup.layout
            else:
                returnlayout = 'error404'

        else:  # logged in
            if pathname == '/logout':
                returnlayout = login.layout
                sessionlogout = True
            elif pathname == '/' or pathname == '/home':
                returnlayout = home.layout
            elif pathname == '/reports/report':
                returnlayout = report.layout
            elif pathname == '/reports/genre_language_report':
                returnlayout = genre_language_report.layout
            elif pathname == '/movies/movie_management':
                returnlayout = movie_management.layout
            elif pathname == '/movies/movie_management_profile':
                returnlayout = movie_management_profile.layout
            elif pathname == '/genres/genre_management':
                returnlayout = genre_management.layout
            elif pathname == '/genres/genre_management_profile':
                returnlayout = genre_management_profile.layout
            elif pathname == '/actors/actor_management':
                returnlayout = actor_management.layout
            elif pathname == '/actors/actor_management_profile':
                returnlayout = actor_management_profile.layout
            else:
                returnlayout = 'error404'

        logout_conditions = [
            pathname in ['/', '/logout'],
            userid == -1,
            not userid
        ]
        sessionlogout = any(logout_conditions)
        navbar_classname = 'd-none' if sessionlogout else ''

        return [returnlayout, sessionlogout, navbar_classname]
    else:
        raise PreventUpdate


if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new=0, autoraise=True)
    app.run(debug=False)

    