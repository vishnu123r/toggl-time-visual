import os
import psycopg2
from sqlalchemy import create_engine
import io
import pandas as pd


from datetime import datetime
from toggl_api import TogglAPI
import os
from dotenv import load_dotenv
from helpers import convert_json_df

load_dotenv()


class PostgresAPI(object):

    def __init__(self, database, password, host = 'localhost', port = 5432,  user = 'postgres', table = 'time_entries'):
        self.database = database
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.table = table
        self.engine_string = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(self.user, self.password, self.host, self.port, self.database)
        self.engine = create_engine(self.engine_string)
        self.table_exists = False

        try:
            conn = self.engine.raw_connection()
            cur = conn.cursor()

            ### Check if table exists
            cur.execute("""SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'""")
            for table in cur.fetchall():
                if table[0] == self.table:
                    self.table_exists = True
        
        finally:
            cur.close()
            conn.close()
    
    def _post_data(self, df):

        if self._df_ok(df):
            try:
                df.to_sql(f'{self.table}', self.engine, index= False, if_exists='append')

                # conn_2 = self.engine.raw_connection()
                # cur_2 = conn_2.cursor()
                # print("Have established a connection to db")
                # output = io.StringIO() # This is created to stream the date directly to the database rather than saving it as csv
                # df.to_csv(output, sep='\t', header=False, index=False)
                # output.seek(0)
                # print('trying to copy to db')
                # cur_2.copy_from(output, self.table, null="") # null values become ''
                # print('Copied to db')
                # conn_2.commit()

                print("Data has been saved to postgres")

            except Exception as error:
                print(error)
                print("The data has not been saved. There was an error in establishing the connection to Postgres")

            # finally:
            #     cur_2.close()
            #     conn_2.close()

        else:
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
        df = round(df.groupby(by= 'date')['duration'].sum()/3600/1000,2)
        df = df.reset_index().reindex(columns = ['date', 'duration'] )
        i = 0
        for date,duration in df.values:
            if duration> 35:
                print("There is an issue with the following date and duration (Please recheck them): ", date, duration)
                i+=1

        if i > 0:
            return False

        else:
            return True
        
    def _get_date_data(self):

        try:
            conn = self.engine.raw_connection()
            cur = conn.cursor()
            
            #cur.execute(f'ALTER TABLE {self.table} ALTER COLUMN date TYPE date using ("date"::text::date)')
            cur.execute(f"select DISTINCT date from {self.table}")
            rows = cur.fetchall()

            date_list = []
            for row in rows:
                date_list.append(row[0])#.isoformat())
            
            return date_list
        
        finally:
            cur.close()
            conn.close()

    def _save_data_from_toggl(self, start_date, end_date):

        """ This method checks the database for existing data and retirves and saves only the required data to the database"""

        if self.table_exists == False:
            df = self._get_toggl_df(start_date, end_date)
            self._post_data(df)
            return "New Table has been created"
        
        date_list = self._get_date_data()
        
        if start_date in date_list and end_date in date_list:
            return "Data is already in the database"

        try:
            conn = self.engine.raw_connection()
            cur = conn.cursor()

            if start_date not in date_list and end_date not in date_list:
                print("No start date and No end date")
                cur.execute(f"DELETE FROM {self.table}")
                conn.commit()
                df = self._get_toggl_df(start_date, end_date)              

            elif end_date not in date_list:
                print("No end date")
                new_start_date = max(date_list, key=lambda d: datetime.strptime(d, '%Y-%m-%d'))
                cur.execute(f"DELETE FROM {self.table} WHERE date = '{new_start_date}'")
                conn.commit()
                df = self._get_toggl_df(new_start_date, end_date)

            elif start_date not in date_list:
                print("No start date")
                new_end_date = min(date_list, key=lambda d: datetime.strptime(d, '%Y-%m-%d'))
                print(new_end_date)
                cur.execute(f"DELETE FROM {self.table} WHERE date = '{new_end_date}'")
                conn.commit()
                df = self._get_toggl_df(start_date, new_end_date)

        finally:
            cur.close()
            conn.close()

        self._post_data(df)


    def get_data(self, start_date, end_date):

        self._save_data_from_toggl(start_date, end_date)
        try:
            conn = self.engine.raw_connection()
            cur = conn.cursor()
            cur.execute(f"select * from {self.table} where date between '{start_date}' and '{end_date}'")
            rows = cur.fetchall()
            df = pd.DataFrame.from_records(rows, columns =['duration', 'description', 'project_name', 'client_name', 'date'])

        finally: 
            cur.close()
            conn.close()
            
        return df

if __name__=='__main__':
    start_date ='2021-08-08'
    end_date = '2021-09-16'
    p = PostgresAPI('toggldb', 'danekane11')
    df = p.get_data(start_date, end_date)

    df = round(df.groupby(by= 'date')['duration'].sum()/3600/1000,2)
    print(df)