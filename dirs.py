from directory_tree import display_tree
import re
import os
from utils import duration
from format import *

__artist_dir = None

allowed_formats = ['mp3', 'wav', 'flac', 'ogg', 'm4a', 'wma']


def get_all_files(path):
    files = []

    dir_items = os.listdir(path)

    for item in dir_items:
        if os.path.isfile(os.path.join(path, item)):
            files.append(os.path.join(path, item))
        else:
            files.extend(get_all_files(os.path.join(path, item)))

    return files


def set_artist_dir(dir):
    global __artist_dir
    __artist_dir = dir


def fetch_local_tracks(album_path):
    '''
    Get all tracks in an album directory
    '''
    return [file for file in get_all_files(album_path) if file.split(
        '.')[-1].lower() in allowed_formats]


def fetch_local_albums(root_path=None, miscs=[], exclude=[]):
    '''
    Get all albums in an artist folder
    '''

    if root_path is None:
        root_path = __artist_dir

    albums = []

    for sub_dir in os.listdir(root_path):

        full_path = os.path.join(root_path, sub_dir)
        if sub_dir in exclude or \
                os.path.isfile(full_path):
            continue

        if sub_dir in miscs:
            albums.extend(fetch_local_albums(root_path=full_path))

        album = {
            'name': sub_dir.split('\\')[-1],
            'path': full_path,
            'tracks': [
                {
                    'name': track.split('\\')[-1],
                    'path': track,
                    'duration': duration(track)
                }
                for track in fetch_local_tracks(full_path)
            ],
        }
        album['duration'] = sum(
            [track['duration'] for track in album['tracks']])
        album['total_tracks'] = len(album['tracks'])

        albums.append(album)

    # clean_albums = filter(collection=[album[0] for album in albums])
    # return [(clean_albums[i], albums[i][1]) for i in range(len(albums))]

    return albums


def inspect(dir, level=0):
    whole_tree = display_tree(dir, True)

    if level == -1:
        print(whole_tree)
        return

    splitted_tree = whole_tree.splitlines()

    constructed_tree = ''
    constructed_tree += splitted_tree[0] + '\n'

    for line in splitted_tree:
        if re.match(r'^(│?(   )*){' + str(level) + r'}├── .*', line):
            constructed_tree += line + '\n'

    print(constructed_tree)
