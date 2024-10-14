def _has_google_bot_header(request: dict) -> bool:
    try:
        return request['headers']['from'] == 'googlebot(at)googlebot.com'
    except KeyError:
        return False
