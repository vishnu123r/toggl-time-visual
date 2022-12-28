import os
import psycopg2
from sqlalchemy import create_engine
import io
import pandas as pd


from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from toggl_api import TogglAPI
import os
from dotenv import load_dotenv
from helpers import convert_json_df

import sys

load_dotenv()


class PostgresAPI(object):

    def __init__(self, database, password, host = 'localhost', port = 5432,  user = 'postgres', table = 'time_entries'):
        self.database = database
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.table = table
        #self.engine_string = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(self.user, self.password, self.host, self.port, self.database)
        self.engine_string = os.getenv('DATABASE_URL')
        self.engine = create_engine(self.engine_string)
        print("******************" + self.engine_string + "*************")
        self.table_exists = False

        try:
            
            conn = self.engine.raw_connection()
            cur = conn.cursor()

            ### Check if table exists
            cur.execute("""SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'""")
            for table in cur.fetchall():
                has_table = table[0] == self.table
                if has_table:
                    self.table_exists = True
        
        finally:
            cur.close()
            conn.close()
    
    def _post_data(self, df):
        engine = create_engine(self.engine_string)
   
        if self._df_ok(df):
            try:
                df.to_sql(f'{self.table}', engine, index= False, if_exists='append')
                print("Data has been saved to postgres")

            except Exception as error:
                print(error)
                print("The data has not been saved. There was an error in establishing the connection to Postgres")

        else:
            print("Data has not been saved. Please recorrect the outlier values")
            return "Please check the time entries. There are outlier values"

    def _get_toggl_df(self,start_date, end_date):
        """
        Connects to toggl api and returns data as a DataFrame
        """

        toggl = TogglAPI(os.getenv('toggl_api_key'), os.getenv('time_zone'))
        json_file = toggl.get_time_entries(start_date, end_date)
        project_dict = toggl._get_project_dict()
        df = convert_json_df(json_file, project_dict)

        return df

    def _df_ok(self, df):
        
        """Checks if the there are any invalid entries from the toggl app. Return s false if the time duration from a day 
        is more than 35 hours and if the time was not logged for client name "phone off".
        """
        
        df = round(df.groupby(by= ['date', 'client_name'])['duration'].sum()/3600/1000,2)
        df = df.reset_index().reindex(columns = ['date', 'client_name', 'duration'] )
        df_sum = df.groupby(by = ['date'])['duration'].sum()
        df_sum = df_sum.reset_index().reindex(columns = ['date', 'duration'] )
        
        no_outlier_values = 0
        for date,duration in df_sum.values:
            has_outlier_time_entry = duration> 35
            if has_outlier_time_entry:
                df_date = df[(df["date"] == date)]
                has_phone_off_client = 'phone off' in df_date['client_name'].values
                if not has_phone_off_client:
                    print("There is an issue with the following date and duration (Please recheck them): ", date, duration)
                    no_outlier_values+=1

        if no_outlier_values > 0:
            return False

        else:
            return True
        
    def _get_date_data(self):

        try:
            conn = self.engine.raw_connection()
            cur = conn.cursor()
            cur.execute(f"select DISTINCT date from {self.table}")
            rows = cur.fetchall()

            date_list = []
            for row in rows:
                date_list.append(row[0])

            date_list = [datetime.strptime(date, "%Y-%m-%d") for date in date_list]

            return date_list
        
        finally:
            cur.close()
            conn.close()

    def _find_missing_dates(self, date_list):
        date_list = sorted(date_list)
        date_sequence = set(date_list[0] + timedelta(x) for x in range((date_list[-1] - date_list[0]).days + 1))
        missing_dates = sorted(date_sequence - set(date_list))
        
        return missing_dates

    def _get_values_end_date_df(self, end_date, date_list):
        new_start_date = (max(date_list) + relativedelta(days = 1)).isoformat()
        df = self._get_toggl_df(new_start_date, end_date)
        return df

    def _get_values_start_date_df(self, start_date, date_list):
        new_end_date = (min(date_list) - relativedelta(days = 1)).isoformat()
        df = self._get_toggl_df(start_date, new_end_date)
        return df

    def _get_missings_values_df(self, missing_dates):
        try:
            conn = self.engine.raw_connection()
            cur = conn.cursor()     
            start_date = min(missing_dates).isoformat()
            end_date = max(missing_dates).isoformat()
            print("Min missing Date: ", start_date)
            print("Max missing Date: ", end_date)
            cur.execute(f"DELETE FROM {self.table} WHERE date between '{start_date}' and '{end_date}'")
            conn.commit()
            df = self._get_toggl_df(start_date, end_date)

        finally:
            cur.close()
            conn.close()

        return df

    def _save_data_from_toggl(self, start_date, end_date):

        """ This method checks the database for existing data and retirves and saves only the required data to the database"""
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if self.table_exists == False:
            print("Table does not exist")
            df = self._get_toggl_df(start_date.isoformat(), end_date.isoformat())
            self._post_data(df)
            return "New Table has been created"
        
        date_list = self._get_date_data()

        missing_dates = self._find_missing_dates(date_list)
        date_missing = len(missing_dates) > 0

        if date_missing:
            print("---Dates Missing---")
            date_list = [min(date_list) + timedelta(x) for x in range((max(date_list) - min(date_list)).days + 1)] # This required as part of the algorithm. We need to check if the dates are between the max and min values

            if start_date in date_list and end_date in date_list:
                print("---Both within the interval---")
                df = self._get_missings_values_df(missing_dates)
                self._post_data(df)

            elif start_date not in date_list and end_date not in date_list:
                print("---None within the interval---")
                is_on_extremes = start_date > max(date_list) or end_date < min(date_list)
                if is_on_extremes:
                    df = self._get_toggl_df(start_date, end_date)
                    self._post_data(df)
                else:
                    df_1 = self._get_missings_values_df(missing_dates)
                    df_2 = self._get_values_start_date_df(start_date.isoformat(), date_list)
                    df_3 = self._get_values_end_date_df(end_date.isoformat(), date_list)
                    df = pd.concat([df_1,df_2, df_3])
                    self._post_data(df)

            elif start_date not in date_list:
                print("---Start date not within the interval---")
                df_1 = self._get_missings_values_df(missing_dates)
                df_2 = self._get_values_start_date_df(start_date.isoformat(), date_list)
                df = pd.concat([df_1, df_2])
                self._post_data(df)

            elif end_date not in date_list:
                print(end_date)
                print("---End date not within the interval---")
                df_1 = self._get_missings_values_df(missing_dates)
                df_2 = self._get_values_end_date_df(end_date.isoformat(), date_list)
                df = pd.concat([df_1, df_2])
                self._post_data(df)

        else:
            print("---Dates not missing---")
            if start_date in date_list and end_date in date_list:
                print("---Both within the interval---")
                return "Data is present in the table"

            elif start_date not in date_list and end_date not in date_list:
                print("---None within the interval---")
                is_on_extremes = start_date > max(date_list) or end_date < min(date_list)
                if is_on_extremes:
                    df = self._get_toggl_df(start_date.isoformat(), end_date.isoformat())
                    self._post_data(df)

                else:
                    df_1 = self._get_values_start_date_df(start_date.isoformat(), date_list)
                    df_2 = self._get_values_end_date_df(end_date.isoformat(), date_list)
                    df = pd.concat([df_1, df_2])
                    self._post_data(df)

            elif start_date not in date_list:
                if start_date < datetime.strptime('2021-02-26', '%Y-%m-%d'):
                    print("There is no need to save data")
                    return "There is no need to save data"
                print("---Start date not within the interval---")
                df = self._get_values_start_date_df(start_date.isoformat(), date_list)
                self._post_data(df)

            elif end_date not in date_list:
                print(end_date)
                print("---End date not within the interval---")
                df = self._get_values_end_date_df(end_date.isoformat(), date_list)
                self._post_data(df)

    def _check_dates(self, start_date, end_date):
        start_greater_than_end  = datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d")
        if start_greater_than_end:
            raise ValueError("End date precedes the start date")

        date_today_or_future = datetime.now() <= datetime.strptime(start_date, "%Y-%m-%d") or datetime.now() <= datetime.strptime(end_date, "%Y-%m-%d")
        if date_today_or_future:
            raise ValueError("Either the start date or the end date is today or in the the future. ONly time entries till yesterday can be gathered")

    def get_data(self, start_date, end_date):
        
        self._check_dates(start_date, end_date)
        self._save_data_from_toggl(start_date, end_date)
        df = pd.read_sql(f"select * from {self.table} where date between '{start_date}' and '{end_date}'", self.engine)

        if self._df_ok(df):
            return df
        else:
            print("The above datapoints been saved multiple times in the database")
            return "The above datapoints been saved multiple times in the database"



if __name__=='__main__':

    #date_list = [('2021-07-20','2021-07-25'), ('2021-07-23','2021-07-30'), ('2021-08-21','2021-08-23'), ('2021-07-26','2021-08-22'),
    #('2021-04-04','2021-05-04'),('2021-07-07','2021-08-25'), ('2021-11-01', '2021-11-17')]

    date_list = [('2022-11-01', '2022-11-17')]
    
    for start_date, end_date in date_list:
        p = PostgresAPI(os.getenv('postgres_db'), os.getenv('postgres_pass'))
        df = p.get_data(start_date, end_date)
        
        
