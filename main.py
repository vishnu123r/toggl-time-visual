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

start_date ='2021-10-01'
end_date = '2021-10-08'
timezone = '+10:00'
client = 'Survival'

d = TogglData(os.getenv('toggl_api_key'), timezone, os.getenv('postgres_db'),os.getenv('postgres_pass'))
df = d.sum_time_by_client(client, start_date = start_date, end_date = end_date, ma = True)

print(df)
