from toggl_api import TogglAPI
from dotenv import load_dotenv
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urlencode
import json
import calendar

load_dotenv()
t = TogglAPI(os.getenv('toggl_api_key'), '+10:00')
