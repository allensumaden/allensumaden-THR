from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from app import app
from apps import dbconnect as db


layout = html.Div(
    [
        html.H2('Reports'),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(html.H3('Movies per Genre and Language')),
                dbc.CardBody(
                    [
                        dbc.Form(
                            [
                                dbc.Row(
                                    [
                                        dbc.Label("Genre", width=1),
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id='glreport_genrefilter',
                                                placeholder='Select Genre',
                                                searchable=True,
                                                options=[],
                                                multi=True
                                            ),
                                            width=5
                                        ),
                                    ],
                                    className='mb-3'
                                ),
                                dbc.Row(
                                    [
                                        dbc.Label("Language", width=1),
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id='glreport_languagefilter',
                                                placeholder='Select Language',
                                                searchable=True,
                                                options=[],
                                                multi=True
                                            ),
                                            width=5
                                        ),
                                    ],
                                    className='mb-3'
                                ),
                            ]
                        ),
                        html.Hr(),
                        html.Div(id='glreport_table')
                    ]
                )
            ]
        )
    ]
)


# Populate dropdown options
@app.callback(
    [
        Output('glreport_genrefilter', 'options'),
        Output('glreport_languagefilter', 'options'),
    ],
    [
        Input('url', 'pathname'),
    ]
)
def glreport_populatefilters(pathname):
    if pathname == '/reports/genre_language_report':
        genre_sql = """
            SELECT genre_name AS label, genre_id AS value
            FROM genres
            WHERE genre_delete_ind = False
            ORDER BY genre_name
        """
        language_sql = """
            SELECT language_name AS label, language_id AS value
            FROM languages
            WHERE language_delete_ind = False
            ORDER BY language_name
        """
        cols = ['label', 'value']
        genres = db.getDataFromDB(genre_sql, [], cols).to_dict('records')
        languages = db.getDataFromDB(language_sql, [], cols).to_dict('records')
        return [genres, languages]
    else:
        raise PreventUpdate


# Build the table
@app.callback(
    Output('glreport_table', 'children'),
    [
        Input('url', 'pathname'),
        Input('glreport_genrefilter', 'value'),
        Input('glreport_languagefilter', 'value'),
    ]
)
def glreport_loadtable(pathname, genre_filter, language_filter):
    if pathname == '/reports/genre_language_report':
        sql = """
            SELECT g.genre_name,
                   COALESCE(l.language_name, 'Unspecified'),
                   COUNT(m.movie_id)
            FROM movies m
                INNER JOIN genres g ON m.genre_id = g.genre_id
                LEFT JOIN languages l ON m.language_id = l.language_id
            WHERE NOT m.movie_delete_ind
        """
        values = []

        if genre_filter:
            sql += " AND g.genre_id IN %s"
            values += [tuple(genre_filter)]

        if language_filter:
            sql += " AND l.language_id IN %s"
            values += [tuple(language_filter)]

        sql += """
            GROUP BY g.genre_name, l.language_name
            ORDER BY g.genre_name, l.language_name
        """

        cols = ['Genre', 'Language', 'Number of Movies']
        df = db.getDataFromDB(sql, values, cols)

        if df.empty:
            return html.P('No movies found.')

        return dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True, size='sm'
        )
    else:
        raise PreventUpdate