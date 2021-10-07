from toggl_api import TogglAPI
from dotenv import load_dotenv
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np


load_dotenv()
t = TogglAPI(os.getenv('toggl_api_key'), '+10:00')
df = t.get_time_entries(start_date='2021-09-23', end_date = '2021-10-06')

print(df.head())




#df = df.reindex(columns = ['date', 'Project_name', 'Client_name', 'Duration'])
#print(df[df['date'] == '2021-09-23'].groupby(['date','Client_name'])['Duration'].sum()/3600)
# df = round(df.groupby(['date','Client_name'])['Duration'].sum()/3600,2)
# print(df)


#df['perc'] = df['time']*100/df['time'].sum()

#print(df)