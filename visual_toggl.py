import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import os
from dotenv import load_dotenv
from datetime import datetime
from toggl_data import TogglData

load_dotenv()


app = Dash(__name__, external_stylesheets = [dbc.themes.CYBORG])

start_date ='2021-05-01'
end_date = '2021-10-14'

d = TogglData(os.getenv('toggl_api_key'),os.getenv('time_zone'), os.getenv('postgres_db'),os.getenv('postgres_pass'))
df = d.sum_time_all_clients_ma(start_date, end_date, window = 14)
clients = d.client_list

dropdown_list = []
for client in clients:
    dict = {}
    dict['label'] = client
    dict['value'] = client

    dropdown_list.append(dict)


fig_phd = px.line(df[df["client_name"] == 'PhD'], y="ma", title='Time spent for {}'.format('PhD'), template = "plotly_dark")
fig_fin = px.line(df[df["client_name"] == 'Financial'], y="ma", title='Time spent for {}'.format('Financial'), template = "plotly_dark")
fig_sleep = px.line(df[df["client_name"] == 'Sleep'], y="ma", title='Time spent for {}'.format('Sleep'), template = "plotly_dark")
fig_novalue = px.line(df[df["client_name"] == 'No Value'], y="ma", title='Time spent for {}'.format('No Value'), template = "plotly_dark")
fig_survival = px.line(df[df["client_name"] == 'Survival'], y="ma", title='Time spent for {}'.format('Survival'), template = "plotly_dark")

app.layout = html.Div(
    [
        html.H1("Activity Time Dashboard", style={"textAlign": "center"}),
        
        html.H4("Offense Metrics", style={"textAlign": "center"}),
            
        
        dbc.Row(
            [
                 dbc.Col(dcc.Graph(id='phd_line', figure= fig_phd), width =6),
                 dbc.Col(dcc.Graph(id='financial_line', figure= fig_fin), width =6)
            ]
            ),

        html.Br(),

        html.H4("Defense Metrics", style={"textAlign": "center"}),
        
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='sleep_line', figure=fig_sleep), width = 4),
                dbc.Col(dcc.Graph(id='no_value_line', figure= fig_novalue), width = 4),
                dbc.Col(dcc.Graph(id='survival_line', figure= fig_survival), width = 4),
            ]
        ),
    ]
)

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
# @app.callback(
#     [Output(component_id='phd_line', component_property='figure'),
#     Output(component_id='financial_line', component_property='figure'),
#     Output(component_id='sleep_line', component_property='figure'),
#     Output(component_id='no_value_line', component_property='figure'),
#     Output(component_id='survival_line', component_property='figure'),
#     ]
# )

# def update_graph():

#     dff = df.copy()
#     dff = dff[dff["Client_name"] == 'PhD']

#     # Plotly Express
#     fig_phd = px.line(dff[dff["Client_name"] == 'PhD'], y="MA", title='Time spent for {}'.format('PhD'))
#     fig_fin = px.line(dff[dff["Client_name"] == 'Financial'], y="MA", title='Time spent for {}'.format('Financial'))
#     fig_sleep = px.line(dff[dff["Client_name"] == 'Sleep'], y="MA", title='Time spent for {}'.format('Sleep'))
#     fig_novalue = px.line(dff[dff["Client_name"] == 'No Value'], y="MA", title='Time spent for {}'.format('No Value'))
#     fig_survival = px.line(dff[dff["Client_name"] == 'Survival'], y="MA", title='Time spent for {}'.format('Survival'))

#     return fig_phd, fig_fin, fig_sleep, fig_novalue, fig_survival


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)