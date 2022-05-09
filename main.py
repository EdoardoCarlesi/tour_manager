import streamlit as st
import geopandas as gpd
import pandas as pd
import shapely
import folium
import airportsdata
from folium.features import DivIcon
from streamlit_folium import st_folium, folium_static
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

def show_airports():
    print('SHOWING AIRPORTS!')

if __name__ == '__main__':

    csv='data/Tour-dates.csv'
    df = pd.read_csv(csv, sep=';')
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

    # Create the folium map!
    m = folium.Map(location=[map_center.y, map_center.x], 
                    tiles=tile,
                    zoom_start=5) 

    st.markdown(""" <style> .title {
    font-size:50px ; font-family: 'Cooper Black'; color: #FF9633;} 
    </style> """, unsafe_allow_html=True)

    st.markdown(""" <style> .text {
    font-size:20px ; font-family: 'Cooper Black'; color: #FFFFFF;} 
    </style> """, unsafe_allow_html=True)


    #st.markdown(""" <style> .font {
    #font-size:50px ; font-family: 'Cooper Black'; color: #FF9633;} 
    #</style> """, unsafe_allow_html=True)

    # Create the actual streamlit stuff
    st.markdown('<p class="title">TOUR MANAGERS M-APP</p>', unsafe_allow_html=True)
    st.markdown('<p class="text">Catch Nanowar Of Steel on Tour on the wings of a Barbagianni</p>', unsafe_allow_html=True)

    #img_path = 'http://www.nanowar.it/imgs/N.png'
    #img_path = 'http://www.nanowar.it/imgs/N_icon.png'
    #img_path = 'https://www.nanowar.it/wp-content/uploads/2022/05/N_icon.png'
    img_path = 'https://www.nanowar.it/wp-content/uploads/2022/05/N_icon_small.png'

    for i, row in df.iterrows():
        #text = f"Event: {row['Event name']}\r\n Date : {row['Event date']}"
        text = "<p>" + row['Event name'] + "<br>" + row['Event date'] + "</p>"
        new_date = convert_date_format(row['Event date'])

        # TODO: make this automatic, find all the IATA codes for the nearby airports!
        iata = row['IATA1']
        
        # Find the ryanair destinations
        dests = find_connected_flights(iata, new_date, new_date)

        # This creates the icon, remember that the img_path is a messy variable
        icon = DivIcon(icon_size=(40, 40), 
                        icon_anchor=(13, 40),
                        html="<img src="+ img_path + ">")

        icon_text = DivIcon(icon_anchor=(0,0),
                            html="<p class='text'><b><em>" + row['City'].replace(' ', '_').replace('-', '_')  + "</em></b></p>")

        # Add the marker!
        marker_sign = folium.Marker(coords[i], 
                        icon=icon,  
                        tooltip=text)
        #marker_sign.on_click()
        marker_sign.add_to(m)


        marker_text = folium.Marker(coords[i], 
                        icon=icon_text).add_to(m)

        marker_text.add_to(m)
        

        if len(dests) > 10000:
            for dest in dests:
                gps2 = gpd.tools.geocode(dest)['geometry'].values[0]
                gps2 = [gps2.y, gps2.x]
                print('POINTs:', gps1, gps2)
                line = [gps1, gps2]
                #folium.Marker(gps2, tooltip=text).add_to(m)
                folium.PolyLine(line).add_to(m)

    #st_data = st_folium(m, width=800, height=600)
    folium_static(m, width=1000, height=800)

    



