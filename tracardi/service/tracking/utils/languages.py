from typing import Optional, Tuple

from tracardi.domain.flat_session import FlatSession
from tracardi.domain.session import Session
from tracardi.common.db.languages import language_codes_dict
from tracardi.common.tools.parser import parse_accept_language


def get_continent(tracker_payload) -> Optional[str]:
    if 'time' in tracker_payload.context:
        tz = tracker_payload.context['time'].get('tz', 'utc')

        if tz.lower() != 'utc':
            continent = tz.split('/')[0]
        else:
            continent = 'n/a'

        return continent

    return None


def get_spoken_languages(flat_session: FlatSession, request: dict) -> Tuple[list, list]:
    spoken_languages = []
    language_codes = []
    try:
        if 'headers' in request and 'accept-language' in request['headers']:
            languages = parse_accept_language(request['headers']['accept-language'])
            if languages:
                spoken_lang_codes = [language for (language, _) in languages if len(language) == 2]
                for lang_code in spoken_lang_codes:
                    if lang_code in language_codes_dict:
                        spoken_languages += language_codes_dict[lang_code]
                        language_codes.append(lang_code)

        if flat_session.get('device.geo.country.code', None):
            lang_code = flat_session['device.geo.country.code'].lower()
            if lang_code in language_codes_dict:
                spoken_languages += language_codes_dict[lang_code]
                language_codes.append(lang_code)
    except Exception:
        pass

    return spoken_languages, language_codes
