import requests
import music_tag
import re
import math
import spotify
import os
from nltk.tokenize import word_tokenize, wordpunct_tokenize
from collections import Counter
from difflib import SequenceMatcher
from format import format_title, track_profile
import format
import copy
from values_adapter import ValuesAdapter


def set_auth_header(TOKEN):
    return {'Authorization': f'Bearer {TOKEN}'}


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


def __normalize_tack_name(track_name):
    removed_chars = ['!', '?', '.', ',', ' ', "'", "the"]

    norm_track_name = track_name.lower()
    for char in removed_chars:
        norm_track_name = norm_track_name.replace(char, '')

    norm_track_name = re.sub(r'\([^)]*\)', '', norm_track_name)

    return norm_track_name


def __norm_release(release_name: str) -> str:
    return release_name.lower().replace(' ', '')


# 1. Exact match
# 2. Normalization, formatting and matching
# 3. Similarity

def is_album_member(track_name, track_list):
    # 1. EXACT MATCH (WEAK)
    for track in track_list:
        if track_name == track:
            return (True, track)

    # 2. NORMALIZATION, FORMATTING AND MATCHING
    norm_track_name = __normalize_tack_name(
        format_title(track_name, track_profile))

    norm_track_list = track_list.copy()
    for i in range(len(norm_track_list)):
        norm_track_list[i] = rm_common(norm_track_list[i], track_list)
        norm_track_list[i] = __normalize_tack_name(
            format_title(norm_track_list[i], track_profile))

    match = None
    for track in norm_track_list:
        if norm_track_name in track or track in norm_track_name:
            match = track_list[norm_track_list.index(track)]
            break

    if match:
        return (True, match)

    # 3. SIMILARITY
    for track in norm_track_list:
        if similarity(norm_track_name, track) > 0.6:
            return (True, track_list[norm_track_list.index(track)])

    return (False, None)


def get_corresponding_release(local_release: str, sp_releases: list, release_type: str, search_first=True) -> tuple:
    '''
    Matches local song/album with the corresponding item on spotify.
    '''
    # TODO: sometimes artist's not accurate, ensure the artist by searching through
    artist_name = sp_releases[0]['artists'][0]['name']  # hack

    profile = track_profile if release_type == 'track' else format.album_profile

    local_release = format_title(local_release, profile, artist_name)

    if search_first:
        search_result = get_corresponding_release(local_release, spotify.search(
            f'{artist_name} {local_release}', release_type), release_type, search_first=False)

        if search_result[0]:
            return search_result

    # 1. EXACT MATCH (WEAK)
    for rel in sp_releases:
        if local_release == rel['name']:
            return (True, rel)

    # 2. NORMALIZATION AND MATCHING

    local_release = __norm_release(local_release)

    norm_sp_releases = copy.deepcopy(sp_releases)
    for i in range(len(norm_sp_releases)):
        norm_sp_releases[i]['name'] = remove_common([
            rel['name'] for rel in norm_sp_releases])[i]

        norm_sp_releases[i]['name'] = __norm_release(
            format_title(norm_sp_releases[i]['name'], profile))

    # 3. SIMILARITY
    threshold = 0.6 if release_type == 'track' else 0.70
    sim = 0
    for sp_rel in norm_sp_releases:
        sim = similarity(strip_if_exists(
            local_release, sp_rel), sp_rel['name'])
        if sim > threshold:
            ValuesAdapter.feed(f'thresh_{release_type}', sim)
            return (True, sp_releases[norm_sp_releases.index(sp_rel)])

    return (False, None)


def __common(ref: list, threshold: int) -> dict:
    # Handle '_', '.' in .mp3 to avoid tokenization issues
    for i in range(len(ref)):
        ref[i] = ref[i].replace('_', '')

    frequency = {}
    for item in ref:
        words = set(wordpunct_tokenize(item))
        for word in words:
            if word not in frequency:
                frequency[word] = 0
            frequency[word] += 1

    # Prevent '-' removal to avoid some issues
    if '-' in frequency:
        del frequency['-']

    common = {}

    for word, count in frequency.items():
        if count >= int(threshold * len(ref)):
            per_item_freq = int(count / len(ref))
            common[word] = per_item_freq if per_item_freq > 1 else 1

    return common


def rm_common(str: str, ref: list, threshold: int = 0.9) -> str:
    '''
    Remove common words present in a string with reference to a collection of strings\n
    `['The Beatles - Abby Road', 'The Beatles - Revolver'] -> ['Abby Road', 'Revolver']`
    '''

    if len(ref) == 1:
        return str

    common = __common(ref, threshold)

    for word, count in common.items():
        str = str.replace(word, '', count).strip()

    return str


def remove_common(list: list, threshold: int = 0.9) -> list:
    '''
    Remove all occurances of substrings present in ALL strings in a list\n
    e.g, \n
    `['The Beatles - Abby Road', 'The Beatles - Revolver'] -> ['Abby Road', 'Revolver']`
    '''

    if len(list) == 1:
        return list

    common = __common(list, threshold)

    new_list = []
    for str in list:
        for token in set(wordpunct_tokenize(str)):
            if token in common:
                str = str.replace(token, '', common[token]).strip()
        new_list.append(str)

    return new_list


def strip_if_exists(local_release: str, sp_release: list) -> str:
    '''
    Strip common words from local release if they exist in spotify release
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
