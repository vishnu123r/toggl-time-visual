import pandas as pd

def convert_json_df(json_file, project_dict):
    '''
    This methods converts the resultant json file from API to a df which can be used for analysis
    '''
    time_list = []

    for json in json_file:

        if int(json['dur']) == 0:
            continue
        start = json['start']
        stop = json['end']
        duration = json['dur']
        try: 
            description = json['description']
        except:
            description = 'no_description'
        try:
            project = project_dict[json['pid']]
        except:
            project = ("no_project", "no_client")
        time_list.append((start, duration, description, project[0], project[1])) 

    df = pd.DataFrame.from_records(time_list, columns =['start_date', 'duration', 'description', 'project_name', 'client_name'])
    df['date'] = df['start_date'].str[0:10]
    #df["date"] = pd.to_datetime(df["date"])
    df.drop(['start_date'], axis = 1, inplace=True)

    return df