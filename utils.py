import requests
import music_tag
import re
import math
import spotify
import os
from collections import Counter
from difflib import SequenceMatcher
from format import *
import format
from values_adapter import ValuesAdapter


def duration(path: str) -> int:
    '''
    Returns the duration of a song in milliseconds.
    '''
    audio_file = music_tag.load_file(path)
    return int(audio_file['#length']) * 1000


def download_cover(url: str, path: str) -> bytes:
    r = requests.get(url)

    if (os.path.exists(path)):
        os.remove(path)

    with open(path, 'wb') as f:
        f.write(r.content)

    return r.content


def set_audio_file_metadata(path, dict):
    audio_file = music_tag.load_file(path)

    for key, value in dict.items():
        del audio_file[key]
        audio_file[key] = value

    # audio_file.save()


def __lev_similarity(a, b):
    '''
    Calculate the Levenshtein Similarity between two strings
    '''
    return SequenceMatcher(None, a, b).ratio()


def __str_to_vector(text):
    '''
    Convert a string to a vector of words
    '''
    WORD = re.compile(r"\w+")
    words = WORD.findall(text)
    return Counter(words)


def __cos_similarity(a, b):
    '''
    Calculate the Cosine Similarity between two strings
    '''
    vec1 = __str_to_vector(a)
    vec2 = __str_to_vector(b)

    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def similarity(a, b):
    '''
    Calculate the similarity between two strings
    using Levenshtein or Cosine similarity.
    '''
    return max(__lev_similarity(a, b), __cos_similarity(b, a))


def __normalize(release_name: str) -> str:
    return release_name.lower().replace(' ', '')


def label_by_duration(local_release, sp_releases, release_type):
    '''
    Label each release with it's duration in a tuple
    '''

    total_duration = local_release['duration']

    labeled_releases = []
    for rel in sp_releases:
        sp_duration = 0

        if release_type == 'album':
            for track in rel['tracks']['items']:
                sp_duration += track['duration_ms']
        elif release_type == 'track':
            sp_duration = rel['duration_ms']

        labeled_releases.append((rel, sp_duration))

    # Sort by difference in duration (Should pick the minimum)
    # labeled_releases.sort(key=lambda x: (abs(x[1] - total_duration)))

    return labeled_releases


def get_corresponding_release(local_release: dict, sp_releases: list, release_type: str, custom_options: dict = None) -> tuple:
    '''
    Matches local song/album with the corresponding item on spotify.
    '''

    # Fingerprint matching:
    #   Album:
    #       [1] number of tracks
    #       [2] duration (ms)
    #   Track:
    #       [1] duration (ms)

    # Labeling each release with it's duration in a tuple
    labeled = label_by_duration(local_release, sp_releases, release_type)

    # if release_type == 'album':
    #     print(f'{total_duration/1000} -> {labeled_releases[0][1]/1000}')
    #     # number of tracks must match
    #     for rel in labeled_releases:
    #         if local_release['total_tracks'] == rel[0]['total_tracks']:
    #             return (True, rel[0])
    #     return (False, None)
    # elif release_type == 'track':
    #     return (True, labeled_releases[0][0])

    artist_name = sp_releases[0]['artists'][0]['name']  # hack

    profile = track_profile if release_type == 'track' else format.album_profile

    release_name = local_release['name']
    release_name = format_title(release_name, profile, artist_name)

    # NORMALIZATION
    # [1] Normalize Local release
    # [2] Normalize Spotify releases

    release_name = __normalize(release_name)

    # 3. NAME SIMILARITY
    threshold = 0.5 if release_type == 'track' else 0.80

    shared = shared_subsequence([rel['name'] for rel in sp_releases])

    # print(__normalize(
    #     format_title(
    #         filter(title='Sweet Thing/Candidate/Sweet Thing - Live; 2005 Mix; 2016 Remaster', ref=shared), profile)))

    sp_releases = [(rel[0], rel[1], -1 * similarity(release_name,
                                                    __normalize(
                                                        format_title(
                                                            filter(title=rel[0]['name'], ref=shared), profile)))) for rel in labeled]

    labeled.sort(key=lambda x: (x[1], x[2]))

    # if release_type == 'track' and custom_options.get('duration'):
    #     sp_releases.sort(key=lambda x: (
    #         abs(x[0]['duration_ms'] - custom_options['duration'])))

    # for rel in sp_releases:
    #     if rel[1] > threshold:
    #         ValuesAdapter.feed(f'thresh_{release_type}', rel[1])

    #         # Type-specific options
    #         # Albums: year, total_tracks
    #         if release_type == 'album':
    #             if custom_options:
    #                 if custom_options.get('year') and custom_options['year'] != rel[0]['release_date'][:4]:
    #                     continue

    #                 if custom_options.get('total_tracks') and custom_options['total_tracks'] != rel[0]['total_tracks']:
    #                     continue

    #         return (True, rel[0])

    return (False, None)


def strip_if_exists(local_release: str, sp_release: list) -> str:
    '''
    Strip commonly appearing words from local release if they exist in spotify release
    e.g, `release-year`, `artist-name` etc.
    '''

    stripped = []

    # 1- Release year
    year = sp_release['release_date'].split('-')[0]
    stripped.append(year)

    for word in stripped:
        if word in local_release:
            local_release = local_release.replace(word, '').strip()

    return local_release
