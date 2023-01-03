import os
import requests
from utils import *

os.system('cls || clear')

# temporary token for testing
TOKEN = 'BQA4zQLMQhd-yJ5nUlScfgeEk7Bqi5cgov_IzyM_9D6r-_e8R5LmTLl_mCFkoyLuAn61BulA1KYpNDnpZtefxkVTrtHu7POTvrROOlQ73ohTtQ2-WNQroX2E5lkfRI6pSEaZC-nPIrMy4gXDo0OOzZEceQzIhFgn_uk2osBcOLM2ZRxf63wOlcVQ542fraQ'


def __del__markets(list):
    for item in list:
        del item['available_markets']


# 1- Get artist ID
# 2- Get artist albums
# 3- Match albums

def get_artist(artist_name):
    '''
    Returns the most popular artist ID for the given artist name
    '''
    response = requests.get(f'https://api.spotify.com/v1/search?q={artist_name}&type=artist',
                            headers={'Authorization': f'Bearer {TOKEN}'})

    # Return the most popular artist
    raw_results = response.json()['artists']['items']
    # raw_results.sort(key=lambda x: x['popularity'], reverse=True)
    return raw_results[0]['id']


def get_artist_albums(artist_id):
    '''
    Returns a list of albums IDs for the given artist ID
    '''

    # Keeps seeking albums and updating offset (max limit 40)

    limit = 50
    offset = 0

    prev_ids = []
    curr_ids = []
    total_ids = []

    while True:
        response = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}/albums?limit={limit}&offset={offset}',
                                headers={'Authorization': f'Bearer {TOKEN}'})

        prev_ids = curr_ids
        curr_ids = [album['id'] for album in response.json()['items']]

        if curr_ids == prev_ids:
            break

        offset += limit
        total_ids += curr_ids

    return total_ids


def get_album(album_id):
    '''
    Returns a dictionary of the album's info for the given album ID
    '''

    response = requests.get(f'https://api.spotify.com/v1/albums/{album_id}',
                            headers={'Authorization': f'Bearer {TOKEN}'})
    raw = response.json()

    desired_keys = ['name', 'release_date', 'genres', 'total_tracks',
                    'tracks', 'id', 'images', 'artists']

    res = {}
    for key in desired_keys:
        res[key] = raw[key]

    __del__markets(res['tracks']['items'])

    return res


def get_album_tracks(album):
    album_id = album['id']
    response = requests.get(f'https://api.spotify.com/v1/albums/{album_id}/tracks?limit=40',
                            headers=set_auth_header(TOKEN))

    tracks = response.json()['items']

    __del__markets(tracks)

    return tracks


def get_album_tracks(album):
    '''
    Returns a list of track IDs for the given album
    '''

    # Keeps seeking albums and updating offset (max limit 40)

    album_id = album['id']

    limit = 50
    offset = 0

    prev_tracks = []
    curr_tracks = []
    total_tracks = []

    while True:
        response = requests.get(f'https://api.spotify.com/v1/albums/{album_id}/tracks?limit={limit}&offset={offset}',
                                headers={'Authorization': f'Bearer {TOKEN}'})

        prev_tracks = curr_tracks
        curr_tracks = response.json()['items']

        if curr_tracks == prev_tracks:
            break

        offset += limit
        total_tracks += curr_tracks

    return total_tracks
