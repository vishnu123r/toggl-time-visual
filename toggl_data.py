#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from toggl_api import TogglAPI
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from postgre_api import PostgresAPI

import os
from dotenv import load_dotenv

load_dotenv()

class TogglData(object):

    start_date = (datetime.now() - relativedelta(years=1)).isoformat()[0:10]
    end_date = datetime.now().isoformat()[0:10]

    def __init__(self, api_token, timezone, pg_db, pg_pass, pg_host = 'localhost', pg_port = 5432,  pg_user = 'postgres',  pg_table = 'time_entries'):
        self.timezone = timezone
        self.api_token = api_token

        toggl_api = TogglAPI(api_token, timezone)
        self.project_dict = toggl_api._get_project_dict()
        self.project_list = []
        self.client_list = []
        for key, value in self.project_dict.items():
            self.project_list.append(value[0])
            self.client_list.append(value[1])
        self.client_list = list(set(self.client_list))
    
        self.pg_db = pg_db
        self.pg_pass = pg_pass
        self.pg_host = pg_host
        self.pg_port = pg_port
        self.pg_user = pg_user
        self.pg_table = pg_table
        


    def _convert_timezone(self, df):
        """
        Converts the time according to the current time zone. Currently not used as the API returns the values in the correct time zone. 
        There is an issue with the algo. It does not change the date appropriately if month end (31st -> 32nd).
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
        """
        Converts dataframe to a time series
        """

        idx = pd.date_range(start_date, end_date)
        df.index = pd.DatetimeIndex(df.index)
        df = df.reindex(idx, fill_value=0)

        return df

    def _deduct_window_date(self, start_date, window):
        start_date_obj = datetime.strptime(start_date,"%Y-%m-%d")   
        start_date = (start_date_obj- relativedelta(days=window-1)).isoformat()[:10]
        
        return start_date

    def sum_time_by_client(self, client_name, start_date = (datetime.now() - relativedelta(years=1)).isoformat()[0:10], end_date = datetime.now().isoformat()[0:10]):
        '''
        Sums all the client activity for the day and adds zero values when there is no activity 
        '''

        if client_name not in self.client_list:
            print('Please enter a client from this list - ', self.client_list)
            sys.exit()

        print("Getting data for client - ", client_name)

        postgres = PostgresAPI(self.pg_db, self.pg_pass, host = self.pg_host, port = self.pg_port,  user = self.pg_user,  table = self.pg_table)
        df = postgres.get_data(start_date, end_date)
        df = round(df.groupby(['client_name','date'])['duration'].sum()/3600/1000,2)
        df = df.reset_index().reindex(columns = ['date', 'client_name', 'duration'] )
        df = df.set_index('date')
        df = df[df['client_name'] == client_name]
        df = self._convert_idx_datetime(df, start_date, end_date)
        df['client_name'] = client_name

        return df


    def sum_time_all_clients(self, start_date = start_date, end_date = end_date):
        '''
        Returns all the client activity for the alotted date interval.
        '''
        df_list = []
        for client in self.client_list:
            df = self.sum_time_by_client(client, start_date, end_date)
            df_list.append(df)
            
        df = pd.concat(df_list)

        return df

    def sum_time_by_client_ma(self, client_name, start_date = (datetime.now() - relativedelta(years=1)).isoformat()[0:10], end_date = datetime.now().isoformat()[0:10], window = 7):

        """"
        Sums all the client activity for each day and adds moving average column
        """

        start_date = self._deduct_window_date(start_date, window)
        df = self.sum_time_by_client(client_name, start_date, end_date)
        df['ma'] = round(df.rolling(window=window).mean(),2)
        df.dropna(inplace=True)

        return df

    def sum_time_all_clients_ma(self, start_date = start_date, end_date = end_date, window = 7):
        '''
        Returns all the client activity for the alotted time and the respective moving averages.
        '''

        df_list = []
        for client in self.client_list:
            df = self.sum_time_by_client_ma(client, start_date, end_date, window)
            df_list.append(df)
            
        df = pd.concat(df_list)

        return df

    def get_all_values_dash(self, window = 7):

        '''Outputs the the historical data and mean for '''

        start_date = '2021-02-26'
        yesterday = (datetime.now()-relativedelta(days=1)).isoformat()[0:10]
        df = self.sum_time_all_clients_ma(start_date = start_date, end_date = yesterday, window = window)
        df = df.reset_index()
        df.columns = ['date', 'client_name', 'duration', 'ma']
        df_mean = round(df.groupby('client_name')['duration'].mean(),2)

        return df, df_mean

if __name__ == '__main__':
    start_date ='2021-05-01'
    end_date = '2021-10-14'
    timezone = '+10:00'
    client = 'Survival'

    d = TogglData(os.getenv('toggl_api_key'), timezone, os.getenv('postgres_db'),os.getenv('postgres_pass'))

    df, df_mean = d.get_all_values_dash()
    print(df_mean)