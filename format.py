import re

__patterns = {
    'numbering': r'^(\d{2}|\d{1})(\s*(\.|-)?\s*)',
    'symbols': r'([^\w ]|_)',
    'brackets': r'(\(|\[\{)(.*)(\)|\]\})',
    'miscs': r'(\s*(\.|-)?\s*)(Outtake|Studio Outtake|Live|Demo|Alternate Take) .*'
}


track_profile = [__patterns['numbering'], __patterns['symbols'],
                 __patterns['brackets'], __patterns['miscs']]

album_profile = [__patterns['symbols'], __patterns['brackets']]


def format_title(title: str, profile: list, inplace=False) -> str:
    '''
    Formats a song\\album title by removing unwanted characters and words.
    params
        title: str
            The title to be formatted
        profile: list
            The regex list used for formatting.

    '''
    formatted = title

    for ptrn in profile:
        formatted = re.sub(ptrn, '', formatted)
    formatted = formatted.strip()

    return formatted
