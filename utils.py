import requests
import music_tag
import re
from difflib import SequenceMatcher


def set_auth_header(TOKEN):
    return {'Authorization': f'Bearer {TOKEN}'}


allowed_formats = ['mp3', 'wav', 'flac', 'ogg']


def download_cover(url, path):
    r = requests.get(url)

    with open(path, 'wb') as f:
        f.write(r.content)

    return r.content


def set_audio_file_metadata(path, dict):

    audio_file = music_tag.load_file(path)

    for key, value in dict.items():
        del audio_file[key]
        audio_file[key] = value

    audio_file.save()


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def __normalize_tack_name(track_name):
    removed_chars = ['!', '?', '.', ',', ' ', "'", "the"]

    norm_track_name = track_name.lower()
    for char in removed_chars:
        norm_track_name = norm_track_name.replace(char, '')

    norm_track_name = re.sub(r'\([^)]*\)', '', norm_track_name)

    return norm_track_name


def is_album_member(track_name, track_list):

    # NORMALIZATION
    norm_track_name = __normalize_tack_name(track_name)

    norm_track_list = track_list.copy()
    for i in range(len(norm_track_list)):
        norm_track_list[i] = __normalize_tack_name(norm_track_list[i])

    try:
        return (True, track_list[norm_track_list.index(norm_track_name)])
    except:
        pass

    # SIMILARITY
    for track in norm_track_list:
        if similarity(norm_track_name, track) > 0.8:
            return (True, track_list[norm_track_list.index(track)])

    return (False, None)
