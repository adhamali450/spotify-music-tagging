from directory_tree import display_tree
import re
import os
from utils import remove_common
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


def fetch_local_albums(miscs=[], exclude=[], format=True):
    albums = []

    for album in os.listdir(__artist_dir):
        if album in exclude or \
                os.path.isfile(os.path.join(__artist_dir, album)):
            continue

        if album not in miscs:

            # title = format_title(album, album_profile) if format else album
            albums.append((album, os.path.join(__artist_dir, album)))
        else:
            utils_path = os.path.join(__artist_dir, album)

            for album in os.listdir(utils_path):
                # title = format_title(album, album_profile) if format else album
                albums.append((album, os.path.join(utils_path, album)))

    # TODO: refactor
    clean_albums = filter(collection=[album[0] for album in albums])
    return [(clean_albums[i], albums[i][1]) for i in range(len(albums))]


def fetch_local_tracks(album_path):
    '''
    Get all tracks in an album folder
    '''
    return [track for track in get_all_files(album_path) if track.split(
        '.')[-1].lower() in allowed_formats]


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
