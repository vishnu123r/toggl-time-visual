from toggl_api import TogglAPI
from dotenv import load_dotenv
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
from toggl_data import Toggl_Data


load_dotenv()

start_date ='2020-09-23'
end_date = '2021-10-06'
timezone = '+10:00'

d = Toggl_Data(os.getenv('toggl_api_key'), timezone, start_date, end_date)
df = d.sum_time_by_client('Survival')

print(df)



