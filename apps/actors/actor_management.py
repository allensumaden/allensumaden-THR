import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from dash.exceptions import PreventUpdate

from app import app
from apps.dbconnect import getDataFromDB

layout = html.Div(
    [
        html.H2('Actors'),
        html.Hr(),
        dbc.Card(
            [
                dbc.CardHeader([html.H3('Manage Records')]),
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                dbc.Button(
                                    "Add Actor",
                                    href='/actors/actor_management_profile?mode=add'
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find Actors'),
                                html.Div(
                                    dbc.Form(
                                        dbc.Row(
                                            [
                                                dbc.Label("Search Name", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='actor_namefilter',
                                                        placeholder='Actor Name'
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
                                        id="actor_showdeleted",
                                        switch=True,
                                    ),
                                    className='mt-2'
                                ),
                                html.Div(
                                    "Table with actors will go here.",
                                    id='actor_actorlist'
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
    Output('actor_actorlist', 'children'),
    [
        Input('url', 'pathname'),
        Input('actor_namefilter', 'value'),
        Input('actor_showdeleted', 'value'),
    ],
)
def updateActorTable(pathname, namefilter, show_deleted):

    if pathname != '/actors/actor_management':
        raise PreventUpdate

    sql = """ SELECT actor_fname, actor_lname, actor_id, actor_delete_ind
    FROM actors
    WHERE 1=1
    """
    val = []

    if "show_deleted" not in show_deleted:
        sql += """ AND NOT actor_delete_ind"""

    if namefilter:
        sql += """ AND (actor_fname || ' ' || actor_lname) ILIKE %s"""
        val += [f'%{namefilter}%']

    col = ["First Name", "Last Name", 'id', 'Deleted']

    df = getDataFromDB(sql, val, col)
    df = df.sort_values(by="Deleted", ascending=True).reset_index(drop=True)

    df['Action'] = [
        html.Div(
            dbc.Button("Edit", color='warning', size='sm',
                       href=f"/actors/actor_management_profile?mode=edit&id={row['id']}"),
            className='text-center'
        ) for idx, row in df.iterrows()
    ]

    df['Status'] = [
        dbc.Badge("Deleted", color="danger") if row['Deleted']
        else dbc.Badge("Active", color="secondary")
        for idx, row in df.iterrows()
    ]

    display_cols = ['First Name', 'Last Name', 'Status', 'Action']

    header = html.Thead(html.Tr([html.Th(col) for col in display_cols]))

    rows = []
    for idx, row in df.iterrows():
        row_style = {"backgroundColor": "#f5f5f5", "color": "#888"} if row['Deleted'] else {}
        rows.append(html.Tr([html.Td(row[col]) for col in display_cols], style=row_style))
    body = html.Tbody(rows)

    actor_table = dbc.Table(
        [header, body],
        striped=True, bordered=True, hover=True, size='sm'
    )

    return actor_table