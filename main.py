import streamlit as st
import geopandas as gpd
import pandas as pd
import shapely
import folium
import airportsdata
from folium.features import DivIcon, CustomIcon
from streamlit_folium import st_folium, folium_static
import matplotlib.pyplot as plt
from ryanair import Ryanair
import json
from ipyleaflet import Marker
import html_pages

airports = airportsdata.load('IATA')

def find_connected_flights(airport_code, date_from, date_to):
    ryanair = Ryanair("EUR")
    flights = ryanair.get_flights(airport_code, date_from, date_to)

    destinations = []
    prices = []
    for flight in flights:
        destinations.append(flight.destinationFull)
        prices.append(flight.price)
        
    return destinations, prices

def iata2gps(airport):
    return [airports[airport]['lat'], airports[airport]['lon']]

def geocode_address(row=None, address=None):
    address = str(row['City'].encode('utf-8')) + ' ' + str(row['Country'].encode('utf-8'))
    #coord = gpd.tools.geocode(address, provider='arcgis')
    coord = gpd.tools.geocode(address, provider='arcgis')
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
    #img_path = 'https://www.nanowar.it/wp-content/uploads/2022/05/N_icon_small.png'
    img_path = 'data/N_icon_small.png'
    img_air_path = 'data/B_icon.png'

    for i, row in df.iterrows():
        text = "<p>" + row['Event name'] + "</p>"
        new_date = convert_date_format(row['Event date'])

        # TODO: make this automatic, find all the IATA codes for the nearby airports!
        iatas = [str(row['IATA1']), str(row['IATA2']), str(row['IATA3'])]
        popup_text = html_pages.popup_html(row)

        icon = CustomIcon(img_path, 
                        icon_size=(30, 40), 
                        icon_anchor=(13, 40)) 
        icon_text = DivIcon(icon_anchor=(0,0),
                            html="<p class='text'><b><em>" + row['City'].replace(' ', '_').replace('-', '_')  + "</em></b></p>")

        # Add the marker!
        marker_sign = folium.Marker(coords[i], 
                        icon=icon,  
                        popup=popup_text,
                        tooltip=text)
        marker_sign.add_to(m)

        marker_text = folium.Marker(coords[i], 
                        popup=popup_text,
                        icon=icon_text)

        # Find the ryanair destinations
        for iata in iatas:

            if (len(iata) == 3) and iata.upper() != 'NAN':
                
                
                if iata in airports.keys():
                    dests, prices = find_connected_flights(iata, new_date, new_date)
                    gps1 = iata2gps(iata)
                    
                    air_name = airports[iata]['name']
                    text_air = html_pages.flights_html(airports[iata]['name'], dests, prices)
                    icon_air = CustomIcon(img_air_path,
                        icon_size=(30, 40), 
                        icon_anchor=(13, 40)) 

                    marker_flight = folium.Marker(gps1,
                                                icon=icon_air,
                                                tooltip=air_name,
                                                popup=text_air)

                    marker_flight.add_to(m)           

        marker_text.add_to(m)

    #st_data = st_folium(m, width=800, height=600)
    folium_static(m, width=1000, height=800)

    



