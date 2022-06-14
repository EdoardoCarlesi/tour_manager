import requests
import json
import os


class SongKick:

    def __init__(self, api_key=None, artist_id=None):
        self.api_key = api_key
        self.artist_id = artist_id

    def get_concerts(self):
        self.api_url_str = f'https://api.songkick.com/api/3.0/artists/{self.artist_id}/calendar.json?apikey={self.api_key}'
        response = requests.get(self.api_url_str)
        concerts = response.json()
        events = concerts['resultsPage']['results']['event']
        return events

    def past_concerts(self):
        self.api_url_str = f'https://api.songkick.com/api/3.0/artists/{self.artist_id}/gigography.json?apikey={self.api_key}'
        response = requests.get(self.api_url_str)
        concerts = response.json()
        events = concerts['resultsPage']['results']['event']
        n_events = int(concerts['resultsPage']['totalEntries']) 

        if not n_events > 50:
            return events

        else:
            n_pages = int(n_events/50) + 1
            all_events = []

            for n_page in range(1, n_pages+1):
                new_url = self.api_url_str + '&page=' + str(n_page)
                print(new_url)
                response = requests.get(new_url)
                concerts = response.json()
                #print(concerts)
                events = concerts['resultsPage']['results']['event']
                
                for event in events:
                    all_events.append(event)
        
            return all_events


if __name__ == '__main__':

    aid = '2322758'
    key = os.environ['SONGKICK_API']
    sk = SongKick(api_key=key, artist_id=aid)

    shows = sk.past_concerts()
    print(len(shows))
    for show in shows:
        print(show['displayName'])
