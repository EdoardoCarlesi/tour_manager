import streamlit as st
import geopandas as gpd
import pandas as pd
import shapely
import folium
import pycountry
import airportsdata
from folium.features import DivIcon, CustomIcon
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
from ryanair import Ryanair

import pickle as pkl
import json
import datetime
from datetime import date
#from state import provide_state
import os

# Local imports 
import html_pages

# These variables will be used throughout the script
airports = airportsdata.load('IATA')
departures = dict()
cities_list = dict()
city2airports = dict()
event_airports_list = []
countries_list = []

# Reset global variables
def reset_vars():
    departures.clear()


@st.cache
def safe_call_ryanair_return_apis(airport_code, date_from, date_to, return_from, return_to):
 
    ryanair = Ryanair("EUR")
    date_today = str(date.today())
    f_name = 'ryan_return_' + airport_code + date_from + date_to + date_today + '.pkl'
    f_tmp = os.path.join('tmp', f_name)
    trips = ryanair.get_return_flights(airport_code, date_from, date_to, return_from, return_to)

    
    #if not os.path.isfile(f_tmp):
    #    trips = ryanair.get_return_flights(airport_code, date_from, date_to, return_from, return_to)
        
    #    with open(f_tmp, 'wb') as f:
    #        pkl.dump(trips, f)
    #else:
    #    with open(f_tmp, 'rb') as f:
    #        trips = pkl.load(f)
    

    return trips


def find_return_flights(airport_code, date_from, date_to, date_event=None):
    
    destinations = []
    prices = []
    codes = []

    # Let's retrieve all the round trips in the desired time span
    if not date_event == None:
        trips = safe_call_ryanair_return_apis(airport_code, date_from, date_event, date_event, date_to)
    else:
        trips = safe_call_ryanair_return_apis(airport_code, date_from, date_from, date_to, date_to)
    
    # Loop on the trips
    for trip in trips:
        
        # The origin is still the 
        flight = trip.outbound
        codes.append(flight.destination)
        destinations.append(flight.destinationFull)
        prices.append(trip.totalPrice)
       
        # Check that the destination airport is legit so we can get some info
        if flight.destination in airports.keys():
            this_city = airports[flight.destination]['city']
            this_country = airports[flight.destination]['country']
            countries_list.append(this_country)

            # Here we map the cities to their airport code name in a dictionary
            if not this_city in city2airports.keys():
                city2airports[this_city] = flight.destination
            
            # For each country we want to keep a unique list of cities
            if this_country in cities_list.keys():
                if not this_city in cities_list[this_country]:
                    cities_list[this_country].append(this_city)
            
            # If the desired city is not in the country then create a specific dictionary entry
            else:
                cities_list[this_country] = [this_city]

    return destinations, prices, codes


def iata2gps(airport):
    return [airports[airport]['lat'], airports[airport]['lon']]

def geocode_address(row=None, address=None):
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


def create_date_range(date, days_before, days_after):

    date_base = datetime.datetime.strptime(date, "%d/%m/%Y")
    date_from = date_base - datetime.timedelta(days_before)
    date_to = date_base + datetime.timedelta(days_after)
    date_from_str = datetime.datetime.strftime(date_from, "%Y-%m-%d")
    date_to_str = datetime.datetime.strftime(date_to, "%Y-%m-%d")

    return date_from_str, date_to_str


def map_init(m, df):
    """ Initialize the map with all the concerts and nearby airports """

    coords = []
    img_path = 'data/N_icon_small.png'
    img_air_path = 'data/B_icon.png'

    # Geolocate all the gigs
    for i, row in df.iterrows():
        gps = geocode_address(row)
        gps1 = [gps.y, gps.x]
        coords.append(gps1)

    for i, row in df.iterrows():
        event = row['Event name']
        text = "<p>" + event + "</p>"

        event_airports_list.append(row['IATA1'])
        event_airports_list.append(row['IATA2'])
        event_airports_list.append(row['IATA3'])

        # TODO: make this automatic, find all the IATA codes for the nearby airports!
        iatas = [str(row['IATA1']), str(row['IATA2']), str(row['IATA3'])]
        popup_text = html_pages.popup_html(row)

        icon_show = CustomIcon(img_path, icon_size=(27, 38), icon_anchor=(13, 40)) 
        icon_text = DivIcon(icon_anchor=(0,0),
                            html="<p class='text'><b><em>" + row['City'].replace(' ', '_').replace('-', '_')  + "</em></b></p>")
    

        concert_group = folium.FeatureGroup(name='Concerts').add_to(m)
        airport_group = folium.FeatureGroup(name='Airports', show=False).add_to(m)

        # Add the marker for the CONCERT location
        concert_marker = folium.Marker(coords[i], icon=icon_show, popup=popup_text, tooltip=text)
        #concert_group.add_child(concert_marker)
        concert_marker.add_to(m)

        # Add the location's name
        concert_text = folium.Marker(coords[i], popup=popup_text, icon=icon_text)
        #concert_group.add_child(concert_text)
        concert_text.add_to(m)

        # Find the ryanair destinations
        for iata in iatas:

            if (len(iata) == 3) and iata.upper() != 'NAN':
                
                if iata in airports.keys():

                    # Initialize looking at all the shows one week before and after the show
                    date_from, date_to = create_date_range(row['Event date'], 7, 7)
                    new_date = convert_date_format(row['Event date'])
                    dests, prices, codes = find_return_flights(iata, date_from, date_to, date_event=new_date)
                    update_departures(codes, dests, prices, iata, event, new_date)

                    gps1 = iata2gps(iata)
                    
                    air_name = airports[iata]['name']
                    air_text = html_pages.flights_html(airports[iata]['name'], dests, prices)
                    air_icon = CustomIcon(img_air_path, icon_size=(27, 38), icon_anchor=(13, 40)) 
                    
                    # Add a marker to the nearby airports
                    air_marker = folium.Marker(gps1, icon=air_icon, tooltip=air_name, popup=air_text)
                    #airport_group.add_child(air_marker)           
                    air_marker.add_to(m)           

        #folium.LayerControl().add_to(m)



def update_flights_time_range(days_before, days_after, df, date_event=False):

    for i, row in df.iterrows():
        event = row['Event name']
        date = row['Event date']
        iatas = [str(row['IATA1']), str(row['IATA2']), str(row['IATA3'])]

        for iata in iatas:
            if (len(iata) == 3) and iata.upper() != 'NAN':
                if iata in airports.keys():
                    date_from, date_to = create_date_range(date, days_before, days_after)
                    new_date = convert_date_format(date)

                    if date_event:
                        dests, prices, codes = find_return_flights(iata, date_from, date_to, date_event=new_date)
                    else:
                        dests, prices, codes = find_return_flights(iata, date_from, date_to)

                    update_departures(codes, dests, prices, iata, event, new_date)
    return 1


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
            departures[code]['event_airport_name'].append(airports[iata])
        else:
            departures[code] = dict()
            departures[code]['origin'] = dest
            departures[code]['event'] = [event]
            departures[code]['date'] = [date]
            departures[code]['price'] = [price]
            departures[code]['event_airport'] = [iata]
            departures[code]['event_airport_name'] = [airports[iata]]

def sort_departures():

    countries_fullname = []
    country2short = dict()

    for country in countries_list:
        country_name = pycountry.countries.get(alpha_2=country).name
        countries_fullname.append(country_name)
        country2short[country_name] = country 

    countries = set(countries_fullname)
    countries = sorted(countries)
    cities = dict()

    for country in countries:
        cities[country] = sorted(cities_list[country2short[country]])

    return countries, cities


def main():
    csv = 'data/Tour-dates.csv'
    df = pd.read_csv(csv, sep=';')
    reset_vars()

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

    st.markdown(""" <style> .text2 {
    font-size:20px ; font-family: 'Cooper Black';} 
    </style> """, unsafe_allow_html=True)

    st.markdown(""" <style> .shows {
    font-size:25px ; font-family: 'Cooper Black'; color: #FF9633;} 
    </style> """, unsafe_allow_html=True)

    st.markdown(""" <style> .credits {
    font-size:12px ; font-family: 'Cooper Black'; color: #FF9633;} 
    </style> """, unsafe_allow_html=True)


    # Band logo
    st.image('data/Logo-nanowar.png')

    #logo_link = ''
    #st.markdown(logo_link, unsafe_allow_html=True)

    # Create the actual streamlit stuff
    st.markdown('<p class="title">IN THE SKY SCANNER</p>', unsafe_allow_html=True)
    st.markdown('<p class="text2">Catch Nanowar Of Steel on Tour on the wings of a Barbagianni</p>', unsafe_allow_html=True)
    #st.markdown('<p>Catch Nanowar Of Steel on Tour on the wings of a Barbagianni</p>', unsafe_allow_html=True)

    # Initialize and plot the map
    map_init(m, df)
    folium_static(m, width=800, height=600)

    # Only show these columns in the general table
    col_keep = ['Event date', 'Event name', 'Country', 'City', 'Website']

    st.markdown('<p class="shows"><br>TOUR MANAGERS TOUR</p>', unsafe_allow_html=True)
    print('STREAMLIT TOUR MANAGERS')
    concerts_text = html_pages.concerts_html(df)
    st.write(concerts_text, unsafe_allow_html=True)
    countries, cities = sort_departures()

    st.write("<br>", unsafe_allow_html=True)
    st.markdown('<p class="shows"> Find your way to the shows!</p>', unsafe_allow_html=True)
    st.markdown('<p class="text2"> Are you a Nanowarrior looking for a show? If we are not performing anywhere near you, do not worry. </p>', unsafe_allow_html=True)
    st.markdown('<p class="text2"> The TOUR MANAGERS are here to help you!</p>', unsafe_allow_html=True)
    st.markdown('<p class="text2"> Choose your origin country and city, we will show you the cheapest (Ryanair) options for return flights to \
            any of our TOUR MANAGERS shows.</p>', unsafe_allow_html=True)
    st.markdown('<p class="text2"> See you on the road! </p>', unsafe_allow_html=True)
    
    st.markdown('<p class="text2">Select a timespan to perform the search. How many days before a show do you want to leave? How many days after?</p>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5  = st.columns([1, 1, 3, 3, 2])
    
    departures_text = ''

    #print(departures)

    def refresh_connections(search_timeframe): 
        print('Refreshing flight connections...')

        try:
            update_flights_time_range(days_before, days_after, df, date_event=search_timeframe)
            success = True
        except:
            departures_text = '<p><b>NO CONNECTIONS AVAILABLE FOR THE SELECTED DATES </b></p>'
        
        if success:
            code = city2airports[choose_city]

            if code in departures.keys():
                departures_text = html_pages.departures_html(departures[code])

        return departures_text

    #countries = ['Liechtenstein', 'Austria']
    #cities = {'Liechtenstein':['Formia'], 'Austria':['Vienna']}


    with st.form('country'):
        choose_country = st.selectbox('Departure country:', countries)
        out1 = st.form_submit_button('Refresh city list')


    with st.form('city'):
        search_timeframe = st.checkbox('Search over time span (if not selected search exact dates)', value=True)
        days_before = st.selectbox('Before', [7,6,5,4,3,2,1,0])
        days_after = st.selectbox('After', [7,6,5,4,3,2,1])
        choose_city = st.selectbox('Departure city: ', cities[choose_country])
        out2 = st.form_submit_button('Submit')

        if out2:
            reset_vars()
            departures_text = refresh_connections(search_timeframe)
            #print(departures)
            st.write(departures_text, unsafe_allow_html=True)

    #st.write(departures_text, unsafe_allow_html=True)
    #st.stop()

    st.markdown('<p class="credits"><br><br><br>Engineered and coded by Gatto Panceri 666, concept by Tiziana Pinessi</p>', unsafe_allow_html=True)
    st.markdown('<p class="credits">For technical questions, check out the freely available <a href="https://github.com/EdoardoCarlesi/tour_manager" target="_blank"> source code </a>or get in touch with the <a href="mailto:gatto@nanowar.it">webmaster</a></p>', unsafe_allow_html=True)


if __name__ == '__main__':

    main()

