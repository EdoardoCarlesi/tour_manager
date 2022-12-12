import os
import time as t
import pandas as pd
import openrouteservice as ors
import geopandas as gpd 
import datetime as dt

class TourManager:

    def __init__(self, api_key=None, artist_id=None):
        """ Initialize the OpenRoute Service client """
        
        self.client = ors.Client(key=api_key)


    def clean_gigs(self, tour_dates : str, skip_first=0, skip_last=0):
        """ Clean the raw DF used for InTheSkyScanner """

        gigs_df = pd.read_csv(tour_dates)
        new_rows = []
        new_cols = ['Date', 'Venue', 'City']
        splits = [' at ', ' and ', ' with ']

        for i, row in gigs_df.iterrows():

            if i >= skip_first and i < (len(gigs_df) - skip_last):
                date = row['Event date']
                city = row['City'] + ', ' + row['Country']    
                name = []
    
                for ssplit in splits:
                    name_tmp = row['Event name'].split(ssplit)

                    if len(name_tmp) > len(name):
                        name = name_tmp

                ev_name = name[-1]   
                new_row = [date, ev_name, city]
                new_rows.append(new_row)
        
        # Add the estimated times + kilometers
        self.gigs = pd.DataFrame(new_rows, columns=new_cols)
        self.gigs.to_csv('data/tour_dates.csv', index=False)


    def add_days_off(self, origin):
        """ """
        pass


    def manage_tour(self, tour_dates : str):
        """ """

        self.gigs = pd.read_csv(tour_dates)

        n_gigs = len(self.gigs)
        cities = self.gigs['City']
    
        distances = []
        times = []

        for i in range(n_gigs-1):
            
            city1 = cities[i]
            city2 = cities[i+1]

            dist, time = self.distance(city1, city2)
            distances.append(dist)
            times.append(f'{time[0]}h : {time[1]} min')

            print(f'Trip from {city1} to {city2} takes {time[0]}h and {time[1]}min ({dist}km)')
            t.sleep(1)

        # The last step is already there
        distances.append(0)
        times.append('0')

        self.gigs['Distance to next city'] = distances
        self.gigs['Duration to next city'] = times

        self.gigs.to_csv('data/tour_dates_with_distances.csv')


    def distance(self, city1 : str, city2 : str) -> float: 
        """ """
        
        gps1 = gpd.tools.geocode(city1)['geometry'].values[0]
        gps2 = gpd.tools.geocode(city2)['geometry'].values[0]

        pt1 = (gps1.x, gps1.y)
        pt2 = (gps2.x, gps2.y)

        print(pt1, city1)
        print(pt2, city2)

        geom = self.client.directions((pt1, pt2), radiuses=2000)['routes'][0]['summary']

        if 'distance' in geom.keys():
            d_km = geom['distance'] / 1000.0
            d_time = geom['duration']
        
            d_time = dt.timedelta(seconds=d_time)
            d_time = str(d_time).split(':')
        
        else:
            d_km = 0
            d_time = ['0', '0', '0']

        return int(d_km), d_time


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
        
    #gig_list = 'data/Tour-dates.csv'
    gig_list = 'data/tour_dates_edit.csv'
    tm = TourManager(api_key=key, artist_id=aid)
    tm.manage_tour(gig_list)
    #tm.clean_gigs(gig_list, skip_first=5, skip_last=4)
    #city1 = 'Milan, Italy'
    #city2 = 'Zurich, Switzerland'
    #dist, time = tm.distance(city1, city2)
    #print(f'{city1} to {city2} is {dist}km {time[0]}h and {time[1]}m')


if __name__ == '__main__':
    """ Execute main function """

    main()

