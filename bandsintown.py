import requests
import json
from geopy.geocoders import Nominatim
import os
import streamlit as st
import pandas as pd
import haversine as hs

class SongKick:

    def __init__(self, api_key=None, artist_id=None):
        self.api_key = api_key
        self.artist_id = artist_id

    def get_concerts(self):
        
            local_csv = 'data/Bandsintown_INPUT.csv'
            df = pd.read_csv(local_csv)
            return df

    def get_airports(self, lng, lat):
        """ Given the gps coordinates of a point we look for the three nearest airports """

        air_csv = 'data/osm-world-airports.csv'
        air_df = pd.read_csv(air_csv, sep=';')
        codes = ['']
        distances = ['']

        def airport_distance(x):
            pt1 = tuple([float(p) for p in x.split(',')])
            pt2 = (lat, lng)
            try:
                return hs.haversine(pt1, pt2)
            except:
                return 0

        air_df['distances'] = air_df['Geo Point'].apply(airport_distance)

        codes = list(air_df.sort_values(by=['distances'])['IATA code'].values[0:3])
        distances = list(air_df.sort_values(by=['distances'])['distances'].values[0:3])
        distances = [int(dist) for dist in distances]

        return codes, distances

    def get_coordinates(self, city, venue, country):
        """
        Get the latitude and longitude of a specific venue in a city and country.
        
        :param city: Name of the city
        :param venue: Name of the venue
        :param country: Name of the country
        :return: Tuple with latitude and longitude (or None if not found)
        """
        try:
            geolocator = Nominatim(user_agent="geo_locator")
            location = geolocator.geocode(f"{venue}, {city}, {country}")
            if location:
                return location.latitude, location.longitude
            else:
                return None  # Return None if the location is not found
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

    def future_events_to_csv(self):
        shows = self.get_concerts()
        columns = ['Event name','Event date','Country','City','Address','Website','IATA','distances']
        shows_file = 'data/Tour-dates.csv'
        
        rows = []
        
        for i, show in shows.iterrows():

            event_name = show['Event Name']
            event_date = show['Start Date* (yyyy-mm-dd)']
            country = show['Country*']
            city = show['City*']
            venue = show['Venue*']
    

            
            lat, lng = self.get_coordinates(city, '', country)
            print(venue, city, country, lng, lat)
            address = f'{venue}, {city}, {country}'
            website = show['Ticket Link']
            IATA, distances = self.get_airports(lng, lat)
            row = [event_name, event_date, country, city, address, website, IATA, distances]
            rows.append(row)

        shows_df = pd.DataFrame(rows, columns=columns)
        shows_df.to_csv(shows_file)


if __name__ == '__main__':

    aid = os.environ['SONGKICK_USER']
    key = os.environ['SONGKICK_API_KEY']
    
    if (key == '') or (aid == ''):
        aid = st.secrets['SONGKICK_USER']
        key = st.secrets['SONGKICK_API_KEY']
    
    
    sk = SongKick(api_key=key, artist_id=aid)
    sk.future_events_to_csv() 
    #sk.to_bandsintown_csv() 


