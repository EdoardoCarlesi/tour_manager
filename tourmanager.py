import requests
import json
import os
import streamlit as st
import pandas as pd
import haversine as hs
import openrouteservice as ors
import geopandas as gpd 
import datetime as dt

class TourManager:

    def __init__(self, api_key=None, artist_id=None, gig_list=None):
        """ """
        
        self.client = ors.Client(key=api_key)
        #self.gig_list = pd.read_csv(gig_list)

    def distance(self, city1 : str, city2 : str) -> float: 
        """ """
        
        gps1 = gpd.tools.geocode(city1)['geometry'].values[0]
        gps2 = gpd.tools.geocode(city2)['geometry'].values[0]

        pt1 = (gps1.x, gps1.y)
        pt2 = (gps2.x, gps2.y)

        print(pt1, city1)

        geom = self.client.directions((pt1, pt2))['routes'][0]['summary']

        d_km = geom['distance'] / 1000.0
        d_time = geom['duration']
        
        d_time = dt.timedelta(seconds=d_time)
        d_time = str(d_time).split(':')
        
        return d_km, d_time


    def tour_to_csv(self):
        """ """

        pass


def main():
    """ Wrapper for main operations """

    aid = os.environ['ORS_USER']
    key = os.environ['ORS_API_KEY']
    
    if (key == '') or (aid == ''):
        aid = st.secrets['ORS_USER']
        key = st.secrets['ORS_API_KEY']
        
    gig_list = ''
    tm = TourManager(api_key=key, artist_id=aid, gig_list=gig_list)
    
    city1 = 'Milan, Italy'
    city2 = 'Zurich, Switzerland'
    dist, time = tm.distance(city1, city2)

    print(f'{city1} to {city2} is {dist}km {time[0]}h and {time[1]}m')
    
    return dist, time


if __name__ == '__main__':
    """ Execute main function """

    main()

