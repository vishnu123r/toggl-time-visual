#!/usr/bin/python
# -*- coding: utf-8 -*-
# @author Mosab Ibrahim <mosab.a.ibrahim@gmail.com>

import requests
from urllib.parse import urlencode
from requests.auth import HTTPBasicAuth
import sys
import pandas as pd
import numpy as np

class TogglAPI(object):
    """A wrapper for Toggl Api"""

    def __init__(self, api_token, timezone):
        if len(timezone) != 6:
            sys.exit('Incorrect Format - Use the following format +tt:tt')
        try:
            int(timezone[1:3])
            int(timezone[4:])
        except ValueError:
            sys.exit('Incorrect Format - Use the following format +tt:tt')

        self.api_token = api_token
        self.timezone = timezone

    def _make_url(self, section='time_entries', params={}):
        """Constructs and returns an api url to call with the section of the API to be called
        and parameters defined by key/pair values in the paramas dict.
        Default section is "time_entries" which evaluates to "time_entries.json"
        >>> t = TogglAPI('_SECRET_TOGGLE_API_TOKEN_')
        >>> t._make_url(section='time_entries', params = {})
        'https://www.toggl.com/api/v8/time_entries'
        >>> t = TogglAPI('_SECRET_TOGGLE_API_TOKEN_')
        >>> t._make_url(section='time_entries', 
                        params = {'start_date': '2010-02-05T15:42:46+02:00', 'end_date': '2010-02-12T15:42:46+02:00'})
        'https://www.toggl.com/api/v8/time_entries?start_date=2010-02-05T15%3A42%3A46%2B02%3A00%2B02%3A00&end_date=2010-02-12T15%3A42%3A46%2B02%3A00%2B02%3A00'
        """

        if section == "projects":
            url = 'https://api.track.toggl.com/api/v8/workspaces/5138622/{}'.format(section)
        else:
            url = 'https://api.track.toggl.com/api/v8/{}'.format(section)
       
        if len(params) > 0:
            url = url + '?{}'.format(urlencode(params))
        return url

    def _query(self, url, method):
        """Performs the actual call to Toggl API"""
        url = url
        headers = {'content-type': 'application/json'}
        if method == 'GET':
            return requests.get(url, headers=headers, auth=HTTPBasicAuth(self.api_token, 'api_token'))
        elif method == 'POST':
            return requests.post(url, headers=headers, auth=HTTPBasicAuth(self.api_token, 'api_token'))
        else:
            raise ValueError('Undefined HTTP method "{}"'.format(method))

    def _format_date(self, date):
        ### This function returns the time period of interest based on the current date
        time_zone_string = "T00:00:00{}".format(self.timezone)
        return date + time_zone_string

    def _check_date_format(self, date):
        try:
            int(date[:4])
            int(date[5:7])
            int(date[8:10])
        except ValueError:
            print("Input format wrong - Use the following format yyyy-mm-dd")
            sys.exit()

    def _get_project_dict(self):
        ### Returns all the projects and clients in the following dict format - Project_id: (Project_name, Client_name)
        url = self._make_url(section='clients')
        r = self._query(url=url, method='GET')
        try:
            client_json = r.json()
            client_dict = {}
            for client in client_json:
                client_dict[client['id']] =  client['name']        
        except:
            print("Something wrong with getting the client dictionary - ", r)
        
        url = self._make_url(section='projects')
        r = self._query(url=url, method='GET')
        try:
            project_json = r.json()
            project_dict = {}
            for project in project_json:
                project_dict[project['id']] = (project['name'], client_dict[project['cid']])
            return project_dict
        except Exception as e:
            print("Something wrong with getting the project tuple - ", e)

    def _convert_timezone(self, df):
        df['Date'] = df['Start_date'].str[8:10].astype(int)
        df['year'] = df['Start_date'].str[0:8]
        df['time'] = df['Start_date'].str[11:13].astype(int) + int(self.timezone[1:3])

        df['que'] = np.where((df['time'] >= 24) , df['Date'] + 1, df['Date'])
        df['Date'] = df['year'] + df['que'].astype(str)
        df.drop(['year', 'time', 'que', 'Start_date'], axis = 1, inplace=True)
        df = df.reindex(columns = ['Date', 'Description','Project_name', 'Client_name', 'Duration'])

        return df

    # Time Entry functions
    def get_time_entries(self, start_date='', end_date='', timezone=''):
        """Get Time Entries JSON object from Toggl within a given start_date and an end_date with a given timezone"""
        
        self._check_date_format(start_date)
        self._check_date_format(end_date)


        url = self._make_url(section='time_entries',
                             params={'start_date': self._format_date(start_date), 'end_date': self._format_date(end_date)})
        r = self._query(url=url, method='GET')

        return self.convert_json_df(r.json())

    def convert_json_df(self, json_file):
        '''
        This methods converts the resultant json file from API to a df which can be used for analysis
        '''
        time_list = []
        project_dict = self._get_project_dict()
        for json in json_file:
            start = json['start']
            stop = json['stop']
            duration = json['duration']
            try: 
                description = json['description']
            except:
                description = 'no_description'
            try:
                project = project_dict[json['pid']]
            except:
                project = ("no_project", "no_client")
            time_list.append((start, duration, description, project[0], project[1])) 

        df = pd.DataFrame.from_records(time_list, columns =['Start_date', 'Duration', 'Description', 'Project_name', 'Client_name'])
        df = self._convert_timezone(df)

        return df

    def get_hours_tracked(self, start_date, end_date):
        """Count the total tracked hours within a given start_date and an end_date
        excluding any RUNNING real time tracked time entries
        """

        time_entries = self.get_time_entries(start_date=start_date, end_date=end_date)
        if time_entries is None:
            return 0

        total_seconds_tracked = sum(max(entry['duration'], 0) for entry in time_entries)

        return (total_seconds_tracked / 60.0) / 60.0


if __name__ == '__main__':
    t = TogglAPI('655a0f52169ca76917ba80cb84cf9840', '+10:00')
    start_month = '2021-06-01'
    end_month = '2021-07-22'
    # tup = t._get_dict()
    # print(tup)
    f = t.get_time_entries(start_date=start_month, end_date = end_month)
    print(f.head())


