import requests
import json
import os
import streamlit as st
import pandas as pd
import haversine as hs

class SongKick:

    def __init__(self, api_key=None, artist_id=None):
        self.api_key = api_key
        self.artist_id = artist_id

    def get_concerts(self):
        self.api_url_str = f'https://api.songkick.com/api/3.0/artists/{self.artist_id}/calendar.json?apikey={self.api_key}'
        response = requests.get(self.api_url_str)
        concerts = response.json()
        events = concerts['resultsPage']['results']['event']
        
        for event in events:
            print(event['displayName'], event['location']['city'])

        return events

    def past_concerts(self):
        self.api_url_str = f'https://api.songkick.com/api/3.0/artists/{self.artist_id}/gigography.json?apikey={self.api_key}'
        response = requests.get(self.api_url_str)
        concerts = response.json()
        events = concerts['resultsPage']['results']#['event']
        n_events = int(concerts['resultsPage']['totalEntries']) 

        if not n_events > 50:
            return events

        else:
            n_pages = int(n_events/50) + 1
            all_events = []

            for n_page in range(1, n_pages+1):
                new_url = self.api_url_str + '&page=' + str(n_page)
                response = requests.get(new_url)
                concerts = response.json()
                #print(concerts)
                events = concerts['resultsPage']['results']#['event']
                
                for event in events:
                    all_events.append(event)
        
            return all_events

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

    def future_events_to_csv(self):
        shows = self.get_concerts()
        columns = ['Event name','Event date','Country','City','Address','Website','IATA','distances']
        shows_file = 'data/Tour-dates.csv'
        
        rows = []
        
        for show in shows:
            event_name = show['displayName'].split('(')[0]
            event_date = show['start']['date']
            country = show['location']['city'].split(',')[-1]
            city = show['location']['city'].split(',')[0]

            # If we have the venue location then it's better otherwise we use the city one 
            lng = show['venue']['lng']            
            lat = show['venue']['lat']            
        
            if (lng == None) or (lat == None):
                lng = show['location']['lng']
                lat = show['location']['lat']
            
            address = show['venue']['metroArea']['displayName']
            website = show['uri']
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

    #shows = sk.past_concerts()
    #shows = sk.get_concerts()
    #print(len(shows))
    
    #sk.get_airports()
    sk.future_events_to_csv()
    #for show in shows:
    #    print(show['displayName'])


