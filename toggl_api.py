#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from urllib.parse import urlencode
from requests.auth import HTTPBasicAuth
import sys
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

class TogglAPI(object):
    """A wrapper for Toggl Api"""

    def __init__(self, api_token, timezone = '+10:00'):
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

    
    def _get_page_number(self, response):

        """
        Gets the number of pages from the json response
        """

        total_count = response.json()['total_count']
        pages = int(total_count/50) + 1
        return pages

    def _extract_data(self, start_date, end_date, response):

        """
        Makes repeated api calls as per the number of pages and gets the required data as a list
        """

        data_list = []
        data_list.append(response.json()['data'])
        pages = self._get_page_number(response)
        print('Retrieving page - 1') 

        for page in range(2, pages+1):
            print('Retrieving page - {}'.format(page))
            url = self._make_url(section='details',
                                params={'since': self._format_date(start_date), 
                                'until': self._format_date(end_date), 'user_agent':'vishnu123r@gmail.com',"workspace_id":'5138622',
                                'page': str(page)})
                
            response = self._query(url=url, method='GET')

            data_list.append(response.json()['data'])

        data_list = [item for sublist in data_list for item in sublist]
        
        return data_list

    def get_time_entries(self, start_date='', end_date=''):
        """Get Time Entries JSON object from Toggl within a given start_date and an end_date with a given timezone"""
        
        self._check_date_format(start_date)
        self._check_date_format(end_date)

        url = self._make_url(section='details',
                             params={'since': self._format_date(start_date), 'until': self._format_date(end_date), 
                             'user_agent':'vishnu123r@gmail.com',"workspace_id":'5138622'})
        
        response = self._query(url=url, method='GET')
        if response.ok:
            data_list = self._extract_data(start_date, end_date, response)

            return data_list

        else:
            sys.exit(response.content)


if __name__ == '__main__':
    api_token = os.getenv('toggl_api_key')
    since ='2021-01-23'
    until = '2021-08-06'
    t = TogglAPI(api_token, '+10:00')
    f = t.get_time_entries( since, until)
    #print([fi['start'] for fi in f])
    print(f[1])


