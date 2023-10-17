from typing import Optional, Tuple

from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.session import Session
from tracardi.service.utils.languages import language_codes_dict
from tracardi.service.utils.parser import parse_accept_language


def get_continent(tracker_payload) -> Optional[str]:
    if 'time' in tracker_payload.context:
        tz = tracker_payload.context['time'].get('tz', 'utc')

        if tz.lower() != 'utc':
            continent = tz.split('/')[0]
        else:
            continent = 'n/a'

        return continent

    return None


def get_spoken_languages(session: Session, tracker_payload: TrackerPayload) -> Tuple[list, list]:
    spoken_languages = []
    language_codes = []
    try:
        if 'headers' in tracker_payload.request and 'accept-language' in tracker_payload.request['headers']:
            languages = parse_accept_language(tracker_payload.request['headers']['accept-language'])
            if languages:
                spoken_lang_codes = [language for (language, _) in languages if len(language) == 2]
                for lang_code in spoken_lang_codes:
                    if lang_code in language_codes_dict:
                        spoken_languages += language_codes_dict[lang_code]
                        language_codes.append(lang_code)

        if session.device.geo.country.code:
            lang_code = session.device.geo.country.code.lower()
            if lang_code in language_codes_dict:
                spoken_languages += language_codes_dict[lang_code]
                language_codes.append(lang_code)
    except Exception:
        pass

    return spoken_languages, language_codes
