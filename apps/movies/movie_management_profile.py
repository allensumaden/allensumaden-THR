from urllib.parse import parse_qs, urlparse

import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB, modifyDB

layout = html.Div(
    [

        dcc.Store(id='movieprofile_movieid', storage_type='memory', data=0),
        
        html.H2('Movie Details'), # Page Header
        html.Hr(),
        dbc.Alert(id='movieprofile_alert', is_open=False), # For feedback purposes
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Label("Title", width=1),
                        dbc.Col(
                            dbc.Input(
                                type='text', 
                                id='movieprofile_title',
                                placeholder="Title"
                            ),
                            width=5
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Genre", width=1),
                        dbc.Col(
                            html.Div(
                                dcc.Dropdown(
                                    id='movieprofile_genre',
                                    placeholder='Genre'
                                ),
                                className='dash-bootstrap'
                            ),
                            width=5,
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Country", width=1),
                        dbc.Col(
                            html.Div(
                                dcc.Dropdown(
                                    id='movieprofile_country',
                                    placeholder='Country'
                                ),
                                className='dash-bootstrap'
                            ),
                            width=5,
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Language", width=1),
                        dbc.Col(
                            html.Div(
                                dcc.Dropdown(
                                    id='movieprofile_language',
                                    placeholder='Language'
                                ),
                                className='dash-bootstrap'
                            ),
                            width=5,
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Actor", width=1),
                        dbc.Col(
                            html.Div(
                                dcc.Dropdown(
                                    id='movieprofile_actor',
                                    placeholder='Actor'
                                ),
                                className='dash-bootstrap'
                            ),
                            width=5,
                        )
                    ],
                    className='mb-3'
                ),
                dbc.Row(
                    [
                        dbc.Label("Release Date", width=1),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id='movieprofile_releasedate',
                                placeholder='Release Date',
                                month_format='MMM Do, YY',
                            ),
                            width=5, 
                            className='dash-bootstrap'
                        )
                    ],
                    className='mb-3'
                ),
                html.Div(
                    [
                        dbc.Checklist(
                            id='movieprofile_deleteind',
                            options= [dict(value=1, label="Mark as Deleted")],
                            value=[] 
                        )
                    ], 
                    id='movieprofile_deletediv'
                )

            ]
        ),
          dbc.Button(
            'Submit',
            id='movieprofile_submit',
            n_clicks=0 # Initialize number of clicks
        ),
        dbc.Modal( # Modal = dialog box; feedback for successful saving.
            [
                dbc.ModalHeader(
                    html.H4('Save Success',
                    id='movieprofile_modaltitle')
                ),
                dbc.ModalBody(
                    'Added to database!',
                    id='movieprofile_modalbody'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/movies/movie_management' # Clicking this would lead to a change of pages
                    )
                )
            ],
            centered=True,
            id='movieprofile_successmodal',
            backdrop='static' # Dialog box does not go away if you click at the background
        )
    ]
)

@app.callback(
    [
        Output('movieprofile_genre', 'options'),
        Output('movieprofile_movieid', 'data'),
        Output('movieprofile_deletediv', 'className')
    ],
    [
        Input('url', 'pathname'),
    ],
    [
        State('url', 'search'),
    ]
)
def movieprofile_populategenres(pathname, urlsearch):
    if pathname == '/movies/movie_management_profile':
        sql = """
        SELECT genre_name as label, genre_id as value
        FROM genres 
        WHERE genre_delete_ind = False
        """
        values = []
        cols = ['label', 'value']

        df = getDataFromDB(sql, values, cols)
        # The output must be a dictionary with the following structure
        # options=[
        #     {'label': "Factorial", 'value': 1},
        #     {'label': "Palindrome Checker", 'value': 2},
        #     {'label': "Greeter", 'value': 3},
        # ]

        genre_options = df.to_dict('records')

        parsed = urlparse(urlsearch)
        create_mode = parse_qs(parsed.query)['mode'][0]
        
        if create_mode == 'add':
            movieid = 0
            deletediv = 'd-none'
        else:
            movieid = int(parse_qs(parsed.query)['id'][0])
            deletediv = ''
        
        return [genre_options, movieid, deletediv]
    else:
        raise PreventUpdate
    
@app.callback(
    [
        Output('movieprofile_country', 'options'),
        Output('movieprofile_actor', 'options'),
        Output('movieprofile_language', 'options'),
    ],
    [
        Input('url', 'pathname'),
    ]
)
def movieprofile_populatelinks(pathname):
    if pathname == '/movies/movie_management_profile':
        country_sql = """
        SELECT country_name as label, country_id as value
        FROM countries
        WHERE NOT country_delete_ind
        ORDER BY country_name
        """
        actor_sql = """
        SELECT CONCAT_WS(' ', actor_fname, actor_lname) as label, actor_id as value
        FROM actors
        WHERE NOT actor_delete_ind
        ORDER BY label
        """
        language_sql = """
        SELECT language_name as label, language_id as value
        FROM languages
        WHERE NOT language_delete_ind
        ORDER BY language_name
        """
        cols = ['label', 'value']

        country_options = getDataFromDB(country_sql, [], cols).to_dict('records')
        actor_options = getDataFromDB(actor_sql, [], cols).to_dict('records')
        language_options = getDataFromDB(language_sql, [], cols).to_dict('records')
        return [country_options, actor_options, language_options]
    else:
        raise PreventUpdate
        
@app.callback(
    [
        # dbc.Alert Properties
        Output('movieprofile_alert', 'color'),
        Output('movieprofile_alert', 'children'),
        Output('movieprofile_alert', 'is_open'),
        # dbc.Modal Properties
        Output('movieprofile_successmodal', 'is_open'),
        Output('movieprofile_modaltitle', 'children'),
        Output('movieprofile_modalbody', 'children'),
    ],
    [
        Input('movieprofile_submit', 'n_clicks')
    ],
    [
        State('movieprofile_title', 'value'),
        State('movieprofile_genre', 'value'),
        State('movieprofile_country', 'value'),
        State('movieprofile_language', 'value'),
        State('movieprofile_actor', 'value'),
        State('movieprofile_releasedate', 'date'),
        State('url', 'search'),
        State('movieprofile_movieid', 'data'),
        State('movieprofile_deleteind', 'value'),
    ]
)
def movieprofile_saveprofile(submitbtn, title, genre, country, language, actor,
                             releasedate, urlsearch, movieid, deleteind):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        parsed = urlparse(urlsearch)
        create_mode = parse_qs(parsed.query)['mode'][0]
    else:
        raise PreventUpdate

    if eventid == 'movieprofile_submit' and submitbtn:

        alert_open = False
        modal_open = False
        modal_title = ''
        modal_text = ''
        alert_color = ''
        alert_text = ''

        if not title:
            alert_open = True
            alert_color = 'danger'
            alert_text = 'Check your inputs. Please supply the movie title.'
        elif not genre:
            alert_open = True
            alert_color = 'danger'
            alert_text = 'Check your inputs. Please supply the movie genre.'
        elif not language:
            alert_open = True
            alert_color = 'danger'
            alert_text = 'Check your inputs. Please supply the movie language.'
        elif not releasedate:
            alert_open = True
            alert_color = 'danger'
            alert_text = 'Check your inputs. Please supply the movie release date.'
        else:

            if create_mode == 'add':

                check_sql = """
                    SELECT movie_id
                    FROM movies
                    WHERE LOWER(movie_name) = LOWER(%s)
                        AND movie_delete_ind = False
                """
                check_df = getDataFromDB(check_sql, [title.strip()], ['movie_id'])

                if not check_df.empty:
                    alert_open = True
                    alert_color = 'danger'
                    alert_text = 'Movie title already exists. Please enter a unique title.'
                    return [alert_color, alert_text, alert_open, modal_open, modal_title, modal_text]

                sql = '''
                    INSERT INTO movies (movie_name, genre_id, country_id, language_id, actor_id,
                        movie_release_date, movie_delete_ind)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                '''
                values = [title, genre, country, language, actor, releasedate, False]

                modal_title = 'Movie Added'
                modal_text = 'The movie was added successfully.'

            elif create_mode == 'edit':
                sql = '''
                    UPDATE movies
                    SET
                        movie_name = %s,
                        genre_id = %s,
                        country_id = %s,
                        language_id = %s,
                        actor_id = %s,
                        movie_release_date = %s,
                        movie_delete_ind = %s
                    WHERE
                        movie_id = %s
                '''
                values = [title, genre, country, language, actor, releasedate,
                          bool(deleteind), movieid]

                if deleteind:
                    modal_title = 'Movie Deleted'
                    modal_text = 'The movie was marked as deleted.'
                else:
                    modal_title = 'Movie Updated'
                    modal_text = 'The movie details were updated successfully.'

            else:
                raise PreventUpdate

            modifyDB(sql, values)
            modal_open = True

        return [alert_color, alert_text, alert_open, modal_open, modal_title, modal_text]

    else:
        raise PreventUpdate

@app.callback(
    [
        Output('movieprofile_title', 'value'),
        Output('movieprofile_genre', 'value'),
        Output('movieprofile_releasedate', 'date'),
        Output('movieprofile_country', 'value'),
        Output('movieprofile_actor', 'value'),
        Output('movieprofile_language', 'value'),
    ],
    [
        Input('movieprofile_movieid', 'modified_timestamp')
    ],
    [
        State('movieprofile_movieid', 'data'),
    ]
)
def movieprofile_loadprofile(timestamp, movieid):
    if movieid:

        sql = """
            SELECT movie_name, genre_id, movie_release_date, country_id, actor_id, language_id
            FROM movies
            WHERE movie_id = %s
        """
        values = [movieid]
        col = ['moviename', 'genreid', 'releasedate', 'countryid', 'actorid', 'languageid']

        df = getDataFromDB(sql, values, col)

        moviename = df['moviename'][0]
        genreid = int(df['genreid'][0])
        releasedate = df['releasedate'][0]

        # Empty database values come back as NaN; convert them to None
        countryid = None if pd.isna(df['countryid'][0]) else int(df['countryid'][0])
        actorid = None if pd.isna(df['actorid'][0]) else int(df['actorid'][0])
        languageid = None if pd.isna(df['languageid'][0]) else int(df['languageid'][0])

        return [moviename, genreid, releasedate, countryid, actorid, languageid]

    else:
        raise PreventUpdate