import pandas as pd
import geopy as geo
import airportsdata
import geopandas as gpd
from geopy.distance import geodesic as GD


airports = airportsdata.load('IATA')


def str2list(str_in):

    str_split = str_in.split(',')
    str_out = []

    for str_ in str_split:
        str_out.append(str_.replace('[', '').replace('\'', '').replace(']', '').replace(' ', ''))
    
    return str_out


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
    print(data.head())
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
