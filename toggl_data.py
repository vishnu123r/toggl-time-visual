#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from toggl_api import TogglAPI
import toggl_api
import sys
import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from helpers import convert_json_df
from postgre_api import PostgresAPI


class TogglData(object):

    def __init__(self, api_token, timezone, postgres_db, postgres_pass):
        self.timezone = timezone
        self.api_token = api_token
        self.postgres_db = postgres_db
        self.postgres_pass = postgres_pass

        toggl_api = TogglAPI(api_token, timezone)
        self.project_dict = toggl_api._get_project_dict()
        self.project_list = []
        self.client_list = []
        for key, value in self.project_dict.items():
            self.project_list.append(value[0])
            self.client_list.append(value[1])
        self.client_list = list(set(self.client_list))

        self.postgres = PostgresAPI(postgres_db, postgres_pass, host = 'localhost', port = 5432,  user = 'postgres')

    def _convert_timezone(self, df):
        """
        Converts the time accorsing to the current time zone. Currently not used as the API returns the values in the correct time zone. 
        There is an issue with the algo. It returns does not change the date appropriately if month end.
        """

        df['Date'] = df['Start_date'].str[8:10].astype(int)
        df['year'] = df['Start_date'].str[0:8]
        df['time'] = df['Start_date'].str[11:13].astype(int) + int(self.timezone[1:3])
        df['que'] = np.where((df['time'] >= 24) , df['Date'] + 1, df['Date'])
        df['Date'] = df['year'] + df['que'].astype(str).str.zfill(2)
        df.drop(['year', 'time', 'que', 'Start_date'], axis = 1, inplace=True)
        df = df.reindex(columns = ['Date', 'Description','Project_name', 'Client_name', 'Duration'])

        return df
    
    def _convert_idx_datetime(self, df, start_date, end_date):
        idx = pd.date_range(start_date, end_date)
        df.index = pd.DatetimeIndex(df.index)
        df = df.reindex(idx, fill_value=0)

        return df

    def sum_time_by_client(self, client_name, start_date = (datetime.now() - relativedelta(years=1)).isoformat()[0:10], end_date = datetime.now().isoformat()[0:10], ma = True):
        '''
        Sums all the client activity for the day and adds zero values when there is no activity 
        '''

        if client_name not in self.client_list:
            print('Please enter a client from this list - ', self.client_list)
            sys.exit()

        df = self.postgres.get_data(start_date, end_date)
        df = round(df.groupby(['client_name','date'])['duration'].sum()/3600/1000,2)
        df = df.reset_index().reindex(columns = ['date', 'client_name', 'duration'] )
        df = df.set_index('date')
        df = df[df['client_name'] == client_name]
        df = self._convert_idx_datetime(df, start_date, end_date)
        df['client_name'] = client_name

        if ma is True:
            df['ma'] = round(df.rolling(window=7).mean(),2)
            df.dropna(inplace=True)

        return df

    def sum_time_all_clients(self, start_date = (datetime.now() - relativedelta(years=1)).isoformat()[0:10], end_date = datetime.now().isoformat()[0:10], ma = True):
        '''
        Combines all the dataframes from sum_time_by_clients() into a single dataframe.
        '''
        df_list = []
        for client in self.client_list:
            df = self.sum_time_by_client(client, start_date, end_date, ma)
            df_list.append(df)
            
        df = pd.concat(df_list)

        return df

if __name__ == '__main__':
    pass