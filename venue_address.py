import geopandas as gpd 
import pandas as pd

f_csv = 'data/Tour-dates.csv'

df = pd.read_csv(f_csv)

#print(df.head())
#print(df.columns)
#print(df['Address'])

for i, row in df.iterrows():

    event = row['Event name'].split(' at ')[-1]
    city = row['City']
    country = row['Country']

    print(event, city, country)
