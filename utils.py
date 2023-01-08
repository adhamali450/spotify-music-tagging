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


def get_corresponding_release(local_release: str, sp_releases: list, release_type: str, custom_options: dict = None) -> tuple:
    '''
    Matches local song/album with the corresponding item on spotify.
    '''

    # TODO: sometimes artist's not accurate, ensure the artist by searching through
    artist_name = sp_releases[0]['artists'][0]['name']  # hack

    profile = track_profile if release_type == 'track' else format.album_profile

    local_release = format_title(local_release, profile, artist_name)

    # NORMALIZATION
    # [1] Normalize Local release
    # [2] Normalize Spotify releases

    local_release = __normalize(local_release)

    # 3. SIMILARITY
    threshold = 0.5 if release_type == 'track' else 0.80

    shared = shared_subsequence([rel['name'] for rel in sp_releases])

    # print(__normalize(
    #     format_title(
    #         filter(title='Sweet Thing/Candidate/Sweet Thing - Live; 2005 Mix; 2016 Remaster', ref=shared), profile)))

    sp_releases = [(rel, similarity(local_release,
                                    __normalize(
                                        format_title(
                                            filter(title=rel['name'], ref=shared), profile)))) for rel in sp_releases]

    sp_releases.sort(key=lambda x: (x[1]), reverse=True)

    if release_type == 'track' and custom_options.get('duration'):
        sp_releases.sort(key=lambda x: (
            abs(x[0]['duration_ms'] - custom_options['duration'])))

    for rel in sp_releases:
        if rel[1] > threshold:
            ValuesAdapter.feed(f'thresh_{release_type}', rel[1])

            # Type-specific options
            # Albums: year, total_tracks
            if release_type == 'album':
                if custom_options:
                    if custom_options.get('year') and custom_options['year'] != rel[0]['release_date'][:4]:
                        continue

                    if custom_options.get('total_tracks') and custom_options['total_tracks'] != rel[0]['total_tracks']:
                        continue

            return (True, rel[0])

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
