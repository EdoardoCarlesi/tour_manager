import streamlit as st
import geopandas as gpd
import pandas as pd
import shapely
import folium
import airportsdata
from folium.features import DivIcon
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from ryanair import Ryanair
import json


def find_connected_flights(airport_code, date_from, date_to):
    ryanair = Ryanair("EUR")
    flights = ryanair.get_flights(airport_code, date_from, date_to)

    destinations = []
    for flight in flights:
        destinations.append(flight.destinationFull)
        
    return destinations


def geocode_address(row=None, address=None):

    address = row['City'] + ' ' + row['Country']
    coord = gpd.tools.geocode(address)

    return coord['geometry'].values[0]


def get_nearby_airport_code(city, country):

    pass

def convert_date_format(date):
    return date[-4:] + '-' + date[3:5] + '-' + date[0:2]


def time_span(date):

    date0 = date
    date1 = date

    return date0, date1


if __name__ == '__main__':

    csv='data/Tour-dates.csv'
    df = pd.read_csv(csv, sep=';')
    #df = df_full.iloc[0:3]
    coords = []
     
    # Geolocate all the gigs
    for i, row in df.iterrows():
        gps = geocode_address(row)
        gps1 = [gps.y, gps.x]
        coords.append(gps1)

    # Center the map on some city around the center of Europe
    eu_center = {'Country':'Germany', 'City':'Darmstadt'}
    map_center = geocode_address(eu_center)

    #tile = 'Stamen Toner'
    tile = 'stamenwatercolor'
    #tile = 'cartobdark_matter'

    # Create the folium map!
    m = folium.Map(location=[map_center.y, map_center.x], 
                    tiles=tile,
                    zoom_start=4) 

    # Create the actual streamlit stuff
    st.title('TOUR MANAGERS MAP')
    st.text('Follow and reach Nanowar wherever they may roam!')
    st.header('\n')

    # FIXME: this is going to look for the png file in some streamlit_folium subfolder!!
    img_path = 'data/N.png'

    for i, row in df.iterrows():
        text = f"Event: {row['Event name']}\r\n Date : {row['Event date']}"
        new_date = convert_date_format(row['Event date'])

        # TODO: make this automatic, find all the IATA codes for the nearby airports!
        iata = row['IATA1']
        
        # Find the ryanair destinations
        dests = find_connected_flights(iata, new_date, new_date)

        # This creates the icon, remember that the img_path is a messy variable
        icon = DivIcon(icon_size=(64, 64), 
            icon_anchor=(0, 0), 
            html="<img src='"+ img_path +"' alt=" + text + ">"
            )

        # Add the marker!
        folium.Marker(coords[i], icon=icon, tooltip=text).add_to(m)

        if len(dests) > 10000:
            for dest in dests:
                gps2 = gpd.tools.geocode(dest)['geometry'].values[0]
                gps2 = [gps2.y, gps2.x]
                print('POINTs:', gps1, gps2)
                line = [gps1, gps2]
                #folium.Marker(gps2, tooltip=text).add_to(m)
                folium.PolyLine(line).add_to(m)

    st_data = st_folium(m, width=800, height=600)

    



