import pandas as pd
import geopy as geo
import airportsdata
#import osmnx
import geopandas as gpd
from geopy.distance import geodesic as GD


airports = airportsdata.load('IATA')


def find_airports(fest_address):
    pass


def airport_to_festival_distance(air_code, fest_address):
    if air_code in airports.keys():
        air_coord = [float(airports[air_code]['lat']), float(airports[air_code]['lon'])]
        fest_coord = gpd.tools.geocode(fest_address, provider='arcgis')
        fest_coord = [fest_coord['geometry'].y[0], fest_coord['geometry'].x[0]]
        dist = GD(air_coord, fest_coord).km
    else:
        print(f'Airport {air_code} not found.')
        dist = -10.0

    return dist

def str2list(str_in):

    str_split = str_in.split(',')
    str_out = []

    for str_ in str_split:
        str_out.append(str_.replace('[', '').replace('\'', '').replace(']', '').replace(' ', ''))
    
    return str_out


def update_data(data=None):
    
    # Find distances from festivals to airports
    distances = []
    for i, row in data.iterrows():
        fest_address = row['Address'] + ', '+ row['City'] + ', ' + row['Country']
        air_codes = str2list(row['IATA'])

        dists = []
        for air_code in air_codes:
            if air_code.lower() != 'nan':
                dist = airport_to_festival_distance(air_code, fest_address)
            else:
                dist = -10.0

            dists.append(int(dist))

        distances.append(dists)

    return distances


def fix_iata(data):

    iatas_col = []

    for i, row in data.iterrows():
        iatas = []

        iatas.append(row['IATA1'])
        iatas.append(row['IATA2'])
        iatas.append(row['IATA3'])

        iatas_col.append(iatas)

    data['IATA'] = iatas_col
    
    return data


def scrape_data():
    pass


def main():

    dataf = 'data/Tour-dates.csv'

    data = pd.read_csv(dataf) 
    #print(data.head())
    #print(data.columns[1])

    distances = update_data(data=data)

    data['distances'] = distances
    #print(data.head())
    data.to_csv(dataf, index=False)


    """
    data = fix_iata(data)
    data.drop(['IATA1', 'IATA2', 'IATA3'], inplace=True, axis=1)
    print(data.head())
    data.to_csv(dataf)
    data.to_csv(dataf, index=False)
    """

if __name__ == '__main__':

    main()
