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
import os

# Local imports 
import html_pages
import edit_data as ed

# These variables will be used throughout the script
airports = airportsdata.load('IATA')
departures = dict()
cities_list = dict()
city2airports = dict()
event_airports_list = []
countries_list = []

#Drop some easter eggs
fictional_countries = ['Liechtenstein', 'Jugoslavija', 'Hujzbekistan', 'Nicaragua', 'Azerbaijan', 'Special Administrative Regions of Southern China']

special_countries = ['Italy', 'Germany', 'Spain']

for fict in fictional_countries:
    special_countries.append(fict)

special_cities = dict()

special_cities['Italy'] = ['Formia', 'Busto Arsizio']
special_cities['Germany'] = ['Freiburg im Geilsgau']
special_cities['Spain'] = ['Maricon']
special_cities['Liechtenstein'] = ['Vaduz', 'Downtown Schaan']
special_cities['Jugoslavija'] = ['Crnogradska Oblast', 'Kitograd']
special_cities['Hujzbekistan'] = ['Hujguryetski International Spaceport']
special_cities['Special Administrative Regions of Southern China'] = ['The Hunter Of The Night Airport']
special_cities['Nicaragua'] = ['404 NOT FOUND']
special_cities['Azerbaijan'] = ['404 NOT FOUND']


def update_airport_event_distance(data=None, departure=None):
    print('Updating airports event distances...')
    events_set = set()

    for event in departure['event']:
        distances = ed.str2list(data[data['Event name'] == event]['distances'].values[0])
        near_airports = ed.str2list(data[data['Event name'] == event]['IATA'].values[0])
        
        if event not in events_set:
            events_set.add(event)

            for distance, airp in zip(distances, near_airports):
                
                if airp in departure['event_airport']:
                    if 'distance_to_event' not in departure.keys():
                        departure['distance_to_event'] = [distance]
                    else:
                        departure['distance_to_event'].append(distance)
    
    return departure

# Reset some variables at each update / refresh
def reset_vars():
    departures.clear()

@st.cache_data
def safe_call_ryanair_return_apis(airport_code, date_from, date_to, return_from, return_to):
 
    ryanair = Ryanair("EUR")
    date_today = str(date.today())
    f_name = 'ryan_return_' + airport_code + date_from + date_to + date_today + '.pkl'
    f_tmp = os.path.join('tmp', f_name)
    
    try:
        trips = ryanair.get_return_flights(airport_code, date_from, date_to, return_from, return_to)
    except:
        print(f'No connection available from {airport_code}')
        trips = []

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

            # There is some name mismatch somewhere so let's just fix this
            if this_city == 'Rome':
                this_city = 'Roma'

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
            #coord = pkl.load(f)
            coord = pd.read_pickle(f)
    else:
        coord = gpd.tools.geocode(address, provider='arcgis')
        with open(f_tmp, 'wb') as f:
            pkl.dump(coord, f)

    return coord['geometry'].values[0]



def create_date_range(date, days_before, days_after):

    date_base = datetime.datetime.strptime(date, "%Y-%m-%d")
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

    concert_group = folium.FeatureGroup(name='Show shows').add_to(m)
    airport_group = folium.FeatureGroup(name='Show airports', show=False).add_to(m)

    # Geolocate all the gigs
    for i, row in df.iterrows():
        gps = geocode_address(row)
        gps1 = [gps.y, gps.x]
        coords.append(gps1)

    for i, row in df.iterrows():
        event = row['Event name']
        text = "<p>" + event + "</p>"

        for iata in ed.str2list(row['IATA']):
            event_airports_list.append(iata)

        iatas = ed.str2list(row['IATA'])
        popup_text = html_pages.popup_html(row)

        icon_show = CustomIcon(img_path, icon_size=(27, 38), icon_anchor=(13, 40)) 
        icon_text = DivIcon(icon_anchor=(0,0),
                            html="<p class='text'><b><em>" + row['City'].replace(' ', '_').replace('-', '_')  + "</em></b></p>")
    


        # Add the marker for the CONCERT location
        concert_marker = folium.Marker(coords[i], icon=icon_show, popup=popup_text, tooltip=text)
        concert_group.add_child(concert_marker)

        # Add the location's name
        concert_text = folium.Marker(coords[i], popup=popup_text, icon=icon_text)
        concert_group.add_child(concert_text)

        # Find the ryanair destinations
        for iata in iatas:

            if (len(iata) == 3) and iata.upper() != 'NAN':
                
                if iata in airports.keys():

                    # Initialize looking at all the shows one week before and after the show
                    date_from, date_to = create_date_range(row['Event date'], 7, 7)
                    new_date = row['Event date']
                    site = row['Website']
                    dests, prices, codes = find_return_flights(iata, date_from, date_to, date_event=new_date)
                    update_departures(codes, dests, prices, iata, event, new_date, site)

                    # Find the coordinate pair of the airport given its code
                    gps1 = iata2gps(iata)
                    
                    # Add a customized icon and some popup informations for the airport
                    air_name = airports[iata]['name']
                    air_text = html_pages.flights_html(airports[iata]['name'], dests, prices)
                    air_icon = CustomIcon(img_air_path, icon_size=(27, 38), icon_anchor=(13, 40)) 
                    
                    # Add a marker to the nearby airports
                    air_marker = folium.Marker(gps1, icon=air_icon, tooltip=air_name, popup=air_text)
                    airport_group.add_child(air_marker)           

    folium.LayerControl().add_to(m)



def update_flights_time_range(days_before, days_after, df, date_event=False):

    for i, row in df.iterrows():
        event = row['Event name']
        date = row['Event date']
        site = row['Website']
        iatas = ed.str2list(row['IATA'])

        for iata in iatas:
            if (len(iata) == 3) and iata.upper() != 'NAN':
                if iata in airports.keys():
                    date_from, date_to = create_date_range(date, days_before, days_after)
                    new_date = date

                    if date_event:
                        dests, prices, codes = find_return_flights(iata, date_from, date_to, date_event=new_date)
                    else:
                        dests, prices, codes = find_return_flights(iata, date_from, date_to)

                    update_departures(codes, dests, prices, iata, event, new_date, site)
    return 1


def update_departures(codes, dests, prices, iata, event, date, site):
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
            departures[code]['site'].append(site)
            departures[code]['event_airport'].append(iata)
            departures[code]['event_airport_name'].append(airports[iata])
        else:
            departures[code] = dict()
            departures[code]['origin'] = dest
            departures[code]['event'] = [event]
            departures[code]['date'] = [date]
            departures[code]['price'] = [price]
            departures[code]['site'] = [site]
            departures[code]['event_airport'] = [iata]
            departures[code]['event_airport_name'] = [airports[iata]]


def sort_departures():
    """ Sort departure locations by city name """

    countries_fullname = []
    country2short = dict()

    for country in countries_list:
        country_name = pycountry.countries.get(alpha_2=country).name
        countries_fullname.append(country_name)
        country2short[country_name] = country 

    for special in special_countries:
        countries_fullname.append(special)

    countries = set(countries_fullname)
    countries = sorted(countries)
    cities = dict()

    for country in countries:
        if country in special_countries:
            for city in special_cities[country]:
                if country not in fictional_countries:
                    
                    try:
                        cities_list[country2short[country]].append(city)
                    except:
                        print(f'Problems with country key: {country}')
                else:
                    if country in cities_list.keys():
                        cities_list[country].append(city)
                    else:
                        cities_list[country] = [city]

        if country not in fictional_countries:
            try:
                cities[country] = sorted(cities_list[country2short[country]])
            except:
                print(f'Problems with country key: {country}')

    return countries, cities


def main():
    """ Wrapper """

    # TODO make this a function that scrapes the gigs from SONGKICK
    csv = 'data/Tour-dates.csv'
    tour_name = 'DEATH TO FALSE TOURS'
    df = pd.read_csv(csv)
    reset_vars()

    # Center the map on some city around the center of Europe
    eu_center = {'Country':'Germany', 'City':'Darmstadt'}
    map_center = geocode_address(eu_center)

    # This tile style is so FEUDALE
    #tile = 'stamenwatercolor'
    tile = 'mapquestopen'

    # Create the folium map. We don't want the tile name to appear in the legend so we initialize it separately
    m = folium.Map(location=[map_center.y, map_center.x], tiles=None, zoom_start=4) #, attr='WorldTour') 
    #tile_layer = folium.TileLayer(tiles=tile, control=False)
    tile_layer = folium.TileLayer(control=False)
    tile_layer.add_to(m)

    #st.set_page_title('In The Sky Scanner')
    img_air_path = 'data/B_icon.png'
    st.set_page_config(page_title='In The Sky Scanner', page_icon=img_air_path)

    # Define some custom styles for the fonts to be used
    st.markdown(""" <style> .title {
    font-size:50px ; font-family: 'Cooper Black'; color: #FF9633;} 
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
    #st.image('data/Logo-nanowar.png')
    
    # SITE LOGO
    st.image('data/intheskyscanner_logo.png')

    # TODO make this an image with an embedded href link to www.nanowar.it
    #logo_link = ''
    #st.markdown(logo_link, unsafe_allow_html=True)

    # Create the actual streamlit stuff
    #st.markdown('<p class="title">IN THE SKY SCANNER</p>', unsafe_allow_html=True)
    st.markdown('<p class="text2">Catch Nanowar Of Steel on Tour on the wings of a Barbagianni</p>', unsafe_allow_html=True)

    # Initialize and plot the map
    map_init(m, df)
    folium_static(m, width=800, height=600)

    # Only show these columns in the general table
    col_keep = ['Event date', 'Event name', 'Country', 'City', 'Website']

    # Write stuff on the home page
    st.markdown(f'<p class="shows"><br>{tour_name} TOUR</p>', unsafe_allow_html=True)
    concerts_text = html_pages.concerts_html(df)
    st.write(concerts_text, unsafe_allow_html=True)
    st.write('<br><p class="text2">Powered by <a href="http://www.songkick.com" target="_blank">SongKick</a></p>', unsafe_allow_html=True)
    st.image('data/songkick_logo2.png', width=200)
    countries, cities = sort_departures()

    # Basic information on the website
    st.write("<br>", unsafe_allow_html=True)
    st.markdown('<p class="shows"> Find your way to the shows!</p>', unsafe_allow_html=True)
    st.markdown('<p class="text2"> Are you a Nanowarrior looking for a show? If we are not performing anywhere near you, do not worry. </p>', unsafe_allow_html=True)
    st.markdown('<p class="text2"> The TOUR MANAGERS are here to help you!</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="text2"> Choose your origin country and city, we will show you the cheapest (Ryanair) options for return flights to \
            any of our {tour_name} Tour shows.</p>', unsafe_allow_html=True)
    st.markdown('<p class="text2"> See you on the road! </p>', unsafe_allow_html=True)
    
    st.markdown('<p class="text2">Select a timespan to perform the search. How many days before a show do you want to leave? How many days after?</p>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5  = st.columns([1, 1, 3, 3, 2])
 
    # Initialize empty text
    departures_text = ''

    # Refresh the flight connections, if search_timeframe=True it means we won't query the exact dates but a range of dates
    def refresh_connections(search_timeframe): 
        print('Refreshing flight connections...')
        departures_text = '<p><b>NO CONNECTIONS AVAILABLE FROM THE SELECTED CITY FOR THE SELECTED DATES </b></p>'

        try:
            update_flights_time_range(days_before, days_after, df, date_event=search_timeframe)
            success = True
            print('Flights updated for the specified time range') 
        except:
            success = False
            print('Flights update did not succeed, maybe there are no connections during the selected dates')
        
        if success:
            code = city2airports[choose_city]

            if code in departures.keys():
                departure = update_airport_event_distance(data=df, departure=departures[code])
                departures_text = html_pages.departures_html(departure)

        return departures_text

    # We need to do two separate forms, otherwise the city will not be refreshed correctly
    with st.form('country'):
        choose_country = st.selectbox('Choose your country of departure:', countries)
        out1 = st.form_submit_button('Refresh city list')


    # This second form has to be reloaded once the country has been chosen, otherwise streamlit won't updade the dict cities[country] in real time
    with st.form('city'):

        submit_text = 'Submit'

        # This is the standard behavior
        if choose_country not in fictional_countries:
            choose_city = st.selectbox('Select your city of departure: ', cities[choose_country])

        # Special cities are stored in a separate dictionary
        else:
            choose_city = st.selectbox('Select your city of departure: ', special_cities[choose_country])

        if choose_country == 'Liechtenstein':
            days_before = st.selectbox('Days before the show', [1, 2, 7, 160])
            days_after = st.selectbox('Days after the show', [1, 2, 7, 160])
            submit_text = 'Hail!'

        elif choose_country == 'Jugoslavija':
            days_before = st.selectbox('Days before the show', [166])
            days_after = st.selectbox('Days after the show', [144])
            submit_text = 'Kita!'

        elif choose_country == 'Germany':
            search_timeframe = st.checkbox('Search over time range. If not selected, it will only look for flights on the exact number of days before/after the show.', value=True)
            days_before = st.selectbox('Days before the show', [1, 2, 3, 28])
            days_after = st.selectbox('Days after the show', [1, 2, 3, 28])

        elif choose_country == 'Hujzbekistan':
            days_before = st.selectbox('Days before the show', [144])
            days_after = st.selectbox('Days after the show', [166])
            submit_text = '8===D'
    
        elif choose_country in ['Nicaragua', 'Azerbaijan']:
            submit_text = 'This is not a submit button'

        elif choose_country == 'Special Administrative Regions of Southern China':
            submit_text = 'Fly!'
            
        else:
            search_timeframe = st.checkbox('Search over time range. If not selected, it will only look for flights on the exact number of days before/after the show.', value=True)
            days_before = st.selectbox('Days before the show', [7,6,5,4,3,2,1,0])
            days_after = st.selectbox('Days after the show', [7,6,5,4,3,2,1])
        
        out2 = st.form_submit_button(submit_text) 

        # When pressing submit do the actual research
        if out2:

            if choose_city == 'Vaduz':
                departures_text = '<br><b>You cannot really fly anywhere from Liechtenstein but you can still get the A13.</b>'

            elif choose_city == 'Downtown Schaan':
                departures_text = '<br><b>Where do you think you are going? Stay here and enjoy the busty Liechtensteinerinnen!</b>'

            elif choose_city == 'Crnogradska Oblast':
                departures_text = '<br><b>Kita</b>'

            elif choose_city == 'Kitograd':
                departures_text = '<br><b>Kurac</b>'

            elif choose_city == 'Maricon':
                departures_text = '<br><b>Aqui tenemos solo chorizo humano, no hay vuelos</b>'

            elif choose_city == 'Freiburg im Geilsgau':
                departures_text = '<br><b>Hier kosten die Reise nur Schwanzig euro! Schwanztastisch</b>'

            elif choose_country == 'Hujzbekistan':
                departures_text = '<br><b>Are you ready to land a shuttle on Uranus? The tickets are paid by the tooth fairy!</b>'
                
            elif choose_city == 'Busto Arsizio':
                departures_text = '<br><b>Flying from the Glory Of Busto Arsizio is always free of charge<b>'
            
            elif choose_city == 'The Hunter Of The Night Airport':
                departures_text = '<br><b>You can fly to Laos, Paraguay or Dutch Guyana from here! Enjoy!'
            
            elif choose_city == 'Formia':
                departures_text = '<br><b>Formia is a FINAL destination, you cannot fly anywhere from there<b>'
            else:
                # This clears the departures dict() from all the previous entries
                reset_vars()
                departures_text = refresh_connections(search_timeframe)
            
            st.write(departures_text, unsafe_allow_html=True)

    st.markdown('<p class="credits"><br><br><br>Engineered and coded by Gatto Panceri 666, concept by Tiziana Pinessi</p>', unsafe_allow_html=True)
    st.markdown('<p class="credits">For technical questions, check out the freely available <a href="https://github.com/EdoardoCarlesi/tour_manager" target="_blank"> source code </a>or get in touch with the <a href="mailto:gatto@nanowar.it">webmaster</a></p>', unsafe_allow_html=True)


if __name__ == '__main__':

    main()

