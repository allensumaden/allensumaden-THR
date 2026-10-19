import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB

layout = html.Div(
    [
        html.H2('Movies'), # Page Header
        html.Hr(),
        dbc.Card( # Card Container
            [
                dbc.CardHeader( # Define Card Header
                    [
                        html.H3('Manage Records')
                    ]
                ),
                dbc.CardBody( # Define Card Contents
                    [
                        html.Div( # Add Movie Btn
                            [
                                # Add movie button will work like a 
                                # hyperlink that leads to another page
                                dbc.Button(
                                    "Add Movie",
                                    href='/movies/movie_management_profile?mode=add'
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div( # Create section to show list of movies
                            [
                                html.H4('Find Movies'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Title", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='movie_titlefilter',
                                                        placeholder='Movie Title'
                                                    ),
                                                    width=5
                                                )
                                            ],
                                        )
                                    )
                                ),
                                html.Div(
                                    dbc.Checklist(
                                        options=[
                                            {"label": "Show deleted records", "value": "show_deleted"}
                                        ],
                                        value=[],
                                        id="movie_showdeleted",
                                        switch=True,
                                    ),
                                    className='mt-2'
                                ),
                                html.Div(
                                    "Table with movies will go here.",
                                    id='movie_movielist'
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)


@app.callback(
    [
        Output('movie_movielist', 'children'),
    ],
    [
        Input('url', 'pathname'),
        Input('movie_titlefilter', 'value'),
        Input('movie_showdeleted', 'value'),
    ],
)
def updateRecordsTable(pathname, titlefilter, show_deleted):

    if pathname == '/movies/movie_management':
        pass
    else:
        raise PreventUpdate

    sql = """ SELECT m.movie_name, g.genre_name,
        to_char(m.movie_release_date, 'DD Mon YYYY'),
        DATE_PART('year', AGE(CURRENT_DATE, m.movie_release_date))::int,
        co.country_name,
        lang.language_name,
        NULLIF(CONCAT_WS(' ', a.actor_fname, a.actor_lname), ''),
        m.movie_id,
        m.movie_delete_ind
    FROM movies m
        INNER JOIN genres g ON m.genre_id = g.genre_id
        LEFT JOIN countries co ON m.country_id = co.country_id
        LEFT JOIN languages lang ON m.language_id = lang.language_id
        LEFT JOIN actors a ON m.actor_id = a.actor_id
    WHERE 1=1
    """
    val = []

    if "show_deleted" not in show_deleted:
        sql += """ AND NOT m.movie_delete_ind"""

    if titlefilter:
        sql += """ AND m.movie_name ilike %s"""
        val += [f'%{titlefilter}%']

    col = ["Movie Title", "Genre", "Release Date", "Age (years)", "Country",
           "Language", "Actor", 'id', 'Deleted']

    df = getDataFromDB(sql, val, col)

    df[['Country', 'Language', 'Actor']] = df[['Country', 'Language', 'Actor']].fillna('-')
    df['Age (years)'] = df['Age (years)'].astype('Int64').astype(str).replace('<NA>', '-')

    df = df.sort_values(by="Deleted", ascending=True).reset_index(drop=True)

    df['Action'] = [
        html.Div(
            dbc.Button("Edit", color='warning', size='sm',
                       href=f"/movies/movie_management_profile?mode=edit&id={row['id']}"),
            className='text-center'
        ) for idx, row in df.iterrows()
    ]

    df['Status'] = [
        dbc.Badge("Deleted", color="danger") if row['Deleted']
        else dbc.Badge("Active", color="secondary")
        for idx, row in df.iterrows()
    ]

    display_cols = ['Movie Title', 'Genre', 'Release Date', 'Age (years)', 'Country',
                    'Language', 'Actor', 'Status', 'Action']

    header = html.Thead(
        html.Tr([html.Th(col) for col in display_cols])
    )

    rows = []
    for idx, row in df.iterrows():
        row_style = {"backgroundColor": "#f5f5f5", "color": "#888"} if row['Deleted'] else {}
        rows.append(
            html.Tr(
                [html.Td(row[col]) for col in display_cols],
                style=row_style
            )
        )
    body = html.Tbody(rows)

    movie_table = dbc.Table(
        [body] if False else [header, body],
        striped=True, bordered=True, hover=True, size='sm'
    )

    return [movie_table]