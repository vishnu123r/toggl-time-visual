import pandas as pd

def convert_json_df(json_file, project_dict):
    '''
    This methods converts the resultant json file from API to a df which can be used for analysis
    '''
    time_list = []

    for json in json_file:

        blank_entry = int(json['dur']) == 0
        if blank_entry:
            continue
        id = str(json['id'])
        start_time = json['start']
        duration = json['dur']
        tags = json['tags']
        try: 
            description = json['description']
        except:
            description = 'no_description'
        try:
            project = project_dict[json['pid']]
        except:
            project = ("no_project", "no_client")
        time_list.append((id, start_time, duration, description, project[0], project[1], tags)) 

    df = pd.DataFrame.from_records(time_list, columns =['id','start_date', 'duration', 'description', 'project_name', 'client_name', 'tags'])
    df['date'] = df['start_date'].str[0:10]
    df.drop(['start_date'], axis = 1, inplace=True)

    return df