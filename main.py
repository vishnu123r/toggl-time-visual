import psycopg2
from toggl_api import TogglAPI
from dotenv import load_dotenv
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
from toggl_data import TogglData
from requests.auth import HTTPBasicAuth
import psycopg2

from sqlalchemy import create_engine
import io

import pandas as pd


load_dotenv()

start_date ='2021-08-01'
end_date = '2022-01-01'
timezone = '+10:00'
client = 'Survival'

# d = TogglData(os.getenv('toggl_api_key'), timezone, os.getenv('postgres_db'),os.getenv('postgres_pass'))
# df = d.sum_time_by_client_ma(client, start_date = start_date, end_date = end_date)

# print(df)

start_greater_than_end  = datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d")
if start_greater_than_end:
    raise ValueError("End date precedes the start date")

print(type(datetime.now()))

date_today_or_future = datetime.now() <= datetime.strptime(start_date, "%Y-%m-%d") or datetime.now() <= datetime.strptime(end_date, "%Y-%m-%d")
if date_today_or_future:
    raise ValueError("Either the start date or the end date is today or in the the future. Enter a date till yesterday.")