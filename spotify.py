import os
import requests
from utils import *

os.system('cls || clear')

# temporary token for testing
TOKEN = 'BQBsIOW2ZJG3BGwaBFEzPDNRTOQu79Fwl0WpcQ2RjmcvQYkS49IYXcJIwJiAiYVfS__ccIq3BhsifFv46xsIP8V-okM7iyH8GE8kK3T4l6JEqUodzmnuSacPTItz9JVysODhqFO-Xqv0GX5Rq-S0a9dFBfcMQ2TcdaLw8tOtrjJ2yJn6Rni5aBiqyXp6A4w'


def __del__markets(list):
    for item in list:
        del item['available_markets']


def get_album(album_title, artist_name=None):
    response = requests.get(f'https://api.spotify.com/v1/search?q={album_title}&type=album',
                            headers={'Authorization': f'Bearer {TOKEN}'})

    raw_results = response.json()['albums']['items']

    filtered_results = []
    for result in raw_results:
        if result['name'].replace(' ', '').lower() == album_title.replace(' ', '').lower():
            if artist_name:
                for artist in result['artists']:
                    if artist['name'] == artist_name:
                        filtered_results.append(result)
            else:
                filtered_results.append(result)

    album = filtered_results[0]

    del album['available_markets']

    return album


def get_album_tracks(album):
    album_id = album['id']
    response = requests.get(f'https://api.spotify.com/v1/albums/{album_id}/tracks?limit=40',
                            headers=set_auth_header(TOKEN))

    tracks = response.json()['items']

    __del__markets(tracks)

    return tracks
