import geopandas as gpd 
import pandas as pd


def get_address():
    f_csv = 'data/Tour-dates.csv'

    df = pd.read_csv(f_csv)
    addresses = []

    for i, row in df.iterrows():

        event = row['Event name'].split(' at ')[-1]
        city = row['City']
        country = row['Country']

        addresses.append(f'{event}, {city}, {country}')

    return addresses


if __name__ == '__main__':

    get_address()
