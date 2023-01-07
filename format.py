import re
from nltk.tokenize import wordpunct_tokenize

__patterns = {
    'numbering': r'^(\d{2}|\d{1})(\s*(\.|-)?\s*)',
    'year': r'^\d{4} - ',
    'symbols': r'([^\w ]|_)',
    'brackets': r'(\(|\[|\{)(.*)(\)|\]|\})',
    'miscs': r'(\s*(\.|-)?\s*)(Outtake|Studio Outtake|Live|Alternate Take) .*',
    'quality': r'320|128'
}


track_profile = [__patterns['numbering'], __patterns['brackets'],
                 __patterns['symbols'], __patterns['miscs']]

album_profile = [__patterns['year'],
                 __patterns['brackets'], __patterns['symbols'],
                 __patterns['quality']]


def format_title(title: str, profile: list, artist_name='') -> str:
    '''
    Formats a song\\album title by removing unwanted characters and words.
    params
        title: str
            The title to be formatted
        profile: list
            The regex list used for formatting.

    '''
    formatted = title

    if artist_name:
        formatted = re.sub(artist_name + r'\s*-\s*', '', formatted)
    for ptrn in profile:
        formatted = re.sub(ptrn, '', formatted)
    formatted = formatted.strip()

    return formatted


def shared_subsequence(collection: list, threshold: float = 0.9) -> tuple:
    '''
    Returns a dictionary of shared, repeated words in a list of strings.\n
    In addition to the tokenizer used for consistency.\n
    params
        collection: `list`
            The list of strings to be compared.
        threshold: `float`
            The threshold for the common words to be included in the dictionary.
    '''

    # Handle '_', '.' in .mp3 to avoid tokenization issues
    for i in range(len(collection)):
        collection[i] = collection[i].replace('_', '')

    frequency = {}
    for item in collection:
        words = set(wordpunct_tokenize(item))
        for word in words:
            if word not in frequency:
                frequency[word] = 0
            frequency[word] += 1

    # Prevent '-' removal to avoid some issues
    if '-' in frequency:
        del frequency['-']

    shared = {}

    for word, count in frequency.items():
        if count >= int(threshold * len(collection)):
            per_item_freq = int(count / len(collection))
            shared[word] = per_item_freq if per_item_freq > 1 else 1

    return (shared, wordpunct_tokenize)


def filter(collection: list = None, title: str = "", ref: tuple = None, threshold: float = 0.9) -> any:
    '''
    Remove all occurances of substrings present in ALL strings in a list\n
    e.g, \n
    `['The Beatles - Abby Road', 'The Beatles - Revolver'] -> ['Abby Road', 'Revolver']`
    '''

    if not ref:
        shared, tokenizer = shared_subsequence(collection, threshold)
    else:
        shared, tokenizer = ref

    # String
    if title:
        for token in set(tokenizer(title)):
            if token in shared:
                title = title.replace(token, '', shared[token]).strip()

        return title

    # List
    if not collection:
        return

    if len(collection) == 1:
        return collection

    filtered = []
    for title in collection:
        for token in set(tokenizer(title)):
            if token in shared:
                title = title.replace(token, '', shared[token]).strip()
        filtered.append(title)

    return filtered
