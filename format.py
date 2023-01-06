import re

__patterns = {
    'numbering': r'^(\d{2}|\d{1})(\s*(\.|-)?\s*)',
    'year': r'^\d{4} - ',
    'symbols': r'([^\w ]|_)',
    'brackets': r'(\(|\[|\{)(.*)(\)|\]|\})',
    'miscs': r'(\s*(\.|-)?\s*)(Outtake|Studio Outtake|Live|Alternate Take) .*'
}


track_profile = [__patterns['numbering'], __patterns['brackets'],
                 __patterns['symbols'], __patterns['miscs']]

album_profile = [__patterns['year'],
                 __patterns['brackets'], __patterns['symbols']]


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
