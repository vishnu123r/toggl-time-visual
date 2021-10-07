#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from toggl_api import TogglAPI
import toggl_api

class Toggl_Data(object):

    def __init__(self, api_token, timezone, start_date, end_date):
        self.timezone = timezone
        self.api_token = api_token
        self.start_date = start_date
        self.end_date = end_date

        toggl_api = TogglAPI(api_token, timezone)
        self.json_file = toggl_api.get_time_entries(self.start_date, self.end_date, self.timezone)
        self.project_dict = toggl_api._get_project_dict()

    def _convert_timezone(self, df):
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

    def convert_json_df(self, json_file):
        '''
        This methods converts the resultant json file from API to a df which can be used for analysis
        '''
        time_list = []

        for json in json_file:
            if int(json['duration']) == 0:
                continue
            start = json['start']
            stop = json['stop']
            duration = json['duration']
            try: 
                description = json['description']
            except:
                description = 'no_description'
            try:
                project = self.project_dict[json['pid']]
            except:
                project = ("no_project", "no_client")
            time_list.append((start, duration, description, project[0], project[1])) 

        df = pd.DataFrame.from_records(time_list, columns =['Start_date', 'Duration', 'Description', 'Project_name', 'Client_name'])
        df = self._convert_timezone(df)

        return df

    def sum_time_by_client(self, client_name):

        df = self.convert_json_df(self.json_file)
        df = round(df.groupby(['Client_name','Date'])['Duration'].sum()/3600,2)
        df = df.reset_index().reindex(columns = ['Date', 'Client_name', 'Duration'] )
        df = df.set_index('Date')
        df = df[df['Client_name'] == client_name]
        #df = self._convert_idx_datetime(df, self.start_date, self.end_date)

        return df

if __name__ == '__main__':
    pass