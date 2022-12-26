import os
import music_tag
from utils import *
import spotify

os.system('cls || clear')

music_dir = f'C:/Users/{os.getlogin()}/Music'

artist = 'The Doors'

albums = os.listdir(f'{music_dir}/{artist}')[:-2]

for album in albums:
    album_title = album.split(' - ')[1]
    genre = "Rock"

    album_dir = f'{music_dir}/{artist}/{album}'

    sp_album = spotify.get_album(album_title, artist)
    sp_tracks = spotify.get_album_tracks(sp_album)
    sp_track_names = [track['name'] for track in sp_tracks]

    local_tracks = [track for track in os.listdir(
        album_dir) if track.split('.')[-1].lower() in allowed_formats]

    cover_path = f'{album_dir}/{album_title}.jpg'
    cover = download_cover(sp_album['images'][0]['url'],
                           cover_path)

    for track in local_tracks:
        track_title = track.split(' - ')[1].split('.')[0]

        is_found, sp_track_name = is_album_member(track_title, sp_track_names)
        if is_found:
            sp_track = sp_tracks[sp_track_names.index(sp_track_name)]

            track_path = f'{album_dir}/{track}'
            set_audio_file_metadata(
                track_path,
                {
                    'discnumber': sp_track['disc_number'],
                    'albumartist': sp_album['artists'][0]['name'],
                    'artist': sp_track['artists'][0]['name'],
                    'artwork': cover,
                    'discnumber': sp_track['disc_number'],
                    'genre': "Rock",  # TODO: get genre from spotify
                    'tracknumber': sp_track['track_number'],
                    'tracktitle': sp_track['name'],
                    'year': sp_album['release_date'].split('-')[0]
                })
        else:
            print(f'{track_title}')
            for track in sp_track_names:
                if similarity(track_title, track) > 0.6:
                    print(track)
                    print(similarity(track_title, track))

            print('=' * 50)
