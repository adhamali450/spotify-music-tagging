import os
from utils import *
from dirs import *
import spotify
import json
from utils import *
from rich import print
import time
from values_adapter import ValuesAdapter
os.system('cls || clear')

start_time = time.time()


def fetch_artist_albums(artist, path='data'):
    '''
    Fetches artist albums from Spotify and saves them locally.
    Or loads them from local file if they exist.
    '''
    artist_id = spotify.get_artist(artist)

    if os.path.exists(f'{path}/{artist}.json'):
        with open(f'{path}/{artist}.json', 'r') as f:
            sp_albums = json.loads(f.read())
    else:
        print(f'Retrieving {artist} albums from Spotify...')

        sp_albums = [spotify.get_album(id)
                     for id in spotify.get_artist_albums(artist_id, ['appears_on', 'album', 'compilation', 'single'])]

        print(f'Saving locally...\n')
        with open(f'{path}/{artist}.json', 'w') as f:
            f.write(json.dumps(sp_albums))

    return sp_albums


music_dir = f'C:/Users/{os.getlogin()}/Music'
artist = "David Bowie"
set_artist_dir(f'{music_dir}/{artist}')

# albums = fetch_local_albums(
#     miscs=['1 - Studio'], exclude=['3 - Bootleg Series', '4 - Compilations', '2 - Live Albums'])

albums = fetch_local_albums(
    miscs=[], exclude=[])

sp_albums = fetch_artist_albums(artist)

print(f'👤 {artist}\n')

# albums = [albums[4]]
for album in albums:

    album_name = album['name']
    album_path = album['path']
    local_tracks = album['tracks']

    is_found, sp_album = get_corresponding_release(
        album, sp_albums, 'album', custom_options={'total_tracks': len(local_tracks)})

    if not is_found:
        print(f'❌ {album_name}\n')
        continue

    print(f'💿 {album_name} -> [bold white on green] {sp_album["name"]} ')

    # ALBUM INFO
    cover_path = f'{album_path}/{album_name}.jpg'
    album_cover = download_cover(sp_album['images'][0]['url'],
                                 cover_path)
    album_year = sp_album['release_date'].split('-')[0]
    album_artist = sp_album['artists'][0]['name']
    # album_genre = sp_album['genres'][0]
    album_genre = 'Rock'

    # TRACK-SPECIFIC INFO
    sp_tracks = spotify.get_album_tracks(sp_album)
    sp_track_names = [track['name'] for track in sp_tracks]

    print(f'Found {len(sp_tracks)} for {len(local_tracks)}', end='')

    failed = []

    track_names = [track['name'] for track in local_tracks]
    for track in local_tracks:

        track['name'] = filter(
            collection=track_names, title=track_name)
        track_name = track['name']

        is_found, sp_track = get_corresponding_release(
            track, sp_tracks, 'track', custom_options={'duration': track['duration']})

        if is_found:
            # TRACK METADATA
            set_audio_file_metadata(
                track['path'],
                {
                    'album': sp_album['name'],
                    'discnumber': sp_track['disc_number'],
                    'albumartist': album_artist,
                    'artist': sp_track['artists'][0]['name'],
                    'discnumber': sp_track['disc_number'],
                    'genre': album_genre,  # TODO: get genre from spotify
                    'tracknumber': sp_track['track_number'],
                    'tracktitle': sp_track['name'],
                    'year': album_year
                })

            # ALBUM COVER
            try:
                set_audio_file_metadata(
                    track['path'],
                    {
                        'artwork': album_cover,
                    })
            except:
                pass
        else:
            # print(f'[red]{track_name}')
            failed.append(track_name)

    print(
        f' -- [green]{round((1 - len(failed) / len(local_tracks)) * 100, 1)}%\n')

    for track in failed:
        print(f'[red]{track}')

    # print(f'{len(local_tracks) - failed}/{len(local_tracks)} Found\n')

    # command = input('Press Enter to continue... \n')

print("--- %s Seconds ---" % round(time.time() - start_time, 4))
print(f'Average album threshold: {ValuesAdapter.get("thresh_album")}')
print(f'Average track threshold: {ValuesAdapter.get("thresh_track")}')
print(f'HTTP requests made: {ValuesAdapter.get("requests")}')
