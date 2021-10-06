#!/usr/bin/python
# -*- coding: utf-8 -*-
# @author Mosab Ibrahim <mosab.a.ibrahim@gmail.com>

import requests
from urllib.parse import urlencode
from requests.auth import HTTPBasicAuth
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
import sys

class TogglAPI(object):
    """A wrapper for Toggl Api"""

    def __init__(self, api_token, timezone):
        if len(timezone) != 6:
            sys.exit('Incorrect Format - Use the following format +tt:t0')
        try:
            int(timezone[1:3])
            int(timezone[4:])
        except ValueError:
            sys.exit('Incorrect Format - Use the following format +tt:t0')

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

        url = 'https://www.toggl.com/api/v8/{}'.format(section)
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

    # Time Entry functions
    def get_time_entries(self, start_date='', end_date='', timezone=''):
        """Get Time Entries JSON object from Toggl within a given start_date and an end_date with a given timezone"""

        try:
            int(start_date[:4])
            int(start_date[5:7])
            int(start_date[8:10])
            print("Valid Input")
        except ValueError:
            print("Input format wrong - Use the following format yyyy-mm-dd")
            sys.exit()

        url = self._make_url(section='time_entries',
                             params={'start_date': self._format_date(start_date), 'end_date': self._format_date(end_date)})
        r = self._query(url=url, method='GET')
        return r.json()

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
    f  =t.get_time_entries(start_date=start_month, end_date = end_month)
    print(f[1])