import streamlit as st
import geopandas as gpd
import pandas as pd
import shapely
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from ryanair import Ryanair


def find_connected_flights(airport_code, date_from, date_to):
    ryanair = Ryanair("EUR")
    flights = ryanair.get_flights(airport_code, date_from, date_to)

    for flight in flights:

            print(flight)



def geocode_address(row):

    address = row['City'] + ' ' + row['Country']
    print(row, address)
    coord = gpd.tools.geocode(address)

    return coord['geometry'].values[0]


def get_nearby_airport_code(city, country):

    pass


if __name__ == '__main__':

    csv='data/Tour-dates.csv'
    df = pd.read_csv(csv)
    pts = []
    
    eu_center = {'Country':'Germany', 'City':'Darmstadt'}
    map_center = geocode_address(eu_center)
    #print(map_center)
    m = folium.Map(location=[map_center.y, map_center.x], zoom_start=4) 
    st.title('TOUR MANAGERS MAP')
    st.text('Follow and reach Nanowar wherever they may roam!')
    st.header('\n')

    for i, row in df.iterrows():
        #print(row)
        gps = geocode_address(row)
        #print(gps, gps.x)
        pts.append([gps.y, gps.x])
        #fest = row['Event name']
        #folium.Marker([gps.y, gps.x], tooltip=fest).add_to(m)

        #gps = row['gps']
        folium.Marker([gps.y, gps.x]).add_to(m)


    df['gps'] = pts
    #print(df.head())
    df.to_csv(csv)
    st_data = st_folium(m, width=800, height=600)

    



