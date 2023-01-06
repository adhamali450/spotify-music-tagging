import os
from utils import *
from dirs import set_artist_dir, fetch_local_albums, fetch_local_tracks
import spotify
import json
from utils import *
from rich import print
import time
from values_adapter import ValuesAdapter

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


os.system('cls || clear')

music_dir = f'C:/Users/{os.getlogin()}/Music'

artist = "Marilyn Manson"

set_artist_dir(f'{music_dir}/{artist}')
# albums = fetch_local_albums(
#     miscs=['1 - Studio'], exclude=['3 - Bootleg Series', '4 - Compilations', '2 - Live Albums'])

albums = fetch_local_albums(
    miscs=[], exclude=[])


sp_albums = fetch_artist_albums(artist)

print(f'👤 {artist}\n')

albums = [albums[9]]
for album in albums:

    album_name = album[0]
    album_dir = album[1]

    is_found, sp_album = get_corresponding_release(
        album_name, sp_albums, 'album')

    if not is_found:
        print(f'❌ {album_name}\n')
        continue

    print(f'💿 {album_name} -> [bold white on green] {sp_album["name"]} ')

    # ALBUM INFO
    cover_path = f'{album_dir}/{album_name}.jpg'
    album_cover = download_cover(sp_album['images'][0]['url'],
                                 cover_path)
    album_year = sp_album['release_date'].split('-')[0]
    album_artist = sp_album['artists'][0]['name']
    # album_genre = sp_album['genres'][0]
    album_genre = 'Rock'

    # TRACK-SPECIFIC INFO
    sp_tracks = spotify.get_album_tracks(sp_album)
    sp_track_names = [track['name'] for track in sp_tracks]

    local_tracks = fetch_local_tracks(album_dir)

    print(f'Found {len(sp_tracks)} for {len(local_tracks)}')

    failed = 0
    for track in local_tracks:

        track_name = track.split('\\')[-1]
        track_name = rm_common(track_name, [track.split('\\')[-1]
                                            for track in local_tracks])
        track_name = format_title(track_name, track_profile)

        is_found, sp_track_name = is_album_member(track_name, sp_track_names)

        if is_found:
            sp_track = sp_tracks[sp_track_names.index(sp_track_name)]

            # TRACK METADATA
            set_audio_file_metadata(
                track,
                {
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
                    track,
                    {
                        'artwork': album_cover,
                    })
            except:
                pass
        else:
            print(f'[red]{track_name}')
            failed += 1

    print(f'{failed}/{len(local_tracks)} failed\n')

    # command = input('Press Enter to continue... \n')

print("--- %s Seconds ---" % round(time.time() - start_time, 4))
print(f'Average album threshold: {ValuesAdapter.get("thresh_album")}')
print(f'Average track threshold: {ValuesAdapter.get("thresh_track")}')
