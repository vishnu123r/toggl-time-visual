import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import dash_daq as daq
from toggl_data import TogglData
import os
from dotenv import load_dotenv


load_dotenv()

from datetime import datetime
from dateutil.relativedelta import relativedelta

app = Dash(
    __name__,
     external_stylesheets=[dbc.themes.CYBORG]
)
server = app.server 

#Getting data from postgres and toggl
d = TogglData(os.getenv('toggl_api_key'),os.getenv('time_zone'), os.getenv('postgres_db'),os.getenv('postgres_pass'))
df,df_mean = d.get_all_values_dash(window = 14)

### Dataframe for off_line and def_line
df_offense = df[(df['client_name'] == 'PhD')| (df['client_name'] == 'Financial')]
df_offense = df_offense.groupby(['date'])['ma'].sum()
df_defence = df[(df['client_name'] == 'Sleep')| (df['client_name'] == 'No Value')| (df['client_name'] == 'Survival')]
df_defence = df_defence.groupby(['date'])['ma'].sum()

### Getting historical means
phd_history_mean = df_mean.loc['PhD']
financial_history_mean = df_mean.loc['Financial']
sleep_history_mean = df_mean.loc['Sleep']
nov_history_mean = df_mean.loc['No Value']
survival_history_mean = df_mean.loc['Survival']

### Getting weekly mean
week_ago = (datetime.now() - relativedelta(days = 8)).isoformat()[0:10].strip()
yesterday = (datetime.now() - relativedelta(days = 1)).isoformat()[0:10].strip()
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

df_weekly_mean = df.loc[(df['date'] <= yesterday) & (df['date'] >= week_ago)]
df_weekly_mean = round(df_weekly_mean.groupby('client_name')['duration'].mean(),2)

def assign_weekly_mean(df, client):
    """
    Assigns 0 if the client is not present in the data frame. Else assigns the value
    """
    if client not in df.index.tolist():
        return 0
    else:
        return df.loc[client]

phd_weekly_mean = assign_weekly_mean(df_weekly_mean, 'PhD')
financial_weekly_mean = assign_weekly_mean(df_weekly_mean, 'Financial')
sleep_weekly_mean = assign_weekly_mean(df_weekly_mean, 'Sleep')
nov_weekly_mean = assign_weekly_mean(df_weekly_mean, 'No Value')
survival_weekly_mean = assign_weekly_mean(df_weekly_mean, 'Survival')
df =df.set_index('date')


fig_off = px.line(df_offense, y="ma",
                  title='Time spent in {}'.format('Offense'), template="plotly_dark")
fig_off.update(layout=dict(title=dict(x=0.5)))

fig_phd = px.line(df[df["client_name"] == 'PhD'], y="ma",
                  title='Time spent for {}'.format('PhD'), template="plotly_dark")
fig_phd.update(layout=dict(title=dict(x=0.5)))

fig_fin = px.line(df[df["client_name"] == 'Financial'], y="ma",
                  title='Time spent for {}'.format('Financial'), template="plotly_dark")
fig_fin.update(layout=dict(title=dict(x=0.5)))

fig_def = px.line(df_defence, y="ma",
                  title='Time spent in {}'.format('Defence'), template="plotly_dark")
fig_def.update(layout=dict(title=dict(x=0.5)))

fig_sleep = px.line(df[df["client_name"] == 'Sleep'], y="ma",
                    title='Time spent for {}'.format('Sleep'), template="plotly_dark")
fig_sleep.update(layout=dict(title=dict(x=0.5)))                

fig_novalue = px.line(df[df["client_name"] == 'No Value'], y="ma",
                      title='Time spent for {}'.format('No Value'), template="plotly_dark")
fig_novalue.update(layout=dict(title=dict(x=0.5)))            

fig_survival = px.line(df[df["client_name"] == 'Survival'], y="ma",
                       title='Time spent for {}'.format('Survival'), template="plotly_dark")
fig_survival.update(layout=dict(title=dict(x=0.5)))                       


def show_ma_phd():
    if phd_history_mean > phd_weekly_mean:
        color_code="#FF5E5E"
    else:
        color_code="#92e0d3"
    return [daq.LEDDisplay(
        id= 'weekly_ma_phd',
        label = 'Weekly Avg',
        value= str(phd_weekly_mean),
        color=color_code,
        backgroundColor="#1e2130",
                        size=25,
        style={"margin-left": "30px"}
    ),
        daq.LEDDisplay(
        id= "history_ma_phd",
        label = 'Historical Avg',
        value= str(phd_history_mean),
        color="#92e0d3",
        backgroundColor="#1e2130",
                        size=25,
        style={"margin-left": "15px"}
   ), 
    ]

def show_ma_fin():
    if financial_history_mean > financial_weekly_mean:
        color_code="#FF5E5E"
    else:
        color_code="#92e0d3"
    return [daq.LEDDisplay(
        id= 'weekly_ma_financial',
        label = 'Weekly Avg',
        value= str(financial_weekly_mean),
        color=color_code,
        backgroundColor="#1e2130",
                        size=25,
        style={"margin-left": "30px"}
    ),
        daq.LEDDisplay(
        id= "history_ma_financial",
        label = 'Historical Avg',
        value= str(financial_history_mean),
        color="#92e0d3",
        backgroundColor="#1e2130",
                        size=25,
        style={"margin-left": "15px"}
   ),
    ]

def show_ma_sleep():
    if sleep_history_mean < sleep_weekly_mean:
        color_code="#FF5E5E"
    else:
        color_code="#92e0d3"
    return [daq.LEDDisplay(
        id= 'weekly_ma_sleep',
        label = 'Weekly Avg',
        value= str(sleep_weekly_mean),
        color=color_code,
        backgroundColor="#1e2130",
                        size=25,
        style={"margin-left": "30px"}
    ),
        daq.LEDDisplay(
        id= "history_ma_sleep",
        label = 'Historical Avg',
        value= str(sleep_history_mean),
        color="#92e0d3",
        backgroundColor="#1e2130",
                        size=25,
        style={"margin-left": "15px"}
   ),
    ]

def show_ma_nov():
    if nov_history_mean < nov_weekly_mean:
        color_code="#FF5E5E"
    else:
        color_code="#92e0d3"
    return [daq.LEDDisplay(
        id= 'weekly_ma_nov',
        label = 'Weekly Avg',
        value= str(nov_weekly_mean),
        color=color_code,
        backgroundColor="#1e2130",
                        size=25,
        style={"margin-left": "30px"}
    ),
        daq.LEDDisplay(
        id= "history_ma_nov",
        label = 'Historical Avg',
        value= str(nov_history_mean),
        color="#92e0d3",
        backgroundColor="#1e2130",
                        size=25,
        style={"margin-left": "15px"}
   ),
    ]

def show_ma_survival():
    if survival_history_mean < survival_weekly_mean:
        color_code="#FF5E5E"
    else:
        color_code="#92e0d3"

    return [daq.LEDDisplay(
        id= 'weekly_ma_survival',
        label = 'Weekly Avg',
        value= str(survival_weekly_mean),
        color = color_code,
        backgroundColor="#1e2130",
                        size=25,
        style={"margin-left": "30px"}
    ),
        daq.LEDDisplay(
        id= "history_ma_survival",
        label = 'Historical Avg',
        value= str(survival_history_mean),
        color="#92e0d3",
        backgroundColor="#1e2130",
                        size=25,
        style={"margin-left": "15px"}
   ),
    ]

def offensive_ma():
    return [
        dbc.Col(html.Div([
        dbc.Row((html.H4(children = ['PhD'], style={"margin-left": "85px"}))), 
        dbc.Row(show_ma_phd()),
        dbc.Row(html.Br()),
    ],className = 'border border-dark')
    ),

        dbc.Col(html.Div([
        dbc.Row((html.H4(children = ['Financial'], style={"margin-left": "60px"}))), 
        dbc.Row(show_ma_fin()),
        dbc.Row(html.Br()),
    ],className = 'border border-dark')
    ),

        ]


def defensive_ma():
    return [dbc.Col(html.Div([
        dbc.Row((html.H4(children = ['Sleep'], style={"margin-left": "80px"}))), 
        dbc.Row(show_ma_sleep()),
        dbc.Row(html.Br()),
    ],className = 'border border-dark')
    ),

    dbc.Col(html.Div([
        dbc.Row((html.H4(children = ['No Value'], style={"margin-left": "60px"}))), 
        dbc.Row(show_ma_nov()),
        dbc.Row(html.Br()),
    ],className = 'border border-dark')
    ),

    dbc.Col(html.Div([
        dbc.Row((html.H4(children = ['Survival'], style={"margin-left": "60px"}))), 
        dbc.Row(show_ma_survival()),
        dbc.Row(html.Br()),
    ],className = 'border border-dark')
    ),]


def show_offense_graphs():
    return [

                dbc.Col(),
                dbc.Col(dcc.Graph(id='phd_line', figure= fig_phd), width = 5.5),
                dbc.Col(dcc.Graph(id='financial_line', figure= fig_fin), width = 5.5),
                dbc.Col(),
            ]

def show_defence_graphs():
    return [    
                dbc.Col(width =0.5),
                dbc.Col(dcc.Graph(id='sleep_line', figure=fig_sleep)),
                dbc.Col(dcc.Graph(id='no_value_line', figure= fig_novalue) ),
                dbc.Col(dcc.Graph(id='survival_line', figure= fig_survival)),
                dbc.Col(width =1),
            ]

def show_ma_headers():
    return [
        html.Div("Weekly Avg", style={"margin-left": "60px"}),
        html.Div("Historical Avg", style={"margin-left": "10px"})
    ]

#===========================================================================================================

app.layout = html.Div([

    html.H3('Time Dashboard', style={'textAlign': 'center'}),

    html.Br(),

    dbc.Row([
        dbc.Col(),

        dbc.Col(
            dbc.Row(offensive_ma()),
            width = 4
        ),

        dbc.Col(
            dbc.Row(defensive_ma()),
            width = 6
        ),

        dbc.Col()

    ]),

    html.Br(),

    dbc.Row([
        
        dbc.Col(),
        dbc.Col(dcc.Graph(id='off_line', figure= fig_off), width = 11),
        dbc.Col(),
        
        
    ]),

    html.Br(),


    dbc.Row(show_offense_graphs()),

    html.Br(),

    dbc.Row([
        
        dbc.Col(),
        dbc.Col(dcc.Graph(id='def_line', figure= fig_def), width = 11),
        dbc.Col(),
        
        
    ]),

    html.Br(),

    dbc.Row(show_defence_graphs()),

    html.Br(),
])

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
