import pandas as pd


def convert(tour_csv, mtbk_csv):

    columns = ['Date', 'Day Type', 'Day Title', 'Location 1 Type', 'Location 1', 'Location 2 Type', 'Location 2']
    df_new = pd.DataFrame(columns=columns)
    df_old = pd.read_csv(tour_csv)
    
    event_dates, day_types, day_titles, location_types1, locations1, location_types2, locations2 = [], [], [], [], [], [], []

    for i, row in df_old.iterrows():
        
        event_date = row['Event date']
        event_dates.append(event_date)
        day_type = row['Event name']

        if ' OFF' in day_type:
            location_type1 = 'OFF'
        else:
            location_type1 = 'VENUE'
        
        location1 = row['Event name'].split(' at ')[-1] + ' ' + row['Address'] + ' ' + row['City'] + ' ' + row['Country']

        location_types1.append(location_type1)
        locations1.append(location1)

        if ' at ' in day_type:
            day_type = 'SHOW DAY'
        else:
            day_type = 'DAY OFF/TRAVEL'
            
        day_types.append(day_type)
        
    df_new['Date'] = event_dates
    df_new['Day Title'] = day_types
    df_new['Day Type'] = location_types1
    df_new['Location 1 Type'] = location_types1
    df_new['Location 1'] = locations1
    df_new.to_csv(mtbk_csv)

if __name__ == '__main__':

    convert('data/Tour-dates.csv', 'toyboys_tbk.csv')
        
