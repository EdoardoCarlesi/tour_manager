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

import pickle as pkl
import json
from datetime import date
import os

# Local imports 
import html_pages

airports = airportsdata.load('IATA')
departures = dict()

def find_connected_flights(airport_code, date_from, date_to):
    ryanair = Ryanair("EUR")

    date_today = str(date.today())
    f_name = 'ryan_' + airport_code + date_from + date_to + date_today + '.pkl'
    f_tmp = os.path.join('tmp', f_name)

    if not os.path.isfile(f_tmp):
        flights = ryanair.get_flights(airport_code, date_from, date_to)
        
        with open(f_tmp, 'wb') as f:
            pkl.dump(flights, f)
    else:
        with open(f_tmp, 'rb') as f:
            flights = pkl.load(f)

    destinations = []
    prices = []
    codes = []
    for flight in flights:
        codes.append(flight.destination)
        destinations.append(flight.destinationFull)
        prices.append(flight.price)
        
    return destinations, prices, codes

def iata2gps(airport):
    return [airports[airport]['lat'], airports[airport]['lon']]

def geocode_address(row=None, address=None):
    #address = str(row['City'].encode('utf-8')) + ' ' + str(row['Country'].encode('utf-8'))
    address = row['City'] + ' ' + row['Country']

    f_tmp = os.path.join('tmp', address.replace(' ', '').replace(',', '') + '.pkl')

    if os.path.isfile(f_tmp):
        with open(f_tmp, 'rb') as f:
            coord = pkl.load(f)
    else:
        coord = gpd.tools.geocode(address, provider='arcgis')
        with open(f_tmp, 'wb') as f:
            pkl.dump(coord, f)

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


def map_init(m):
    """ Initialize the map with all the concerts and nearby airports """

    img_path = 'data/N_icon_small.png'
    img_air_path = 'data/B_icon.png'

    for i, row in df.iterrows():
        event = row['Event name']
        text = "<p>" + event + "</p>"
        new_date = convert_date_format(row['Event date'])

        # TODO: make this automatic, find all the IATA codes for the nearby airports!
        iatas = [str(row['IATA1']), str(row['IATA2']), str(row['IATA3'])]
        popup_text = html_pages.popup_html(row)

        icon = CustomIcon(img_path, 
                        icon_size=(27, 38), 
                        icon_anchor=(13, 40)) 

        icon_text = DivIcon(icon_anchor=(0,0),
                            html="<p class='text'><b><em>" + row['City'].replace(' ', '_').replace('-', '_')  + "</em></b></p>")

        # Add the marker for the CONCERT location
        marker_sign = folium.Marker(coords[i], 
                        icon=icon,  
                        popup=popup_text,
                        tooltip=text)
        marker_sign.add_to(m)

        # Add the location's name
        marker_text = folium.Marker(coords[i], 
                        popup=popup_text,
                        icon=icon_text)
        marker_text.add_to(m)

        # Find the ryanair destinations
        for iata in iatas:

            if (len(iata) == 3) and iata.upper() != 'NAN':
                
                if iata in airports.keys():
                    dests, prices, codes = find_connected_flights(iata, new_date, new_date)
                    update_departures(codes, dests, prices, iata, event, new_date)

                    gps1 = iata2gps(iata)
                    
                    air_name = airports[iata]['name']
                    text_air = html_pages.flights_html(airports[iata]['name'], dests, prices)
                    icon_air = CustomIcon(img_air_path,
                        icon_size=(27, 38), 
                        icon_anchor=(13, 40)) 
                    
                    # Add a marker to the nearby airports
                    marker_flight = folium.Marker(gps1,
                                                icon=icon_air,
                                                tooltip=air_name,
                                                popup=text_air)

                    marker_flight.add_to(m)           


def update_departures(codes, dests, prices, iata, event, date):
    """
        IATA: airport code for the festival airport
        dests: airports connected to the concert
        event: festival or concert name
    """

    for code, dest, price in zip(codes, dests, prices):
        if code in departures.keys():
            departures[code]['event'].append(event)
            departures[code]['date'].append(date)
            departures[code]['price'].append(price)
            departures[code]['event_airport'].append(iata)
        else:
            departures[code] = dict()
            departures[code]['origin'] = dest
            departures[code]['event'] = [event]
            departures[code]['date'] = [date]
            departures[code]['price'] = [price]
            departures[code]['event_airport'] = [iata]


if __name__ == '__main__':

    csv = 'data/Tour-dates.csv'
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

    st.markdown(""" <style> .shows {
    font-size:2px ; font-family: 'Cooper Black'; color: #FFFFFF;} 
    </style> """, unsafe_allow_html=True)

    # Create the actual streamlit stuff
    st.markdown('<p class="title">TOUR MANAGERS M-APP</p>', unsafe_allow_html=True)
    st.markdown('<p class="text">Catch Nanowar Of Steel on Tour on the wings of a Barbagianni</p>', unsafe_allow_html=True)

    map_init(m)
    folium_static(m, width=800, height=600)

    #print(departures)

    col_keep = ['Event date', 'Event name', 'Country', 'City', 'Website']

    concerts_text = html_pages.concerts_html(df)
    st.write(concerts_text, unsafe_allow_html=True)
    #concerts_text = "<p class='shows'>" + html_pages.concerts_html(df) + "</p>"
    #st.markdown(concerts_text, unsafe_allow_html=True)

   
    for key in departures:

        if key in airports.keys():
            airport = airports[key]['city']
        else:
            airport = key

        departures_text = html_pages.departures_html(departures[key])
        st.write(departures_text, unsafe_allow_html=True)
        
            #print(airport['city'])
    

