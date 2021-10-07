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
        """

        if section == "projects":
            url = 'https://api.track.toggl.com/api/v8/workspaces/5138622/{}'.format(section)
        elif section == "details":
            url = 'https://api.track.toggl.com/reports/api/v2/{}'.format(section)
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

    # Time Entry functions
    def get_time_entries(self, start_date='', end_date=''):
        """Get Time Entries JSON object from Toggl within a given start_date and an end_date with a given timezone"""
        
        self._check_date_format(start_date)
        self._check_date_format(end_date)


        url = self._make_url(section='details',
                             params={'start_date': self._format_date(start_date), 'end_date': self._format_date(end_date), 'user_agent':'vishnu123r@gmail.com',"workspace_id":'5138622'})
        r = self._query(url=url, method='GET')

        return r.json()

if __name__ == '__main__':
    api_token = '655a0f52169ca76917ba80cb84cf9840'
    start_date ='2020-09-23'
    end_date = '2021-10-06'
    t = TogglAPI(api_token, '+10:00')
    f = t.get_time_entries( start_date, end_date)
    print(f.keys())
    print(f['data'])


