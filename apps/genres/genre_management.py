import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB

layout = html.Div(
    [
        html.H2('Genres'),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.H3('Manage Records')
                    ]
                ),
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                dbc.Button(
                                    "Add Genre",
                                    href='/genres/genre_management_profile?mode=add'
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find Genres'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Name", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='genre_namefilter',
                                                        placeholder='Genre Name'
                                                    ),
                                                    width=5
                                                )
                                            ],
                                        )
                                    )
                                ),
                                html.Div(
                                    "Table with genres will go here.",
                                    id='genre_genrelist'
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
        Output('genre_genrelist', 'children'),
    ],
    [
        Input('url', 'pathname'),
        Input('genre_namefilter', 'value'),
    ],
)
def updateGenreTable(pathname, namefilter):

    if pathname == '/genres/genre_management':
        pass
    else:
        raise PreventUpdate

    sql = """ SELECT genre_name, genre_id
    FROM genres
    WHERE NOT genre_delete_ind
    """
    val = []

    if namefilter:
        sql += """ AND genre_name ilike %s"""
        val += [f'%{namefilter}%']

    col = ["Genre Name", 'id']

    df = getDataFromDB(sql, val, col)

    df['Action'] = [
        html.Div(
            dbc.Button("Edit", color='warning', size='sm',
                        href = f"/genres/genre_management_profile?mode=edit&id={row['id']}"),
            className='text-center'
        ) for idx, row in df.iterrows()
    ]

    df = df[['Genre Name', 'Action']]

    genre_table = dbc.Table.from_dataframe(df, striped=True, bordered=True,
                                        hover=True, size='sm')

    return [genre_table]